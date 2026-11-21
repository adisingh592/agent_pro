"""
Workflows Page (Automation Builder).
Matches 05_workflow_builder.png reference design.
Features custom canvas with interconnected nodes and amber connector lines.
"""
from PySide6.QtCore import Qt, QPoint, QRectF
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QFont
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QMessageBox, QSizePolicy
)


class WorkflowCanvasWidget(QWidget):
    """Custom canvas that renders interactive workflow nodes and connecting wires."""

    def __init__(self):
        super().__init__()
        self.setMinimumHeight(240)
        self.nodes = [
            {"title": "Trigger", "desc": "On file created"},
            {"title": "Wait for download", "desc": "Check file size stable"},
            {"title": "Move files", "desc": "Transfer to target drive"},
            {"title": "Verify", "desc": "Confirm checksum & notify"},
        ]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        width = self.width()
        height = self.height()

        node_w = 140
        node_h = 70
        spacing = 40
        total_w = len(self.nodes) * node_w + (len(self.nodes) - 1) * spacing
        start_x = max(24, (width - total_w) // 2)
        y = (height - node_h) // 2

        # 1. Draw connecting amber lines matching reference 05_workflow_builder.png
        pen = QPen(QColor("#e59840"), 2)
        painter.setPen(pen)
        
        for i in range(len(self.nodes) - 1):
            x1 = start_x + i * (node_w + spacing) + node_w
            x2 = start_x + (i + 1) * (node_w + spacing)
            mid_y = y + node_h // 2
            painter.drawLine(x1, mid_y, x2, mid_y)

        # 2. Draw Nodes
        for i, node in enumerate(self.nodes):
            x = start_x + i * (node_w + spacing)
            rect = QRectF(x, y, node_w, node_h)

            # Node card background
            brush = QBrush(QColor("#1f2127"))
            border_pen = QPen(QColor("#2d3039"), 1.2)
            painter.setBrush(brush)
            painter.setPen(border_pen)
            painter.drawRoundedRect(rect, 8, 8)

            # Title
            painter.setPen(QColor("#ffffff"))
            font_title = QFont()
            font_title.setBold(True)
            font_title.setPointSize(10)
            painter.setFont(font_title)
            painter.drawText(
                QRectF(x + 10, y + 24, node_w - 20, 24),
                Qt.AlignCenter,
                node["title"]
            )


class WorkflowsPage(QWidget):
    """Full Automation Builder page matching reference image 05."""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("Automation Builder")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Create reusable task flows with triggers, waits and actions.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)

        # Main Builder Card Container
        builder_card = QFrame()
        builder_card.setProperty("class", "surfaceCard")
        b_layout = QVBoxLayout(builder_card)
        b_layout.setContentsMargins(24, 20, 24, 20)
        b_layout.setSpacing(16)

        # Action Buttons Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        add_trigger_btn = QPushButton("＋ Add Trigger")
        add_trigger_btn.setProperty("class", "secondaryButton")
        add_trigger_btn.setCursor(Qt.PointingHandCursor)

        add_action_btn = QPushButton("＋ Add Action")
        add_action_btn.setProperty("class", "secondaryButton")
        add_action_btn.setCursor(Qt.PointingHandCursor)

        add_condition_btn = QPushButton("＋ Add Condition")
        add_condition_btn.setProperty("class", "secondaryButton")
        add_condition_btn.setCursor(Qt.PointingHandCursor)

        save_btn = QPushButton("💾 Save Workflow")
        save_btn.setProperty("class", "secondaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(lambda: QMessageBox.information(self, "Workflow Saved", "Workflow configuration saved to local database."))

        run_btn = QPushButton("▶ Run Workflow")
        run_btn.setProperty("class", "primaryButton")
        run_btn.setCursor(Qt.PointingHandCursor)
        run_btn.clicked.connect(lambda: QMessageBox.information(self, "Workflow Started", "Automation execution pipeline dispatched."))

        toolbar.addWidget(add_trigger_btn)
        toolbar.addWidget(add_action_btn)
        toolbar.addWidget(add_condition_btn)
        toolbar.addStretch()
        toolbar.addWidget(save_btn)
        toolbar.addWidget(run_btn)
        b_layout.addLayout(toolbar)

        # Canvas Frame
        self.canvas = WorkflowCanvasWidget()
        b_layout.addWidget(self.canvas, 1)

        # Canvas description text matching reference 05_workflow_builder.png
        desc_layout = QVBoxLayout()
        desc_layout.setSpacing(4)
        
        canvas_title = QLabel("Workflow canvas")
        canvas_title.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: 700;")
        
        canvas_desc = QLabel("Drag actions into a sequence. Configure triggers, waits, conditions and tools.")
        canvas_desc.setStyleSheet("color: #8e929b; font-size: 13px;")

        desc_layout.addWidget(canvas_title)
        desc_layout.addWidget(canvas_desc)
        b_layout.addLayout(desc_layout)

        layout.addWidget(builder_card, 1)
