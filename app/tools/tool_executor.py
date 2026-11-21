"""
Tool Executor for Personal Agent.
Coordinates validation, permission enforcement, execution isolation, confirmation requests, and result formatting.
"""
import time
import logging
from dataclasses import dataclass
from typing import Dict, Any, Optional

from .tool_registry import ToolRegistry, default_tool_registry
from .tool_validator import ToolValidator
from .tool_permissions import ToolPermissionPolicy, PermissionLevel, default_permission_policy

logger = logging.getLogger("PersonalAgent.ToolExecutor")


@dataclass
class ToolExecutionResult:
    """Encapsulates the outcome of a tool execution."""
    success: bool
    tool_name: str
    result: Optional[Any] = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    requires_confirmation: bool = False
    confirmation_data: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to structured dictionary representation for LLM and UI."""
        data: Dict[str, Any] = {
            "success": self.success,
            "tool": self.tool_name,
            "duration_ms": round(self.duration_ms, 2)
        }
        if self.requires_confirmation:
            data["requires_confirmation"] = True
            data["confirmation_data"] = self.confirmation_data
            data["message"] = self.confirmation_data.get("message") if self.confirmation_data else "User confirmation required."

        if self.success:
            data["result"] = self.result
        else:
            data["error"] = self.error
        return data


class ToolExecutor:
    """Executes validated and permitted tools with safety boundaries, confirmation, and error containment."""

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        permission_policy: Optional[ToolPermissionPolicy] = None
    ):
        self.registry = registry or default_tool_registry
        self.permission_policy = permission_policy or default_permission_policy

    def execute(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> ToolExecutionResult:
        """
        Executes a tool through the full safety pipeline:
        1. Tool Existence Check
        2. Argument Validation
        3. Permission Policy Check (Read-only vs Moderate Write vs Destructive)
        4. Isolated Execution with Timing
        """
        if arguments is None:
            arguments = {}

        start_time = time.perf_counter()

        # Step 1: Check existence
        tool_def = self.registry.get(tool_name)
        if not tool_def:
            duration_ms = (time.perf_counter() - start_time) * 1000
            err_msg = f"Unknown tool: '{tool_name}'. Tool is not registered in the system."
            logger.warning("Tool execution rejected: %s", err_msg)
            return ToolExecutionResult(
                success=False,
                tool_name=tool_name,
                error=err_msg,
                duration_ms=duration_ms
            )

        # Step 2: Validation
        is_valid, val_err = ToolValidator.validate_call(
            tool_name=tool_name,
            arguments=arguments,
            parameter_schema=tool_def.parameters
        )
        if not is_valid:
            duration_ms = (time.perf_counter() - start_time) * 1000
            err_msg = f"Validation failed for tool '{tool_name}': {val_err}"
            logger.warning("Tool execution rejected: %s", err_msg)
            return ToolExecutionResult(
                success=False,
                tool_name=tool_name,
                error=err_msg,
                duration_ms=duration_ms
            )

        # Step 3: Permission Check
        is_confirmed = bool(arguments.get("confirmed", False))
        is_allowed, perm_reason = self.permission_policy.is_tool_allowed(
            tool_name=tool_name,
            permission_level=tool_def.permission_level,
            is_confirmed=is_confirmed
        )

        # If it's a moderate write tool and not confirmed, let the handler execute to build confirmation payload
        if not is_allowed and tool_def.permission_level == PermissionLevel.MODERATE_WRITE:
            pass # We will let the handler return its requires_confirmation payload
        elif not is_allowed:
            duration_ms = (time.perf_counter() - start_time) * 1000
            err_msg = f"Permission denied for tool '{tool_name}': {perm_reason}"
            logger.warning("Tool execution denied: %s", err_msg)
            return ToolExecutionResult(
                success=False,
                tool_name=tool_name,
                error=err_msg,
                duration_ms=duration_ms
            )

        # Step 4: Execute handler safely
        try:
            handler_result = tool_def.handler(**arguments)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # If the handler returned a dictionary
            if isinstance(handler_result, dict):
                # Check for confirmation requirement
                if handler_result.get("requires_confirmation"):
                    return ToolExecutionResult(
                        success=False,
                        tool_name=tool_name,
                        requires_confirmation=True,
                        confirmation_data=handler_result,
                        error=handler_result.get("message", "User confirmation required."),
                        duration_ms=duration_ms
                    )

                is_success = handler_result.get("success", True)
                result_val = handler_result.get("result")
                error_val = handler_result.get("error")
                return ToolExecutionResult(
                    success=is_success,
                    tool_name=tool_name,
                    result=result_val if is_success else None,
                    error=error_val if not is_success else None,
                    duration_ms=duration_ms
                )

            return ToolExecutionResult(
                success=True,
                tool_name=tool_name,
                result=handler_result,
                duration_ms=duration_ms
            )

        except Exception as exc:
            duration_ms = (time.perf_counter() - start_time) * 1000
            err_msg = f"Execution exception in tool '{tool_name}': {str(exc)}"
            logger.exception("Error executing tool '%s': %s", tool_name, exc)
            return ToolExecutionResult(
                success=False,
                tool_name=tool_name,
                error=err_msg,
                duration_ms=duration_ms
            )


# Global default executor
default_tool_executor = ToolExecutor()
