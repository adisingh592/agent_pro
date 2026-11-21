"""
Home Page - Primary dashboard for the Personal Agent.
Matches 01_home_dashboard.png reference design.
"""
from typing import Callable, Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QGridLayout, QSizePolicy
)
from ...core.agent import AgentCore


class HomePage(QWidget):
    """Home Dashboard matching reference UI."""

    def __init__(self, agent_core: AgentCore, navigate_cb: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.agent_core = agent_core
        self.navigate_cb = navigate_cb
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(24)
        layout.setAlignment(Qt.AlignTop)

        # Page Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("Home")
        title_label.setObjectName("homeTitle")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Your personal workspace for tasks, automation and coding.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)

        # Main Command Card: "What would you like me to do?"
        cmd_card = QFrame()
        cmd_card.setProperty("class", "surfaceCard")
        cmd_card_layout = QVBoxLayout(cmd_card)
        cmd_card_layout.setContentsMargins(24, 24, 24, 24)
        cmd_card_layout.setSpacing(12)

        card_title = QLabel("What would you like me to do?")
        card_title.setProperty("class", "cardHeading")
        
        card_sub = QLabel("Ask, automate, code, or control your desktop.")
        card_sub.setProperty("class", "cardSubheading")

        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Type a task or use voice...")
        self.cmd_input.setStyleSheet("""
            QLineEdit {
                background-color: #16171b;
                border: 1px solid #282a30;
                border-radius: 8px;
                padding: 10px 16px;
                color: #ffffff;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #e59840;
            }
        """)
        self.cmd_input.returnPressed.connect(self._on_command_submit)

        cmd_card_layout.addWidget(card_title)
        cmd_card_layout.addWidget(card_sub)
        cmd_card_layout.addWidget(self.cmd_input)
        layout.addWidget(cmd_card)

        # QUICK ACTIONS Section
        actions_header = QLabel("QUICK ACTIONS")
        actions_header.setStyleSheet("""
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.8px;
            margin-top: 8px;
        """)
        layout.addWidget(actions_header)

        actions_grid = QGridLayout()
        actions_grid.setSpacing(14)

        actions = [
            ("Automate task", "Workflows"),
            ("Open application", "Tasks"),
            ("Manage files", "Files"),
            ("Start coding", "Coding Workspace")
        ]

        for i, (label, target_page) in enumerate(actions):
            btn = QPushButton(label)
            btn.setProperty("class", "quickActionButton")
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(52)
            btn.clicked.connect(lambda checked=False, p=target_page: self._on_quick_action(p))
            actions_grid.addWidget(btn, 0, i)

        layout.addLayout(actions_grid)

        # ACTIVE TASKS Section
        active_header = QLabel("ACTIVE TASKS")
        active_header.setStyleSheet("""
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.8px;
            margin-top: 8px;
        """)
        layout.addWidget(active_header)

        self.active_tasks_card = QFrame()
        self.active_tasks_card.setProperty("class", "surfaceCard")
        tasks_card_layout = QVBoxLayout(self.active_tasks_card)
        tasks_card_layout.setContentsMargins(20, 20, 20, 20)
        tasks_card_layout.setSpacing(6)

        self.active_task_status = QLabel("Nothing running right now")
        self.active_task_status.setStyleSheet("color: #e2e4e9; font-size: 14px; font-weight: 500;")
        
        self.active_task_desc = QLabel("Your active tasks and progress will appear here.")
        self.active_task_desc.setStyleSheet("color: #8e929b; font-size: 12px;")

        tasks_card_layout.addWidget(self.active_task_status)
        tasks_card_layout.addWidget(self.active_task_desc)
        layout.addWidget(self.active_tasks_card)

        layout.addStretch()

        # Connect Agent updates
        self.agent_core.current_task_changed.connect(self._on_task_changed)

    def _on_command_submit(self) -> None:
        text = self.cmd_input.text().strip()
        if text:
            self.cmd_input.clear()
            self.agent_core.process_user_input(text)
            if self.navigate_cb:
                self.navigate_cb("Agent Chat")

    def _on_quick_action(self, target_page: str) -> None:
        if self.navigate_cb:
            self.navigate_cb(target_page)

    def _on_task_changed(self, title: str, detail: str) -> None:
        if title and title != "No task running":
            self.active_task_status.setText(title)
            self.active_task_desc.setText(detail or "In progress...")
        else:
            self.active_task_status.setText("Nothing running right now")
            self.active_task_desc.setText("Your active tasks and progress will appear here.")
