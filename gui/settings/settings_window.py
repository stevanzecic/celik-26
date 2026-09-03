"""
CELIK-26 GUI settings window.
Handles application language and theme settings.
"""

from PyQt6.QtWidgets import QComboBox, QDialog, QFormLayout, QPushButton, QVBoxLayout
from PyQt6.QtCore import QSettings, pyqtSignal
from gui.i18n import DEFAULT_LANGUAGE, LANGUAGES, tr


class SettingsWindow(QDialog):

    theme_changed = pyqtSignal(str)
    language_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.language = self.settings_language()
        self.setWindowTitle(tr("settings", self.language))
        self.setMinimumWidth(300)

        self.settings = QSettings("CELIK-26", "CardReader")

        layout = QVBoxLayout(self)

        form = QFormLayout()

        self.language_combo = QComboBox()
        for code, label in LANGUAGES.items():
            self.language_combo.addItem(label, code)
        form.addRow(tr("language", self.language), self.language_combo)

        self.theme_combo = QComboBox()
        for key in ("dark", "light", "auto"):
            self.theme_combo.addItem(tr(key, self.language), key)
        form.addRow(tr("theme", self.language), self.theme_combo)

        layout.addLayout(form)

        save_btn = QPushButton(tr("save", self.language))
        save_btn.clicked.connect(self.save)
        layout.addWidget(save_btn)

        self.load()

    def load(self):
        language = self.settings.value("language", DEFAULT_LANGUAGE)
        index = self.language_combo.findData(language)
        self.language_combo.setCurrentIndex(index if index >= 0 else 0)
        theme = self.settings.value("theme", "dark")
        theme_index = self.theme_combo.findData(theme)
        self.theme_combo.setCurrentIndex(theme_index if theme_index >= 0 else 0)

    def save(self):
        theme = self.theme_combo.currentData()
        language = self.language_combo.currentData()
        self.settings.setValue("theme", theme)
        self.settings.setValue("language", language)

        self.theme_changed.emit(theme)
        self.language_changed.emit(language)
        self.accept()

    @staticmethod
    def settings_language():
        return QSettings("CELIK-26", "CardReader").value(
            "language", DEFAULT_LANGUAGE
        )
