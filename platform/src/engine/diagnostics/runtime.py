"""Bounded background logging and transactional lifetime metrics.

Only the writer thread owns SQLite and rotating files. Producers never wait
for disk I/O. Logs and statistics degrade visibly without changing commands.
"""
from __future__ import annotations

import atexit
import fcntl
import json
import logging
import math
import os
import queue
import sqlite3
import sys
import threading
import time
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from uuid import uuid4

from .events import current_context


def default_directory() -> Path:
    override = os.environ.get("ROBOT_PLATFORM_DIAGNOSTICS_DIR")
    if override:
        return Path(override).expanduser()
    data_root = os.environ.get("ROBOT_PLATFORM_DATA_ROOT")
    if data_root:
        return Path(data_root).expanduser() / "diagnostics"
    state_root = Path(os.environ.get("XDG_STATE_HOME", str(Path.home() / ".local" / "state")))
    return state_root / "robot-platform" / "diagnostics"


def _utc(timestamp: float | None = None) -> str:
    return datetime.fromtimestamp(time.time() if timestamp is None else timestamp, timezone.utc).isoformat()


class _Ingress(logging.Handler):
    def __init__(self, runtime):
        super().__init__(logging.INFO)
        self.runtime = runtime

    def emit(self, record):
        try:
            event = getattr(record, 'diagnostic_event', {})
            payload = {
                'timestamp': _utc(record.created), 'level': record.levelname,
                'logger': getattr(record, 'diagnostic_source', record.name), 'thread': record.threadName,
                'source': f'{record.pathname}:{record.lineno}',
                'message': record.getMessage(),
                'context': current_context(),
                'event': event.get('event'), 'fields': event.get('fields', {}),
                'metrics': event.get('metrics', {}), 'output': event.get('output'),
                'monotonic': event.get('monotonic', time.monotonic()),
            }
            if record.exc_info:
                payload['traceback'] = logging.Formatter().formatException(record.exc_info)
            # Freeze fields so producer mutation cannot affect queued observations.
            serialized = json.dumps(payload, default=str, allow_nan=False)
            if len(serialized) > 16384:
                payload['fields'] = {'truncated': True}
                payload['message'] = payload['message'][:4096]
                if 'traceback' in payload:
                    payload['traceback'] = payload['traceback'][:8192]
                serialized = json.dumps(payload, default=str, allow_nan=False)
            payload = json.loads(serialized)
            self.runtime._enqueue(payload)
        except Exception as exc:
            self.runtime._report_failure(exc)


class DiagnosticsRuntime:
    def __init__(self, directory: str | Path, *, machine_id: str = '',
                 queue_size: int = 2048, max_bytes: int = 10 * 1024 * 1024,
                 backups: int = 5, checkpoint_seconds: float = 5.0):
        if queue_size <= 0 or max_bytes <= 0 or backups <= 0:
            raise ValueError("Diagnostics queue and retention limits must be positive")
        self.directory = Path(directory)
        self.session_id = uuid4().hex
        self.machine_id = machine_id
        self._queue = queue.Queue(maxsize=queue_size)
        self._lock = threading.Lock()
        self._closing = threading.Event()
        self._ready = threading.Event()
        self._closed = False
        self._error: str | None = None
        self._dropped = 0
        self._reported = False
        self._overflow_reported = False
        self._max_bytes = max_bytes
        self._backups = backups
        self._checkpoint = max(0.05, checkpoint_seconds)
        self._handler = _Ingress(self)
        self._thread = threading.Thread(target=self._run, name='DiagnosticsWriter', daemon=True)

    def start(self) -> bool:
        """Initialize before startup; return False if persistence is unavailable."""
        self._thread.start()
        if not self._ready.wait(5):
            self._report_failure(TimeoutError('Diagnostics initialization timed out'))
            self._closing.set()
            return False
        if self._error is not None or self._closing.is_set():
            return False
        logging.getLogger().addHandler(self._handler)
        atexit.register(self.close)
        return True

    @property
    def status(self) -> dict:
        with self._lock:
            return {'session_id': self.session_id, 'directory': str(self.directory),
                    'dropped_events': self._dropped, 'queue_depth': self._queue.qsize(),
                    'last_error': self._error,
                    'running': self._thread.is_alive() and not self._closing.is_set()}

    def _enqueue(self, payload):
        with self._lock:
            if self._closing.is_set():
                return
            try:
                self._queue.put_nowait(payload)
            except queue.Full:
                self._dropped += 1
                # Missing output transitions make runtime accounting uncertain.
                # The worker invalidates active states at its next checkpoint.
                if not self._overflow_reported:
                    print('Diagnostics queue full: observations dropped; see diagnostics status.', file=sys.stderr)
                    self._overflow_reported = True

    def _report_failure(self, exc):
        with self._lock:
            self._error = str(exc)
            if not self._reported:
                print(f'Diagnostics persistence unavailable: {exc}', file=sys.stderr)
                self._reported = True

    def close(self) -> None:
        """Drain within a bounded deadline; unfinished sessions remain unclean."""
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._closing.set()
        logging.getLogger().removeHandler(self._handler)
        if self._thread.ident is not None:
            self._thread.join(5)
        if self._thread.is_alive():
            self._report_failure(TimeoutError('Diagnostics did not drain within five seconds'))
        atexit.unregister(self.close)

    @staticmethod
    def _metric(db, name, value):
        value = float(value)
        if not math.isfinite(value) or value < 0:
            raise ValueError(f'Invalid metric sample: {name}')
        db.execute('''INSERT INTO metrics(name,samples,total,maximum) VALUES(?,1,?,?)
            ON CONFLICT(name) DO UPDATE SET samples=samples+1,
            total=total+excluded.total,maximum=max(maximum,excluded.maximum)''',
            (name, value, value))

    def _run(self):
        db = None
        handler = None
        lease = None
        outputs = {}
        output_states = {}
        accounted_drops = 0
        uptime_since = time.monotonic()
        try:
            self.directory.mkdir(parents=True, exist_ok=True)
            lease = (self.directory / "writer.lock").open("a")
            fcntl.flock(lease.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            db = sqlite3.connect(self.directory / 'statistics.sqlite3', timeout=2)
            db.execute('PRAGMA journal_mode=WAL')
            db.execute('PRAGMA synchronous=FULL')
            version = db.execute('PRAGMA user_version').fetchone()[0]
            if version not in (0, 1):
                raise RuntimeError(f'Unsupported diagnostics schema: {version}')
            db.executescript('''CREATE TABLE IF NOT EXISTS metrics(
                name TEXT PRIMARY KEY, samples INTEGER NOT NULL,
                total REAL NOT NULL, maximum REAL NOT NULL);
                CREATE TABLE IF NOT EXISTS sessions(
                id TEXT PRIMARY KEY, started TEXT NOT NULL, ended TEXT,
                interrupted INTEGER NOT NULL DEFAULT 0);
                CREATE TABLE IF NOT EXISTS outputs(
                name TEXT PRIMARY KEY, state INTEGER);
                CREATE TABLE IF NOT EXISTS metadata(name TEXT PRIMARY KEY, value TEXT NOT NULL);
                PRAGMA user_version=1;''')
            interrupted = db.execute('SELECT count(*) FROM sessions WHERE ended IS NULL AND interrupted=0').fetchone()[0]
            if interrupted:
                self._metric(db, 'diagnostics.interrupted_sessions', interrupted)
                db.execute('UPDATE sessions SET interrupted=1 WHERE ended IS NULL')
            for (name,) in db.execute('SELECT name FROM outputs WHERE state=1').fetchall():
                self._metric(db, f'{name}.unconfirmed_intervals', 1)
            db.execute('UPDATE outputs SET state=NULL')
            db.execute('INSERT INTO sessions(id,started) VALUES(?,?)', (self.session_id, _utc()))
            self._metric(db, 'diagnostics.sessions', 1)
            if self.machine_id:
                db.execute('INSERT INTO metadata(name,value) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET value=excluded.value', ('machine_id', self.machine_id))
            # Keep session metadata bounded; lifetime counters are independent.
            db.execute('DELETE FROM sessions WHERE id IN (SELECT id FROM sessions ORDER BY started DESC LIMIT -1 OFFSET 1000)')
            db.commit()
            handler = RotatingFileHandler(self.directory / 'events.jsonl',
                maxBytes=self._max_bytes, backupCount=self._backups, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(message)s'))
            self._ready.set()
            deadline = time.monotonic() + self._checkpoint
            while not self._closing.is_set() or not self._queue.empty():
                try:
                    payload = self._queue.get(timeout=min(0.1, self._checkpoint))
                except queue.Empty:
                    payload = None
                now = time.monotonic()
                if payload is not None:
                    build_info = payload['fields'].get('build_info')
                    if isinstance(build_info, dict):
                        for key, value in build_info.items():
                            if key in {'release_version', 'platform_version', 'backend_version',
                                       'robot_driver', 'backend', 'backend_profile'}:
                                db.execute('INSERT INTO metadata(name,value) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET value=excluded.value', (key, str(value)))
                    for name, value in payload['metrics'].items():
                        self._metric(db, name, value)
                    transition = payload['output']
                    observed_at = payload.pop('monotonic')
                    if transition is not None:
                        name, state = transition
                        previous = outputs.get(name)
                        if previous is not None:
                            self._metric(db, f'{name}.commanded_on_seconds', max(0, observed_at - previous))
                        if state is True:
                            if previous is None:
                                self._metric(db, f'{name}.commanded_on_intervals', 1)
                            if output_states.get(name) is False:
                                self._metric(db, f'{name}.off_to_on_transitions', 1)
                            outputs[name] = max(observed_at, previous or observed_at)
                        else:
                            outputs.pop(name, None)
                            if state is None:
                                self._metric(db, f'{name}.unknown_state_events', 1)
                        output_states[name] = state
                        db.execute('INSERT INTO outputs(name,state) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET state=excluded.state', (name, state))
                    payload.update(session_id=self.session_id, machine_id=self.machine_id)
                    record = logging.LogRecord('diagnostics', logging.INFO, '', 0,
                        json.dumps(payload, ensure_ascii=False, allow_nan=False), (), None)
                    # Call directly: logging.Handler.emit normally suppresses disk
                    # errors, preventing the status from reporting persistence loss.
                    if handler.shouldRollover(record):
                        handler.doRollover()
                    if handler.stream is None:
                        handler.stream = handler._open()
                    handler.stream.write(handler.format(record) + '\n')
                    handler.flush()
                if now >= deadline:
                    self._metric(db, 'diagnostics.application_uptime_seconds', now - uptime_since)
                    uptime_since = now
                    with self._lock:
                        drops = self._dropped
                    if drops != accounted_drops:
                        self._metric(db, 'diagnostics.dropped_events', drops - accounted_drops)
                        for name in outputs:
                            self._metric(db, f'{name}.unconfirmed_intervals', 1)
                        outputs.clear()
                        output_states.clear()
                        db.execute('UPDATE outputs SET state=NULL')
                        accounted_drops = drops
                    # Account only through the most recent observed timestamp.
                    # Heartbeat durations are added only once the input queue is
                    # drained, so older OFF events cannot double-count runtime.
                    if self._queue.empty():
                        for name, since in list(outputs.items()):
                            self._metric(db, f'{name}.commanded_on_seconds', max(0, now - since))
                            outputs[name] = now
                    db.commit()
                    deadline = now + self._checkpoint
            now = time.monotonic()
            with self._lock:
                remaining_drops = self._dropped - accounted_drops
            for name, since in outputs.items():
                if not remaining_drops:
                    self._metric(db, f'{name}.commanded_on_seconds', max(0, now - since))
                self._metric(db, f'{name}.unconfirmed_intervals', 1)
            if remaining_drops:
                self._metric(db, 'diagnostics.dropped_events', remaining_drops)
            # Closing the application does not prove outputs are physically OFF.
            db.execute('UPDATE outputs SET state=NULL')
            self._metric(db, 'diagnostics.application_uptime_seconds', now - uptime_since)
            db.execute('UPDATE sessions SET ended=? WHERE id=?', (_utc(), self.session_id))
            db.commit()
        except Exception as exc:
            self._report_failure(exc)
        finally:
            self._closing.set()
            self._ready.set()
            if handler is not None:
                handler.close()
            if db is not None:
                db.close()
            if lease is not None:
                lease.close()
