"""Best-effort console projection, independent of commands and persistence."""
from __future__ import annotations

import logging
import queue
import threading


class ObservationConsole:
    def __init__(self, capacity=256):
        self._queue = queue.Queue(maxsize=capacity)
        self._closing = threading.Event()
        self._thread = threading.Thread(target=self._run, name='DiagnosticsConsole', daemon=True)
        self.dropped = 0
        self._logger = logging.getLogger('diagnostics.events')

    def start(self):
        self._thread.start()

    def submit(self, payload):
        # Filter before queueing: DEBUG evidence parts normally have no console
        # audience and must not consume console worker/queue capacity.
        if not self._logger.isEnabledFor(getattr(logging, payload['level'], logging.INFO)):
            return
        try:
            self._queue.put_nowait(payload)
        except queue.Full:
            self.dropped += 1

    def close(self):
        self._closing.set()
        while True:
            try:
                self._queue.get_nowait()
                self.dropped += 1
            except queue.Empty:
                break
        # A third-party handler may never return. It is not a control/writer
        # dependency, and this daemon must never hold up shutdown indefinitely.
        if self._thread.ident is not None:
            self._thread.join(0.05)

    def _run(self):
        while not self._closing.is_set():
            try:
                payload = self._queue.get(timeout=0.05)
            except queue.Empty:
                continue
            try:
                self._logger.log(getattr(logging, payload['level'], logging.INFO),
                           payload['event'], extra={'diagnostics_captured': True})
            except Exception:
                self.dropped += 1
