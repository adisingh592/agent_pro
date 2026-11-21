"""
Unit and Integration Tests for Phase 2.3 — Windows UI Automation Engine.
Tests window discovery, UI tree inspection, element searching, action execution,
permission policies, key allowlists, and Tool Executor integration.
"""
import unittest
import time
from unittest.mock import MagicMock, patch

from app.automation.automation_models import (
    WindowInfo,
    UIElementInfo,
    ElementMatch,
    AutomationResult
)
from app.automation.window_manager import WindowManager, window_manager
from app.automation.element_inspector import ElementInspector, element_inspector
from app.automation.element_finder import ElementFinder, element_finder
from app.automation.action_executor import ActionExecutor, action_executor, SAFE_KEYS, SENSITIVE_KEYS
from app.automation.windows_automation import WindowsAutomationEngine, windows_automation
from app.tools.tool_registry import default_tool_registry, ToolDefinition
from app.tools.tool_permissions import default_permission_policy, PermissionLevel
from app.tools.tool_executor import default_tool_executor


class TestWindowsUIAutomation(unittest.TestCase):
    """Test suite for Phase 2.3 Windows UI Automation capabilities."""

    # -----------------------------------------------------------------------
    # 1. Window Discovery Tests
    # -----------------------------------------------------------------------

    def test_list_windows_returns_structured_data(self):
        """Verify list_windows returns a non-empty list of WindowInfo objects with valid fields."""
        windows = window_manager.list_windows(visible_only=True, maximum_results=20)
        self.assertIsInstance(windows, list)
        if windows:
            first = windows[0]
            self.assertIsInstance(first.window_title, str)
            self.assertIsInstance(first.process_id, int)
            self.assertIsInstance(first.hwnd, int)
            self.assertTrue(first.visible)
            d = first.to_dict()
            self.assertIn("window_title", d)
            self.assertIn("process_name", d)
            self.assertIn("process_id", d)
            self.assertIn("bounds", d)

    def test_list_windows_respects_max_results(self):
        """Verify maximum_results limits the output list length."""
        windows = window_manager.list_windows(visible_only=False, maximum_results=5)
        self.assertLessEqual(len(windows), 5)

    def test_find_window_exact_and_substring(self):
        """Verify window matching with exact and substring queries."""
        all_wins = window_manager.list_windows(visible_only=True, maximum_results=30)
        if not all_wins:
            self.skipTest("No visible windows found on system.")

        target = all_wins[0]
        # Exact match
        found = window_manager.find_window(target.window_title)
        self.assertIsNotNone(found)
        self.assertEqual(found.hwnd, target.hwnd)

        # Substring match (first word of title if multi-word)
        words = target.window_title.split()
        if len(words) > 1 and len(words[0]) >= 3:
            found_sub = window_manager.find_window(words[0])
            self.assertIsNotNone(found_sub)

    def test_find_window_nonexistent_returns_none(self):
        """Verify searching for a non-existent window returns None without crashing."""
        found = window_manager.find_window("NonExistent_Fake_Window_123456789_XYZ")
        self.assertIsNone(found)

    def test_get_active_window(self):
        """Verify get_active_window returns a WindowInfo or None without error."""
        active = window_manager.get_active_window()
        if active is not None:
            self.assertIsInstance(active, WindowInfo)
            self.assertIsInstance(active.window_title, str)

    # -----------------------------------------------------------------------
    # 2. UI Inspection & Observation Tests
    # -----------------------------------------------------------------------

    def test_inspect_window_nonexistent(self):
        """Verify inspect_window gracefully fails on non-existent window."""
        res = element_inspector.inspect_window("NonExistent_Window_999999")
        self.assertFalse(res.success)
        self.assertEqual(res.error, "WINDOW_NOT_FOUND")

    def test_compact_observation_generation(self):
        """Verify compact observation text formatting for LLMs."""
        win = WindowInfo(
            window_title="Untitled - Notepad",
            process_name="notepad.exe",
            process_id=1234,
            hwnd=5678,
            visible=True,
            minimized=False,
            maximized=False
        )
        root = UIElementInfo(
            name="Untitled - Notepad",
            control_type="WindowControl",
            automation_id="NotepadWindow"
        )
        # Add simulated buttons and inputs
        file_menu = UIElementInfo(name="File", control_type="MenuItemControl", depth=1)
        save_btn = UIElementInfo(name="Save", control_type="ButtonControl", depth=2)
        edit_area = UIElementInfo(name="Text Area", control_type="EditControl", value="Hello World", focused=True, depth=2)

        root.children.extend([file_menu, save_btn, edit_area])

        obs = element_inspector.generate_compact_observation(win, root, is_truncated=False)
        self.assertIn("ACTIVE WINDOW: Untitled - Notepad", obs)
        self.assertIn("notepad.exe", obs)
        self.assertIn("MenuItem 'File'", obs)
        self.assertIn("Button 'Save'", obs)
        self.assertIn("Edit 'Text Area'", obs)
        self.assertIn("[FOCUSED]", obs)

    # -----------------------------------------------------------------------
    # 3. Element Finder Tests
    # -----------------------------------------------------------------------

    def test_find_element_in_nonexistent_window(self):
        """Verify finding elements in a non-existent window returns an error."""
        res = element_finder.find_elements(
            window_title="NonExistent_Fake_Window_XYZ",
            element_name="Save"
        )
        self.assertFalse(res.success)
        self.assertEqual(res.error, "WINDOW_NOT_FOUND")

    def test_element_matching_logic_mocked(self):
        """Verify finder matching logic: exact name, substring, fuzzy, ambiguity."""
        win_info = WindowInfo("TestApp", "test.exe", 100, 200, True)

        # Mock inspect_window output
        mock_tree = {
            "name": "TestApp",
            "control_type": "WindowControl",
            "children": [
                {"name": "Save", "control_type": "ButtonControl", "automation_id": "btnSave", "enabled": True},
                {"name": "Save As", "control_type": "ButtonControl", "automation_id": "btnSaveAs", "enabled": True},
                {"name": "Cancel", "control_type": "ButtonControl", "automation_id": "btnCancel", "enabled": True},
                {"name": "Username", "control_type": "EditControl", "automation_id": "txtUser", "enabled": True}
            ]
        }

        with patch.object(window_manager, "find_window", return_value=win_info):
            with patch.object(element_inspector, "inspect_window", return_value=AutomationResult(True, "OK", {"tree": mock_tree})):
                # 1. Exact match on Save
                res = element_finder.find_elements("TestApp", element_name="Save")
                self.assertTrue(res.success)
                matches = res.data["matches"]
                self.assertGreaterEqual(len(matches), 1)
                self.assertEqual(matches[0]["element"]["name"], "Save")
                self.assertEqual(matches[0]["match_type"], "exact_name")

                # 2. AutomationId match
                res_id = element_finder.find_elements("TestApp", automation_id="btnCancel")
                self.assertTrue(res_id.success)
                self.assertEqual(res_id.data["matches"][0]["element"]["automation_id"], "btnCancel")

                # 3. Ambiguity check: Searching "Save" matches "Save" and "Save As"
                self.assertGreaterEqual(res.data["match_count"], 2)

    # -----------------------------------------------------------------------
    # 4. Action Executor & Key Allowlist Tests
    # -----------------------------------------------------------------------

    def test_key_allowlist_enforcement(self):
        """Verify key allowlist rejects unauthorized or dangerous arbitrary strings."""
        # Unapproved random string
        res = action_executor.press_key("Notepad", "arbitrary_malicious_string_#$@")
        self.assertFalse(res.success)
        self.assertEqual(res.error, "KEY_NOT_ALLOWED")

        # Sensitive key without approval parameter
        res_sensitive = action_executor.press_key("Notepad", "alt+f4")
        self.assertFalse(res_sensitive.success)
        self.assertEqual(res_sensitive.error, "CONFIRMATION_REQUIRED")

    def test_safe_keys_recognized(self):
        """Verify safe keys exist in SAFE_KEYS constant."""
        self.assertIn("escape", SAFE_KEYS)
        self.assertIn("tab", SAFE_KEYS)
        self.assertIn("ctrl+s", SAFE_KEYS)
        self.assertIn("ctrl+a", SAFE_KEYS)
        self.assertIn("f5", SAFE_KEYS)

    def test_action_executor_disabled_element_protection(self):
        """Verify action_executor blocks clicking disabled controls."""
        win_info = WindowInfo("TestApp", "test.exe", 100, 200, True)
        mock_find_res = AutomationResult(
            success=True,
            message="Found",
            data={
                "matches": [
                    {
                        "element": {
                            "name": "Submit",
                            "control_type": "ButtonControl",
                            "automation_id": "btnSubmit",
                            "enabled": False  # Disabled element
                        },
                        "confidence": 1.0,
                        "match_type": "exact_name"
                    }
                ],
                "is_ambiguous": False
            }
        )

        with patch.object(window_manager, "focus_window", return_value=AutomationResult(True, "Focused")):
            with patch.object(window_manager, "find_window", return_value=win_info):
                with patch.object(element_finder, "find_elements", return_value=mock_find_res):
                    res = action_executor.click_element("TestApp", "Submit")
                    self.assertFalse(res.success)
                    self.assertEqual(res.error, "ELEMENT_DISABLED")
                    self.assertIn("disabled", res.message.lower())

    def test_read_element_sensitive_masking(self):
        """Verify password controls are masked during element reading."""
        win_info = WindowInfo("LoginWindow", "app.exe", 100, 200, True)

        mock_ctrl = MagicMock()
        mock_ctrl.Name = "Password input"
        mock_ctrl.ControlTypeName = "EditControl"
        mock_ctrl.IsEnabled = True
        mock_ctrl.AutomationId = "user_password"
        mock_ctrl.IsPassword = True

        with patch.object(window_manager, "find_window", return_value=win_info):
            with patch.object(element_finder, "locate_live_control", return_value=mock_ctrl):
                res = action_executor.read_element("LoginWindow", "Password input")
                self.assertTrue(res.success)
                self.assertEqual(res.data["value"], "********")
                self.assertTrue(res.data["is_sensitive"])

    # -----------------------------------------------------------------------
    # 5. Permission Policy Integration Tests
    # -----------------------------------------------------------------------

    def test_read_only_automation_tools_auto_approved(self):
        """Verify all read-only UI automation tools are auto-approved under security policy."""
        read_tools = [
            ("list_windows", PermissionLevel.SAFE_READ_ONLY),
            ("get_active_window", PermissionLevel.SAFE_READ_ONLY),
            ("inspect_window", PermissionLevel.SAFE_READ_ONLY),
            ("find_ui_element", PermissionLevel.SAFE_READ_ONLY),
            ("read_ui_element", PermissionLevel.SAFE_READ_ONLY),
            ("focus_window", PermissionLevel.CONTROLLED_ACTION)
        ]
        for t_name, level in read_tools:
            allowed, reason = default_permission_policy.is_tool_allowed(
                tool_name=t_name,
                permission_level=level,
                is_confirmed=False
            )
            self.assertTrue(allowed, f"Tool '{t_name}' should be auto-approved, got: {reason}")

    def test_controlled_action_requires_confirmation(self):
        """Verify clicking and typing require user confirmation when not confirmed."""
        controlled_tools = [
            ("click_ui_element", PermissionLevel.CONTROLLED_ACTION),
            ("type_into_ui_element", PermissionLevel.CONTROLLED_ACTION),
            ("press_key", PermissionLevel.CONTROLLED_ACTION)
        ]
        for t_name, level in controlled_tools:
            # Without confirmation: must be blocked
            allowed, reason = default_permission_policy.is_tool_allowed(
                tool_name=t_name,
                permission_level=level,
                is_confirmed=False
            )
            self.assertFalse(allowed, f"Tool '{t_name}' without confirmation should be blocked")
            self.assertIn("user confirmation", reason.lower())

            # With confirmation: must be permitted
            allowed_conf, reason_conf = default_permission_policy.is_tool_allowed(
                tool_name=t_name,
                permission_level=level,
                is_confirmed=True
            )
            self.assertTrue(allowed_conf, f"Tool '{t_name}' with confirmation should be permitted")

    # -----------------------------------------------------------------------
    # 6. Tool Registry & Tool Executor Integration Tests
    # -----------------------------------------------------------------------

    def test_phase2_3_tools_registered(self):
        """Verify all 9 new UI Automation tools are registered in default_tool_registry."""
        expected_tools = [
            "list_windows",
            "get_active_window",
            "inspect_window",
            "find_ui_element",
            "click_ui_element",
            "type_into_ui_element",
            "read_ui_element",
            "focus_window",
            "press_key"
        ]
        for tool_name in expected_tools:
            tool = default_tool_registry.get(tool_name)
            self.assertIsNotNone(tool, f"Tool '{tool_name}' must be registered in default_tool_registry")
            self.assertEqual(tool.category, "ui_automation")
            self.assertIsNotNone(tool.handler)
            self.assertIn("parameters", tool.to_ollama_tool()["function"])

    def test_list_windows_executor_execution(self):
        """Verify list_windows executes through the 5-stage ToolExecutor pipeline."""
        res = default_tool_executor.execute_tool(
            tool_name="list_windows",
            arguments={"visible_only": True, "maximum_results": 10},
            is_confirmed=False
        )
        self.assertTrue(res.success)
        self.assertEqual(res.status, "success")
        self.assertIsInstance(res.result, dict)
        self.assertIn("windows", res.result.get("data", {}))
        self.assertGreater(res.duration_ms, 0)

    def test_get_active_window_executor_execution(self):
        """Verify get_active_window executes through ToolExecutor."""
        res = default_tool_executor.execute_tool(
            tool_name="get_active_window",
            arguments={},
            is_confirmed=False
        )
        self.assertTrue(res.success)
        self.assertEqual(res.status, "success")

    def test_click_ui_element_requires_confirmation_in_executor(self):
        """Verify calling click_ui_element unconfirmed in ToolExecutor stages for approval."""
        res = default_tool_executor.execute_tool(
            tool_name="click_ui_element",
            arguments={"window_title": "Notepad", "element_name": "Save"},
            is_confirmed=False
        )
        self.assertFalse(res.success)
        self.assertEqual(res.status, "requires_confirmation")
        self.assertIn("confirmation", res.error.lower())

    def test_press_key_requires_confirmation_in_executor(self):
        """Verify press_key unconfirmed in ToolExecutor stages for approval."""
        res = default_tool_executor.execute_tool(
            tool_name="press_key",
            arguments={"window_title": "Notepad", "key": "Ctrl+S"},
            is_confirmed=False
        )
        self.assertFalse(res.success)
        self.assertEqual(res.status, "requires_confirmation")


if __name__ == "__main__":
    unittest.main(verbosity=2)
