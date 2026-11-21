"""
Voice Assistant Page - Hands-free speech interaction and audio settings.
"""
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QComboBox, QSlider, QScrollArea, QSizePolicy
)


class VoicePage(QWidget):
    """Voice Assistant dashboard with listening toggle, visualizer, and settings."""

    def __init__(self):
        super().__init__()
        self.is_listening = False
        self._init_ui()

    def _init_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(20)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        title_label = QLabel("Voice Assistant")
        title_label.setProperty("class", "pageTitle")
        
        subtitle_label = QLabel("Hands-free voice commands, audio input and speech synthesis.")
        subtitle_label.setProperty("class", "pageSubtitle")
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        layout.addLayout(header_layout)

        # Main Voice Interaction Card
        voice_card = QFrame()
        voice_card.setProperty("class", "surfaceCard")
        vc_layout = QVBoxLayout(voice_card)
        vc_layout.setContentsMargins(28, 28, 28, 28)
        vc_layout.setSpacing(20)
        vc_layout.setAlignment(Qt.AlignCenter)

        # Mic Status
        self.mic_status = QLabel("Microphone: Standby")
        self.mic_status.setStyleSheet("color: #8e929b; font-size: 13px; font-weight: 600;")
        vc_layout.addWidget(self.mic_status, alignment=Qt.AlignCenter)

        # Waveform Visualizer Placeholder
        self.waveform_label = QLabel("  ▂ ▃ ▄ ▅ ▆ ▇ █ ▇ ▆ ▅ ▄ ▃ ▂  ")
        self.waveform_label.setStyleSheet("color: #383a42; font-size: 26px; letter-spacing: 2px;")
        self.waveform_label.setAlignment(Qt.AlignCenter)
        vc_layout.addWidget(self.waveform_label, alignment=Qt.AlignCenter)

        # Listening Status Text
        self.status_text = QLabel("Press 'Start Listening' to speak to Personal Agent")
        self.status_text.setStyleSheet("color: #d1d5db; font-size: 15px; font-weight: 500;")
        self.status_text.setAlignment(Qt.AlignCenter)
        vc_layout.addWidget(self.status_text, alignment=Qt.AlignCenter)

        # Start Listening Button
        self.listen_btn = QPushButton("🎙 Start Listening")
        self.listen_btn.setProperty("class", "primaryButton")
        self.listen_btn.setMinimumHeight(44)
        self.listen_btn.setFixedWidth(200)
        self.listen_btn.setCursor(Qt.PointingHandCursor)
        self.listen_btn.clicked.connect(self._toggle_listening)
        vc_layout.addWidget(self.listen_btn, alignment=Qt.AlignCenter)

        layout.addWidget(voice_card)

        # Voice Settings Card
        settings_card = QFrame()
        settings_card.setProperty("class", "surfaceCard")
        sc_layout = QVBoxLayout(settings_card)
        sc_layout.setContentsMargins(20, 20, 20, 20)
        sc_layout.setSpacing(14)

        sec_title = QLabel("VOICE SETTINGS")
        sec_title.setStyleSheet("color: #ffffff; font-size: 12px; font-weight: 700; letter-spacing: 0.8px;")
        sc_layout.addWidget(sec_title)

        # Input device
        dev_layout = QHBoxLayout()
        dev_lbl = QLabel("Input Device:")
        dev_lbl.setStyleSheet("color: #8e929b; font-size: 13px;")
        self.dev_combo = QComboBox()
        self.dev_combo.addItems(["Default System Microphone", "Realtek High Definition Audio", "Headset Microphone"])
        dev_layout.addWidget(dev_lbl)
        dev_layout.addWidget(self.dev_combo, 1)
        sc_layout.addLayout(dev_layout)

        # Speech recognition engine
        eng_layout = QHBoxLayout()
        eng_lbl = QLabel("Speech Engine:")
        eng_lbl.setStyleSheet("color: #8e929b; font-size: 13px;")
        self.eng_combo = QComboBox()
        self.eng_combo.addItems(["Whisper Local (Fast / Accurate)", "Cloud Speech-to-Text", "Windows SAPI"])
        eng_layout.addWidget(eng_lbl)
        eng_layout.addWidget(self.eng_combo, 1)
        sc_layout.addLayout(eng_layout)

        layout.addWidget(settings_card)
        layout.addStretch()

    def _toggle_listening(self) -> None:
        self.is_listening = not self.is_listening
        if self.is_listening:
            self.listen_btn.setText("⏹ Stop Listening")
            self.status_text.setText("Listening... Speak now")
            self.mic_status.setText("Microphone: Active (Listening)")
            self.waveform_label.setStyleSheet("color: #e59840; font-size: 26px; letter-spacing: 2px;")
        else:
            self.listen_btn.setText("🎙 Start Listening")
            self.status_text.setText("Press 'Start Listening' to speak to Personal Agent")
            self.mic_status.setText("Microphone: Standby")
            self.waveform_label.setStyleSheet("color: #383a42; font-size: 26px; letter-spacing: 2px;")
