"""Translate process/robot lifecycle notifications into non-blocking guidance commands."""

from math import isfinite

from src.engine.core.i_messaging_service import IMessagingService
from src.engine.robot.services.robot_state_snapshot import RobotStateSnapshot
from src.robot_systems.paint.component_ids import ProcessID
from src.robot_systems.paint.paint_head_check.live_guidance import PaintHeadLiveGuidance
from src.shared_contracts.events.process_events import (
    ProcessState,
    ProcessStateEvent,
    ProcessTopics,
)
from src.shared_contracts.events.robot_events import RobotTopics


class PaintHeadGuidanceLifecycle:
    def __init__(self, messaging: IMessagingService, guidance: PaintHeadLiveGuidance) -> None:
        self._messaging = messaging
        self._guidance = guidance
        self._subscribed = False

    def start(self) -> None:
        if self._subscribed:
            return
        self._subscribed = True
        self._messaging.subscribe(ProcessTopics.ACTIVE, self._on_process_state)
        self._messaging.subscribe(RobotTopics.STATE, self._on_robot_state)
        self._messaging.subscribe(RobotTopics.ROBOT_CONFIG_CHANGED, self._on_configuration_changed)
        self._messaging.subscribe(
            RobotTopics.TARGETING_DEFINITIONS_CHANGED, self._on_configuration_changed
        )

    def stop(self) -> None:
        if self._subscribed:
            self._subscribed = False
            self._messaging.unsubscribe(ProcessTopics.ACTIVE, self._on_process_state)
            self._messaging.unsubscribe(RobotTopics.STATE, self._on_robot_state)
            self._messaging.unsubscribe(
                RobotTopics.ROBOT_CONFIG_CHANGED, self._on_configuration_changed
            )
            self._messaging.unsubscribe(
                RobotTopics.TARGETING_DEFINITIONS_CHANGED, self._on_configuration_changed
            )
        self._guidance.close()

    def _on_process_state(self, event: object) -> None:
        if not self._subscribed or not isinstance(event, ProcessStateEvent):
            return
        if event.state is ProcessState.RUNNING:
            self._guidance.cancel()
        elif event.process_id == ProcessID.MAIN_PROCESS and event.state is ProcessState.STOPPED:
            self._guidance.start_pending()

    def _on_robot_state(self, event: object) -> None:
        if self._subscribed and isinstance(event, RobotStateSnapshot):
            if not isfinite(event.velocity) or abs(event.velocity) > 1e-6:
                self._guidance.cancel()

    def _on_configuration_changed(self, event: object) -> None:
        if self._subscribed:
            self._guidance.cancel()
