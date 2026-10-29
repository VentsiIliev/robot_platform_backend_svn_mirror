"""Publish the last inspection result without owning camera acquisition or motion."""

from threading import RLock

from src.engine.core.i_messaging_service import IMessagingService
from src.robot_systems.paint.contracts.events.paint_head_check_events import (
    PaintHeadCheckStatusEvent,
    PaintHeadCheckTopics,
    PaintHeadFeedbackMode,
)
from src.robot_systems.paint.contracts.paint_head_check.errors import HeadInspectionFailure
from src.robot_systems.paint.contracts.paint_head_check.interfaces import IPaintHeadCheckObserver
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckContext,
    PaintHeadObservation,
)
from src.robot_systems.paint.contracts.paint_head_check.results import HeadCheckEvidence


class DashboardPaintHeadCheckObserver(IPaintHeadCheckObserver):
    """Replay status when the dashboard opens; unsubscribe on system shutdown."""

    def __init__(self, messaging: IMessagingService) -> None:
        self._messaging = messaging
        self._lock = RLock()
        self._latest: PaintHeadCheckStatusEvent | None = None
        self._revision = 0
        self._subscribed = False

    def start(self) -> None:
        with self._lock:
            if not self._subscribed:
                self._messaging.subscribe(
                    PaintHeadCheckTopics.REQUEST_STATUS, self._on_status_requested
                )
                self._subscribed = True

    def stop(self) -> None:
        with self._lock:
            if self._subscribed:
                self._messaging.unsubscribe(
                    PaintHeadCheckTopics.REQUEST_STATUS, self._on_status_requested
                )
                self._subscribed = False

    def inspection_started(self, context: HeadCheckContext) -> None:
        self._publish(None)

    def observation_received(
        self, observation: PaintHeadObservation, context: HeadCheckContext
    ) -> None:
        self._publish(observation)

    def inspection_failed(self, failure: HeadInspectionFailure, context: HeadCheckContext) -> None:
        self._publish(failure, context.previous_observation)

    def guidance_started(self) -> None:
        self._publish(None, mode=PaintHeadFeedbackMode.LIVE_GUIDANCE)

    def guidance_observation(self, observation: PaintHeadObservation) -> None:
        self._publish(observation, mode=PaintHeadFeedbackMode.LIVE_GUIDANCE)

    def guidance_failed(self, failure: HeadInspectionFailure) -> None:
        # No previous pose: a lost stream must not leave stale correction arrows visible.
        self._publish(failure, mode=PaintHeadFeedbackMode.LIVE_GUIDANCE)

    def guidance_ended(self, failure: HeadInspectionFailure | None = None) -> None:
        self._publish(failure, mode=PaintHeadFeedbackMode.GUIDANCE_ENDED)

    def _publish(
        self,
        evidence: HeadCheckEvidence | None,
        previous_observation: PaintHeadObservation | None = None,
        *,
        mode: PaintHeadFeedbackMode = PaintHeadFeedbackMode.CHECK,
    ) -> None:
        with self._lock:
            self._revision += 1
            self._latest = PaintHeadCheckStatusEvent(
                self._revision,
                evidence,
                previous_observation,
                mode,
            )
            self._messaging.publish(PaintHeadCheckTopics.STATUS, self._latest)

    def _on_status_requested(self, request: object) -> None:
        with self._lock:
            if self._latest is not None:
                self._messaging.publish(PaintHeadCheckTopics.STATUS, self._latest)
