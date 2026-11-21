"""
Tools package initialization for Personal Agent.
Automatically registers initial built-in tools upon import.
"""
from .tool_permissions import PermissionLevel, ToolPermissionPolicy, default_permission_policy
from .tool_validator import ToolValidator, ToolValidationError
from .tool_registry import ToolDefinition, ToolRegistry, default_tool_registry
from .tool_executor import ToolExecutor, ToolExecutionResult, default_tool_executor
from .built_in_tools import register_built_in_tools

# Register built-in tools into global registry
register_built_in_tools(default_tool_registry)

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
    "register_built_in_tools"
]
