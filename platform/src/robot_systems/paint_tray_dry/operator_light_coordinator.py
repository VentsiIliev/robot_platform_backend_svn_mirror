import logging
from threading import Condition, Thread
from time import monotonic
from typing import Callable

from src.engine.core.i_health_checkable import IHealthCheckable
from src.shared_contracts.events.notification_events import (
    NotificationTopics, NotificationSeverity, UserNotificationEvent, DismissNotificationEvent,
)

from src.engine.core.i_messaging_service import IMessagingService
from src.engine.hardware.operator_lights.config import OperatorLightsConfig
from src.engine.hardware.operator_lights.i_operator_lights import IOperatorLights
from src.shared_contracts.events.process_events import ProcessState, ProcessStateEvent, ProcessTopics


class OperatorLightCoordinator(IHealthCheckable):
    """Map one process's states to configured channels without blocking its callbacks."""

    def __init__(self, lights: IOperatorLights, config: OperatorLightsConfig,
                 messaging: IMessagingService, process_id: str,
                 state_getter: Callable[[], ProcessState], *,
                 retry_interval: float = 0.25, max_retry_interval: float = 5.0,
                 shutdown_timeout: float = 2.0) -> None:
        if retry_interval <= 0 or max_retry_interval < retry_interval or shutdown_timeout < 0:
            raise ValueError("Invalid operator light retry/shutdown timing")
        self._retry_interval = retry_interval
        self._max_retry_interval = max_retry_interval
        self._shutdown_timeout = shutdown_timeout
        self._healthy = False
        self._last_error: str | None = None
        self._lights = lights
        self._messaging = messaging
        self._topic = ProcessTopics.state(process_id)
        self._state_getter = state_getter
        self._mapping = {
            ProcessState(state): tuple(lights.get_channel(name) for name in names)
            for state, names in config.state_mapping.items()
        }
        missing = set(ProcessState) - self._mapping.keys()
        if missing:
            raise ValueError(f"Light mapping is missing process states: {sorted(s.value for s in missing)}")
        self._condition = Condition()
        self._pending: ProcessState | None = None
        self._stopping = False
        self._thread: Thread | None = None

    def start(self) -> None:
        """Subscribe, seed the current state, then start the single output worker."""
        if self._thread is not None or self._stopping:
            raise RuntimeError("Operator light coordinator cannot be restarted")
        self._messaging.subscribe(self._topic, self._on_state)
        try:
            initial = self._state_getter()
            with self._condition:
                # Events received after subscribing take precedence over the snapshot.
                if self._pending is None:
                    self._pending = initial
            self._thread = Thread(target=self._run, name="OperatorLights", daemon=True)
            self._thread.start()
        except Exception:
            self._messaging.unsubscribe(self._topic, self._on_state)
            raise

    def _on_state(self, event: ProcessStateEvent) -> None:
        with self._condition:
            if not self._stopping:
                self._pending = event.state
                self._healthy = False
                self._condition.notify()

    def is_healthy(self) -> bool:
        """Whether the latest requested indication was written successfully (no readback)."""
        with self._condition:
            return self._healthy and not self._stopping

    @property
    def last_error(self) -> str | None:
        with self._condition:
            return self._last_error

    def _notify_fault(self, error: str | None) -> None:
        try:
            if error is None:
                self._messaging.publish(NotificationTopics.DISMISS,
                    DismissNotificationEvent(dedupe_key="operator_lights.output"))
            else:
                self._messaging.publish(NotificationTopics.USER, UserNotificationEvent(
                    source="operator_lights", severity=NotificationSeverity.ERROR,
                    title_key="notification.operator_lights.title",
                    message_key="notification.operator_lights.failed",
                    fallback_title="Operator lights unavailable",
                    fallback_message="Light indication may be stale. Retrying output writes.",
                    detail=error, dedupe_key="operator_lights.output",
                ))
        except Exception:
            logging.getLogger(__name__).exception("Could not publish operator light health")

    def _run(self) -> None:
        state = None
        retry_at = 0.0
        delay = self._retry_interval
        try:
            while True:
                with self._condition:
                    while not self._stopping and self._pending is None:
                        if state is None:
                            self._condition.wait()
                        else:
                            remaining = retry_at - monotonic()
                            if remaining <= 0:
                                break
                            self._condition.wait(remaining)
                    if self._stopping:
                        return
                    if self._pending is not None:
                        state = self._pending
                        self._pending = None
                        delay = self._retry_interval
                try:
                    self._lights.set_active(self._mapping[state])
                except Exception as exc:
                    with self._condition:
                        first_failure = self._last_error is None
                        self._healthy = False
                        self._last_error = str(exc)
                    if first_failure:
                        logging.getLogger(__name__).exception("Could not apply operator light indication")
                    # Repeat with a dedupe key: startup may precede the UI subscriber.
                    self._notify_fault(str(exc))
                    retry_at = monotonic() + delay
                    delay = min(delay * 2, self._max_retry_interval)
                else:
                    with self._condition:
                        recovered = self._last_error is not None
                        self._last_error = None
                        self._healthy = self._pending is None
                    if recovered:
                        self._notify_fault(None)
                    state = None
                    delay = self._retry_interval
        finally:
            # This worker owns the transport, including after stop() times out.
            try:
                self._lights.close()
            except Exception:
                logging.getLogger(__name__).exception("Could not close operator lights")
            with self._condition:
                self._healthy = False

    def stop(self) -> None:
        """Bound the caller's wait; the writer closes its own transport on exit."""
        try:
            self._messaging.unsubscribe(self._topic, self._on_state)
        finally:
            with self._condition:
                self._stopping = True
                self._pending = None
                self._condition.notify()
            if self._thread is None or self._thread.ident is None:
                # Also close asynchronously if startup failed before a worker existed.
                self._thread = Thread(target=self._run, name="OperatorLightsClose", daemon=True)
                self._thread.start()
            self._thread.join(self._shutdown_timeout)
            if self._thread.is_alive():
                raise TimeoutError("Operator light worker still owns its transport; close deferred")
