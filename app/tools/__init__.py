"""
Tools package initialization for Personal Agent.
Automatically registers initial built-in system tools, file tools, and application/process tools upon import.
"""
from .tool_permissions import PermissionLevel, ToolPermissionPolicy, default_permission_policy
from .tool_validator import ToolValidator, ToolValidationError
from .tool_registry import ToolDefinition, ToolRegistry, default_tool_registry
from .tool_executor import ToolExecutor, ToolExecutionResult, default_tool_executor
from .built_in_tools import register_built_in_tools
from .filesystem_safety import FilesystemSafety, FilesystemSafetyError
from .file_tools import (
    register_file_tools,
    search_files,
    list_directory,
    get_file_info,
    read_text_file,
    find_recent_files,
    find_large_files,
    copy_file,
    move_file,
    rename_file,
    create_directory,
    organize_files_preview,
    organize_files
)
from .app_discovery import (
    DiscoveredApplication,
    ApplicationDiscovery,
    ApplicationResolver,
    ResolutionResult,
    default_app_discovery,
    default_app_resolver
)
from .process_manager import (
    ProcessManager,
    default_process_manager
)
from .app_tools import (
    register_app_tools,
    search_applications,
    list_installed_applications,
    launch_application,
    open_file_with_application,
    open_folder,
    list_running_processes,
    check_application_status,
    get_process_info,
    close_application
)
from .ui_automation_tools import (
    register_ui_automation_tools,
    handle_list_windows,
    handle_get_active_window,
    handle_inspect_window,
    handle_find_ui_element,
    handle_click_ui_element,
    handle_type_into_ui_element,
    handle_read_ui_element,
    handle_focus_window,
    handle_press_key
)
from .desktop_action_tools import (
    register_desktop_action_tools,
    handle_get_screen_metrics,
    handle_move_mouse,
    handle_click_at,
    handle_double_click_at,
    handle_right_click_at,
    handle_drag_mouse,
    handle_scroll_at,
    handle_type_desktop_text,
    handle_press_desktop_key,
    handle_trigger_emergency_stop,
    handle_reset_emergency_stop
)

# Register built-in system tools
register_built_in_tools(default_tool_registry)

# Register Phase 2.2.2 file intelligence & operation tools
register_file_tools(default_tool_registry)

# Register Phase 2.2.3 application & process control tools
register_app_tools(default_tool_registry)

# Register Phase 2.3 Windows UI Automation tools
register_ui_automation_tools(default_tool_registry)

# Register Milestone C Desktop Actions & Coordinate Grounding tools
register_desktop_action_tools(default_tool_registry)

__all__ = [
    "PermissionLevel",
    "ToolPermissionPolicy",
    "default_permission_policy",
    "ToolValidator",
    "ToolValidationError",
    "ToolDefinition",
    "ToolRegistry",
    "default_tool_registry",
    "ToolExecutor",
    "ToolExecutionResult",
    "default_tool_executor",
    "register_built_in_tools",
    "FilesystemSafety",
    "FilesystemSafetyError",
    "register_file_tools",
    "search_files",
    "list_directory",
    "get_file_info",
    "read_text_file",
    "find_recent_files",
    "find_large_files",
    "copy_file",
    "move_file",
    "rename_file",
    "create_directory",
    "organize_files_preview",
    "organize_files",
    "DiscoveredApplication",
    "ApplicationDiscovery",
    "ApplicationResolver",
    "ResolutionResult",
    "default_app_discovery",
    "default_app_resolver",
    "ProcessManager",
    "default_process_manager",
    "register_app_tools",
    "search_applications",
    "list_installed_applications",
    "launch_application",
    "open_file_with_application",
    "open_folder",
    "list_running_processes",
    "check_application_status",
    "get_process_info",
    "close_application",
    "register_ui_automation_tools",
    "handle_list_windows",
    "handle_get_active_window",
    "handle_inspect_window",
    "handle_find_ui_element",
    "handle_click_ui_element",
    "handle_type_into_ui_element",
    "handle_read_ui_element",
    "handle_focus_window",
    "handle_press_key",
    "register_desktop_action_tools",
    "handle_get_screen_metrics",
    "handle_move_mouse",
    "handle_click_at",
    "handle_double_click_at",
    "handle_right_click_at",
    "handle_drag_mouse",
    "handle_scroll_at",
    "handle_type_desktop_text",
    "handle_press_desktop_key",
    "handle_trigger_emergency_stop",
    "handle_reset_emergency_stop"
]
