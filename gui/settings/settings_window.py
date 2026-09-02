"""
CELIK-26 GUI settings window.
Handles the application theme setting.
"""

from PyQt6.QtWidgets import QComboBox, QDialog, QFormLayout, QPushButton, QVBoxLayout
from PyQt6.QtCore import QSettings, pyqtSignal


class SettingsWindow(QDialog):

    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(300)

        self.settings = QSettings("CELIK-26", "CardReader")

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light", "auto"])

        form.addRow("Theme:", self.theme_combo)

        layout.addLayout(form)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        self.load()

    def load(self):
        self.theme_combo.setCurrentText(
            self.settings.value("theme", "dark")
        )

    def save(self):
        theme = self.theme_combo.currentText()
        self.settings.setValue("theme", theme)

        self.theme_changed.emit(theme)
        self.accept()
