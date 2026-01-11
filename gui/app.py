"""
CELIK-26 GUI application entry point.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QSettings

from qt_material import apply_stylesheet

from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    settings = QSettings("CELIK-26", "CardReader")
    theme = settings.value("theme", "dark")

    if theme == "dark":
        apply_stylesheet(app, theme="dark_teal.xml")
    elif theme == "light":
        apply_stylesheet(app, theme="light_teal.xml")
    else:
        apply_stylesheet(app, theme="dark_teal.xml")

    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
