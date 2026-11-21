"""
Tool Registry for Personal Agent.
Manages tool definitions, parameter schemas, and metadata formatting for LLM tool calling.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, Callable, List, Optional
from .tool_permissions import PermissionLevel


@dataclass
class ToolDefinition:
    """Definition of an individual tool registered with the agent."""
    name: str
    description: str
    parameters: Dict[str, Any]
    handler: Callable[..., Any]
    permission_level: PermissionLevel = PermissionLevel.SAFE_READ_ONLY
    category: str = "general"

    def to_ollama_tool(self) -> Dict[str, Any]:
        """Convert to Ollama / OpenAI function format."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


class ToolRegistry:
    """Central registry of tools available to the AI agent."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a new tool definition."""
        self._tools[tool.name] = tool

    def get(self, name: str) -> Optional[ToolDefinition]:
        """Retrieve a registered tool by name."""
        return self._tools.get(name)

    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools

    def list_tools(self) -> List[ToolDefinition]:
        """List all registered tools."""
        return list(self._tools.values())

    def get_ollama_tools(self) -> List[Dict[str, Any]]:
        """Return all tools formatted for the Ollama /api/chat 'tools' parameter."""
        return [tool.to_ollama_tool() for tool in self._tools.values()]

    def unregister(self, name: str) -> bool:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]
            return True
        return False

    def clear(self) -> None:
        """Clear all registered tools."""
        self._tools.clear()


# Global default tool registry
default_tool_registry = ToolRegistry()
