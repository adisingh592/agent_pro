"""
Tool Permissions and Security Categorization for Personal Agent.
Determines whether tools execute automatically or require explicit user approval.
"""
from enum import Enum
from typing import Dict, Any, Optional


class PermissionLevel(str, Enum):
    """Permission levels for tool execution safety."""
    SAFE_READ_ONLY = "safe_read_only"      # Read-only information (time, system stats); always auto-approved
    SAFE_ACTION = "safe_action"            # Safe non-destructive operations (file reading, search)
    SENSITIVE_READ = "sensitive_read"      # Sensitive reads (private files, process lists)
    MODERATE_WRITE = "moderate_write"      # Modifying files, creating folders (requires confirmation in later phases)
    DESTRUCTIVE = "destructive"            # Deleting files, killing processes, system modifications (always requires user approval)


class ToolPermissionPolicy:
    """Policy rules governing tool execution permissions."""

    def __init__(self, allow_auto_execution: bool = True):
        self.allow_auto_execution = allow_auto_execution
        # Tools explicitly permitted to run without prompt
        self._auto_approved_tools = {
            "get_current_time",
            "get_system_info",
            "get_gpu_info"
        }

    def is_tool_allowed(self, tool_name: str, permission_level: PermissionLevel) -> tuple[bool, str]:
        """
        Check if a tool is permitted to execute.
        Returns: (is_allowed, reason)
        """
        if not self.allow_auto_execution:
            return False, "Automated tool execution is disabled in settings."

        if permission_level == PermissionLevel.SAFE_READ_ONLY:
            return True, "Safe read-only tool auto-approved."

        if tool_name in self._auto_approved_tools:
            return True, f"Tool '{tool_name}' is in auto-approved safe list."

        if permission_level in (PermissionLevel.MODERATE_WRITE, PermissionLevel.DESTRUCTIVE):
            return False, f"Tool '{tool_name}' requires explicit user confirmation (destructive/write level)."

        return True, "Tool approved under current security policy."

    def add_auto_approved_tool(self, tool_name: str) -> None:
        self._auto_approved_tools.add(tool_name)

    def remove_auto_approved_tool(self, tool_name: str) -> None:
        self._auto_approved_tools.discard(tool_name)


# Global default permission policy
default_permission_policy = ToolPermissionPolicy()
