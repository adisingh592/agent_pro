"""
Data models for Windows UI Automation Engine.
Defines schemas for windows, UI elements, inspection results, and action outcomes.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple


@dataclass
class WindowInfo:
    """Represents a discovered desktop window."""
    window_title: str
    process_name: str
    process_id: int
    hwnd: int
    visible: bool = True
    minimized: bool = False
    maximized: bool = False
    bounds: Tuple[int, int, int, int] = (0, 0, 0, 0)  # (left, top, right, bottom)
    class_name: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        return {
            "window_title": self.window_title,
            "process_name": self.process_name,
            "process_id": self.process_id,
            "hwnd": self.hwnd,
            "visible": self.visible,
            "minimized": self.minimized,
            "maximized": self.maximized,
            "class_name": self.class_name,
            "bounds": {
                "left": self.bounds[0],
                "top": self.bounds[1],
                "right": self.bounds[2],
                "bottom": self.bounds[3],
                "width": max(0, self.bounds[2] - self.bounds[0]),
                "height": max(0, self.bounds[3] - self.bounds[1])
            }
        }


@dataclass
class UIElementInfo:
    """Represents an accessible UI control inside a window."""
    name: str
    control_type: str
    automation_id: str = ""
    class_name: str = ""
    enabled: bool = True
    visible: bool = True
    focused: bool = False
    bounds: Optional[Dict[str, int]] = None  # left, top, right, bottom, width, height
    value: Optional[str] = None
    depth: int = 0
    children: List["UIElementInfo"] = field(default_factory=list)

    def to_dict(self, include_children: bool = True) -> Dict[str, Any]:
        """Convert to JSON-serializable dictionary."""
        data: Dict[str, Any] = {
            "name": self.name,
            "control_type": self.control_type,
            "automation_id": self.automation_id,
            "class_name": self.class_name,
            "enabled": self.enabled,
            "visible": self.visible,
            "focused": self.focused,
            "depth": self.depth
        }
        if self.bounds is not None:
            data["bounds"] = self.bounds
        if self.value is not None:
            data["value"] = self.value
        if include_children and self.children:
            data["children"] = [c.to_dict(include_children=True) for c in self.children]
        return data


@dataclass
class ElementMatch:
    """Represents a matched UI element with confidence score."""
    element: UIElementInfo
    confidence: float
    match_type: str  # "exact_id", "exact_name", "case_insensitive", "substring", "fuzzy"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "element": self.element.to_dict(include_children=False),
            "confidence": round(self.confidence, 2),
            "match_type": self.match_type
        }


@dataclass
class AutomationResult:
    """Result of an automation action or inspection."""
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None
    verification: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        res: Dict[str, Any] = {
            "success": self.success,
            "message": self.message
        }
        if self.data is not None:
            res["data"] = self.data
        if self.error is not None:
            res["error"] = self.error
        if self.verification is not None:
            res["verification"] = self.verification
        return res
