from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt

class LabelRow(QWidget):
    def __init__(self, label: str, value: str = ""):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)

        self.label = QLabel(label)
        self.label.setFixedWidth(180)
        self.label.setStyleSheet("font-weight: 600;")

        self.value = QLabel(value)
        self.value.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self.value.setWordWrap(True)

        layout.addWidget(self.label)
        layout.addWidget(self.value)

    def set_value(self, value: str):
        self.value.setText(value or "")

    def set_optional_value(self, value):
        if value:
            self.setVisible(True)
            self.set_value(value)
        else:
            self.setVisible(False)
