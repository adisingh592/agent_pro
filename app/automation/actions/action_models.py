"""
Data models for Milestone C Desktop Actions & Coordinate Grounding.
Defines schemas for coordinates, screen metrics, and structured action results.
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Tuple


@dataclass
class Coordinate:
    """Actual screen pixel coordinates."""
    x: int
    y: int

    def __iter__(self):
        yield self.x
        yield self.y

    def to_dict(self) -> Dict[str, int]:
        return {"x": self.x, "y": self.y}


@dataclass
class NormalizedCoordinate:
    """Normalized coordinates in range [0, 1000]."""
    norm_x: float
    norm_y: float

    def __iter__(self):
        yield self.norm_x
        yield self.norm_y

    def to_dict(self) -> Dict[str, float]:
        return {"norm_x": round(self.norm_x, 1), "norm_y": round(self.norm_y, 1)}


@dataclass
class ScreenMetrics:
    """Resolution and monitor geometry metrics."""
    primary_width: int
    primary_height: int
    virtual_x: int
    virtual_y: int
    virtual_width: int
    virtual_height: int
    dpi_scale: float = 1.0
    cursor_x: Optional[int] = None
    cursor_y: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary_screen": {
                "width": self.primary_width,
                "height": self.primary_height
            },
            "virtual_screen": {
                "x": self.virtual_x,
                "y": self.virtual_y,
                "width": self.virtual_width,
                "height": self.virtual_height
            },
            "dpi_scale": round(self.dpi_scale, 2),
            "cursor_position": {
                "x": self.cursor_x,
                "y": self.cursor_y
            } if self.cursor_x is not None else None
        }


@dataclass
class DesktopActionResult:
    """Structured result of a desktop mouse or keyboard action."""
    action_type: str
    success: bool
    message: str
    coordinates: Optional[Dict[str, Any]] = None  # Contains 'actual' and 'normalized'
    verification_status: str = "NOT_VERIFIED"     # INPUT_SENT, POSITION_VERIFIED, TARGET_LOST, EMERGENCY_STOPPED
    duration_ms: float = 0.0
    target_window: Optional[str] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "action_type": self.action_type,
            "success": self.success,
            "message": self.message,
            "verification_status": self.verification_status,
            "duration_ms": round(self.duration_ms, 2)
        }
        if self.coordinates is not None:
            data["coordinates"] = self.coordinates
        if self.target_window is not None:
            data["target_window"] = self.target_window
        if self.error is not None:
            data["error"] = self.error
        if self.metadata:
            data["metadata"] = self.metadata
        return data
