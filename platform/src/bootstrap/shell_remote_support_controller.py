"""Lifetime-scoped background remote-support monitoring for the shell."""

import threading

from PyQt6.QtCore import QObject, QThread, pyqtSignal


class _Worker(QObject):
    status_updated = pyqtSignal(str)

    def __init__(self, support_client, session_client, interval: float) -> None:
        super().__init__()
        self._support = support_client
        self._sessions = session_client
        self._interval = interval
        self.stopped = threading.Event()

    def run(self) -> None:
        while not self.stopped.is_set():
            try:
                status = self._support.status()
                # Query sessions even when the desired enable marker is OFF:
                # an independently started service may still host a session.
                if status["active"]:
                    count = self._sessions.get_session_count()
                    state = "connected" if count else "ready"
                else:
                    state = "unavailable" if status["enabled"] else "disabled"
            except (OSError, ValueError, RuntimeError):
                state = "unavailable"
            if not self.stopped.is_set():
                self.status_updated.emit(state)
            self.stopped.wait(self._interval)


class ShellRemoteSupportController(QObject):
    def __init__(self, header, support_client, session_client, interval: float = 2) -> None:
        super().__init__(header)
        self._header = header
        self._thread = QThread(self)
        self._worker = _Worker(support_client, session_client, interval)
        self._worker.moveToThread(self._thread)
        self._thread.started.connect(self._worker.run)
        self._worker.status_updated.connect(self._on_status)
        self._thread.finished.connect(self._worker.deleteLater)

    def start(self) -> None:
        self._header.set_remote_support_state("unavailable")
        self._thread.start()

    def stop(self) -> None:
        self._worker.stopped.set()
        self._thread.quit()
        # Clients have bounded timeouts; join before destroying Qt objects.
        self._thread.wait()

    def _on_status(self, state: str) -> None:
        if not self._worker.stopped.is_set():
            self._header.set_remote_support_state(state)
