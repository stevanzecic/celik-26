import sys
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from gui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    apply_stylesheet(app, theme="dark_teal.xml")

    win = MainWindow()
    win.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
