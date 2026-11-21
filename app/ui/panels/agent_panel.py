"""
Right Agent Panel - Persistent status, task, and execution monitoring panel.
Matches reference images (01_home_dashboard.png to 05_workflow_builder.png).
"""
from typing import List
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar,
    QScrollArea, QSizePolicy
)
from ...core.agent import AgentCore
from ...core.model_manager import ModelManager


class RightAgentPanel(QFrame):
    """Persistent right sidebar monitoring Agent Status, Tasks, and Activity."""

    def __init__(self, agent_core: AgentCore, model_manager: ModelManager):
        super().__init__()
        self.agent_core = agent_core
        self.model_manager = model_manager
        self.setObjectName("rightAgentPanel")
        self._init_ui()

        # Connect Agent Signals
        self.agent_core.status_changed.connect(self._on_status_changed)
        self.agent_core.current_task_changed.connect(self._on_task_changed)
        self.agent_core.execution_state_changed.connect(self._on_execution_state_changed)
        self.agent_core.activity_logged.connect(self._on_activity_logged)
        self.model_manager.connection_changed.connect(self._on_model_changed)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignTop)

        # 1. AGENT STATUS Section matching reference images
        status_sec_lbl = QLabel("AGENT STATUS")
        status_sec_lbl.setProperty("class", "sectionHeader")
        layout.addWidget(status_sec_lbl)

        self.status_card = QFrame()
        self.status_card.setProperty("class", "panelCard")
        sc_layout = QHBoxLayout(self.status_card)
        sc_layout.setContentsMargins(12, 10, 12, 10)
        sc_layout.setSpacing(8)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #a0a5b0; font-size: 11px;")
        
        self.status_lbl = QLabel(self.agent_core.status)
        self.status_lbl.setProperty("class", "panelCardTitle")

        sc_layout.addWidget(self.status_dot)
        sc_layout.addWidget(self.status_lbl, 1)
        layout.addWidget(self.status_card)

        # 2. CURRENT TASK Section matching reference images
        task_sec_lbl = QLabel("CURRENT TASK")
        task_sec_lbl.setProperty("class", "sectionHeader")
        layout.addWidget(task_sec_lbl)

        self.task_card = QFrame()
        self.task_card.setProperty("class", "panelCard")
        tc_layout = QVBoxLayout(self.task_card)
        tc_layout.setContentsMargins(12, 10, 12, 10)
        tc_layout.setSpacing(4)

        t_title, t_detail = self.agent_core.current_task
        self.task_title_lbl = QLabel(t_title)
        self.task_title_lbl.setProperty("class", "panelCardTitle")
        
        self.task_detail_lbl = QLabel(t_detail)
        self.task_detail_lbl.setProperty("class", "panelCardSubtitle")

        tc_layout.addWidget(self.task_title_lbl)
        tc_layout.addWidget(self.task_detail_lbl)
        layout.addWidget(self.task_card)

        # 3. CURRENT EXECUTION STATE & PROGRESS
        exec_sec_lbl = QLabel("EXECUTION STATE")
        exec_sec_lbl.setProperty("class", "sectionHeader")
        layout.addWidget(exec_sec_lbl)

        self.exec_card = QFrame()
        self.exec_card.setProperty("class", "panelCard")
        ec_layout = QVBoxLayout(self.exec_card)
        ec_layout.setContentsMargins(12, 10, 12, 10)
        ec_layout.setSpacing(6)

        self.exec_state_lbl = QLabel(f"State: {self.agent_core.execution_state}")
        self.exec_state_lbl.setProperty("class", "panelCardSubtitle")

        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(6)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #16171b;
                border: 1px solid #282a30;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #e59840;
                border-radius: 2px;
            }
        """)

        ec_layout.addWidget(self.exec_state_lbl)
        ec_layout.addWidget(self.progress_bar)
        layout.addWidget(self.exec_card)

        # 4. MODEL CONNECTION STATUS
        model_sec_lbl = QLabel("MODEL CONNECTION")
        model_sec_lbl.setProperty("class", "sectionHeader")
        layout.addWidget(model_sec_lbl)

        self.model_card = QFrame()
        self.model_card.setProperty("class", "panelCard")
        mc_layout = QVBoxLayout(self.model_card)
        mc_layout.setContentsMargins(12, 10, 12, 10)
        mc_layout.setSpacing(4)

        self.model_name_lbl = QLabel(self.model_manager.active_model_display)
        self.model_name_lbl.setProperty("class", "panelCardTitle")

        status_text = "Connected" if self.model_manager.is_connected else "Standby / Local"
        self.model_status_lbl = QLabel(status_text)
        self.model_status_lbl.setProperty("class", "panelCardSubtitle")

        mc_layout.addWidget(self.model_name_lbl)
        mc_layout.addWidget(self.model_status_lbl)
        layout.addWidget(self.model_card)

        # 5. RECENT ACTIVITY Section matching reference images
        act_sec_lbl = QLabel("RECENT ACTIVITY")
        act_sec_lbl.setProperty("class", "sectionHeader")
        layout.addWidget(act_sec_lbl)

        self.activity_container = QWidget()
        self.activity_container.setStyleSheet("background: transparent;")
        self.activity_layout = QVBoxLayout(self.activity_container)
        self.activity_layout.setContentsMargins(0, 0, 0, 0)
        self.activity_layout.setSpacing(8)

        self._render_activities()
        layout.addWidget(self.activity_container)

        layout.addStretch()

    def _render_activities(self) -> None:
        while self.activity_layout.count() > 0:
            item = self.activity_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for act in self.agent_core.recent_activities[:6]:
            lbl = QLabel(f"•  {act}")
            lbl.setProperty("class", "activityItem")
            lbl.setWordWrap(True)
            self.activity_layout.addWidget(lbl)

    def _on_status_changed(self, status: str) -> None:
        self.status_lbl.setText(status)
        if status.lower() == "working":
            self.status_dot.setStyleSheet("color: #e59840; font-size: 11px;")
            self.progress_bar.setValue(50)
        else:
            self.status_dot.setStyleSheet("color: #a0a5b0; font-size: 11px;")
            self.progress_bar.setValue(0)

    def _on_task_changed(self, title: str, detail: str) -> None:
        self.task_title_lbl.setText(title or "No task running")
        self.task_detail_lbl.setText(detail or "Waiting for instruction")

    def _on_execution_state_changed(self, state: str) -> None:
        self.exec_state_lbl.setText(f"State: {state}")

    def _on_activity_logged(self, activity: str) -> None:
        self._render_activities()

    def _on_model_changed(self, display_name: str, is_connected: bool) -> None:
        self.model_name_lbl.setText(display_name)
        self.model_status_lbl.setText("Connected" if is_connected else "Standby / Local")
