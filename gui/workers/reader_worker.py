"""
CELIK-26 GUI worker thread for reader management.
Handles reader connection, card detection and reading.
"""

from PyQt6.QtCore import QThread, pyqtSignal
import time

from smartcard.Exceptions import NoCardException, CardConnectionException

from card_reader_cli import (
    get_readers_list,
    connect_reader,
    read_card
)


class ReaderWorker(QThread):
    reader_connected = pyqtSignal(str)
    reader_disconnected = pyqtSignal()
    card_read_success = pyqtSignal(dict)
    card_read_failed = pyqtSignal(str)
    no_card_present = pyqtSignal()
    read_started = pyqtSignal()

    def __init__(self, poll_interval=1.5):
        super().__init__()
        self.poll_interval = poll_interval
        self._running = True

        self.reader_connected_once = False
        self.card_connected = False
        self.card_read = False

        self.current_reader = None
        self.current_reader_name = None

        self.manual_reader_name = None  # 👈 NEW

    def stop(self):
        self._running = False

    def try_connect_reader(self, reader_name):
        try:
            return connect_reader(reader_name)
        except NoCardException:
            return None  # Reader present, no card

    def set_manual_reader(self, reader_name: str | None):
        """
        If reader_name is None → AUTO mode
        Otherwise → MANUAL mode
        """
        self.manual_reader_name = reader_name
        self.current_reader = None
        self.current_reader_name = None

    def is_card_present(self) -> bool:
        try:
            self.current_reader.atr()
            return True
        except Exception:
            return False

    def force_read(self):
        """
        Trigger a one-shot card read without reconnecting.
        """
        if self.card_connected:
            self.card_read = False
            self.read_started.emit()

    def _reset_all_state(self):
        self.current_reader = None
        self.current_reader_name = None
        self.card_connected = False
        self.card_read = False

    def run(self):
        while self._running:
            readers = get_readers_list(override_exception=True)

            # ---------- NO READER ----------
            if not readers:
                if self.reader_connected_once:
                    self._reset_all_state()
                    self.reader_connected_once = False
                    self.reader_disconnected.emit()

                time.sleep(self.poll_interval)
                continue

            reader_name = (
                self.manual_reader_name
                if self.manual_reader_name
                else str(readers[0])
            )

            # ---------- READER PRESENT ----------
            if not self.reader_connected_once:
                self.current_reader_name = reader_name
                self.reader_connected.emit(reader_name)
                self.reader_connected_once = True

                self.no_card_present.emit()

            # ---------- CARD CONNECTION ----------
            if not self.card_connected:
                try:
                    self.current_reader = connect_reader(reader_name)
                    self.card_connected = True
                    self.card_read = False
                except NoCardException:
                    time.sleep(self.poll_interval)
                    continue

            # ---------- READ CARD (ONCE) ----------
            if self.card_connected and not self.is_card_present():
                self.card_connected = False
                self.card_read = False
                self.current_reader = None
                self.no_card_present.emit()
                continue
            if self.card_connected and not self.card_read:
                try:
                    card_data = read_card(self.current_reader)
                    self.card_read_success.emit(card_data)
                    self.card_read = True
                except CardConnectionException:
                    # Card was removed mid-read
                    self.card_connected = False
                    self.card_read = False
                    self.no_card_present.emit()
                except Exception as e:
                    self.card_read_failed.emit(str(e))

            time.sleep(self.poll_interval)
