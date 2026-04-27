import platform
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QComboBox, QCheckBox, QLabel, QPushButton, QFrame,
)
from PyQt6.QtCore import pyqtSignal
from core.mapping import SCOPE_LETTERS, SCOPE_LETTERS_NUMBERS, SCOPE_ALL_PRINTABLE


_SCOPE_LABELS = [
    ("Letters only",       SCOPE_LETTERS),
    ("Letters + Numbers",  SCOPE_LETTERS_NUMBERS),
    ("All printable",      SCOPE_ALL_PRINTABLE),
]

_DIALOG_STYLE = """
    QDialog {
        background-color: #1a1a1a;
        color: #f0f0f0;
    }
    QLabel {
        color: #f0f0f0;
    }
    QComboBox {
        background-color: #2b2b2b;
        color: #f0f0f0;
        border: 1px solid #555;
        border-radius: 4px;
        padding: 4px 8px;
        min-width: 160px;
    }
    QComboBox QAbstractItemView {
        background-color: #2b2b2b;
        color: #f0f0f0;
        selection-background-color: #4a90d9;
    }
    QCheckBox {
        color: #f0f0f0;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
    }
"""


class SettingsDialog(QDialog):
    settings_changed = pyqtSignal(str, bool)  # (scope, os_level_enabled)

    def __init__(self, current_scope: str, os_level_enabled: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setModal(True)
        self.setMinimumWidth(340)
        self.setStyleSheet(_DIALOG_STYLE)
        self._build(current_scope, os_level_enabled)

    def _build(self, current_scope: str, os_level_enabled: bool) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        form.setSpacing(12)
        form.setLabelAlignment(form.labelAlignment())

        # Key scope
        self._scope_box = QComboBox()
        for label, value in _SCOPE_LABELS:
            self._scope_box.addItem(label, userData=value)
        current_index = next(
            (i for i, (_, v) in enumerate(_SCOPE_LABELS) if v == current_scope), 1
        )
        self._scope_box.setCurrentIndex(current_index)

        scope_label = QLabel("Key scope:")
        scope_label.setStyleSheet("color: #aaaaaa;")
        form.addRow(scope_label, self._scope_box)

        layout.addLayout(form)

        # OS-level remapping
        self._os_check = QCheckBox("OS-level remapping")
        self._os_check.setChecked(os_level_enabled)
        layout.addWidget(self._os_check)

        # Platform warning
        warning_text = self._os_warning()
        if warning_text:
            warn_label = QLabel(warning_text)
            warn_label.setWordWrap(True)
            warn_label.setStyleSheet("color: #aaaaaa; font-size: 11px;")
            layout.addWidget(warn_label)
        else:
            info = QLabel(
                "Remaps keys system-wide via a global keyboard hook.\n"
                "Linux: requires user in 'input' group or an X11 session."
            )
            info.setWordWrap(True)
            info.setStyleSheet("color: #777777; font-size: 11px;")
            layout.addWidget(info)

        # Separator
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #333;")
        layout.addWidget(line)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("Cancel")
        btn_cancel.setFixedSize(90, 34)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #2b2b2b; color: #f0f0f0;
                border: 1px solid #555; border-radius: 5px;
            }
            QPushButton:hover { background-color: #3b3b3b; }
        """)
        btn_cancel.clicked.connect(self.reject)

        btn_ok = QPushButton("OK")
        btn_ok.setFixedSize(90, 34)
        btn_ok.setStyleSheet("""
            QPushButton {
                background-color: #4a90d9; color: white;
                border: none; border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #5aa0e9; }
        """)
        btn_ok.clicked.connect(self._on_ok)

        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _on_ok(self) -> None:
        scope = self._scope_box.currentData()
        os_level = self._os_check.isChecked()
        self.settings_changed.emit(scope, os_level)
        self.accept()

    @staticmethod
    def _os_warning() -> str:
        system = platform.system()
        session = platform.os.environ.get('XDG_SESSION_TYPE', '').lower() if hasattr(platform, 'os') else ''
        import os
        session = os.environ.get('XDG_SESSION_TYPE', '').lower()
        if system == 'Linux' and 'wayland' in session:
            return (
                "OS-level remapping is not supported on Wayland. "
                "Switch to an X11 session to use this feature."
            )
        return ''
