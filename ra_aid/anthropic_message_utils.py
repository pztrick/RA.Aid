"""Utilities for handling Anthropic-specific message formats and trimming."""

from typing import Callable, List, Literal, Optional, Sequence, Union, cast
from ra_aid.logging_config import get_logger

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    FunctionMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

logger = get_logger(__name__)


def _is_message_type(
    message: BaseMessage, message_types: Union[str, type, List[Union[str, type]]]
) -> bool:
    """Check if a message is of a specific type or types.

    Args:
        message: The message to check
        message_types: Type(s) to check against (string name or class)

    Returns:
        bool: True if message matches any of the specified types
    """
    if not isinstance(message_types, list):
        message_types = [message_types]

    types_str = [t for t in message_types if isinstance(t, str)]
    types_classes = tuple(t for t in message_types if isinstance(t, type))

    return message.type in types_str or isinstance(message, types_classes)


def has_tool_use(message: BaseMessage) -> bool:
    """Check if a message contains tool use.

    Args:
        message: The message to check

    Returns:
        bool: True if the message contains tool use
    """
    if not isinstance(message, AIMessage):
        return False

    # Check content for tool_use
    if isinstance(message.content, str) and "tool_use" in message.content:
        return True

    # Check content list for tool_use blocks
    if isinstance(message.content, list):
        for item in message.content:
            if isinstance(item, dict) and item.get("type") == "tool_use":
                return True

    # Check additional_kwargs for tool_calls
    if hasattr(message, "additional_kwargs") and message.additional_kwargs.get(
        "tool_calls"
    ):
        return True

    return False


def is_tool_pair(message1: BaseMessage, message2: BaseMessage) -> bool:
    """Check if two messages form a tool use/result pair.

    Args:
        message1: First message
        message2: Second message

    Returns:
        bool: True if the messages form a tool use/result pair
    """
    return (
        isinstance(message1, AIMessage)
        and isinstance(message2, ToolMessage)
        and has_tool_use(message1)
    )



def anthropic_trim_messages(
    messages: Sequence[BaseMessage],
    *,
    max_tokens: int,
    token_counter: Callable[[List[BaseMessage]], int],
    strategy: Literal["first", "last"] = "last",
    num_messages_to_keep: int = 2,
    allow_partial: bool = False,
    include_system: bool = True,
    start_on: Optional[Union[str, type, List[Union[str, type]]]] = None,
) -> List[BaseMessage]:
    """Trim messages to fit within a token limit, with Anthropic-specific handling.

    This function is designed to be robust for conversations that mix tool calls
    with regular text messages. It preserves the most recent messages while
    ensuring that tool call pairs (`AIMessage` + `ToolMessage`) are not broken.

    Args:
        messages: Sequence of messages to trim.
        max_tokens: Maximum number of tokens allowed.
        token_counter: Function to count tokens in messages.
        strategy: Whether to keep the "first" or "last" messages. Only "last" is robustly supported.
        num_messages_to_keep: Number of messages to always keep from the start (typically 2 for system prompt and initial user query).
        allow_partial: Not supported.
        include_system: If True, the first message is always kept if it's a system message.
        start_on: Not supported.

    Returns:
        List[BaseMessage]: A list of messages trimmed to fit the token limit.
    """
    if not messages:
        return []

    # Check if trimming is needed at all
    initial_tokens = token_counter(list(messages))
    if initial_tokens <= max_tokens:
        return list(messages)

    logger.debug(
        f"Trimming messages: initial_tokens={initial_tokens}, max_tokens={max_tokens}, messages={len(messages)}"
    )

    # Adjust num_messages_to_keep to not split a tool pair at the boundary.
    if (
        num_messages_to_keep > 0
        and len(messages) > num_messages_to_keep
        and is_tool_pair(
            messages[num_messages_to_keep - 1], messages[num_messages_to_keep]
        )
    ):
        num_messages_to_keep += 1

    # The first messages are always kept.
    kept_messages = messages[:num_messages_to_keep]
    remaining_msgs = messages[num_messages_to_keep:]

    kept_tokens = token_counter(kept_messages)
    logger.debug(f"Keeping first {len(kept_messages)} messages, tokens={kept_tokens}")

    # Segment the remaining messages into atomic units.
    # A segment is either a single message or an AIMessage + ToolMessage pair.
    segments = []
    i = 0
    while i < len(remaining_msgs):
        if i + 1 < len(remaining_msgs) and is_tool_pair(
            remaining_msgs[i], remaining_msgs[i + 1]
        ):
            # This is a tool pair, treat it as a single segment.
            segments.append([remaining_msgs[i], remaining_msgs[i + 1]])
            i += 2
        else:
            # This is a standalone message.
            segments.append([remaining_msgs[i]])
            i += 1

    # If using the "last" strategy, add segments from the end until the token limit is reached.
    if strategy == "last":
        result_messages = []
        # Iterate through segments in reverse order (newest to oldest).
        for segment in reversed(segments):
            segment_tokens = token_counter(segment)
            current_result_tokens = token_counter(result_messages)
            # Check if adding the next segment would exceed the token limit.
            # The check includes the always-kept messages and the messages already added to the result.
            if (kept_tokens + segment_tokens + current_result_tokens) > max_tokens:
                # Adding this segment would make the list too long, so we stop.
                logger.debug(
                    f"Cannot add segment ({len(segment)} messages, {segment_tokens} tokens). "
                    f"Total would be {kept_tokens + segment_tokens + current_result_tokens} > {max_tokens}. Stopping."
                )
                break

            logger.debug(
                f"Adding segment ({len(segment)} messages, {segment_tokens} tokens). "
                f"New total: {kept_tokens + segment_tokens + current_result_tokens} <= {max_tokens}"
            )
            # Prepend the segment to maintain chronological order in the final list.
            result_messages = segment + result_messages

        final_result = kept_messages + result_messages

        # Final validation: Ensure the last message is not an AIMessage with an unfulfilled tool call.
        if (
            final_result
            and isinstance(final_result[-1], AIMessage)
            and has_tool_use(final_result[-1])
        ):
            # This can happen if the last segment was a standalone AIMessage with a tool call.
            # To maintain a valid conversation state, we remove it.
            final_result.pop()

        final_tokens = token_counter(final_result)
        logger.debug(
            f"Trimming complete. Final messages: {len(final_result)}, final_tokens: {final_tokens}"
        )
        return final_result

    # Fallback for "first" strategy (less common for agent history)
    elif strategy == "first":
        result_messages = []
        for segment in segments:
            if (
                token_counter(kept_messages + result_messages + segment)
                > max_tokens
            ):
                break
            result_messages.extend(segment)
        return kept_messages + result_messages

    return list(messages)
