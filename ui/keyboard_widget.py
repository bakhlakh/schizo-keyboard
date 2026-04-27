from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt
from .key_button import KeyButton
from core.mapping import KeyMapping


ROWS = [
    list("`1234567890-="),   # 13 keys
    list("QWERTYUIOP[]\\"),  # 13 keys
    list("ASDFGHJKL;'"),     # 11 keys
    list("ZXCVBNM,./"),      # 10 keys
]


class KeyboardWidget(QWidget):
    def __init__(self, mapping: KeyMapping, parent=None):
        super().__init__(parent)
        self._mapping = mapping
        self._buttons: dict[str, KeyButton] = {}
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 12, 12, 12)

        for row in ROWS:
            row_layout = QHBoxLayout()
            row_layout.setSpacing(6)
            row_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            for key in row:
                btn = KeyButton(key)
                btn.set_label(self._mapping.get(key))
                self._buttons[key] = btn
                row_layout.addWidget(btn)
            layout.addLayout(row_layout)

    def refresh_labels(self) -> None:
        active = self._mapping.active_keys
        for key, btn in self._buttons.items():
            btn.set_label(self._mapping.get(key))
            btn.set_active(key in active)

    def flash_key(self, physical_key: str) -> None:
        key = physical_key.upper()
        if key in self._buttons:
            self._buttons[key].flash()
