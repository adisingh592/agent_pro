"""
Settings Page - Configuration for AI models, API providers, voice, and system options.
"""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QTabWidget, QCheckBox, QComboBox,
    QSpinBox, QSlider, QMessageBox, QScrollArea, QSizePolicy
)


class SettingsPage(QWidget):
    """Settings interface with 8 modular configuration sections."""

    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(18)

        # Header
        header_layout = QHBoxLayout()
        header_text = QVBoxLayout()
        header_text.setSpacing(4)
        
        title_label = QLabel("Settings")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Configure application behavior, AI models, API keys and system preferences.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_text.addWidget(title_label)
        header_text.addWidget(subtitle_label)
        header_layout.addLayout(header_text, 1)

        save_btn = QPushButton("Save Changes")
        save_btn.setProperty("class", "primaryButton")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(lambda: QMessageBox.information(self, "Settings Saved", "Preferences stored to configuration."))
        header_layout.addWidget(save_btn)

        layout.addLayout(header_layout)

        # Tabs for Sections
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #282a30;
                background-color: #17181c;
                border-radius: 6px;
                padding: 16px;
            }
            QTabBar::tab {
                background-color: #1c1d22;
                border: 1px solid #282a30;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                color: #8e929b;
                padding: 8px 16px;
                margin-right: 4px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background-color: #23252b;
                color: #e59840;
                font-weight: 600;
            }
            QTabBar::tab:hover:!selected {
                background-color: #202227;
                color: #ffffff;
            }
        """)

        # Add 8 settings sections
        self.tabs.addTab(self._build_general_tab(), "General")
        self.tabs.addTab(self._build_appearance_tab(), "Appearance")
        self.tabs.addTab(self._build_ai_models_tab(), "AI Models")
        self.tabs.addTab(self._build_local_models_tab(), "Local Models")
        self.tabs.addTab(self._build_api_providers_tab(), "API Providers")
        self.tabs.addTab(self._build_voice_tab(), "Voice")
        self.tabs.addTab(self._build_automation_tab(), "Automation")
        self.tabs.addTab(self._build_permissions_tab(), "Permissions")

        layout.addWidget(self.tabs, 1)

    def _build_general_tab(self) -> QWidget:
        widget = QWidget()
        l = QVBoxLayout(widget)
        l.setSpacing(14)

        l.addWidget(QCheckBox("Start Personal Agent automatically on Windows logon"))
        l.addWidget(QCheckBox("Minimize to system tray on close"))
        l.addWidget(QCheckBox("Enable verbose diagnostic logging"))

        l.addStretch()
        return widget

    def _build_appearance_tab(self) -> QWidget:
        widget = QWidget()
        l = QVBoxLayout(widget)
        l.setSpacing(14)

        lbl = QLabel("Color Theme:")
        lbl.setStyleSheet("color: #ffffff; font-weight: 600;")
        theme_combo = QComboBox()
        theme_combo.addItems(["Dark Charcoal (Default)", "OLED Black", "Muted Slate"])
        l.addWidget(lbl)
        l.addWidget(theme_combo)

        lbl_accent = QLabel("Accent Highlight:")
        lbl_accent.setStyleSheet("color: #ffffff; font-weight: 600;")
        accent_combo = QComboBox()
        accent_combo.addItems(["Warm Amber / Orange (#e59840)", "Subtle Gold (#d97706)", "Neutral Bronze"])
        l.addWidget(lbl_accent)
        l.addWidget(accent_combo)

        l.addStretch()
        return widget

    def _build_ai_models_tab(self) -> QWidget:
        widget = QWidget()
        l = QVBoxLayout(widget)
        l.setSpacing(14)

        lbl = QLabel("Default Primary Model:")
        lbl.setStyleSheet("color: #ffffff; font-weight: 600;")
        m_combo = QComboBox()
        m_combo.addItems(["Local Qwen 2.5 7B", "Google Gemini 1.5 Pro", "Anthropic Claude 3.5 Sonnet", "OpenAI GPT-4o"])
        l.addWidget(lbl)
        l.addWidget(m_combo)

        l.addWidget(QCheckBox("Enable fallback to secondary model on timeout"))
        l.addWidget(QCheckBox("Log token usage metrics"))

        l.addStretch()
        return widget

    def _build_local_models_tab(self) -> QWidget:
        widget = QWidget()
        l = QVBoxLayout(widget)
        l.setSpacing(14)

        l.addWidget(QLabel("Ollama Server Endpoint:"))
        ollama_inp = QLineEdit("http://localhost:11434")
        l.addWidget(ollama_inp)

        l.addWidget(QLabel("LM Studio Server Endpoint:"))
        lms_inp = QLineEdit("http://localhost:1234/v1")
        l.addWidget(lms_inp)

        l.addWidget(QCheckBox("Auto-pull missing model weights"))
        l.addStretch()
        return widget

    def _build_api_providers_tab(self) -> QWidget:
        widget = QWidget()
        l = QVBoxLayout(widget)
        l.setSpacing(12)

        l.addWidget(QLabel("Google Gemini API Key:"))
        gemini_inp = QLineEdit()
        gemini_inp.setEchoMode(QLineEdit.Password)
        gemini_inp.setPlaceholderText("AIzaSy...")
        l.addWidget(gemini_inp)

        l.addWidget(QLabel("Anthropic API Key:"))
        claude_inp = QLineEdit()
        claude_inp.setEchoMode(QLineEdit.Password)
        claude_inp.setPlaceholderText("sk-ant-...")
        l.addWidget(claude_inp)

        l.addWidget(QLabel("OpenAI API Key:"))
        openai_inp = QLineEdit()
        openai_inp.setEchoMode(QLineEdit.Password)
        openai_inp.setPlaceholderText("sk-proj-...")
        l.addWidget(openai_inp)

        l.addStretch()
        return widget

    def _build_voice_tab(self) -> QWidget:
        widget = QWidget()
        l = QVBoxLayout(widget)
        l.setSpacing(14)

        l.addWidget(QCheckBox("Enable Wake Word ('Hey Agent')"))
        l.addWidget(QCheckBox("Speak agent responses with Text-To-Speech (TTS)"))

        lbl_voice = QLabel("TTS Voice Pitch / Speed:")
        lbl_voice.setStyleSheet("color: #ffffff; font-weight: 600;")
        l.addWidget(lbl_voice)
        slider = QSlider(Qt.Horizontal)
        slider.setValue(50)
        l.addWidget(slider)

        l.addStretch()
        return widget

    def _build_automation_tab(self) -> QWidget:
        widget = QWidget()
        l = QVBoxLayout(widget)
        l.setSpacing(14)

        l.addWidget(QCheckBox("Enable scheduled background triggers"))
        l.addWidget(QCheckBox("Monitor Downloads folder automatically"))
        l.addWidget(QCheckBox("Auto-index newly modified code workspaces"))

        l.addStretch()
        return widget

    def _build_permissions_tab(self) -> QWidget:
        widget = QWidget()
        l = QVBoxLayout(widget)
        l.setSpacing(14)

        l.addWidget(QCheckBox("Allow desktop application launching"))
        l.addWidget(QCheckBox("Allow file system read access"))
        l.addWidget(QCheckBox("Require confirmation before moving or copying files"))
        l.addWidget(QCheckBox("Allow terminal command execution (Guarded)"))

        l.addStretch()
        return widget
