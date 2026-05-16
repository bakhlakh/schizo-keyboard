from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QKeyEvent, QFont

from core.mapping import KeyMapping
from core.os_remapper import OSRemapper
from .keyboard_widget import KeyboardWidget
from .settings_dialog import SettingsDialog
from .decoder_window import DecoderWindow


class TypingArea(QTextEdit):
    key_pressed = pyqtSignal(str)

    def __init__(self, mapping: KeyMapping, parent=None):
        super().__init__(parent)
        self._mapping = mapping
        self._intercept_enabled = True
        self.setPlaceholderText("Type here to test your layout...")
        self.setFixedHeight(100)
        self.setFont(QFont("Monospace", 12))
        self.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 6px;
            }
        """)

    def set_intercept_enabled(self, enabled: bool) -> None:
        self._intercept_enabled = enabled

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if not self._intercept_enabled:
            super().keyPressEvent(event)
            return

        text = event.text()
        if text and text.upper() in self._mapping.active_keys:
            mapped = self._mapping.get(text)
            if text.islower():
                mapped = mapped.lower()
            self.insertPlainText(mapped)
            self.key_pressed.emit(text.upper())
        else:
            super().keyPressEvent(event)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keyboard Randomizer")
        self.setMinimumWidth(720)
        self._mapping = KeyMapping()
        self._os_remapper = OSRemapper(self._mapping)
        self._secret: str = ""
        self._decoder: DecoderWindow | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        root.setStyleSheet("background-color: #1a1a1a;")

        layout = QVBoxLayout(root)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title row with gear button
        title_row = QHBoxLayout()
        title_label = QLabel("Keyboard Randomizer")
        title_label.setStyleSheet("color: #f0f0f0; font-size: 16px; font-weight: bold;")
        title_row.addWidget(title_label)
        title_row.addStretch()

        btn_settings = QPushButton("⚙")
        btn_settings.setFixedSize(36, 36)
        btn_settings.setToolTip("Settings")
        btn_settings.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #aaaaaa;
                border: 1px solid #555;
                border-radius: 6px;
                font-size: 16px;
            }
            QPushButton:hover { background-color: #3b3b3b; color: #f0f0f0; }
        """)
        btn_settings.clicked.connect(self._on_settings)
        title_row.addWidget(btn_settings)
        layout.addLayout(title_row)

        # Keyboard display
        self._keyboard = KeyboardWidget(self._mapping)
        layout.addWidget(self._keyboard)

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        btn_row.setSpacing(16)

        self._btn_randomize = QPushButton("Randomize")
        self._btn_randomize.setFixedSize(140, 40)
        self._btn_randomize.setStyleSheet("""
            QPushButton {
                background-color: #4a90d9;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5aa0e9; }
            QPushButton:pressed { background-color: #3a80c9; }
        """)
        self._btn_randomize.clicked.connect(self._on_randomize)

        self._btn_reset = QPushButton("Reset")
        self._btn_reset.setFixedSize(140, 40)
        self._btn_reset.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #f0f0f0;
                border: 1px solid #555;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3b3b3b; }
            QPushButton:pressed { background-color: #1b1b1b; }
        """)
        self._btn_reset.clicked.connect(self._on_reset)

        btn_decoder = QPushButton("Decoder")
        btn_decoder.setFixedSize(140, 40)
        btn_decoder.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b;
                color: #aaaaaa;
                border: 1px solid #555;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #3b3b3b; color: #f0f0f0; }
            QPushButton:pressed { background-color: #1b1b1b; }
        """)
        btn_decoder.clicked.connect(self._on_decoder)

        btn_row.addWidget(self._btn_randomize)
        btn_row.addWidget(self._btn_reset)
        btn_row.addWidget(btn_decoder)
        layout.addLayout(btn_row)

        # Typing area
        label = QLabel("Type here to test:")
        label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        layout.addWidget(label)

        self._typing_area = TypingArea(self._mapping)
        self._typing_area.key_pressed.connect(self._keyboard.flash_key)
        layout.addWidget(self._typing_area)

    def _on_randomize(self) -> None:
        self._mapping.randomize(self._secret)
        self._keyboard.refresh_labels()

    def _on_reset(self) -> None:
        self._mapping.reset()
        self._keyboard.refresh_labels()

    def _on_decoder(self) -> None:
        if self._decoder is None:
            self._decoder = DecoderWindow(secret=self._secret, scope=self._mapping.scope)
            self._decoder.destroyed.connect(lambda: setattr(self, '_decoder', None))
            self._decoder.show()
        else:
            self._decoder.raise_()
            self._decoder.activateWindow()

    def _on_settings(self) -> None:
        dlg = SettingsDialog(
            current_scope=self._mapping.scope,
            os_level_enabled=self._os_remapper.active,
            current_secret=self._secret,
            parent=self,
        )
        dlg.settings_changed.connect(self._apply_settings)
        dlg.exec()

    def _apply_settings(self, scope: str, os_level: bool, secret: str) -> None:
        self._secret = secret
        self._mapping.set_scope(scope)
        self._keyboard.refresh_labels()

        if os_level and not self._os_remapper.active:
            self._os_remapper.start()
            self._typing_area.set_intercept_enabled(False)
        elif not os_level and self._os_remapper.active:
            self._os_remapper.stop()
            self._typing_area.set_intercept_enabled(True)

    def closeEvent(self, event) -> None:
        self._os_remapper.stop()
        if self._decoder:
            self._decoder.close()
        super().closeEvent(event)
