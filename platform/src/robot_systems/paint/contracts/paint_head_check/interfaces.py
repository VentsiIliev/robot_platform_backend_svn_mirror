"""Policy boundaries depend only on paint-owned values and the standard library."""

from abc import ABC, abstractmethod

from .errors import HeadInspectionFailure
from .models import (
    HeadCheckContext,
    HeadCheckOperatingMode,
    HeadCheckProgress,
    HeadCheckScheduleDecision,
    HeadInspectionTarget,
    HeadInspectionWindow,
    PaintHeadCheckConfiguration,
    PaintHeadObservation,
)
from .results import (
    HeadCheckResult,
    HeadInspectionMoveResult,
    HeadObservationResult,
    HeadReactionDecision,
)


class IHeadInspectionControl(ABC):
    @abstractmethod
    def should_stop(self) -> bool:
        """Whether the owning run has been cancelled."""

    @abstractmethod
    def pause_requested(self) -> bool:
        """Whether acquisition should return control to the paused workflow."""


class IPaintHeadInspector(ABC):
    """Observation port; neither images nor backend types cross this boundary."""

    @abstractmethod
    def begin_inspection(self) -> None:
        """Reset confirmation and begin receiving new camera observations."""

    @abstractmethod
    def next_observation(
        self,
        window: HeadInspectionWindow,
        control: IHeadInspectionControl,
    ) -> HeadObservationResult:
        """Return a distinct fresh observation or a typed interruption/failure."""

    @abstractmethod
    def end_inspection(self) -> None:
        """Release subscriptions and buffered frames on every exit path."""


class IHeadInspectionTargetProvider(ABC):
    @abstractmethod
    def resolve(self) -> HeadInspectionTarget:
        """Resolve the mandatory taught target or raise PaintHeadInspectionTargetError."""


class IHeadInspectionMotion(ABC):
    @abstractmethod
    def move_to_inspection(
        self,
        target: HeadInspectionTarget,
        control: IHeadInspectionControl,
    ) -> HeadInspectionMoveResult:
        """Reach the explicitly validated stopped pose, or report a typed interruption."""


class IHeadInspectionRetryPosition(ABC):
    @abstractmethod
    def remember_stop(self, target: HeadInspectionTarget) -> None:
        """Retain a freshly verified position after a prepared startup stops inspection."""

    @abstractmethod
    def try_reuse(self, target: HeadInspectionTarget) -> bool:
        """Reverify the retained target using fresh feedback; restore its observed area."""

    @abstractmethod
    def invalidate(self) -> None:
        """Discard retained position without hardware I/O."""


class IPaintHeadAlignmentGuidance(ABC):
    @abstractmethod
    def offer(self, target: HeadInspectionTarget, max_frame_age_seconds: float) -> None:
        """Arm guidance after a stopped misalignment; do not begin before process STOPPED."""

    @abstractmethod
    def cancel(self) -> None:
        """Revoke pending/active guidance and late publications without blocking on I/O."""


class IPaintHeadCheckRun(ABC):
    def close(self) -> None:
        """Release run-scoped resources; pure scheduling implementations have none."""

    @abstractmethod
    def prepare_retry_in_place(self) -> bool:
        """Verify whether the previous inspection stop still satisfies startup positioning."""

    @abstractmethod
    def retain_retry_position(self) -> None:
        """Remember this inspection stop after the workflow confirms startup was prepared."""

    @abstractmethod
    def inspection_target(self) -> HeadInspectionTarget:
        """Validate the configured inspection position before cycle startup motion."""

    @abstractmethod
    def check_before_cycle_due(self) -> bool: ...

    @abstractmethod
    def record_completed_cycle(self) -> None: ...

    @abstractmethod
    def check_before_cycle(self, control: IHeadInspectionControl) -> HeadCheckResult: ...


class IPaintHeadCheckRunFactory(ABC):
    @abstractmethod
    def create_run(
        self,
        configuration: PaintHeadCheckConfiguration,
        mode: HeadCheckOperatingMode,
    ) -> IPaintHeadCheckRun:
        """Create isolated progress for a newly accepted Start, without moving hardware."""


class IPaintHeadCheckPolicy(ABC):
    """Choose when inspection is due; no I/O or mutable run ownership."""

    @abstractmethod
    def evaluate(self, progress: HeadCheckProgress) -> HeadCheckScheduleDecision:
        """Decide whether the next painted workpiece requires a check."""


class IPaintHeadReactionPolicy(ABC):
    """Choose responses; execution and deadlines belong to the coordinator."""

    @abstractmethod
    def on_observation(
        self,
        observation: PaintHeadObservation,
        context: HeadCheckContext,
    ) -> HeadReactionDecision:
        """Respond to each distinct observation during an active inspection."""

    @abstractmethod
    def on_failure(
        self,
        failure: HeadInspectionFailure,
        context: HeadCheckContext,
    ) -> HeadReactionDecision:
        """Respond to a known inspection failure, separately from head state."""


class IPaintHeadCheckObserver(ABC):
    """Reporting side effects stay outside pure scheduling/reaction policies."""

    @abstractmethod
    def inspection_started(self, context: HeadCheckContext) -> None:
        """Replace the previous result when a fresh inspection begins."""

    @abstractmethod
    def observation_received(
        self,
        observation: PaintHeadObservation,
        context: HeadCheckContext,
    ) -> None:
        """Report a received state without changing its policy decision."""

    @abstractmethod
    def inspection_failed(
        self,
        failure: HeadInspectionFailure,
        context: HeadCheckContext,
    ) -> None:
        """Report a known inspection failure without reclassifying head state."""
