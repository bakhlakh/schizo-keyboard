from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout,
    QLabel, QLineEdit, QTextEdit, QComboBox,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

from core.mapping import KeyMapping, SCOPE_LETTERS, SCOPE_LETTERS_NUMBERS, SCOPE_ALL_PRINTABLE


_SCOPE_LABELS = [
    ("Letters only",      SCOPE_LETTERS),
    ("Letters + Numbers", SCOPE_LETTERS_NUMBERS),
    ("All printable",     SCOPE_ALL_PRINTABLE),
]

_FIELD_STYLE = """
    QLineEdit, QTextEdit {
        background-color: #1e1e1e;
        color: #f0f0f0;
        border: 1px solid #555;
        border-radius: 6px;
        padding: 6px;
    }
"""

_COMBO_STYLE = """
    QComboBox {
        background-color: #2b2b2b; color: #f0f0f0;
        border: 1px solid #555; border-radius: 4px; padding: 4px 8px;
    }
    QComboBox QAbstractItemView {
        background-color: #2b2b2b; color: #f0f0f0;
        selection-background-color: #4a90d9;
    }
"""


class DecoderWindow(QWidget):
    def __init__(self, secret: str = "", scope: str = SCOPE_LETTERS_NUMBERS, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Decoder")
        self.setMinimumWidth(480)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setStyleSheet("background-color: #1a1a1a;")
        self._build(secret, scope)

    def _build(self, secret: str, scope: str) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Decoder")
        title.setStyleSheet("color: #f0f0f0; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        secret_label = QLabel("Secret:")
        secret_label.setStyleSheet("color: #aaaaaa;")
        self._secret_input = QLineEdit()
        self._secret_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._secret_input.setPlaceholderText("Secret used when randomizing")
        self._secret_input.setText(secret)
        self._secret_input.setStyleSheet(_FIELD_STYLE)
        self._secret_input.textChanged.connect(self._update)
        form.addRow(secret_label, self._secret_input)

        scope_label = QLabel("Key scope:")
        scope_label.setStyleSheet("color: #aaaaaa;")
        self._scope_box = QComboBox()
        self._scope_box.setStyleSheet(_COMBO_STYLE)
        for lbl, val in _SCOPE_LABELS:
            self._scope_box.addItem(lbl, userData=val)
        idx = next((i for i, (_, v) in enumerate(_SCOPE_LABELS) if v == scope), 1)
        self._scope_box.setCurrentIndex(idx)
        self._scope_box.currentIndexChanged.connect(self._update)
        form.addRow(scope_label, self._scope_box)

        layout.addLayout(form)

        input_label = QLabel("Encoded text:")
        input_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        layout.addWidget(input_label)

        self._input_area = QTextEdit()
        self._input_area.setPlaceholderText("Paste text typed with the scrambled layout…")
        self._input_area.setFixedHeight(110)
        self._input_area.setFont(QFont("Monospace", 12))
        self._input_area.setStyleSheet(_FIELD_STYLE)
        self._input_area.textChanged.connect(self._update)
        layout.addWidget(self._input_area)

        output_label = QLabel("Decoded text:")
        output_label.setStyleSheet("color: #aaaaaa; font-size: 12px;")
        layout.addWidget(output_label)

        self._output_area = QTextEdit()
        self._output_area.setReadOnly(True)
        self._output_area.setFixedHeight(110)
        self._output_area.setFont(QFont("Monospace", 12))
        self._output_area.setStyleSheet("""
            QTextEdit {
                background-color: #141414;
                color: #88d498;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 6px;
            }
        """)
        layout.addWidget(self._output_area)

        self._hint = QLabel("Enter the secret that was active when the text was typed.")
        self._hint.setStyleSheet("color: #666666; font-size: 11px;")
        layout.addWidget(self._hint)

        self._update()

    def _update(self) -> None:
        secret = self._secret_input.text()
        if not secret:
            self._output_area.setPlainText("")
            self._hint.setVisible(True)
            return

        self._hint.setVisible(False)
        scope = self._scope_box.currentData()
        encoded = self._input_area.toPlainText()

        mapping = KeyMapping(scope)
        mapping.randomize(secret)
        inverse = {v: k for k, v in mapping.map.items()}

        decoded = []
        for ch in encoded:
            upper = ch.upper()
            if upper in inverse:
                result = inverse[upper]
                decoded.append(result.lower() if ch.islower() else result)
            else:
                decoded.append(ch)

        self._output_area.setPlainText("".join(decoded))
