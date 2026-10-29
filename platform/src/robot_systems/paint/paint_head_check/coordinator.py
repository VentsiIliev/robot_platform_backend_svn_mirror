"""Execute one bounded observation session through detector-independent ports."""

from collections.abc import Callable
from threading import Event
from time import monotonic
from typing import assert_never

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadCheckError,
    PaintHeadConfigurationError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl,
    IPaintHeadCheckObserver,
    IPaintHeadInspector,
    IPaintHeadReactionPolicy,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckContext,
    HeadCheckProgress,
    HeadInspectionWindow,
    PaintHeadObservation,
    PaintHeadState,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    ContinuePainting,
    HeadCheckCancelled,
    HeadCheckEvidence,
    HeadCheckPassed,
    HeadCheckPaused,
    HeadCheckRejected,
    HeadCheckResult,
    HeadCheckStopped,
    HeadObservationResult,
    ObservationCancelled,
    ObservationFailed,
    ObservationPaused,
    ObservationReceived,
    PauseForOperator,
    RejectPainting,
    ReportOnly,
    RetryObservation,
    StopPainting,
)


class PaintHeadCheckCoordinator:
    """Own acquisition, deadlines and decisions; callers own motion and scheduling."""

    def __init__(
        self,
        inspector: IPaintHeadInspector,
        reaction_policy: IPaintHeadReactionPolicy,
        observer: IPaintHeadCheckObserver,
        *,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._inspector = inspector
        self._reaction_policy = reaction_policy
        self._observer = observer
        self._clock = clock

    def inspect(
        self,
        progress: HeadCheckProgress,
        window: HeadInspectionWindow,
        control: IHeadInspectionControl,
    ) -> HeadCheckResult:
        active = False
        attempt = 0
        previous: PaintHeadObservation | None = None
        try:
            while True:
                if control.should_stop():
                    return HeadCheckCancelled()
                if control.pause_requested():
                    return HeadCheckPaused(None)
                attempt += 1
                context = HeadCheckContext(
                    progress,
                    attempt,
                    max(0.0, self._clock() - window.started_at),
                    previous,
                )
                received: HeadObservationResult
                if self._clock() >= window.deadline_at:
                    received = ObservationFailed(
                        HeadInspectionFailure(
                            HeadInspectionFailureCode.TIMEOUT,
                            "Paint-head inspection reached its configured time limit",
                        )
                    )
                else:
                    try:
                        if not active:
                            self._inspector.begin_inspection()
                            active = True
                        received = self._inspector.next_observation(window, control)
                    except PaintHeadCheckError as error:
                        received = ObservationFailed(error.failure)

                if control.should_stop():
                    return HeadCheckCancelled()
                if control.pause_requested():
                    return HeadCheckPaused(None)
                if self._clock() >= window.deadline_at:
                    received = ObservationFailed(
                        HeadInspectionFailure(
                            HeadInspectionFailureCode.TIMEOUT,
                            "Paint-head inspection reached its configured time limit",
                        )
                    )

                evidence: HeadCheckEvidence
                match received:
                    case ObservationCancelled():
                        return HeadCheckCancelled()
                    case ObservationPaused():
                        return HeadCheckPaused(None)
                    case ObservationReceived(observation):
                        evidence = observation
                        self._observer.observation_received(observation, context)
                        decision = self._reaction_policy.on_observation(observation, context)
                        previous = observation
                    case ObservationFailed(failure):
                        evidence = failure
                        self._observer.inspection_failed(failure, context)
                        decision = self._reaction_policy.on_failure(failure, context)
                    case _ as unexpected_observation:
                        assert_never(unexpected_observation)

                match decision:
                    case ContinuePainting():
                        return HeadCheckPassed(evidence)
                    case ReportOnly(await_confirmation):
                        if not (
                            await_confirmation
                            and isinstance(evidence, PaintHeadObservation)
                            and evidence.state is PaintHeadState.UNKNOWN
                        ):
                            return HeadCheckPassed(evidence)
                    case RejectPainting():
                        return HeadCheckRejected(evidence)
                    case StopPainting():
                        return HeadCheckStopped(
                            evidence,
                            previous if isinstance(evidence, HeadInspectionFailure) else None,
                        )
                    case PauseForOperator():
                        return HeadCheckPaused(evidence)
                    case RetryObservation():
                        if (
                            isinstance(evidence, HeadInspectionFailure)
                            and evidence.code is HeadInspectionFailureCode.TIMEOUT
                        ):
                            raise PaintHeadConfigurationError(
                                "A timeout reaction cannot retry an expired inspection window",
                            )
                    case _ as unexpected_decision:
                        assert_never(unexpected_decision)

                if isinstance(evidence, HeadInspectionFailure):
                    # Pace retries when initialization/backend failures arrive without a frame.
                    Event().wait(timeout=min(0.05, max(0.0, window.deadline_at - self._clock())))
        finally:
            self._inspector.end_inspection()
