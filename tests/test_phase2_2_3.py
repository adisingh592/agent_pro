"""
Comprehensive Test Suite for Phase 2.2.3: Application & Process Control.
Tests application discovery, name resolution, caching, safe launching,
open file/folder, process listing/filtering, status checking, graceful close,
critical process security restrictions, and tool executor pipeline integration.
Uses mock/dummy subprocesses to avoid touching real user applications.
"""
import os
import sys
import time
import subprocess
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.tools.app_discovery import (
    ApplicationDiscovery,
    ApplicationResolver,
    DiscoveredApplication,
    ResolutionResult,
    default_app_discovery,
    default_app_resolver
)
from app.tools.process_manager import (
    ProcessManager,
    default_process_manager
)
from app.tools.tool_permissions import PermissionLevel, ToolPermissionPolicy
from app.tools.tool_registry import ToolRegistry, default_tool_registry
from app.tools.tool_executor import ToolExecutor, default_tool_executor
from app.tools.app_tools import (
    search_applications,
    list_installed_applications,
    launch_application,
    open_file_with_application,
    open_folder,
    list_running_processes,
    check_application_status,
    get_process_info,
    close_application,
    register_app_tools
)


class TestAppDiscoveryAndResolution(unittest.TestCase):
    """Tests application discovery, caching, and natural language name resolution."""

    def setUp(self):
        self.discovery = ApplicationDiscovery()
        # Seed test discovery with controlled items
        self.test_apps = {
            "notepad": DiscoveredApplication(
                name="Notepad",
                display_name="Notepad",
                executable=r"C:\Windows\System32\notepad.exe",
                launch_command="notepad.exe",
                category="Productivity",
                source="Known Builtin",
                aliases=["editor", "txt"]
            ),
            "visual studio code": DiscoveredApplication(
                name="Visual Studio Code",
                display_name="Visual Studio Code",
                executable=r"C:\Users\test\Code.exe",
                launch_command="code",
                category="Development",
                source="App Paths",
                aliases=["code", "vs code", "vscode"]
            ),
            "visual studio 2022": DiscoveredApplication(
                name="Visual Studio 2022",
                display_name="Visual Studio 2022",
                executable=r"C:\Program Files\VS2022\devenv.exe",
                launch_command="devenv.exe",
                category="Development",
                source="Uninstall Registry",
                aliases=["devenv", "vs2022"]
            ),
            "google chrome": DiscoveredApplication(
                name="Google Chrome",
                display_name="Google Chrome",
                executable=r"C:\Program Files\Google\Chrome\chrome.exe",
                launch_command="chrome",
                category="Browser",
                source="App Paths",
                aliases=["chrome", "browser"]
            )
        }
        self.discovery._cache = dict(self.test_apps)
        self.discovery._last_scan_time = time.time()
        self.resolver = ApplicationResolver(self.discovery)

    def test_caching_behavior(self):
        """Verifies cache hits and cache invalidation without repeated scans."""
        cached = self.discovery.get_applications(force_refresh=False)
        self.assertEqual(len(cached), 4)
        self.assertIn("notepad", cached)

        # Invalidate cache
        self.discovery.clear_cache()
        self.assertEqual(len(self.discovery._cache), 0)

    def test_exact_resolution(self):
        """Tests exact application name resolution."""
        res = self.resolver.resolve("Notepad")
        self.assertTrue(res.resolved)
        self.assertFalse(res.ambiguous)
        self.assertEqual(res.app.name, "Notepad")
        self.assertEqual(res.confidence, 1.0)

    def test_alias_resolution(self):
        """Tests alias mapping (e.g. 'vs code' -> 'Visual Studio Code', 'chrome' -> 'Google Chrome')."""
        res_code = self.resolver.resolve("vs code")
        self.assertTrue(res_code.resolved)
        self.assertEqual(res_code.app.name, "Visual Studio Code")

        res_chrome = self.resolver.resolve("chrome")
        self.assertTrue(res_chrome.resolved)
        self.assertEqual(res_chrome.app.name, "Google Chrome")

    def test_fuzzy_resolution(self):
        """Tests fuzzy matching for slight typos."""
        res = self.resolver.resolve("google chrom")
        self.assertTrue(res.resolved)
        self.assertEqual(res.app.name, "Google Chrome")
        self.assertGreater(res.confidence, 0.65)

    def test_ambiguous_resolution(self):
        """Tests ambiguity guard when multiple applications match (e.g. 'Visual Studio')."""
        res = self.resolver.resolve("Visual Studio")
        self.assertFalse(res.resolved)
        self.assertTrue(res.ambiguous)
        self.assertGreaterEqual(len(res.candidates), 2)
        candidate_names = [c.name for c in res.candidates]
        self.assertIn("Visual Studio Code", candidate_names)
        self.assertIn("Visual Studio 2022", candidate_names)

    def test_unknown_application(self):
        """Tests rejection of completely unknown application names."""
        res = self.resolver.resolve("completely_unknown_quantum_browser_99")
        self.assertFalse(res.resolved)
        self.assertFalse(res.ambiguous)


class TestApplicationLaunchAndFileOperations(unittest.TestCase):
    """Tests launch_application, open_file_with_application, and open_folder."""

    def setUp(self):
        self.discovery = ApplicationDiscovery()
        self.discovery._cache = {
            "notepad": DiscoveredApplication(
                name="Notepad",
                display_name="Notepad",
                executable=r"C:\Windows\System32\notepad.exe",
                launch_command="notepad.exe",
                category="Productivity",
                source="Known Builtin"
            )
        }
        self.discovery._last_scan_time = time.time()
        self.resolver = ApplicationResolver(self.discovery)

    def test_launch_requires_confirmation(self):
        """Verifies launch_application requests confirmation when confirmed=False."""
        res = launch_application(
            application_name="Notepad",
            confirmed=False,
            resolver=self.resolver
        )
        self.assertFalse(res["success"])
        self.assertTrue(res["requires_confirmation"])
        self.assertEqual(res["tool"], "launch_application")
        self.assertEqual(res["application"], "Notepad")
        self.assertIn("Approval Required", res["title"])

    def test_launch_rejects_dangerous_shell_injection(self):
        """Verifies launch_application rejects command injection metacharacters."""
        res = launch_application(
            application_name="Notepad",
            optional_arguments="file.txt; calc.exe",
            confirmed=True,
            resolver=self.resolver
        )
        self.assertFalse(res["success"])
        self.assertIn("shell metacharacters", res["error"])

    def test_launch_handles_invalid_application(self):
        """Verifies launch fails safely for non-existent application."""
        res = launch_application(
            application_name="nonexistent_virtual_app_xyz",
            confirmed=True,
            resolver=self.resolver
        )
        self.assertFalse(res["success"])
        self.assertIn("Could not find", res["error"])

    def test_open_file_requires_confirmation_and_validates_path(self):
        """Verifies open_file_with_application enforces confirmation and safe path boundaries."""
        # Non-existent file
        res_nonexistent = open_file_with_application(
            file_path=r"C:\test_nonexistent_12345.txt",
            confirmed=False,
            resolver=self.resolver
        )
        self.assertFalse(res_nonexistent["success"])
        self.assertIn("does not exist", res_nonexistent["error"])

        # Create temporary valid text file
        test_file = PROJECT_ROOT / "test_dummy_app_file.txt"
        test_file.write_text("Hello World", encoding="utf-8")
        try:
            # Unconfirmed call
            res_conf = open_file_with_application(
                file_path=str(test_file),
                application_name="Notepad",
                confirmed=False,
                resolver=self.resolver
            )
            self.assertFalse(res_conf["success"])
            self.assertTrue(res_conf["requires_confirmation"])
            self.assertEqual(res_conf["tool"], "open_file_with_application")
        finally:
            if test_file.exists():
                test_file.unlink()

    def test_open_folder_requires_confirmation(self):
        """Verifies open_folder requires confirmation and validates directory existence."""
        res = open_folder(
            folder_path=str(PROJECT_ROOT),
            confirmed=False
        )
        self.assertFalse(res["success"])
        self.assertTrue(res["requires_confirmation"])
        self.assertEqual(res["tool"], "open_folder")


class TestProcessManagementTools(unittest.TestCase):
    """Tests process enumeration, filtering, status checking, and graceful closure."""

    def setUp(self):
        self.pm = ProcessManager()

    def test_list_running_processes(self):
        """Tests process listing with sorting and filtering."""
        res = self.pm.list_processes(maximum_results=10, sort_by="memory")
        self.assertTrue(res["success"])
        procs = res["result"]["processes"]
        self.assertGreater(len(procs), 0)
        first = procs[0]
        self.assertIn("pid", first)
        self.assertIn("name", first)
        self.assertIn("memory_mb", first)
        self.assertIn("cpu_percent", first)

        # Test filtering by python
        res_filter = self.pm.list_processes(filter_str="python", maximum_results=5)
        self.assertTrue(res_filter["success"])
        for p in res_filter["result"]["processes"]:
            self.assertIn("python", p["name"].lower())

    def test_check_application_status(self):
        """Tests checking status of running vs non-running applications."""
        # Current python is running
        res_running = self.pm.check_application_status("python")
        self.assertTrue(res_running["success"])
        self.assertTrue(res_running["result"]["is_running"])
        self.assertGreater(res_running["result"]["process_count"], 0)

        # Fake process is not running
        res_not_running = self.pm.check_application_status("totally_fake_agent_process_999.exe")
        self.assertTrue(res_not_running["success"])
        self.assertFalse(res_not_running["result"]["is_running"])
        self.assertEqual(res_not_running["result"]["process_count"], 0)

    def test_get_process_info_by_pid(self):
        """Tests retrieving detailed process stats for current PID."""
        current_pid = os.getpid()
        res = self.pm.get_process_info(optional_pid=current_pid)
        self.assertTrue(res["success"])
        p_data = res["result"]["processes"][0]
        self.assertEqual(p_data["pid"], current_pid)
        self.assertIn("python", p_data["name"].lower())
        self.assertGreater(p_data["memory_mb"], 0)

    def test_critical_process_protection(self):
        """Verifies that critical Windows system processes cannot be terminated."""
        critical_names = ["explorer.exe", "svchost.exe", "System", "csrss.exe", "dwm.exe"]
        for cname in critical_names:
            is_crit = self.pm.is_critical_process(cname)
            self.assertTrue(is_crit, f"{cname} should be protected as critical process.")

        # Attempting close_application on a critical process must be blocked
        res = close_application(application_name="explorer.exe", confirmed=True, process_manager=self.pm)
        self.assertFalse(res["success"])
        self.assertIn("Security restriction", res["error"])

        # Also current agent process PID must be protected
        res_self = close_application(application_name="python", optional_pid=os.getpid(), confirmed=True, process_manager=self.pm)
        self.assertFalse(res_self["success"])
        self.assertIn("Security restriction", res_self["error"])

    def test_graceful_process_closure_on_dummy_subprocess(self):
        """
        Tests graceful termination and verification using a safe dummy python subprocess.
        Spawns python -c 'import time; time.sleep(20)', confirms closure, and verifies exit.
        """
        dummy_proc = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(20)"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        dummy_pid = dummy_proc.pid
        time.sleep(0.3)

        try:
            # 1. Unconfirmed call must request confirmation
            res_unconf = close_application(
                application_name="dummy_python",
                optional_pid=dummy_pid,
                confirmed=False,
                process_manager=self.pm
            )
            self.assertFalse(res_unconf["success"])
            self.assertTrue(res_unconf["requires_confirmation"])
            self.assertEqual(res_unconf["tool"], "close_application")

            # 2. Confirmed call must gracefully terminate and verify exit
            res_conf = close_application(
                application_name="dummy_python",
                optional_pid=dummy_pid,
                confirmed=True,
                process_manager=self.pm
            )
            self.assertTrue(res_conf["success"])
            self.assertEqual(res_conf["result"]["status"], "closed")
            self.assertIn(dummy_pid, res_conf["result"]["closed_pids"])

            # 3. Post-verification: dummy process must no longer be running
            dummy_proc.poll()
            self.assertIsNotNone(dummy_proc.returncode)

        finally:
            if dummy_proc.poll() is None:
                dummy_proc.kill()


class TestToolRegistryAndExecutorIntegration(unittest.TestCase):
    """Verifies that all Phase 2.2.3 tools are properly registered and run through ToolExecutor."""

    def setUp(self):
        self.registry = default_tool_registry
        self.executor = default_tool_executor

    def test_phase2_2_3_tools_registered(self):
        """Verifies that all 9 Phase 2.2.3 tools exist in registry with correct permission levels."""
        expected_tools = {
            "search_applications": PermissionLevel.SAFE_READ_ONLY,
            "list_installed_applications": PermissionLevel.SAFE_READ_ONLY,
            "launch_application": PermissionLevel.CONTROLLED_ACTION,
            "open_file_with_application": PermissionLevel.CONTROLLED_ACTION,
            "open_folder": PermissionLevel.CONTROLLED_ACTION,
            "list_running_processes": PermissionLevel.SAFE_READ_ONLY,
            "check_application_status": PermissionLevel.SAFE_READ_ONLY,
            "get_process_info": PermissionLevel.SAFE_READ_ONLY,
            "close_application": PermissionLevel.PROCESS_MODIFICATION
        }

        for tname, expected_perm in expected_tools.items():
            tool_def = self.registry.get(tname)
            self.assertIsNotNone(tool_def, f"Tool '{tname}' must be registered.")
            self.assertEqual(tool_def.permission_level, expected_perm)

    def test_search_applications_executor_execution(self):
        """Verifies search_applications runs through ToolExecutor pipeline."""
        res = self.executor.execute("search_applications", {"query": "Notepad"})
        self.assertTrue(res.success)
        self.assertEqual(res.tool_name, "search_applications")
        self.assertGreater(res.duration_ms, 0)
        self.assertIn("applications", res.result)

    def test_list_running_processes_executor_execution(self):
        """Verifies list_running_processes runs through ToolExecutor pipeline."""
        res = self.executor.execute("list_running_processes", {"maximum_results": 5})
        self.assertTrue(res.success)
        self.assertEqual(res.tool_name, "list_running_processes")
        self.assertIn("processes", res.result)


if __name__ == "__main__":
    unittest.main()
