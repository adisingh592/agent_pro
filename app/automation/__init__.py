"""
Windows UI Automation Engine package for Personal Agent.
Provides window discovery, UI tree inspection, control matching, and native pattern actions.
"""
from .automation_models import (
    WindowInfo,
    UIElementInfo,
    ElementMatch,
    AutomationResult
)
from .window_manager import WindowManager, window_manager
from .element_inspector import ElementInspector, element_inspector
from .element_finder import ElementFinder, element_finder
from .action_executor import ActionExecutor, action_executor
from .windows_automation import WindowsAutomationEngine, windows_automation
from .actions import (
    Coordinate,
    NormalizedCoordinate,
    ScreenMetrics,
    DesktopActionResult,
    CoordinateMapper,
    coordinate_mapper,
    EmergencyStopController,
    emergency_stop,
    InputSimulator,
    input_simulator
)

__all__ = [
    "WindowInfo",
    "UIElementInfo",
    "ElementMatch",
    "AutomationResult",
    "WindowManager",
    "window_manager",
    "ElementInspector",
    "element_inspector",
    "ElementFinder",
    "element_finder",
    "ActionExecutor",
    "action_executor",
    "WindowsAutomationEngine",
    "windows_automation",
    "Coordinate",
    "NormalizedCoordinate",
    "ScreenMetrics",
    "DesktopActionResult",
    "CoordinateMapper",
    "coordinate_mapper",
    "EmergencyStopController",
    "emergency_stop",
    "InputSimulator",
    "input_simulator"
]
