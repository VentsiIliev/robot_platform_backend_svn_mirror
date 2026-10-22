"""Optional diagnostics composition, independent of Qt and RobotSystem domains."""
import os
import logging

from .config import DiagnosticsConfig
from .i_diagnostics_service import IDiagnosticsService


class NullDiagnosticsService(IDiagnosticsService):
    def start(self) -> bool:
        return False

    @property
    def status(self) -> dict:
        return {'enabled': False, 'running': False, 'state': 'disabled', 'last_error': None}

    def close(self) -> None:
        pass


class DiagnosticsService(IDiagnosticsService):
    """Own one recorder session; start/close are idempotent, close is terminal."""
    def __init__(self, config: DiagnosticsConfig, *, directory=None, machine_id=None):
        self._config = config
        self._directory = directory
        self._machine_id = machine_id
        self._runtime = None
        self._closed = False
        self._attempted = False
        self._error = None

    def start(self) -> bool:
        if self._closed or not self._config.enabled:
            return False
        if self._attempted:
            return self.status['running']
        self._attempted = True
        try:
            # Disabled/omitted capabilities do not import storage machinery.
            from .runtime import DiagnosticsRuntime, default_directory
            self._runtime = DiagnosticsRuntime(
                default_directory() if self._directory is None else self._directory,
                machine_id=os.environ.get('ROBOT_PLATFORM_MACHINE_ID', '') if self._machine_id is None else self._machine_id,
                capture_logs=self._config.capture_logs, console_events=self._config.console_events,
            )
            started = self._runtime.start()
            if started:
                from .events import observe
                observe(logging.getLogger(__name__), 'diagnostics.capture.started',
                        capture_logs=self._config.capture_logs, console_events=self._config.console_events)
            return started
        except Exception as exc:
            self._error = str(exc)
            if self._runtime is not None:
                self._close_runtime()
            return False

    @property
    def status(self) -> dict:
        details = self._runtime.status if self._runtime is not None else {}
        running = details.get('running', False) and not self._closed
        state = ('disabled' if not self._config.enabled else 'stopped' if self._closed else
                 'unavailable' if self._error or details.get('last_error') else
                 'recording' if running else 'not_started')
        return {**details, 'enabled': self._config.enabled, 'running': running, 'state': state,
                'last_error': self._error or details.get('last_error')}

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self._runtime is not None:
            self._close_runtime()

    def _close_runtime(self):
        try:
            self._runtime.close()
        except Exception as exc:
            # Optional cleanup must not mask an original application exception.
            self._error = self._error or str(exc)


def build_diagnostics_service(config: DiagnosticsConfig | None = None, **options) -> IDiagnosticsService:
    """Omission selects a no-op; bootstrap explicitly supplies deployment policy."""
    if config is None or not config.enabled:
        return NullDiagnosticsService()
    return DiagnosticsService(config, **options)
