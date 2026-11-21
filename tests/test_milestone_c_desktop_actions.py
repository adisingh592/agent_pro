"""
Automated Unit and Integration Tests for Milestone C: Desktop Actions & Coordinate Grounding.
Tests coordinate mapping, input simulation, emergency stop circuit breaker, keyboard allowlists,
safety confirmation barriers, and tool executor integration.
All Win32 and UI Automation desktop interaction calls are mocked to ensure zero real desktop disruption.
"""
import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.automation.actions.action_models import (
    Coordinate,
    NormalizedCoordinate,
    ScreenMetrics,
    DesktopActionResult
)
from app.automation.actions.coordinate_mapper import (
    get_screen_metrics,
    normalized_to_actual,
    actual_to_normalized,
    clamp_to_screen
)
from app.automation.actions.emergency_stop import (
    EmergencyStopController,
    emergency_stop
)
from app.automation.actions.input_simulator import (
    InputSimulator,
    input_simulator,
    move_mouse,
    click,
    double_click,
    drag,
    scroll,
    type_text,
    press_key,
    key_combination,
    SAFE_KEYS,
    SENSITIVE_KEYS
)
from app.tools.tool_registry import default_tool_registry
from app.tools.tool_executor import default_tool_executor
from app.tools.tool_permissions import default_permission_policy, PermissionLevel


class TestCoordinateMapper(unittest.TestCase):
    """Tests for resolution detection, DPI scaling, and coordinate mapping."""

    def test_screen_metrics(self):
        """Verify screen metrics retrieval returns valid structure."""
        metrics = get_screen_metrics()
        self.assertIsInstance(metrics, ScreenMetrics)
        self.assertGreater(metrics.primary_width, 0)
        self.assertGreater(metrics.primary_height, 0)
        self.assertGreater(metrics.dpi_scale, 0)
        d = metrics.to_dict()
        self.assertIn("primary_screen", d)
        self.assertIn("virtual_screen", d)
        self.assertIn("dpi_scale", d)
        self.assertEqual(d["primary_screen"]["width"], metrics.primary_width)

    def test_normalized_to_actual_center(self):
        """Test converting normalized (500, 500) to actual pixels on 1920x1080 screen."""
        mock_metrics = ScreenMetrics(
            primary_width=1920,
            primary_height=1080,
            virtual_x=0,
            virtual_y=0,
            virtual_width=1920,
            virtual_height=1080,
            dpi_scale=1.0
        )
        actual = normalized_to_actual(500, 500, metrics=mock_metrics)
        self.assertEqual(actual.x, 960)
        self.assertEqual(actual.y, 540)

    def test_normalized_to_actual_corners(self):
        """Test converting normalized (0, 0) and (1000, 1000)."""
        mock_metrics = ScreenMetrics(
            primary_width=1920,
            primary_height=1080,
            virtual_x=0,
            virtual_y=0,
            virtual_width=1920,
            virtual_height=1080,
            dpi_scale=1.0
        )
        top_left = normalized_to_actual(0, 0, metrics=mock_metrics)
        self.assertEqual(top_left.x, 0)
        self.assertEqual(top_left.y, 0)

        bottom_right = normalized_to_actual(1000, 1000, metrics=mock_metrics)
        self.assertEqual(bottom_right.x, 1920)
        self.assertEqual(bottom_right.y, 1080)

    def test_actual_to_normalized(self):
        """Test converting actual pixels back to normalized [0, 1000] scale."""
        mock_metrics = ScreenMetrics(
            primary_width=1920,
            primary_height=1080,
            virtual_x=0,
            virtual_y=0,
            virtual_width=1920,
            virtual_height=1080,
            dpi_scale=1.0
        )
        norm = actual_to_normalized(960, 540, metrics=mock_metrics)
        self.assertEqual(norm.norm_x, 500.0)
        self.assertEqual(norm.norm_y, 540 / 1080 * 1000)

    def test_out_of_bounds_rejection(self):
        """Test that out-of-bounds normalized coordinates raise ValueError."""
        with self.assertRaises(ValueError):
            normalized_to_actual(-10, 500)

        with self.assertRaises(ValueError):
            normalized_to_actual(500, 1050)

    def test_clamp_to_screen(self):
        """Test clamping physical coordinates to display bounds."""
        mock_metrics = ScreenMetrics(
            primary_width=1920,
            primary_height=1080,
            virtual_x=0,
            virtual_y=0,
            virtual_width=1920,
            virtual_height=1080,
            dpi_scale=1.0
        )
        clamped_x, clamped_y = clamp_to_screen(2500, -50, metrics=mock_metrics)
        self.assertEqual(clamped_x, 1920)
        self.assertEqual(clamped_y, 0)


class TestEmergencyStop(unittest.TestCase):
    """Tests for the emergency circuit breaker and failsafe corner detection."""

    def setUp(self):
        self.controller = EmergencyStopController()

    def test_initial_state_inactive(self):
        """Emergency stop should be inactive by default."""
        self.assertFalse(self.controller.is_stopped)

    def test_trigger_emergency_stop(self):
        """Triggering emergency stop sets active flag and records reason."""
        with patch.object(self.controller, "release_held_inputs") as mock_release:
            result = self.controller.trigger_stop("User invoked emergency circuit breaker")
            self.assertTrue(self.controller.is_stopped)
            self.assertTrue(result["emergency_stopped"])
            mock_release.assert_called_once()

    def test_failsafe_corner_detection(self):
        """Moving to (0, 0) or near corner should automatically trigger emergency stop."""
        with patch.object(self.controller, "trigger_stop") as mock_trigger:
            self.controller.check_failsafe(0, 0)
            mock_trigger.assert_called_with("Mouse moved to screen corner (0,0) failsafe trigger.")

        with patch.object(self.controller, "trigger_stop") as mock_trigger:
            self.controller.check_failsafe(3, 4)
            mock_trigger.assert_called()

        with patch.object(self.controller, "trigger_stop") as mock_trigger:
            self.controller.check_failsafe(500, 500)
            mock_trigger.assert_not_called()

    def test_reset_emergency_stop(self):
        """Reset clears the emergency stop state."""
        self.controller.trigger_stop("test")
        self.assertTrue(self.controller.is_stopped)
        res = self.controller.reset_stop()
        self.assertFalse(self.controller.is_stopped)
        self.assertFalse(res["emergency_stopped"])


class TestInputSimulator(unittest.TestCase):
    """Tests for physical input simulation using mocks."""

    def setUp(self):
        self.simulator = InputSimulator()
        self.simulator.stop_ctrl.reset_stop()

    def tearDown(self):
        self.simulator.stop_ctrl.reset_stop()

    def test_move_mouse_normalized(self):
        """Test moving mouse to normalized coordinates."""
        mock_metrics = ScreenMetrics(
            primary_width=1920,
            primary_height=1080,
            virtual_x=0,
            virtual_y=0,
            virtual_width=1920,
            virtual_height=1080,
            dpi_scale=1.0
        )
        with patch.object(self.simulator.mapper, "get_screen_metrics", return_value=mock_metrics), \
             patch("app.automation.actions.input_simulator.auto.MoveTo") as mock_move:
            res = self.simulator.move_mouse(500, 500, normalized=True)
            self.assertTrue(res.success)
            self.assertEqual(res.action_type, "move_mouse")
            self.assertEqual(res.verification_status, "INPUT_SENT")
            mock_move.assert_called_with(960, 540)

    def test_click_mouse(self):
        """Test mouse click action dispatch."""
        mock_metrics = ScreenMetrics(
            primary_width=1000,
            primary_height=1000,
            virtual_x=0,
            virtual_y=0,
            virtual_width=1000,
            virtual_height=1000,
            dpi_scale=1.0
        )
        with patch("app.automation.actions.coordinate_mapper.get_screen_metrics", return_value=mock_metrics), \
             patch("app.automation.actions.input_simulator.auto.Click") as mock_click, \
             patch("app.automation.actions.input_simulator.auto.MoveTo") as mock_move:
            res = self.simulator.click(200, 300, button="left", normalized=False)
            self.assertTrue(res.success)
            self.assertEqual(res.action_type, "click")
            mock_click.assert_called_with(200, 300)

    @patch("win32api.mouse_event")
    def test_scroll_mouse(self, mock_mouse_event):
        """Test scroll wheel dispatch."""
        with patch.object(self.simulator, "move_mouse") as mock_move:
            mock_move.return_value = DesktopActionResult(
                action_type="move_mouse",
                success=True,
                message="Moved",
                coordinates={"actual": {"x": 100, "y": 100}, "normalized": {"norm_x": 100, "norm_y": 100}}
            )
            res = self.simulator.scroll(wheel_units=3, horizontal=False, x=100, y=100, normalized=False)
            self.assertTrue(res.success)
            self.assertEqual(res.action_type, "scroll")

    def test_type_text(self):
        """Test keyboard typing text."""
        with patch("app.automation.actions.input_simulator.auto.SendKeys") as mock_send_keys:
            res = self.simulator.type_text("Hello", delay_per_char=0.001)
            self.assertTrue(res.success)
            self.assertEqual(res.action_type, "type_text")
            mock_send_keys.assert_called_with("Hello", waitTime=0.001)

    def test_press_safe_key(self):
        """Test pressing an approved safe key (e.g. Tab, Escape)."""
        with patch("app.automation.actions.input_simulator.auto.SendKeys") as mock_send_keys:
            res = self.simulator.press_key("Tab")
            self.assertTrue(res.success)
            self.assertEqual(res.action_type, "press_key")
            mock_send_keys.assert_called_with("{Tab}", waitTime=0.05)

    def test_blocked_unapproved_key(self):
        """Test that unauthorized/dangerous keys are blocked."""
        res = self.simulator.press_key("ArbitraryUnknownKey123")
        self.assertFalse(res.success)
        self.assertEqual(res.error, "KEY_NOT_ALLOWED")

    def test_actions_blocked_during_emergency_stop(self):
        """Test that all physical actions are rejected when emergency stop is active."""
        self.simulator.stop_ctrl.trigger_stop("Emergency active test")
        res = self.simulator.move_mouse(100, 100)
        self.assertFalse(res.success)
        self.assertEqual(res.error, "EMERGENCY_STOP_ACTIVE")

        res_click = self.simulator.click(100, 100)
        self.assertFalse(res_click.success)
        self.assertEqual(res_click.error, "EMERGENCY_STOP_ACTIVE")

        res_type = self.simulator.type_text("test")
        self.assertFalse(res_type.success)
        self.assertEqual(res_type.error, "EMERGENCY_STOP_ACTIVE")


class TestDesktopToolsAndPermissions(unittest.TestCase):
    """Tests for tool registry, tool permission policy, and ToolExecutor safety barriers."""

    def setUp(self):
        emergency_stop.reset_stop()

    def tearDown(self):
        emergency_stop.reset_stop()

    def test_tools_registered(self):
        """Verify all 11 Milestone C desktop action tools are registered."""
        tool_names = [
            "get_screen_metrics",
            "move_mouse",
            "click_at",
            "double_click_at",
            "right_click_at",
            "drag_mouse",
            "scroll_at",
            "type_desktop_text",
            "press_desktop_key",
            "trigger_emergency_stop",
            "reset_emergency_stop"
        ]
        for name in tool_names:
            tool = default_tool_registry.get(name)
            self.assertIsNotNone(tool, f"Tool '{name}' must be registered.")
            self.assertEqual(tool.category, "desktop_actions")

    def test_screen_metrics_auto_approved(self):
        """get_screen_metrics should be auto-approved and execute safely."""
        res = default_tool_executor.execute("get_screen_metrics", {})
        self.assertTrue(res.success)
        self.assertIn("primary_screen", res.result)

    def test_emergency_stop_auto_approved(self):
        """trigger_emergency_stop should be auto-approved for instant emergency response."""
        res = default_tool_executor.execute("trigger_emergency_stop", {})
        self.assertTrue(res.success)
        self.assertTrue(emergency_stop.is_stopped)

    def test_mutating_action_requires_confirmation(self):
        """Mutating physical actions must return requires_confirmation: True when unconfirmed."""
        # Unconfirmed click_at
        res = default_tool_executor.execute(
            "click_at",
            {"x": 500, "y": 500, "button": "left", "confirmed": False}
        )
        self.assertFalse(res.success)
        self.assertTrue(res.requires_confirmation)
        self.assertIn("Approval Required", res.confirmation_data.get("title", ""))

    def test_type_desktop_text_requires_confirmation(self):
        """Physical typing must return requires_confirmation: True when unconfirmed."""
        res = default_tool_executor.execute(
            "type_desktop_text",
            {"text": "Sample text", "confirmed": False}
        )
        self.assertFalse(res.success)
        self.assertTrue(res.requires_confirmation)

    def test_confirmed_action_executes(self):
        """Confirmed physical click should execute successfully."""
        mock_metrics = ScreenMetrics(
            primary_width=1000,
            primary_height=1000,
            virtual_x=0,
            virtual_y=0,
            virtual_width=1000,
            virtual_height=1000,
            dpi_scale=1.0
        )
        with patch("app.automation.actions.coordinate_mapper.get_screen_metrics", return_value=mock_metrics), \
             patch("app.automation.actions.input_simulator.auto.Click"), \
             patch("app.automation.actions.input_simulator.auto.MoveTo"):
            res = default_tool_executor.execute(
                "click_at",
                {"x": 500, "y": 500, "button": "left", "confirmed": True}
            )
            self.assertTrue(res.success)
            self.assertFalse(res.requires_confirmation)
            self.assertEqual(res.result.get("action_type"), "click")
            self.assertEqual(res.result.get("verification_status"), "INPUT_SENT")


if __name__ == "__main__":
    unittest.main()
