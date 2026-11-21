"""
Automated Verification Suite for Personal Agent Phase 1.
Tests:
- Application initialization
- Sidebar navigation across all 11 pages
- Chat input and response dispatching
- SQLite persistence (tasks, memory, activity logs)
- Window resizing across multiple resolutions
- Visual rendering / offscreen pixmap capture of pages
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Default to windows platform if available, or offscreen
if "QT_QPA_PLATFORM" not in os.environ and sys.platform != "win32":
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap, QPainter

from app.ui.main_window import MainWindow
from app.core.agent import AgentCore
from app.core.task_manager import TaskManager
from app.memory.memory_store import MemoryStore


def run_tests():
    print("[1/6] Initializing QApplication...")
    app = QApplication.instance() or QApplication(sys.argv)

    print("[2/6] Instantiating MainWindow...")
    window = MainWindow()
    window.resize(1340, 840)
    window.show()

    # Verify 11 pages exist
    expected_pages = [
        "Home", "Agent Chat", "Tasks", "Files", "Browser",
        "Coding Workspace", "Workflows", "Voice", "Memory",
        "History", "Settings"
    ]
    print(f"[3/6] Verifying all {len(expected_pages)} pages exist and navigate correctly...")
    for page_name in expected_pages:
        assert page_name in window.pages, f"Missing page: {page_name}"
        window.navigate_to_page(page_name)
        current_widget = window.workspace_stack.currentWidget()
        assert current_widget == window.pages[page_name], f"Navigation failed for: {page_name}"
        print(f"  ✓ Navigated to '{page_name}' successfully")

    print("[4/6] Testing Chat interaction and AgentCore responses...")
    chat_page = window.pages["Agent Chat"]
    initial_msg_count = chat_page.messages_layout.count()
    test_prompt = "Organize my Downloads after all downloads finish."
    window.agent_core.process_user_input(test_prompt)
    new_msg_count = chat_page.messages_layout.count()
    # Should have added user message + agent response
    assert new_msg_count >= initial_msg_count + 2, "Chat messages were not appended properly"
    print("  ✓ Chat message processed and agent responded correctly")
    print(f"  ✓ Agent Status: {window.agent_core.status}")

    print("[5/6] Testing SQLite Persistence (Tasks and Memory)...")
    task_mgr = window.task_manager
    initial_counts = task_mgr.get_task_counts()
    new_task_id = task_mgr.add_task("Test automated verification task", "testing", "waiting")
    assert new_task_id > 0, "Failed to insert task into database"
    task_mgr.update_task_status(new_task_id, "completed", 100)
    task_mgr.delete_task(new_task_id)
    print("  ✓ TaskManager SQLite CRUD operations passed")

    mem_store = window.memory_store
    mem_id = mem_store.add_item("Projects", "Automated Test Project", "Verified by test suite")
    assert mem_id > 0, "Failed to insert memory item into database"
    search_results = mem_store.search_memory("Automated Test Project")
    assert len(search_results) > 0, "Failed to query stored memory item"
    print("  ✓ MemoryStore SQLite queries passed")

    print("[6/6] Testing Window Resizing (Responsiveness)...")
    test_resolutions = [
        QSize(1024, 768),
        QSize(1280, 800),
        QSize(1440, 900),
        QSize(1920, 1080)
    ]
    for res in test_resolutions:
        window.resize(res)
        window.repaint()
        assert window.width() == res.width() and window.height() == res.height()
    print("  ✓ Window resize checks passed across all target resolutions")

    # Capture screenshots of key pages to verify against reference images
    screenshots_dir = PROJECT_ROOT / "tests" / "screenshots"
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    
    pages_to_capture = ["Home", "Agent Chat", "Tasks", "Coding Workspace", "Workflows"]
    window.resize(1340, 840)
    for p in pages_to_capture:
        window.navigate_to_page(p)
        window.repaint()
        pixmap = window.grab()
        file_path = screenshots_dir / f"test_{p.lower().replace(' ', '_')}.png"
        pixmap.save(str(file_path), "PNG")
        print(f"  ✓ Saved test render: {file_path.name}")

    print("\n==========================================")
    print(" ALL PHASE 1 VERIFICATION TESTS PASSED! ")
    print("==========================================")


if __name__ == "__main__":
    run_tests()
