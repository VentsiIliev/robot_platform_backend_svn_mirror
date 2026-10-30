"""Pin one selected calibration per production run and transfer ownership to guidance."""

from collections.abc import Callable
from functools import partial
from threading import Lock

from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    PaintHeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_calibration.interfaces import (
    IRevisionLease,
    IRuntimeCalibrationProvider,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import CalibrationDefinition
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    PaintHeadCalibrationError as HeadCalibrationError,
)
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    PaintHeadConfigurationError,
    PaintHeadContractError,
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
    HeadCheckOperatingMode,
    HeadInspectionTarget,
    HeadInspectionWindow,
    PaintHeadCheckConfiguration,
)
from src.robot_systems.paint.contracts.paint_head_check.results import (
    HeadCheckResult,
    HeadObservationResult,
)
from src.robot_systems.paint.paint_head_check.live_guidance import PaintHeadLiveGuidance
from src.robot_systems.paint.paint_head_check.run import PaintHeadCheckRunFactory

type SnapshotInspectorFactory = Callable[[CalibrationDefinition], IPaintHeadInspector]


class _UnusedInspector(IPaintHeadInspector):
    def begin_inspection(self) -> None:
        raise PaintHeadConfigurationError("Disabled checks have no bound calibration")

    def next_observation(
        self, window: HeadInspectionWindow, control: IHeadInspectionControl
    ) -> HeadObservationResult:
        raise PaintHeadConfigurationError("Disabled checks cannot acquire observations")

    def end_inspection(self) -> None:
        return None


class _RunGuidance(IPaintHeadAlignmentGuidance):
    def __init__(
        self,
        guidance: PaintHeadLiveGuidance,
        lease: IRevisionLease,
        inspector_factory: SnapshotInspectorFactory,
    ) -> None:
        self._guidance = guidance
        self._lease = lease
        self._inspector_factory = inspector_factory

    def cancel(self) -> None:
        self._guidance.cancel()

    def offer(self, target: HeadInspectionTarget, max_frame_age_seconds: float) -> None:
        lease = self._lease.clone()
        try:
            self._guidance.offer_with_inspector(
                target,
                max_frame_age_seconds,
                partial(self._inspector_factory, lease.definition),
                on_finished=lease.close,
            )
        except Exception:
            lease.close()
            raise


class CalibratedHeadCheckRun(IPaintHeadCheckRun):
    """Delegate policies/results unchanged; own and release the run's calibration."""

    def __init__(
        self, run: IPaintHeadCheckRun, inspector: IPaintHeadInspector, lease: IRevisionLease
    ) -> None:
        self._inner: IPaintHeadCheckRun | None = run
        self._inspector: IPaintHeadInspector | None = inspector
        self._lease = lease
        self._lock = Lock()

    def _run(self) -> IPaintHeadCheckRun:
        if self._inner is None:
            raise PaintHeadContractError("This head-check run has already released its calibration")
        return self._inner

    def prepare_retry_in_place(self) -> bool:
        return self._run().prepare_retry_in_place()

    def retain_retry_position(self) -> None:
        self._run().retain_retry_position()

    def inspection_target(self) -> HeadInspectionTarget:
        return self._run().inspection_target()

    def check_before_cycle_due(self) -> bool:
        return self._run().check_before_cycle_due()

    def record_completed_cycle(self) -> None:
        self._run().record_completed_cycle()

    def check_before_cycle(self, control: IHeadInspectionControl) -> HeadCheckResult:
        return self._run().check_before_cycle(control)

    def close(self) -> None:
        with self._lock:
            if self._inner is None:
                return
            try:
                self._inner.close()
            finally:
                try:
                    if self._inspector is not None:
                        self._inspector.end_inspection()
                finally:
                    self._inner = None
                    self._inspector = None
                    self._lease.close()


class CalibratedHeadCheckRunFactory(IPaintHeadCheckRunFactory):
    def __init__(
        self,
        calibrations: IRuntimeCalibrationProvider,
        inspector_factory: SnapshotInspectorFactory,
        target_provider: IHeadInspectionTargetProvider,
        motion: IHeadInspectionMotion,
        observer: IPaintHeadCheckObserver,
        *,
        retry_position: IHeadInspectionRetryPosition | None = None,
        guidance: PaintHeadLiveGuidance | None = None,
    ) -> None:
        self._calibrations = calibrations
        self._inspector_factory = inspector_factory
        self._target_provider = target_provider
        self._motion = motion
        self._observer = observer
        self._retry_position = retry_position
        self._guidance = guidance

    def _factory(
        self, inspector: IPaintHeadInspector, guidance: IPaintHeadAlignmentGuidance | None
    ) -> PaintHeadCheckRunFactory:
        return PaintHeadCheckRunFactory(
            inspector,
            self._target_provider,
            self._motion,
            self._observer,
            retry_position=self._retry_position,
            guidance=guidance,
        )

    def create_run(
        self,
        configuration: PaintHeadCheckConfiguration,
        mode: HeadCheckOperatingMode,
    ) -> IPaintHeadCheckRun:
        if self._guidance is not None:
            self._guidance.cancel()
        if not configuration.enabled or mode is HeadCheckOperatingMode.PICKUP_ONLY:
            return self._factory(_UnusedInspector(), None).create_run(configuration, mode)
        try:
            lease = self._calibrations.acquire_selected()
        except PaintHeadCalibrationError as error:
            raise HeadCalibrationError(error.failure.detail) from error
        inspector: IPaintHeadInspector | None = None
        try:
            # Preparing the immutable detector here keeps reference I/O outside
            # startup motion, Qt and the bounded camera-acquisition window.
            inspector = self._inspector_factory(lease.definition)
            guidance = (
                None
                if self._guidance is None
                else _RunGuidance(self._guidance, lease, self._inspector_factory)
            )
            run = self._factory(inspector, guidance).create_run(configuration, mode)
            return CalibratedHeadCheckRun(run, inspector, lease)
        except PaintHeadCalibrationError as error:
            lease.close()
            if inspector is not None:
                inspector.end_inspection()
            raise HeadCalibrationError(error.failure.detail) from error
        except Exception:
            lease.close()
            if inspector is not None:
                inspector.end_inspection()
            raise
