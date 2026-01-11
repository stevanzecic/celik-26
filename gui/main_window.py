"""
CELIK-26 GUI main window.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QApplication,
    QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QMessageBox,
    QMenu, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer

from qt_material import apply_stylesheet

from gui.workers.reader_worker import ReaderWorker
from gui.settings.settings_window import SettingsWindow
from card_reader_cli import get_readers_list

from gui.widgets.id_card_widget import IdCardWidget
from gui.widgets.medical_card_widget import MedicalCardWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CELIK-26")
        self.resize(900, 700)

        self.reader_name = None
        self.card_data = None
        self.manual_mode = False

        self._build_ui()
        self._build_menu()
        self._start_worker()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        self.info_label = QLabel("No reader connected.")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.info_label)

        # -------- Card display --------
        self.card_stack = QStackedWidget()

        self.empty_label = QLabel("Insert a card to view data.")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.id_widget = IdCardWidget()
        self.med_widget = MedicalCardWidget()

        self.card_stack.addWidget(self.empty_label)
        self.card_stack.addWidget(self.id_widget)
        self.card_stack.addWidget(self.med_widget)

        layout.addWidget(self.card_stack)

        # -------- Buttons --------

        self.button_layout = QHBoxLayout()

        self.read_btn = QPushButton("Read Card")
        self.read_btn.setEnabled(False)
        self.read_btn.setToolTip("No reader connected")
        self.read_btn.clicked.connect(self.manual_read)

        self.save_btn = QPushButton("Save")
        self.save_btn.setEnabled(False)

        self.print_btn = QPushButton("Print")
        self.print_btn.setEnabled(False)

        self.button_layout.addStretch(1)

        self.button_layout.addWidget(self.save_btn)
        self.button_layout.addWidget(self.print_btn)
        self.button_layout.addWidget(self.read_btn)

        layout.addLayout(self.button_layout)

        self.setCentralWidget(central)

        # -------- Status bar --------
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # -------- Reader icon --------
        self.reader_icon = QLabel()
        self.reader_icon.setFixedSize(14, 14)
        self.reader_icon.setStyleSheet("""
            QLabel {
                border-radius: 7px;
                background-color: #aa0000;
            }
        """)
        self.reader_icon.setToolTip("No reader connected")
        self.status.addPermanentWidget(self.reader_icon)

        # -------- Blink timer --------
        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(500)
        self._blink_timer.timeout.connect(self._toggle_blink)
        self._blink_on = True

        # -------- Initial state --------
        self.set_reader_status("no_reader")
        self.status.showMessage("No reader connected")

    def _build_menu(self):
        menubar = self.menuBar()

        self.reader_menu = QMenu("Reader Selection", self)
        self.refresh_action = self.reader_menu.addAction("Refresh")
        self.refresh_action.triggered.connect(self.refresh_readers)

        self.auto_action = self.reader_menu.addAction("Auto Select")
        self.auto_action.setCheckable(True)
        self.auto_action.setChecked(True)
        self.auto_action.triggered.connect(self.enable_auto_mode)


        menubar.addMenu(self.reader_menu)

        settings_menu = QMenu("Settings", self)
        pref_action = settings_menu.addAction("Preferences")
        pref_action.triggered.connect(self.open_settings)
        menubar.addMenu(settings_menu)

    def _start_worker(self):
        self.worker = ReaderWorker()
        self.worker.reader_connected.connect(self.on_reader_connected)
        self.worker.reader_disconnected.connect(self.on_reader_disconnected)
        self.worker.card_read_success.connect(self.on_card_read)
        self.worker.card_read_failed.connect(self.on_card_failed)
        self.worker.no_card_present.connect(self.on_no_card)
        self.worker.read_started.connect(self.on_read_started)
        self.worker.start()

    def refresh_readers(self):
        readers = get_readers_list(override_exception=True)

        # Remove old reader actions (keep first 2 items - "Refresh" and "Auto")
        for act in self.reader_menu.actions()[2:]:
            self.reader_menu.removeAction(act)

        if readers:
            self.reader_menu.addSeparator()

        for r in readers:
            name = str(r)
            act = self.reader_menu.addAction(name)
            act.setCheckable(True)
            act.setChecked(name == self.reader_name)

            act.triggered.connect(
                lambda checked, n=name: self.select_manual_reader(n)
            )

    def select_manual_reader(self, reader_name: str):
        self.manual_mode = True
        self.auto_action.setChecked(False)

        self.worker.set_manual_reader(reader_name)
        self.status.showMessage(f"Manually selected reader: {reader_name}")

        self.refresh_readers()

    def enable_auto_mode(self):
        self.manual_mode = False
        self.auto_action.setChecked(True)

        self.worker.set_manual_reader(None)
        self.status.showMessage("Reader selection set to AUTO")

        self.refresh_readers()

    def open_settings(self):
        dlg = SettingsWindow(self)
        dlg.theme_changed.connect(self.apply_theme)
        dlg.exec()

    # ---------- Reader status and icon ----------

    def _start_blinking(self):
        if not self._blink_timer.isActive():
            self._blink_on = True
            self._blink_timer.start()

    def _stop_blinking(self):
        if self._blink_timer.isActive():
            self._blink_timer.stop()

    def _toggle_blink(self):
        self._blink_on = not self._blink_on
        color = "#e6b800" if self._blink_on else "#6b5a00"  # bright / dim yellow

        self.reader_icon.setStyleSheet(f"""
            QLabel {{
                border-radius: 7px;
                background-color: {color};
            }}
        """)

    def set_reader_status(self, state: str):
        if not hasattr(self, "reader_icon"):
            return

        if state == "no_reader":
            self._stop_blinking()
            color = "#aa0000"   # red
            tooltip = "No reader connected"

        elif state == "no_card":
            color = "#e6b800"   # base yellow (bright)
            tooltip = "Reader connected, waiting for card"
            self._start_blinking()

        elif state == "card_ok":
            self._stop_blinking()
            color = "#00aa00"   # green
            tooltip = "Card read successfully"

        else:
            return

        self.reader_icon.setStyleSheet(f"""
            QLabel {{
                border-radius: 7px;
                background-color: {color};
            }}
        """)
        self.reader_icon.setToolTip(tooltip)

    # ---------- Worker slots ----------

    def on_reader_connected(self, reader_name):
        self.reader_name = reader_name

        self.read_btn.setEnabled(True)
        self.read_btn.setToolTip("")

        self.info_label.setText("Reader connected. Insert card.")
        self.status.showMessage(f"Connected to reader: {reader_name}")

        # self.set_reader_status("no_reader")
        self.refresh_readers()
        self.refresh_readers()

    def on_reader_disconnected(self):
        self.reader_name = None

        self.read_btn.setEnabled(False)
        self.read_btn.setToolTip("No reader connected")

        self.info_label.setText("No reader connected.")
        self.status.showMessage("No reader connected")

        self.set_reader_status("no_reader")
        self.refresh_readers()

    def on_card_read(self, data):
        self.card_data = data

        if data["type"] == "ID":
            self.id_widget.set_data(data["data"])
            self.card_stack.setCurrentWidget(self.id_widget)
            label = "ID card read successfully"

        elif data["type"] == "MED":
            self.med_widget.set_data(data["data"])
            self.card_stack.setCurrentWidget(self.med_widget)
            label = "Medical card read successfully"

        else:
            label = "Card read successfully"

        # Update top label
        self.info_label.setText(label)

        # Update status bar
        self.status.showMessage(label)

        # Enable actions
        self.save_btn.setEnabled(True)
        self.print_btn.setEnabled(True)

        # Update status icon
        self.set_reader_status("card_ok")

    def on_card_failed(self, msg):
        self.info_label.setText("Failed to read card. Retrying...")
        self.status.showMessage(msg)

    def on_no_card(self):
        self.card_data = None
        self.card_stack.setCurrentWidget(self.empty_label)

        self.info_label.setText("Reader connected. Insert card.")
        self.status.showMessage("No card in reader")

        self.save_btn.setEnabled(False)
        self.print_btn.setEnabled(False)

        self.set_reader_status("no_card")

    def on_read_started(self):
        self.info_label.setText("Reading card...")
        self.status.showMessage("Reading card...")
        self.set_reader_status("no_card")  # yellow (blinking)

    def manual_read(self):
        if not self.reader_name:
            QMessageBox.information(
                self,
                "No reader",
                "No reader connected."
            )
            return

        if not self.worker.card_connected:
            QMessageBox.information(
                self,
                "No card",
                "Insert a card before reading."
            )
            return

        self.status.showMessage("Manual read triggered...")
        self.worker.force_read()

    # ---------- Theme management ----------

    def apply_theme(self, theme_name: str):
        """
        Apply qt-material theme at runtime.

        Parameters:
            theme_name (str): Theme name
        """
        app = QApplication.instance()

        if theme_name == "dark":
            apply_stylesheet(app, theme="dark_teal.xml")

        elif theme_name == "light":
            apply_stylesheet(app, theme="light_blue.xml")

        elif theme_name == "auto":
            # Simple auto logic: default to dark
            apply_stylesheet(app, theme="dark_teal.xml")

        self.status.showMessage(f"Theme changed to {theme_name}")
