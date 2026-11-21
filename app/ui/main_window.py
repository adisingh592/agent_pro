"""
Main Window for the Personal Agent Desktop Application.
Assembles Persistent Top Bar, Left Sidebar, Main Workspace, Right Agent Panel, and Status Bar.
Matches visual design from reference images (01_home_dashboard.png to 05_workflow_builder.png).
"""
import sys
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QStackedWidget, QStatusBar, QFrame, QSizePolicy
)

from ..core.agent import AgentCore
from ..core.model_manager import ModelManager
from ..core.task_manager import TaskManager
from ..core.system_monitor import SystemMonitor
from ..memory.memory_store import MemoryStore

from .sidebar import Sidebar
from .panels.agent_panel import RightAgentPanel
from .pages.home_page import HomePage
from .pages.chat_page import ChatPage
from .pages.tasks_page import TasksPage
from .pages.files_page import FilesPage
from .pages.browser_page import BrowserPage
from .pages.coding_page import CodingPage
from .pages.workflows_page import WorkflowsPage
from .pages.voice_page import VoicePage
from .pages.memory_page import MemoryPage
from .pages.history_page import HistoryPage
from .pages.settings_page import SettingsPage


class MainWindow(QMainWindow):
    """Primary application window for Personal Agent."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Agent")
        self.resize(1340, 840)
        self.setMinimumSize(1024, 680)

        # Initialize Core Services
        self.model_manager = ModelManager()
        self.agent_core = AgentCore(self.model_manager)
        self.task_manager = TaskManager()
        self.memory_store = MemoryStore()
        self.system_monitor = SystemMonitor(interval_ms=2500)

        self._init_ui()
        self._load_stylesheet()

        # Connect system monitor to status bar
        self.system_monitor.metrics_updated.connect(self._on_metrics_updated)
        self.model_manager.connection_changed.connect(self._on_model_changed)
        self.agent_core.status_changed.connect(self._on_agent_status_changed)

        # Initial model status sync
        self._on_model_changed(
            self.model_manager.active_model_display,
            self.model_manager.is_connected,
            self.model_manager.processor_info
        )

    def _init_ui(self) -> None:
        # Central Root Container
        central_widget = QWidget()
        central_widget.setObjectName("centralWidget")
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. TOP HEADER BAR matching reference images
        top_bar = self._create_top_bar()
        root_layout.addWidget(top_bar)

        # 2. THREE-PART MAIN BODY (Sidebar, Center Workspace, Right Panel)
        body_container = QWidget()
        body_container.setObjectName("mainContainer")
        body_layout = QHBoxLayout(body_container)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Left Sidebar
        self.sidebar = Sidebar()
        self.sidebar.page_selected.connect(self._on_navigate)
        body_layout.addWidget(self.sidebar)

        # Center Workspace (QStackedWidget)
        self.workspace_stack = QStackedWidget()
        self._init_workspace_pages()
        body_layout.addWidget(self.workspace_stack, 1)

        # Right Agent Panel
        self.right_panel = RightAgentPanel(self.agent_core, self.model_manager)
        body_layout.addWidget(self.right_panel)

        root_layout.addWidget(body_container, 1)

        # 3. BOTTOM STATUS BAR matching reference images
        self._create_status_bar()

        self.setCentralWidget(central_widget)

    def _create_top_bar(self) -> QWidget:
        """Top Header Bar with Brand Title, Global Search, and Agent Status Dot."""
        top_bar = QFrame()
        top_bar.setObjectName("topBar")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(20, 10, 20, 10)
        top_layout.setSpacing(20)

        # Left: Brand Title
        brand_lbl = QLabel("PERSONAL AGENT")
        brand_lbl.setObjectName("brandTitle")
        top_layout.addWidget(brand_lbl)

        # Center: Global Search Input
        top_layout.addStretch(1)
        self.search_box = QLineEdit()
        self.search_box.setObjectName("topSearchBox")
        self.search_box.setPlaceholderText("🔍  Search tasks, files, or commands")
        self.search_box.returnPressed.connect(self._on_global_search)
        top_layout.addWidget(self.search_box)
        top_layout.addStretch(1)

        # Right: Agent Ready Status Dot
        self.top_status_dot = QLabel("●  Agent ready")
        self.top_status_dot.setObjectName("topStatusDot")
        top_layout.addWidget(self.top_status_dot)

        return top_bar

    def _init_workspace_pages(self) -> None:
        """Instantiate all 11 pages into the stacked widget."""
        self.pages = {
            "Home": HomePage(self.agent_core, navigate_cb=self.navigate_to_page),
            "Agent Chat": ChatPage(self.agent_core, self.model_manager),
            "Tasks": TasksPage(self.task_manager),
            "Files": FilesPage(),
            "Browser": BrowserPage(),
            "Coding Workspace": CodingPage(),
            "Workflows": WorkflowsPage(),
            "Voice": VoicePage(),
            "Memory": MemoryPage(self.memory_store),
            "History": HistoryPage(),
            "Settings": SettingsPage(),
        }

        for name, page_widget in self.pages.items():
            self.workspace_stack.addWidget(page_widget)

    def _create_status_bar(self) -> None:
        status_bar = self.statusBar()
        status_bar.setObjectName("statusBar")

        # Left: Agent status dot
        self.sb_agent_status = QLabel("● Agent Ready")
        self.sb_agent_status.setStyleSheet("color: #9ca3af; padding-left: 8px;")
        status_bar.addWidget(self.sb_agent_status)

        # Center/Left: Model status matching reference: "Local model: not connected"
        self.sb_model_status = QLabel("        Local model: not connected")
        self.sb_model_status.setStyleSheet("color: #8e929b;")
        status_bar.addWidget(self.sb_model_status)

        # Right: System metrics (CPU / RAM)
        self.sb_metrics = QLabel("CPU: --% | RAM: --% | Phase 1 Active")
        self.sb_metrics.setStyleSheet("color: #8e929b; padding-right: 12px;")
        status_bar.addPermanentWidget(self.sb_metrics)

    def _on_navigate(self, page_name: str) -> None:
        # Handle "Voice" vs "Voice Assistant" mapping if necessary
        target = "Voice" if "voice" in page_name.lower() else page_name
        if target in self.pages:
            self.workspace_stack.setCurrentWidget(self.pages[target])

    def navigate_to_page(self, page_name: str) -> None:
        """Programmatic navigation (e.g. from Home quick actions)."""
        self.sidebar.select_page(page_name)
        self._on_navigate(page_name)

    def _on_global_search(self) -> None:
        query = self.search_box.text().strip()
        if query:
            self.agent_core.process_user_input(query)
            self.navigate_to_page("Agent Chat")
            self.search_box.clear()

    def _on_model_changed(self, display_name: str, is_connected: bool, processor_info: str = "") -> None:
        if is_connected:
            proc_text = f" ({processor_info})" if processor_info else ""
            self.sb_model_status.setText(f"        Ollama: {self.model_manager.active_model}{proc_text}")
            self.sb_model_status.setStyleSheet("color: #8e929b;")
            self.top_status_dot.setText("●  Agent ready (Ollama)")
            self.top_status_dot.setStyleSheet("color: #9ca3af;")
        else:
            self.sb_model_status.setText("        Local model: not connected")
            self.sb_model_status.setStyleSheet("color: #f87171;")
            self.top_status_dot.setText("●  Ollama offline")
            self.top_status_dot.setStyleSheet("color: #f87171;")

    def _on_agent_status_changed(self, status: str) -> None:
        if status.lower() == "working":
            self.sb_agent_status.setText("● Working...")
            self.sb_agent_status.setStyleSheet("color: #e59840; padding-left: 8px;")
        else:
            self.sb_agent_status.setText("● Agent Ready")
            self.sb_agent_status.setStyleSheet("color: #9ca3af; padding-left: 8px;")

    def _on_metrics_updated(self, cpu: float, ram: float, gpu: dict = None) -> None:
        gpu_str = ""
        if gpu and gpu.get("available"):
            util = gpu.get("utilization", 0)
            used_gb = gpu.get("vram_used_mb", 0) / 1024.0
            total_gb = gpu.get("vram_total_mb", 0) / 1024.0
            gpu_str = f" | GPU: {util}% ({used_gb:.1f}/{total_gb:.1f} GB)"
        self.sb_metrics.setText(f"CPU: {cpu:.1f}% | RAM: {ram:.1f}%{gpu_str} | Phase 2.1")

    def _load_stylesheet(self) -> None:
        qss_path = Path(__file__).parent / "theme.qss"
        if qss_path.exists():
            with open(qss_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
