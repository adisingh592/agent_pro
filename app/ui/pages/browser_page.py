"""
Browser Page - Layout for future AI-controlled browser.
Prepared for Playwright/CDP automation in Phase 2.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy
)


class BrowserPage(QWidget):
    """Layout for AI-controlled browser with address bar, agent controls, and viewport."""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("AI-Controlled Browser")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Automate web research, form submissions and web monitoring.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)

        # Top URL Navigation Bar
        nav_card = QFrame()
        nav_card.setProperty("class", "surfaceCard")
        nav_layout = QHBoxLayout(nav_card)
        nav_layout.setContentsMargins(10, 8, 10, 8)
        nav_layout.setSpacing(8)

        back_btn = QPushButton("◀")
        back_btn.setProperty("class", "secondaryButton")
        back_btn.setFixedWidth(36)
        
        fwd_btn = QPushButton("▶")
        fwd_btn.setProperty("class", "secondaryButton")
        fwd_btn.setFixedWidth(36)

        reload_btn = QPushButton("↻")
        reload_btn.setProperty("class", "secondaryButton")
        reload_btn.setFixedWidth(36)

        self.url_bar = QLineEdit("https://duckduckgo.com")
        self.url_bar.setStyleSheet("""
            QLineEdit {
                background-color: #16171b;
                border: 1px solid #282a30;
                border-radius: 6px;
                color: #ffffff;
                padding: 6px 12px;
                font-size: 13px;
            }
        """)

        go_btn = QPushButton("Go")
        go_btn.setProperty("class", "primaryButton")
        go_btn.setCursor(Qt.PointingHandCursor)
        go_btn.clicked.connect(self._on_navigate)

        nav_layout.addWidget(back_btn)
        nav_layout.addWidget(fwd_btn)
        nav_layout.addWidget(reload_btn)
        nav_layout.addWidget(self.url_bar, 1)
        nav_layout.addWidget(go_btn)
        layout.addWidget(nav_card)

        # Agent Browser Controls Bar
        agent_controls = QHBoxLayout()
        agent_controls.setSpacing(10)

        ctrl_screenshot = QPushButton("📸 Take Screenshot")
        ctrl_screenshot.setProperty("class", "secondaryButton")
        ctrl_screenshot.setCursor(Qt.PointingHandCursor)

        ctrl_extract = QPushButton("📄 Extract Page Text")
        ctrl_extract.setProperty("class", "secondaryButton")
        ctrl_extract.setCursor(Qt.PointingHandCursor)

        ctrl_inspect = QPushButton("🔍 Inspect Elements")
        ctrl_inspect.setProperty("class", "secondaryButton")
        ctrl_inspect.setCursor(Qt.PointingHandCursor)

        ctrl_autopilot = QPushButton("▶ Agent Autopilot (Standby)")
        ctrl_autopilot.setStyleSheet("""
            QPushButton {
                background-color: #23252b;
                border: 1px solid #4a381e;
                border-radius: 6px;
                color: #e59840;
                padding: 7px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2b271d;
            }
        """)
        ctrl_autopilot.setCursor(Qt.PointingHandCursor)

        agent_controls.addWidget(ctrl_screenshot)
        agent_controls.addWidget(ctrl_extract)
        agent_controls.addWidget(ctrl_inspect)
        agent_controls.addStretch()
        agent_controls.addWidget(ctrl_autopilot)
        layout.addLayout(agent_controls)

        # Browser Viewport Canvas (Placeholder)
        self.viewport_frame = QFrame()
        self.viewport_frame.setStyleSheet("""
            QFrame {
                background-color: #18191d;
                border: 1px solid #282a30;
                border-radius: 8px;
            }
        """)
        vp_layout = QVBoxLayout(self.viewport_frame)
        vp_layout.setAlignment(Qt.AlignCenter)
        vp_layout.setSpacing(12)

        icon_label = QLabel("🌐")
        icon_label.setStyleSheet("font-size: 48px; color: #8e929b;")
        icon_label.setAlignment(Qt.AlignCenter)

        self.vp_title = QLabel("AI Browser Engine Placeholder")
        self.vp_title.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: 700;")
        self.vp_title.setAlignment(Qt.AlignCenter)

        vp_desc = QLabel("Embedded browser engine and automated DOM actions will be activated in Phase 2.\nThe layout is pre-wired for session management and screenshot streaming.")
        vp_desc.setStyleSheet("color: #8e929b; font-size: 13px; text-align: center;")
        vp_desc.setAlignment(Qt.AlignCenter)

        vp_layout.addWidget(icon_label)
        vp_layout.addWidget(self.vp_title)
        vp_layout.addWidget(vp_desc)

        layout.addWidget(self.viewport_frame, 1)

        # Status footer
        status_bar = QLabel("Browser status: Idle • Mode: Sandboxed • Session: Ready")
        status_bar.setStyleSheet("color: #8e929b; font-size: 11px;")
        layout.addWidget(status_bar)

    def _on_navigate(self) -> None:
        url = self.url_bar.text().strip()
        self.vp_title.setText(f"Navigating to {url} (Simulated)")
