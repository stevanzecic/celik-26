"""
CELIK-26 GUI main window.
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QApplication,
    QVBoxLayout, QHBoxLayout, QStackedWidget,
    QLabel, QPushButton, QMessageBox,
    QMenu, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer, QSettings

from qt_material import apply_stylesheet

from gui.workers.reader_worker import ReaderWorker
from gui.settings.settings_window import SettingsWindow
from card_reader_cli import get_readers_list

from gui.widgets.id_card_widget import IdCardWidget
from gui.widgets.medical_card_widget import MedicalCardWidget
from gui.id_card_printer import print_id_document
from gui.i18n import DEFAULT_LANGUAGE, tr


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CELIK-26")
        self.resize(900, 700)

        self.reader_name = None
        self.card_data = None
        self.manual_mode = False
        self.language = QSettings("CELIK-26", "CardReader").value("language", DEFAULT_LANGUAGE)

        self._build_ui()
        self._build_menu()
        self.apply_language(self.language)
        self._start_worker()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)

        self.info_label = QLabel(tr("no_reader", self.language))
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.info_label)

        # -------- Card display --------
        self.card_stack = QStackedWidget()

        self.empty_label = QLabel(tr("insert_card", self.language))
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.id_widget = IdCardWidget()
        self.med_widget = MedicalCardWidget()

        self.card_stack.addWidget(self.empty_label)
        self.card_stack.addWidget(self.id_widget)
        self.card_stack.addWidget(self.med_widget)

        layout.addWidget(self.card_stack)

        # -------- Buttons --------

        self.button_layout = QHBoxLayout()

        self.read_btn = QPushButton(tr("read_card", self.language))
        self.read_btn.setEnabled(False)
        self.read_btn.setToolTip(tr("no_reader_short", self.language))
        self.read_btn.clicked.connect(self.manual_read)

        self.save_btn = QPushButton(tr("save", self.language))
        self.save_btn.setEnabled(False)
        self.save_btn.setToolTip(tr("save_unimplemented", self.language))

        self.print_btn = QPushButton(tr("print", self.language))
        self.print_btn.setEnabled(False)
        self.print_btn.setToolTip(tr("read_id_before_print", self.language))
        self.print_btn.clicked.connect(self.print_current_card)

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
        self.reader_icon.setToolTip(tr("no_reader_short", self.language))
        self.status.addPermanentWidget(self.reader_icon)

        # -------- Blink timer --------
        self._blink_timer = QTimer(self)
        self._blink_timer.setInterval(500)
        self._blink_timer.timeout.connect(self._toggle_blink)
        self._blink_on = True

        # -------- Initial state --------
        self.set_reader_status("no_reader")
        self.status.showMessage(tr("no_reader", self.language))

    def _build_menu(self):
        menubar = self.menuBar()

        self.reader_menu = QMenu(tr("reader_selection", self.language), self)
        self.refresh_action = self.reader_menu.addAction(tr("refresh", self.language))
        self.refresh_action.triggered.connect(self.refresh_readers)

        self.auto_action = self.reader_menu.addAction(tr("auto_select", self.language))
        self.auto_action.setCheckable(True)
        self.auto_action.setChecked(True)
        self.auto_action.triggered.connect(self.enable_auto_mode)


        menubar.addMenu(self.reader_menu)

        self.settings_menu = QMenu(tr("settings", self.language), self)
        self.pref_action = self.settings_menu.addAction(tr("preferences", self.language))
        self.pref_action.triggered.connect(self.open_settings)
        menubar.addMenu(self.settings_menu)

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
        self.status.showMessage(tr("manual_reader", self.language, name=reader_name))

        self.refresh_readers()

    def enable_auto_mode(self):
        self.manual_mode = False
        self.auto_action.setChecked(True)

        self.worker.set_manual_reader(None)
        self.status.showMessage(tr("auto_reader", self.language))

        self.refresh_readers()

    def open_settings(self):
        dlg = SettingsWindow(self)
        dlg.theme_changed.connect(self.apply_theme)
        dlg.language_changed.connect(self.apply_language)
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
            tooltip = tr("no_reader_short", self.language)

        elif state == "no_card":
            color = "#e6b800"   # base yellow (bright)
            tooltip = tr("connected_insert", self.language)
            self._start_blinking()

        elif state == "card_ok":
            self._stop_blinking()
            color = "#00aa00"   # green
            tooltip = tr("card_success", self.language)

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

        self.info_label.setText(tr("connected_insert", self.language))
        self.status.showMessage(tr("connected_reader", self.language, name=reader_name))

        self.refresh_readers()

    def on_reader_disconnected(self):
        self.reader_name = None
        self._clear_card_data()

        self.read_btn.setEnabled(False)
        self.read_btn.setToolTip(tr("no_reader_short", self.language))

        self.info_label.setText(tr("no_reader", self.language))
        self.status.showMessage(tr("no_reader", self.language))

        self.set_reader_status("no_reader")
        self.refresh_readers()

    def on_card_read(self, data):
        self.card_data = data

        if data["type"] == "ID":
            self.id_widget.set_data(data["data"])
            self.card_stack.setCurrentWidget(self.id_widget)
            self.print_btn.setEnabled(True)
            self.print_btn.setToolTip("")
            label = tr("id_success", self.language)

        elif data["type"] == "MED":
            self.med_widget.set_data(data["data"])
            self.card_stack.setCurrentWidget(self.med_widget)
            self.print_btn.setEnabled(False)
            self.print_btn.setToolTip(tr("print_medical", self.language))
            label = tr("medical_success", self.language)

        else:
            self.print_btn.setEnabled(False)
            self.print_btn.setToolTip(tr("read_id_before_print", self.language))
            label = tr("card_success", self.language)

        # Update top label
        self.info_label.setText(label)

        # Update status bar
        self.status.showMessage(label)

        # Update status icon
        self.set_reader_status("card_ok")

    def on_card_failed(self, msg):
        self.info_label.setText(tr("failed_retry", self.language))
        self.status.showMessage(msg)
        self.save_btn.setEnabled(False)
        self.print_btn.setEnabled(False)
        self.set_reader_status("no_card")

    def on_no_card(self):
        self._clear_card_data()

        self.info_label.setText(tr("connected_insert", self.language))
        self.status.showMessage(tr("no_card", self.language))

        self.save_btn.setEnabled(False)
        self.print_btn.setEnabled(False)

        self.set_reader_status("no_card")

    def on_read_started(self):
        self._clear_card_data()
        self.info_label.setText(tr("reading", self.language))
        self.status.showMessage(tr("reading", self.language))
        self.save_btn.setEnabled(False)
        self.print_btn.setEnabled(False)
        self.set_reader_status("no_card")  # yellow (blinking)

    def _clear_card_data(self):
        self.card_data = None
        self.print_btn.setEnabled(False)
        self.print_btn.setToolTip(tr("read_id_before_print", self.language))
        self.id_widget.clear_data()
        self.med_widget.clear_data()
        self.card_stack.setCurrentWidget(self.empty_label)

    def print_current_card(self):
        if not self.card_data or self.card_data.get("type") != "ID":
            QMessageBox.information(
                self,
                tr("read_before_print_title", self.language),
                tr("read_before_print_msg", self.language),
            )
            return

        try:
            printed = print_id_document(
                self, self.card_data["data"], language=self.language
            )
        except Exception as error:
            QMessageBox.critical(
                self,
                tr("print_failed", self.language),
                tr("could_not_print", self.language, error=error),
            )
            self.status.showMessage(tr("print_failed", self.language))
            return

        if printed:
            self.status.showMessage(tr("sent_printer", self.language))

    def manual_read(self):
        if not self.reader_name:
            QMessageBox.information(
                self,
                tr("no_reader_title", self.language),
                tr("no_reader_msg", self.language)
            )
            return

        if not self.worker.is_card_connected():
            QMessageBox.information(
                self,
                tr("no_card_title", self.language),
                tr("no_card_msg", self.language)
            )
            return

        self.status.showMessage(tr("manual_triggered", self.language))
        if not self.worker.force_read():
            self.on_no_card()

    def closeEvent(self, event):
        """Stop the polling thread before Qt destroys the window."""
        self.worker.stop()
        if not self.worker.wait(3000):
            event.ignore()
            QMessageBox.warning(
                self,
                tr("reader_busy", self.language),
                tr("reader_busy_msg", self.language),
            )
            return
        event.accept()

    # ---------- Theme management ----------

    def apply_language(self, language: str):
        """Apply a language to the window and all currently visible widgets."""
        self.language = language if language in ("sr", "en") else DEFAULT_LANGUAGE
        self.read_btn.setText(tr("read_card", self.language))
        self.save_btn.setText(tr("save", self.language))
        self.print_btn.setText(tr("print", self.language))
        self.empty_label.setText(tr("insert_card", self.language))
        self.read_btn.setToolTip(
            "" if self.reader_name else tr("no_reader_short", self.language)
        )
        self.save_btn.setToolTip(tr("save_unimplemented", self.language))
        self.print_btn.setToolTip(
            tr("print_medical", self.language)
            if self.card_data and self.card_data.get("type") == "MED"
            else tr("read_id_before_print", self.language)
        )
        self.reader_menu.setTitle(tr("reader_selection", self.language))
        self.refresh_action.setText(tr("refresh", self.language))
        self.auto_action.setText(tr("auto_select", self.language))
        self.settings_menu.setTitle(tr("settings", self.language))
        self.pref_action.setText(tr("preferences", self.language))
        self.id_widget.set_language(self.language)
        self.med_widget.set_language(self.language)
        if self.card_data:
            current_label = (
                "id_success" if self.card_data.get("type") == "ID"
                else "medical_success" if self.card_data.get("type") == "MED"
                else "card_success"
            )
            self.info_label.setText(tr(current_label, self.language))
            self.status.showMessage(tr(current_label, self.language))
        elif self.reader_name:
            self.info_label.setText(tr("connected_insert", self.language))
            self.status.showMessage(tr("connected_insert", self.language))
        else:
            self.info_label.setText(tr("no_reader", self.language))
            self.status.showMessage(tr("no_reader", self.language))
        self.set_reader_status(
            "card_ok" if self.card_data else "no_card" if self.reader_name else "no_reader"
        )

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

        self.status.showMessage(
            tr("theme_changed", self.language, theme=tr(theme_name, self.language))
        )
