"""
Task Manager Page - Task queues, filters, and execution tracking.
Matches 03_task_manager.png reference design.
"""
from typing import Optional
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QScrollArea, QDialog, QLineEdit,
    QComboBox, QMessageBox, QSizePolicy
)
from ...core.task_manager import TaskManager


class TaskRowWidget(QFrame):
    """Single row representing a task in the queue."""

    def __init__(self, task: dict, on_details: callable, on_stop: callable):
        super().__init__()
        self.task = task
        self.on_details = on_details
        self.on_stop = on_stop
        self._init_ui()

    def _init_ui(self) -> None:
        self.setProperty("class", "surfaceCard")
        self.setStyleSheet("""
            TaskRowWidget {
                background-color: #1c1d22;
                border: 1px solid #282a30;
                border-radius: 8px;
                padding: 12px 16px;
            }
            TaskRowWidget:hover {
                border: 1px solid #383a42;
                background-color: #202228;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(16)

        # Task Name
        name_label = QLabel(self.task.get("name", "Unnamed Task"))
        name_label.setStyleSheet("color: #ffffff; font-size: 13px; font-weight: 500;")
        layout.addWidget(name_label, 1)

        # Progress bar placeholder
        progress_val = self.task.get("progress", 0)
        if progress_val > 0:
            pbar = QProgressBar()
            pbar.setValue(progress_val)
            pbar.setFixedHeight(8)
            pbar.setFixedWidth(100)
            pbar.setTextVisible(False)
            pbar.setStyleSheet("""
                QProgressBar {
                    background-color: #16171b;
                    border: 1px solid #282a30;
                    border-radius: 4px;
                }
                QProgressBar::chunk {
                    background-color: #e59840;
                    border-radius: 3px;
                }
            """)
            layout.addWidget(pbar)

        # Status text matching reference 03_task_manager.png
        status_text = self.task.get("status", "waiting").capitalize()
        status_label = QLabel(status_text)
        if status_text.lower() == "running":
            status_label.setStyleSheet("color: #e59840; font-size: 12px; font-weight: 600;")
        else:
            status_label.setStyleSheet("color: #8e929b; font-size: 12px;")
        layout.addWidget(status_label)

        # Details Button
        details_btn = QPushButton("Details")
        details_btn.setProperty("class", "secondaryButton")
        details_btn.setCursor(Qt.PointingHandCursor)
        details_btn.clicked.connect(lambda: self.on_details(self.task))
        layout.addWidget(details_btn)

        # Stop Button Placeholder
        stop_btn = QPushButton("Stop")
        stop_btn.setProperty("class", "secondaryButton")
        stop_btn.setCursor(Qt.PointingHandCursor)
        stop_btn.clicked.connect(lambda: self.on_stop(self.task))
        layout.addWidget(stop_btn)


class TasksPage(QWidget):
    """Full Task Manager page with metrics, filters, and task rows."""

    def __init__(self, task_manager: TaskManager):
        super().__init__()
        self.task_manager = task_manager
        self._current_filter = "all"
        self._init_ui()
        self.refresh_tasks()

        self.task_manager.tasks_updated.connect(self.refresh_tasks)

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()
        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(4)
        
        title_label = QLabel("Task Manager")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Track running, waiting, scheduled and completed work.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_text_layout.addWidget(title_label)
        header_text_layout.addWidget(subtitle_label)
        header_layout.addLayout(header_text_layout, 1)

        # New Task Button
        new_task_btn = QPushButton("＋ Add Task")
        new_task_btn.setProperty("class", "primaryButton")
        new_task_btn.setCursor(Qt.PointingHandCursor)
        new_task_btn.clicked.connect(self._open_new_task_dialog)
        header_layout.addWidget(new_task_btn)

        layout.addLayout(header_layout)

        # Top Metric Card matching reference: "Running 0   Waiting 3   Scheduled 0   Completed 0"
        self.metric_card = QFrame()
        self.metric_card.setProperty("class", "surfaceCard")
        metric_layout = QHBoxLayout(self.metric_card)
        metric_layout.setContentsMargins(24, 20, 24, 20)
        metric_layout.setSpacing(32)

        self.lbl_running = QLabel("Running 0")
        self.lbl_waiting = QLabel("Waiting 0")
        self.lbl_scheduled = QLabel("Scheduled 0")
        self.lbl_completed = QLabel("Completed 0")

        for lbl in (self.lbl_running, self.lbl_waiting, self.lbl_scheduled, self.lbl_completed):
            lbl.setStyleSheet("color: #e2e4e9; font-size: 15px; font-weight: 500;")
            metric_layout.addWidget(lbl)

        metric_layout.addStretch()
        layout.addWidget(self.metric_card)

        # Section Header: "TASK QUEUE"
        queue_header = QLabel("TASK QUEUE")
        queue_header.setStyleSheet("""
            color: #ffffff;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.8px;
            margin-top: 10px;
        """)
        layout.addWidget(queue_header)

        # Scrollable Task Queue Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.queue_container = QWidget()
        self.queue_container.setStyleSheet("background: transparent;")
        self.queue_layout = QVBoxLayout(self.queue_container)
        self.queue_layout.setContentsMargins(0, 0, 0, 0)
        self.queue_layout.setSpacing(12)
        self.queue_layout.addStretch()

        self.scroll_area.setWidget(self.queue_container)
        layout.addWidget(self.scroll_area, 1)

    def refresh_tasks(self) -> None:
        # Update metrics
        counts = self.task_manager.get_task_counts()
        self.lbl_running.setText(f"Running  {counts.get('running', 0)}")
        self.lbl_waiting.setText(f"Waiting  {counts.get('waiting', 0)}")
        self.lbl_scheduled.setText(f"Scheduled  {counts.get('scheduled', 0)}")
        self.lbl_completed.setText(f"Completed  {counts.get('completed', 0)}")

        # Clear existing items
        while self.queue_layout.count() > 1:
            item = self.queue_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Populate rows
        tasks = self.task_manager.get_all_tasks()
        for task in tasks:
            row = TaskRowWidget(task, self._show_details, self._stop_task)
            idx = max(0, self.queue_layout.count() - 1)
            self.queue_layout.insertWidget(idx, row)

    def _show_details(self, task: dict) -> None:
        QMessageBox.information(
            self,
            "Task Details",
            f"Task: {task.get('name')}\n"
            f"Category: {task.get('category')}\n"
            f"Status: {task.get('status')}\n"
            f"Progress: {task.get('progress')}%\n"
            f"Start Time: {task.get('start_time')}\n"
            f"Created: {task.get('created_at')}"
        )

    def _stop_task(self, task: dict) -> None:
        self.task_manager.update_task_status(task["id"], "completed", 100)

    def _open_new_task_dialog(self) -> None:
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Task")
        dialog.setFixedSize(380, 240)
        dialog.setStyleSheet("background-color: #1c1d22; color: #ffffff;")
        
        dlg_layout = QVBoxLayout(dialog)
        dlg_layout.setSpacing(12)

        lbl = QLabel("Task Name:")
        inp_name = QLineEdit()
        inp_name.setPlaceholderText("e.g., Scan local directory")

        lbl_cat = QLabel("Category:")
        cat_combo = QComboBox()
        cat_combo.addItems(["automation", "coding", "file_ops", "general", "browser"])

        btn_box = QHBoxLayout()
        add_btn = QPushButton("Create Task")
        add_btn.setProperty("class", "primaryButton")
        add_btn.clicked.connect(lambda: self._create_task(inp_name.text(), cat_combo.currentText(), dialog))
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("class", "secondaryButton")
        cancel_btn.clicked.connect(dialog.reject)

        btn_box.addStretch()
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(add_btn)

        dlg_layout.addWidget(lbl)
        dlg_layout.addWidget(inp_name)
        dlg_layout.addWidget(lbl_cat)
        dlg_layout.addWidget(cat_combo)
        dlg_layout.addStretch()
        dlg_layout.addLayout(btn_box)

        dialog.exec()

    def _create_task(self, name: str, category: str, dialog: QDialog) -> None:
        if name.strip():
            self.task_manager.add_task(name.strip(), category, "waiting")
            dialog.accept()
