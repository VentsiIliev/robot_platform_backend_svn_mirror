"""Live operator feedback after a stopped misalignment; never authorize painting."""

import logging
from collections.abc import Callable
from dataclasses import dataclass
from threading import Event, RLock, Thread, current_thread
from time import monotonic
from typing import Protocol, assert_never

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadCheckError,
    PaintHeadProcessingError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl,
    IPaintHeadAlignmentGuidance,
    IPaintHeadInspector,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionTarget,
    HeadInspectionWindow,
    PaintHeadObservation,
    PaintHeadObservationReason,
    PaintHeadState,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    ObservationCancelled,
    ObservationFailed,
    ObservationPaused,
    ObservationReceived,
)


class IHeadGuidancePositionGuard(Protocol):
    def check(self, target: HeadInspectionTarget) -> HeadInspectionFailure | None: ...


class IHeadGuidanceObserver(Protocol):
    def guidance_started(self) -> None: ...
    def guidance_observation(self, observation: PaintHeadObservation) -> None: ...
    def guidance_failed(self, failure: HeadInspectionFailure) -> None: ...
    def guidance_ended(self, failure: HeadInspectionFailure | None = None) -> None: ...


@dataclass(frozen=True, slots=True)
class _GuidanceRequest:
    target: HeadInspectionTarget
    max_frame_age_seconds: float
    cancelled: Event


class _GuidanceControl(IHeadInspectionControl):
    def __init__(self, cancelled: Event) -> None:
        self._cancelled = cancelled

    def should_stop(self) -> bool:
        return self._cancelled.is_set()

    def pause_requested(self) -> bool:
        return False


class PaintHeadLiveGuidance(IPaintHeadAlignmentGuidance):
    """Each session owns its inspector; cancellation revokes even in-flight results.

    The process STOPPED event admits a pending offer. Hardware cleanup must finish
    before acquisition starts. Neither alignment nor any other observed state can
    resume painting, complete a scheduled check, or invoke a reaction policy.
    """

    def __init__(
        self,
        inspector_factory: Callable[[], IPaintHeadInspector],
        position_guard: IHeadGuidancePositionGuard,
        observer: IHeadGuidanceObserver,
        ready: Callable[[], bool],
        *,
        logger: logging.Logger,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._inspector_factory = inspector_factory
        self._guard = position_guard
        self._observer = observer
        self._ready = ready
        self._logger = logger
        self._clock = clock
        self._lock = RLock()
        self._pending: _GuidanceRequest | None = None
        self._active: _GuidanceRequest | None = None
        self._workers: set[Thread] = set()
        self._closed = False

    def offer(self, target: HeadInspectionTarget, max_frame_age_seconds: float) -> None:
        # Reuse the validated timing contract without inventing a guidance timeout.
        HeadInspectionWindow(0.0, max_frame_age_seconds, max_frame_age_seconds)
        with self._lock:
            self.cancel()
            if not self._closed:
                self._pending = _GuidanceRequest(target, max_frame_age_seconds, Event())

    def start_pending(self) -> None:
        """Non-blocking process lifecycle callback; camera work stays on the worker."""
        with self._lock:
            request = self._pending
            if request is None or self._closed:
                return
            self._pending = None
            self._active = request
            worker = Thread(
                target=self._run, args=(request,), name="PaintHeadLiveGuidance", daemon=True
            )
            self._workers.add(worker)
            worker.start()

    def cancel(self) -> None:
        with self._lock:
            if self._pending is not None:
                self._pending.cancelled.set()
                self._pending = None
            if self._active is not None:
                self._active.cancelled.set()
                self._active = None
                self._observer.guidance_ended()

    def close(self) -> None:
        """Join outside the process lock before camera/broker dependencies close."""
        with self._lock:
            self._closed = True
            self.cancel()
            workers = tuple(self._workers)
        for worker in workers:
            worker.join(timeout=2.0)
        if any(worker.is_alive() for worker in workers):
            raise PaintHeadProcessingError(
                "Live paint-head guidance did not shut down within two seconds"
            )

    def _run(self, request: _GuidanceRequest) -> None:
        inspector: IPaintHeadInspector | None = None
        terminal_failure: HeadInspectionFailure | None = None
        last_transition: (
            tuple[PaintHeadState, PaintHeadState, PaintHeadObservationReason, bool] | None
        ) = None
        try:
            while not request.cancelled.is_set() and not self._ready():
                request.cancelled.wait(0.05)
            if request.cancelled.is_set():
                return
            terminal_failure = self._guard.check(request.target)
            if terminal_failure is not None:
                return
            inspector = self._inspector_factory()
            inspector.begin_inspection()
            started = self._clock()
            control = _GuidanceControl(request.cancelled)
            with self._lock:
                if self._active is not request:
                    return
                self._observer.guidance_started()
            while not request.cancelled.is_set():
                terminal_failure = self._guard.check(request.target)
                if terminal_failure is not None:
                    break
                window = HeadInspectionWindow(
                    started,
                    self._clock() + request.max_frame_age_seconds,
                    request.max_frame_age_seconds,
                )
                result = inspector.next_observation(window, control)
                terminal_failure = self._guard.check(request.target)
                if terminal_failure is not None:
                    break
                with self._lock:
                    if self._active is not request or request.cancelled.is_set():
                        break
                    match result:
                        case ObservationReceived(observation):
                            transition = (
                                observation.state,
                                observation.observed_state,
                                observation.reason,
                                observation.held_warning,
                            )
                            if transition != last_transition:
                                self._logger.info(
                                    "Paint-head live feedback state=%s observed=%s reason=%s held_warning=%s frame=%d",
                                    observation.state.name,
                                    observation.observed_state.name,
                                    observation.reason.name,
                                    observation.held_warning,
                                    observation.frame_sequence,
                                )
                                last_transition = transition
                            self._observer.guidance_observation(observation)
                        case ObservationFailed(failure):
                            # Clear directional feedback during lost/stale frames, then allow recovery.
                            self._observer.guidance_failed(failure)
                        case ObservationCancelled() | ObservationPaused():
                            break
                        case _ as unreachable:
                            assert_never(unreachable)
                request.cancelled.wait(0.05)
        except PaintHeadCheckError as error:
            terminal_failure = error.failure
        except Exception:
            self._logger.exception("Live paint-head guidance failed")
            terminal_failure = HeadInspectionFailure(
                HeadInspectionFailureCode.PROCESSING_FAILED,
                "Live paint-head guidance failed; check the application log",
            )
        finally:
            try:
                if inspector is not None:
                    inspector.end_inspection()
            finally:
                with self._lock:
                    if self._active is request:
                        self._active = None
                        self._observer.guidance_ended(terminal_failure)
                    self._workers.discard(current_thread())
