"""Background reader/card polling for the CELIK-26 GUI."""

from threading import Event, RLock

from PyQt6.QtCore import QThread, pyqtSignal
from smartcard.Exceptions import CardConnectionException, NoCardException

from card_reader_cli import connect_reader, get_readers_list, read_card


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
        self._stop_event = Event()
        self._lock = RLock()

        self.reader_connected_once = False
        self.card_connected = False
        self.card_read = False
        self.current_reader = None
        self.current_reader_name = None
        self.manual_reader_name = None
        self._selection_changed = False

    def stop(self):
        """Request a prompt, clean thread shutdown."""
        self._stop_event.set()

    def set_manual_reader(self, reader_name: str | None):
        """Select a named reader, or ``None`` to restore automatic selection."""
        with self._lock:
            self.manual_reader_name = reader_name
            self._selection_changed = True

    def is_card_connected(self) -> bool:
        with self._lock:
            return self.card_connected

    def force_read(self) -> bool:
        """Request a one-shot reread of the currently connected card."""
        with self._lock:
            if not self.card_connected:
                return False
            self.card_read = False
            return True

    def _wait(self):
        self._stop_event.wait(self.poll_interval)

    def _disconnect_card(self):
        if self.current_reader is not None:
            try:
                self.current_reader.disconnect()
            except Exception:
                pass
        self.current_reader = None
        self.card_connected = False
        self.card_read = False

    def _reset_all_state(self, *, disconnect=False):
        if disconnect:
            self._disconnect_card()
        else:
            self.current_reader = None
            self.card_connected = False
            self.card_read = False
        self.current_reader_name = None
        self.reader_connected_once = False

    def _card_is_present(self) -> bool:
        try:
            return self.current_reader is not None and bool(self.current_reader.atr())
        except Exception:
            return False

    def run(self):
        try:
            while not self._stop_event.is_set():
                try:
                    available_readers = get_readers_list(override_exception=True)
                except Exception as exc:
                    self.card_read_failed.emit(str(exc))
                    self._wait()
                    continue

                with self._lock:
                    manual_reader = self.manual_reader_name
                    selection_changed = self._selection_changed
                    self._selection_changed = False

                if selection_changed:
                    with self._lock:
                        had_reader = self.reader_connected_once
                        self._reset_all_state(disconnect=True)
                    if had_reader:
                        self.reader_disconnected.emit()

                if not available_readers or (
                    manual_reader is not None and manual_reader not in available_readers
                ):
                    with self._lock:
                        was_connected = self.reader_connected_once
                        self._reset_all_state(disconnect=True)
                    if was_connected:
                        self.reader_disconnected.emit()
                    self._wait()
                    continue

                reader_name = manual_reader or available_readers[0]

                with self._lock:
                    if not self.reader_connected_once:
                        self.current_reader_name = reader_name
                        self.reader_connected_once = True
                        announce_reader = True
                    else:
                        announce_reader = False

                if announce_reader:
                    self.reader_connected.emit(reader_name)
                    self.no_card_present.emit()

                with self._lock:
                    needs_connection = not self.card_connected

                if needs_connection:
                    try:
                        connection = connect_reader(reader_name)
                    except (NoCardException, CardConnectionException):
                        self._wait()
                        continue
                    except Exception as exc:
                        # A reader can disappear between enumeration and connection.
                        self.card_read_failed.emit(str(exc))
                        self._wait()
                        continue

                    with self._lock:
                        self.current_reader = connection
                        self.card_connected = True
                        self.card_read = False

                with self._lock:
                    card_present = self._card_is_present()
                    should_read = self.card_connected and not self.card_read
                    connection = self.current_reader

                if not card_present:
                    with self._lock:
                        self._disconnect_card()
                    self.no_card_present.emit()
                    self._wait()
                    continue

                if should_read:
                    self.read_started.emit()
                    try:
                        card_data = read_card(connection)
                    except (NoCardException, CardConnectionException):
                        with self._lock:
                            self._disconnect_card()
                        self.no_card_present.emit()
                    except Exception as exc:
                        self.card_read_failed.emit(str(exc))
                    else:
                        with self._lock:
                            self.card_read = True
                        self.card_read_success.emit(card_data)

                self._wait()
        finally:
            with self._lock:
                self._reset_all_state(disconnect=True)
