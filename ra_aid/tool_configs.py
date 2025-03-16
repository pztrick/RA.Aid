import importlib.util
import sys
from typing import List, Optional

from langchain_core.tools import BaseTool
from ra_aid.logging_config import get_logger
from ra_aid.tools import (
    ask_expert,
    ask_human,
    emit_expert_context,
    emit_key_facts,
    emit_key_snippet,
    emit_related_files,
    emit_research_notes,
    file_str_replace,
    fuzzy_find_project_files,
    list_directory_tree,
    put_complete_file_contents,
    read_file_tool,
    ripgrep_search,
    run_programming_task,
    run_shell_command,
    task_completed,
    web_search_tavily,
)
from ra_aid.tools.agent import (
    request_implementation,
    request_research,
    request_research_and_implementation,
    request_task_implementation,
    request_web_research,
)
from ra_aid.tools.memory import plan_implementation_completed
from ra_aid.database.repositories.config_repository import get_config_repository


def set_modification_tools(use_aider=False):
    """Set the MODIFICATION_TOOLS list based on configuration.

    Args:
        use_aider: Whether to use run_programming_task (True) or file modification tools (False)
    """
    global MODIFICATION_TOOLS
    if use_aider:
        MODIFICATION_TOOLS.clear()
        MODIFICATION_TOOLS.append(run_programming_task)
    else:
        MODIFICATION_TOOLS.clear()
        MODIFICATION_TOOLS.extend([file_str_replace, put_complete_file_contents])


# Read-only tools that don't modify system state
def get_read_only_tools(
    human_interaction: bool = False,
    web_research_enabled: bool = False,
    use_aider: bool = False,
):
    """Get the list of read-only tools, optionally including human interaction tools.

    Args:
        human_interaction: Whether to include human interaction tools
        web_research_enabled: Whether to include web research tools
        use_aider: Whether aider is being used for code modifications

    Returns:
        List of tool functions
    """
    tools = get_custom_tools() + [
        emit_key_snippet,
        # Only include emit_related_files if use_aider is True
        *([emit_related_files] if use_aider else []),
        emit_key_facts,
        # *TEMPORARILY* disabled to improve tool calling perf.
        # delete_key_facts,
        # delete_key_snippets,
        # deregister_related_files,
        list_directory_tree,
        read_file_tool,
        fuzzy_find_project_files,
        ripgrep_search,
        run_shell_command,  # can modify files, but we still need it for read-only tasks.
    ]

    if web_research_enabled:
        tools.append(request_web_research)

    if human_interaction:
        tools.append(ask_human)

    return tools


def get_all_tools() -> list[BaseTool]:
    """Return a list containing all available tools from different groups."""
    all_tools = []
    all_tools.extend(get_read_only_tools())
    all_tools.extend(MODIFICATION_TOOLS)
    all_tools.extend(EXPERT_TOOLS)
    all_tools.extend(RESEARCH_TOOLS)
    all_tools.extend(get_web_research_tools())
    all_tools.extend(get_chat_tools())
    return all_tools


# Define constant tool groups
# Get config from repository for use_aider value
_config = {}
try:
    _config = get_config_repository().get_all()
except (ImportError, RuntimeError):
    pass

READ_ONLY_TOOLS = get_read_only_tools(use_aider=_config.get("use_aider", False))

# MODIFICATION_TOOLS will be set dynamically based on config, default defined here
MODIFICATION_TOOLS = [file_str_replace, put_complete_file_contents]
COMMON_TOOLS = get_read_only_tools(use_aider=_config.get("use_aider", False))
EXPERT_TOOLS = [emit_expert_context, ask_expert]
RESEARCH_TOOLS = [
    emit_research_notes,
    # *TEMPORARILY* disabled to improve tool calling perf.
    # one_shot_completed,
    # monorepo_detected,
    # ui_detected,
]


def get_research_tools(
    research_only: bool = False,
    expert_enabled: bool = True,
    human_interaction: bool = False,
    web_research_enabled: bool = False,
):
    """Get the list of research tools based on mode and whether expert is enabled.

    Args:
        research_only: Whether to exclude modification tools
        expert_enabled: Whether to include expert tools
        human_interaction: Whether to include human interaction tools
        web_research_enabled: Whether to include web research tools
    """
    # Get config for use_aider value
    use_aider = False
    try:
        use_aider = get_config_repository().get("use_aider", False)
    except (ImportError, RuntimeError):
        pass

    # Start with read-only tools
    tools = get_read_only_tools(
        human_interaction, web_research_enabled, use_aider=use_aider
    ).copy()

    tools.extend(RESEARCH_TOOLS)

    # Add modification tools if not research_only
    if not research_only:
        # For now, we ONLY do modifications after planning.
        # tools.extend(MODIFICATION_TOOLS)
        tools.append(request_implementation)

    # Add expert tools if enabled
    if expert_enabled:
        tools.extend(EXPERT_TOOLS)

    # Add chat-specific tools
    tools.append(request_research)

    return tools


def get_planning_tools(
    expert_enabled: bool = True, web_research_enabled: bool = False
) -> list:
    """Get the list of planning tools based on whether expert is enabled.

    Args:
        expert_enabled: Whether to include expert tools
        web_research_enabled: Whether to include web research tools
    """
    # Get config for use_aider value
    use_aider = False
    try:
        use_aider = get_config_repository().get("use_aider", False)
    except (ImportError, RuntimeError):
        pass

    # Start with read-only tools
    tools = get_read_only_tools(
        web_research_enabled=web_research_enabled, use_aider=use_aider
    ).copy()

    # Add planning-specific tools
    planning_tools = [
        request_task_implementation,
        plan_implementation_completed,
        # *TEMPORARILY* disabled to improve tool calling perf.
        # emit_plan,
    ]
    tools.extend(planning_tools)

    # Add expert tools if enabled
    if expert_enabled:
        tools.extend(EXPERT_TOOLS)

    return tools


def get_implementation_tools(
    expert_enabled: bool = True, web_research_enabled: bool = False
) -> list:
    """Get the list of implementation tools based on whether expert is enabled.

    Args:
        expert_enabled: Whether to include expert tools
        web_research_enabled: Whether to include web research tools
    """
    # Get config for use_aider value
    use_aider = False
    try:
        use_aider = get_config_repository().get("use_aider", False)
    except (ImportError, RuntimeError):
        pass

    # Start with read-only tools
    tools = get_read_only_tools(
        web_research_enabled=web_research_enabled, use_aider=use_aider
    ).copy()

    # Add modification tools since it's not research-only
    tools.extend(MODIFICATION_TOOLS)
    tools.extend([task_completed])

    # Add expert tools if enabled
    if expert_enabled:
        tools.extend(EXPERT_TOOLS)

    return tools


def get_web_research_tools(expert_enabled: bool = True):
    """Get the list of tools available for web research.

    Args:
        expert_enabled: Whether expert tools should be included
        human_interaction: Whether to include human interaction tools
        web_research_enabled: Whether to include web research tools

    Returns:
        list: List of tools configured for web research
    """
    tools = [web_search_tavily, emit_research_notes, task_completed]

    if expert_enabled:
        tools.append(emit_expert_context)
        tools.append(ask_expert)

    return tools


def get_custom_tools() -> List[BaseTool]:
    """Dynamically import and return custom tools from the configured module.
    
    The custom tools module must export a 'tools' attribute that is a list of
    langchain Tool objects (e.g. StructuredTool or other tool classes).
    
    Returns:
        List[BaseTool]: List of custom tools, or empty list if no custom tools configured
    """
    logger = get_logger(__name__)
    
    try:
        config = get_config_repository().get_all()
        custom_tools_path = config.get("custom_tools")
        
        if not custom_tools_path:
            return []
            
        # Convert module path to system path
        module_path = custom_tools_path.replace(".", "/") + ".py"
        
        # Import the module
        spec = importlib.util.spec_from_file_location(custom_tools_path, module_path)
        if not spec or not spec.loader:
            logger.error(f"Could not load custom tools module: {custom_tools_path}")
            return []
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[custom_tools_path] = module
        spec.loader.exec_module(module)
        
        # Get the tools list
        if not hasattr(module, "tools"):
            logger.error(f"Custom tools module {custom_tools_path} does not export 'tools' attribute")
            return []
            
        tools = module.tools
        if not isinstance(tools, list):
            logger.error(f"Custom tools module {custom_tools_path} 'tools' attribute must be a list")
            return []
            
        for tool in tools:
            if not isinstance(tool, BaseTool):
                logger.error(f"Custom tool {tool} is not a BaseTool instance")
                return []
                
        logger.info(f"Loaded {len(tools)} custom tools from {custom_tools_path}")
        return tools
        
    except Exception as e:
        logger.error(f"Error loading custom tools: {str(e)}")
        return []


def get_chat_tools(expert_enabled: bool = True, web_research_enabled: bool = False):
    """Get the list of tools available in chat mode.

    Chat mode includes research and implementation capabilities but excludes
    complex planning tools. Human interaction is always enabled.

    Args:
        expert_enabled: Whether to include expert tools
        web_research_enabled: Whether to include web research tools
    """
    tools = [
        ask_human,
        request_research,
        request_research_and_implementation,
        emit_key_facts,
        # *TEMPORARILY* disabled to improve tool calling perf.
        # delete_key_facts,
        # delete_key_snippets,
        # deregister_related_files,
    ]

    if web_research_enabled:
        tools.append(request_web_research)

    return tools
