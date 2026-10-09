import logging
from threading import Condition, Thread
from typing import Callable

from src.engine.core.i_messaging_service import IMessagingService
from src.engine.hardware.operator_lights.config import OperatorLightsConfig
from src.engine.hardware.operator_lights.i_operator_lights import IOperatorLights
from src.shared_contracts.events.process_events import ProcessState, ProcessStateEvent, ProcessTopics


class OperatorLightCoordinator:
    """Map one process's states to configured channels without blocking its callbacks."""

    def __init__(self, lights: IOperatorLights, config: OperatorLightsConfig,
                 messaging: IMessagingService, process_id: str,
                 state_getter: Callable[[], ProcessState]) -> None:
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
        if self._thread is not None:
            raise RuntimeError("Operator light coordinator has already started")
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
                self._condition.notify()

    def _run(self) -> None:
        while True:
            with self._condition:
                self._condition.wait_for(lambda: self._stopping or self._pending is not None)
                if self._stopping:
                    return
                state = self._pending
                self._pending = None
            try:
                self._lights.set_active(self._mapping[state])
            except Exception:
                logging.getLogger(__name__).exception("Could not apply operator light indication")

    def stop(self) -> None:
        """Unsubscribe and finish output work before the light service is closed."""
        self._messaging.unsubscribe(self._topic, self._on_state)
        with self._condition:
            self._stopping = True
            self._pending = None
            self._condition.notify()
        if self._thread is not None:
            self._thread.join()
