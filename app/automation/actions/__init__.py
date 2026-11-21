"""
Desktop physical actions and coordinate mapping subsystem for Personal Agent.
Provides physical mouse simulation, keyboard injection, coordinate mapping, and emergency stop.
"""
from .action_models import (
    Coordinate,
    NormalizedCoordinate,
    ScreenMetrics,
    DesktopActionResult
)
from .coordinate_mapper import (
    CoordinateMapper,
    coordinate_mapper,
    get_screen_metrics,
    normalized_to_actual,
    actual_to_normalized,
    clamp_to_screen
)
from .emergency_stop import EmergencyStopController, emergency_stop
from .input_simulator import (
    InputSimulator,
    input_simulator,
    move_mouse,
    click,
    double_click,
    right_click,
    drag,
    scroll,
    type_text,
    press_key,
    key_combination,
    SAFE_KEYS,
    SENSITIVE_KEYS
)

__all__ = [
    "Coordinate",
    "NormalizedCoordinate",
    "ScreenMetrics",
    "DesktopActionResult",
    "CoordinateMapper",
    "coordinate_mapper",
    "EmergencyStopController",
    "emergency_stop",
    "InputSimulator",
    "input_simulator",
    "move_mouse",
    "click",
    "double_click",
    "right_click",
    "drag",
    "scroll",
    "type_text",
    "press_key",
    "key_combination",
    "SAFE_KEYS",
    "SENSITIVE_KEYS"
]
