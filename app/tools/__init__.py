"""
Tools package initialization for Personal Agent.
Automatically registers initial built-in system tools and file tools upon import.
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

# Register built-in system tools
register_built_in_tools(default_tool_registry)

# Register Phase 2.2.2 file intelligence & operation tools
register_file_tools(default_tool_registry)

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
    "organize_files"
]
