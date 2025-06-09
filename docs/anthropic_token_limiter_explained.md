# Understanding the Anthropic Token Limiter in RA.Aid

## Purpose

The `ra_aid/anthropic_token_limiter.py` script is designed to manage and truncate message histories to ensure they fit within the token limits of various language models, particularly Anthropic models. This is crucial for preventing API errors that can arise from exceeding these token limits in conversational AI agents.

## Core Functionality & How it Works

The script employs several mechanisms to count tokens, determine limits, and trim messages.

### 1. Token Counting

Accurate token counting is essential for effective limiting.

-   **`litellm.token_counter`**: This is the primary tool used for counting tokens. It offers support for a wide range of models.
-   **`convert_message_to_litellm_format(message)`**: This function plays a key role by preprocessing LangChain `BaseMessage` objects. It converts them into a dictionary format that is compatible with `litellm`. It handles various content types within messages, such as simple text, tool calls, and lists of content parts (e.g., for multimodal inputs or complex tool interactions), ensuring consistent input for `litellm`.
-   **`create_token_counter_wrapper(model)`**: This utility wraps `litellm.token_counter`. Its purpose is to allow the token counter to seamlessly handle `BaseMessage` objects by internally using the `convert_message_to_litellm_format` function.
-   **`estimate_messages_tokens(messages)`**: An alternative, likely simpler, method for token estimation. It uses `CiaynAgent._estimate_tokens`.

### 2. Determining Token Limits

The system dynamically determines the token limit for the specific model in use.

-   **`get_model_token_limit(config, agent_type, model)`**: This function is responsible for fetching the maximum input token limit.
    *   It first attempts to get this limit by querying `litellm.get_model_info()` for the model's `max_input_tokens`.
    *   If `litellm` does not provide the limit, the function falls back to a predefined dictionary named `models_params` (located in `ra_aid.models_params`). This dictionary stores token limits for various provider and model combinations. It tries to find the model using both its original name and a normalized version (with hyphens removed).
-   **`adjust_claude_37_token_limit(max_input_tokens, model)`**: This function provides specific handling for models identified as "Claude 3.7". If such a model has a `max_tokens` attribute (which typically defines the output token limit), this value is subtracted from the `max_input_tokens`. This suggests a particular way Claude 3.7's context window is calculated or managed.

### 3. Message Trimming (`state_modifier` function)

This is the core function where message history trimming occurs. It's designed to be integrated into an agent's state management lifecycle (e.g., within a LangGraph agent).

-   **Role**: To modify the agent's state by trimming the message history if it exceeds token limits.
-   **Inputs**: It takes the current agent `state` (which contains the message history), the `model` instance, and the `max_input_tokens` (obtained via `get_model_token_limit`).
-   **Uses `anthropic_trim_messages`**: The actual trimming logic is delegated to `anthropic_trim_messages` (from `ra_aid.anthropic_message_utils`).
-   **Trimming Strategy**:
    *   **Preservation of First Two Messages**: The first two messages in the history are always preserved. This common practice ensures that system prompts and/or initial user queries remain intact.
    *   **Handling Tool Pairs**: The trimming process ensures that tool call pairs (an `AIMessage` with a tool call followed by a `ToolMessage` with the result) are kept together and never split.
    *   **Trimming Older Messages**: For messages beyond the first two, trimming occurs from the "last" (i.e., the oldest among the non-preserved messages) if the total token count (calculated by the `wrapped_token_counter`) surpasses `max_input_tokens`.
    *   **Logging**: The system logs an event when trimming takes place.

### 4. Helper Functions

-   **`base_state_modifier`**: A more generic trimming function. It keeps the first message and uses LangChain's `trim_messages` for the rest of the history.
-   **`get_provider_and_model_for_agent_type`**: This function retrieves the provider and model names based on the agent type (e.g., "default", "research", "planner"). It sources this information from the configuration, which can be either a passed dictionary or a `ConfigRepository`.

## When it Triggers

The token limiting mechanism, specifically the message trimming performed by `state_modifier`, is triggered under the following conditions:

-   It is called as part of the agent's process, typically right before an API call is made to a language model.
-   It activates if the total token count of the current message history exceeds the dynamically determined `max_input_tokens` for the specific model being used.

## Tool Pairs and Claude's Message API

### What Are Tool Pairs?

Tool pairs are a critical concept when working with Claude models and function calling. A tool pair consists of:

1. An `AIMessage` containing a tool call or function invocation
2. A subsequent `ToolMessage` (or `FunctionMessage`) containing the result of that tool call

This pairing is essential for Claude's API to correctly understand the conversation flow involving tools.

### Why Tool Pairs Matter

Claude's message API has specific requirements regarding how tool calls and their responses must be structured:

- Tool calls and their responses must appear sequentially in the conversation history
- A tool call must always be followed by its corresponding response
- Breaking this pairing can lead to several issues:
  - API errors when Claude can't match tool calls to responses
  - Confusion in the model's understanding of the conversation state
  - Potential for the model to attempt to re-invoke tools that were already called

If a tool call lacks its corresponding response, Claude may become confused about whether the tool execution was completed. Similarly, if a tool response appears without its preceding call, the context is meaningless to the model.

### How the Token Limiter Preserves Tool Pairs

The implementation in `anthropic_message_utils.py` includes several mechanisms to ensure tool pairs remain intact during trimming:

1. **Tool Pair Detection**: The `is_tool_pair()` function identifies when two consecutive messages form a tool pair by checking if:
   - The first message is an `AIMessage`
   - The second message is a `ToolMessage`
   - The first message contains a tool call (verified by `has_tool_use()`)

2. **Atomic Segmentation**: Before trimming, the message history is segmented into atomic units:
   - Single messages that don't participate in tool pairs
   - Tool pairs that are treated as inseparable units

3. **Boundary Protection**: If the boundary between kept and trimmed messages would split a tool pair, the `num_messages_to_keep` is automatically adjusted to include both messages of the pair.

4. **Final Message Validation**: After trimming, a validation step ensures the last message isn't an `AIMessage` with an unfulfilled tool call. If such a message is detected, it's removed to maintain a valid conversation state.

### Error Prevention

This careful handling of tool pairs prevents several types of errors:

- **400 Bad Request errors** from Claude's API when tool pairs are improperly structured
- **Invalid tool references** where Claude might reference tool calls that were trimmed from the history
- **Conversation coherence issues** where the model might be confused by seeing tool responses without their initiating calls

By preserving the integrity of tool pairs during trimming, RA.Aid ensures that conversations with Claude models remain coherent and functional, even when long histories need to be condensed to fit within token limits.

## Key Dependencies

The functionality of `anthropic_token_limiter.py` relies on several key libraries and internal modules:

-   **`litellm`**: Essential for robust token counting and retrieving model information.
-   **`langchain_core`**: Provides `BaseMessage` objects and base utilities for message trimming.
-   **Internal `ra_aid` modules**:
    *   `ra_aid.config`: For accessing configuration.
    *   `ra_aid.model_detection`: For model identification.
    *   `ra_aid.anthropic_message_utils`: For Anthropic-specific message handling during trimming.
    *   `ra_aid.models_params`: For predefined model token limits.