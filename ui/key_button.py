from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import QTimer, Qt


NORMAL_STYLE = """
    QPushButton {
        background-color: #2b2b2b;
        color: #f0f0f0;
        border: 1px solid #555;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
"""

DIMMED_STYLE = """
    QPushButton {
        background-color: #1a1a1a;
        color: #444444;
        border: 1px solid #333;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
"""

FLASH_STYLE = """
    QPushButton {
        background-color: #3a7d44;
        color: #ffffff;
        border: 1px solid #5db86a;
        border-radius: 6px;
        font-size: 14px;
        font-weight: bold;
    }
"""


class KeyButton(QPushButton):
    def __init__(self, physical_key: str, parent=None):
        super().__init__(physical_key, parent)
        self.physical_key = physical_key
        self._is_active = True
        self.setFixedSize(44, 44)
        self.setStyleSheet(NORMAL_STYLE)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._unflash)

    def set_label(self, label: str) -> None:
        self.setText(label)

    def set_active(self, active: bool) -> None:
        self._is_active = active
        self.setStyleSheet(NORMAL_STYLE if active else DIMMED_STYLE)

    def flash(self) -> None:
        if not self._is_active:
            return
        self.setStyleSheet(FLASH_STYLE)
        self._timer.start(200)

    def _unflash(self) -> None:
        self.setStyleSheet(NORMAL_STYLE if self._is_active else DIMMED_STYLE)
