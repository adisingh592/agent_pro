"""
Tool Validator for Personal Agent.
Validates tool names, schemas, required arguments, data types, and unexpected parameters.
"""
from typing import Dict, Any, Tuple, Optional


class ToolValidationError(Exception):
    """Raised when tool validation fails."""
    pass


class ToolValidator:
    """Validates requested tool calls against their defined parameter schemas."""

    TYPE_MAP = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict
    }

    @classmethod
    def validate_call(
        cls,
        tool_name: str,
        arguments: Any,
        parameter_schema: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates a tool invocation.
        
        Args:
            tool_name: The name of the tool requested.
            arguments: The arguments provided (must be a dictionary).
            parameter_schema: JSON Schema defining expected parameters.
            
        Returns:
            (is_valid: bool, error_message: Optional[str])
        """
        if not isinstance(arguments, dict):
            return False, f"Arguments for tool '{tool_name}' must be a dictionary/object, got {type(arguments).__name__}."

        properties = parameter_schema.get("properties", {})
        required = parameter_schema.get("required", [])

        # 1. Check required parameters
        for req_field in required:
            if req_field not in arguments:
                return False, f"Missing required parameter '{req_field}' for tool '{tool_name}'."

        # 2. Check for unexpected parameters
        allowed_keys = set(properties.keys())
        for arg_key in arguments.keys():
            if arg_key not in allowed_keys:
                return False, f"Unexpected parameter '{arg_key}' passed to tool '{tool_name}'. Allowed: {list(allowed_keys)}."

        # 3. Check parameter types
        for key, val in arguments.items():
            prop_def = properties.get(key, {})
            expected_type_str = prop_def.get("type")
            if not expected_type_str:
                continue

            expected_type = cls.TYPE_MAP.get(expected_type_str)
            if expected_type is None:
                continue

            # In Python, bool is a subclass of int, so handle bool vs int strictly
            if expected_type_str in ("integer", "number") and isinstance(val, bool):
                return False, f"Parameter '{key}' in tool '{tool_name}' expected {expected_type_str}, got boolean."

            if expected_type_str == "boolean" and not isinstance(val, bool):
                return False, f"Parameter '{key}' in tool '{tool_name}' expected boolean, got {type(val).__name__}."

            if not isinstance(val, expected_type):
                return False, f"Parameter '{key}' in tool '{tool_name}' expected {expected_type_str}, got {type(val).__name__}."

        return True, None
