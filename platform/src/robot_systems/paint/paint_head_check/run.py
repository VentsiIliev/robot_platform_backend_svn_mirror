"""Compose one run's schedule, strict positioning and bounded inspections."""

from collections.abc import Callable
from time import monotonic
from typing import assert_never

from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadContractError,
    PaintHeadInspectionTargetError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionControl,
    IHeadInspectionMotion,
    IHeadInspectionRetryPosition,
    IHeadInspectionTargetProvider,
    IPaintHeadAlignmentGuidance,
    IPaintHeadCheckObserver,
    IPaintHeadCheckRun,
    IPaintHeadCheckRunFactory,
    IPaintHeadInspector,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadCheckContext,
    HeadCheckOperatingMode,
    HeadInspectionTarget,
    HeadInspectionWindow,
    PaintHeadCheckConfiguration,
    PaintHeadState,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadCheckCancelled,
    HeadCheckPassed,
    HeadCheckPaused,
    HeadCheckRejected,
    HeadCheckResult,
    HeadCheckSkipped,
    HeadCheckStopped,
    HeadInspectionMoveCancelled,
    HeadInspectionMoveFailed,
    HeadInspectionMovePaused,
    HeadInspectionMoveResult,
    HeadInspectionPositionReached,
)

from .coordinator import PaintHeadCheckCoordinator
from .policy_registry import PaintHeadCheckPolicyRegistry, build_head_check_policy_registry
from .reactions import ConfiguredPaintHeadReactionPolicy
from .scheduling import DisabledHeadCheckPolicy
from .session import PaintHeadCheckSession

type PolicyRegistryFactory = Callable[[int], PaintHeadCheckPolicyRegistry]


class PaintHeadCheckRun(IPaintHeadCheckRun):
    def __init__(
        self,
        configuration: PaintHeadCheckConfiguration,
        session: PaintHeadCheckSession,
        coordinator: PaintHeadCheckCoordinator,
        target_provider: IHeadInspectionTargetProvider,
        motion: IHeadInspectionMotion,
        observer: IPaintHeadCheckObserver,
        *,
        retry_position: IHeadInspectionRetryPosition | None = None,
        guidance: IPaintHeadAlignmentGuidance | None = None,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._configuration = configuration
        self._session = session
        self._coordinator = coordinator
        self._target_provider = target_provider
        self._motion = motion
        self._observer = observer
        self._clock = clock
        self._retry_position = retry_position
        self._guidance = guidance
        self._prepared_retry_target: HeadInspectionTarget | None = None
        self._stopped_target: HeadInspectionTarget | None = None

    def prepare_retry_in_place(self) -> bool:
        self._prepared_retry_target = None
        if self._retry_position is None or not self.check_before_cycle_due():
            return False
        target = self._target_provider.resolve()
        if self._retry_position.try_reuse(target):
            self._prepared_retry_target = target
            return True
        return False

    def retain_retry_position(self) -> None:
        if self._stopped_target is None:
            raise PaintHeadContractError("Only a stopped inspection may retain its retry position")
        if self._retry_position is not None:
            self._retry_position.remember_stop(self._stopped_target)

    def check_before_cycle_due(self) -> bool:
        return self._session.check_before_cycle_due()

    def inspection_target(self) -> HeadInspectionTarget:
        return self._target_provider.resolve()

    def record_completed_cycle(self) -> None:
        self._session.record_completed_cycle()

    def check_before_cycle(self, control: IHeadInspectionControl) -> HeadCheckResult:
        if not self.check_before_cycle_due():
            return HeadCheckSkipped()
        return self._inspect(control)

    def _inspect(self, control: IHeadInspectionControl) -> HeadCheckResult:
        if control.should_stop():
            return HeadCheckCancelled()
        if control.pause_requested():
            return HeadCheckPaused(None)
        try:
            target = self._target_provider.resolve()
        except PaintHeadInspectionTargetError as error:
            if self._retry_position is not None:
                self._retry_position.invalidate()
            self._observer.inspection_failed(
                error.failure,
                HeadCheckContext(self._session.progress, 1, 0.0, None),
            )
            # Mandatory position validity cannot be overridden by reporting-only reactions.
            return HeadCheckRejected(error.failure)

        self._stopped_target = None
        moved: HeadInspectionMoveResult
        if self._prepared_retry_target is not None:
            reuse_target = self._prepared_retry_target
            self._prepared_retry_target = None
            if (
                target == reuse_target
                and self._retry_position is not None
                and self._retry_position.try_reuse(target)
            ):
                moved = HeadInspectionPositionReached()
            else:
                if self._retry_position is not None:
                    self._retry_position.invalidate()
                moved = HeadInspectionMoveFailed(
                    HeadInspectionFailure(
                        HeadInspectionFailureCode.INSPECTION_POSITION_CHANGED,
                        "Robot pose or inspection target changed while preparing an in-place retry",
                    )
                )
        else:
            if self._retry_position is not None:
                self._retry_position.invalidate()
            moved = self._motion.move_to_inspection(target, control)
        match moved:
            case HeadInspectionMoveCancelled():
                return HeadCheckCancelled()
            case HeadInspectionMovePaused():
                return HeadCheckPaused(None)
            case HeadInspectionMoveFailed(failure):
                self._observer.inspection_failed(
                    failure,
                    HeadCheckContext(self._session.progress, 1, 0.0, None),
                )
                return HeadCheckRejected(failure)
            case HeadInspectionPositionReached():
                pass
            case _ as unreachable:
                assert_never(unreachable)

        started = self._clock()
        self._observer.inspection_started(
            HeadCheckContext(self._session.progress, 1, 0.0, None),
        )
        window = HeadInspectionWindow(
            started_at=started,
            deadline_at=started + self._configuration.timeout_seconds,
            max_frame_age_seconds=self._configuration.timeout_seconds,
        )
        result = self._coordinator.inspect(self._session.progress, window, control)
        if isinstance(result, HeadCheckPassed):
            self._session.mark_check_complete()
            if self._retry_position is not None:
                self._retry_position.invalidate()
        elif isinstance(result, HeadCheckStopped):
            self._stopped_target = target
            last = result.last_observation
            if (
                self._guidance is not None
                and last is not None
                and last.state is PaintHeadState.MISALIGNED
            ):
                self._guidance.offer(target, self._configuration.timeout_seconds)
        elif self._retry_position is not None:
            self._retry_position.invalidate()
        return result


class PaintHeadCheckRunFactory(IPaintHeadCheckRunFactory):
    def __init__(
        self,
        inspector: IPaintHeadInspector,
        target_provider: IHeadInspectionTargetProvider,
        motion: IHeadInspectionMotion,
        observer: IPaintHeadCheckObserver,
        *,
        retry_position: IHeadInspectionRetryPosition | None = None,
        guidance: IPaintHeadAlignmentGuidance | None = None,
        registry_factory: PolicyRegistryFactory = build_head_check_policy_registry,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        self._inspector = inspector
        self._target_provider = target_provider
        self._motion = motion
        self._observer = observer
        self._registry_factory = registry_factory
        self._clock = clock
        self._retry_position = retry_position
        self._guidance = guidance

    def create_run(
        self,
        configuration: PaintHeadCheckConfiguration,
        mode: HeadCheckOperatingMode,
    ) -> IPaintHeadCheckRun:
        if self._guidance is not None:
            self._guidance.cancel()
        enabled = configuration.enabled and mode is not HeadCheckOperatingMode.PICKUP_ONLY
        if not enabled and self._retry_position is not None:
            self._retry_position.invalidate()
        policy = (
            self._registry_factory(configuration.interval_cycles).create(configuration.policy_id)
            if enabled
            else DisabledHeadCheckPolicy()
        )
        reactions = ConfiguredPaintHeadReactionPolicy(
            configuration.state_reactions,
            failure_action=configuration.failure_action,
            timeout_action=configuration.timeout_action,
            report_until_confirmed=configuration.report_until_confirmed,
        )
        return PaintHeadCheckRun(
            configuration,
            PaintHeadCheckSession(policy),
            PaintHeadCheckCoordinator(
                self._inspector,
                reactions,
                self._observer,
                clock=self._clock,
            ),
            self._target_provider,
            self._motion,
            self._observer,
            retry_position=self._retry_position,
            guidance=self._guidance,
            clock=self._clock,
        )
