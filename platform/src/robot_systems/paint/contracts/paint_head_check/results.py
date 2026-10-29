"""Explicit result variants for observations, policy decisions and workflow gates."""

from dataclasses import dataclass

from .errors import HeadInspectionFailure
from .models import PaintHeadObservation


@dataclass(frozen=True, slots=True)
class ObservationReceived:
    observation: PaintHeadObservation


@dataclass(frozen=True, slots=True)
class ObservationFailed:
    failure: HeadInspectionFailure


@dataclass(frozen=True, slots=True)
class ObservationCancelled:
    """Cancellation is neither an unknown head nor an inspection failure."""


@dataclass(frozen=True, slots=True)
class ObservationPaused:
    """External pause interrupted acquisition; no head classification is implied."""


type HeadObservationResult = (
    ObservationReceived | ObservationFailed | ObservationCancelled | ObservationPaused
)


@dataclass(frozen=True, slots=True)
class ContinuePainting:
    """The reaction policy accepts the observation or known failure."""


@dataclass(frozen=True, slots=True)
class ReportOnly:
    """Report without blocking production; optionally finish temporal confirmation."""

    await_confirmation: bool


@dataclass(frozen=True, slots=True)
class RetryObservation:
    """Request a new distinct frame within the existing inspection deadline."""


@dataclass(frozen=True, slots=True)
class PauseForOperator:
    """Hold at the inspection checkpoint until the operator resumes."""


@dataclass(frozen=True, slots=True)
class RejectPainting:
    """The triggering observation/failure must be retained by the coordinator."""


@dataclass(frozen=True, slots=True)
class StopPainting:
    """End this run at the checkpoint; a new Start may inspect again."""


type HeadReactionDecision = (
    ContinuePainting
    | ReportOnly
    | RetryObservation
    | PauseForOperator
    | StopPainting
    | RejectPainting
)


type HeadCheckEvidence = PaintHeadObservation | HeadInspectionFailure


@dataclass(frozen=True, slots=True)
class HeadCheckPassed:
    evidence: HeadCheckEvidence


@dataclass(frozen=True, slots=True)
class HeadCheckSkipped:
    """The selected scheduling policy does not require this check."""


@dataclass(frozen=True, slots=True)
class HeadCheckRejected:
    evidence: HeadCheckEvidence


@dataclass(frozen=True, slots=True)
class HeadCheckStopped:
    evidence: HeadCheckEvidence
    previous_observation: PaintHeadObservation | None = None

    @property
    def last_observation(self) -> PaintHeadObservation | None:
        if isinstance(self.evidence, PaintHeadObservation):
            return self.evidence
        return self.previous_observation


@dataclass(frozen=True, slots=True)
class HeadCheckCancelled:
    """Process cancellation interrupted the checkpoint."""


@dataclass(frozen=True, slots=True)
class HeadCheckPaused:
    """The checkpoint remains due; resume must acquire fresh evidence."""

    evidence: HeadCheckEvidence | None


type HeadCheckResult = (
    HeadCheckPassed
    | HeadCheckSkipped
    | HeadCheckRejected
    | HeadCheckStopped
    | HeadCheckCancelled
    | HeadCheckPaused
)


@dataclass(frozen=True, slots=True)
class HeadInspectionPositionReached:
    """The requested inspection move completed at its stopped endpoint."""


@dataclass(frozen=True, slots=True)
class HeadInspectionMoveFailed:
    failure: HeadInspectionFailure


@dataclass(frozen=True, slots=True)
class HeadInspectionMoveCancelled:
    """The owning run cancelled the inspection move."""


@dataclass(frozen=True, slots=True)
class HeadInspectionMovePaused:
    """Resume must complete/revalidate positioning before collecting evidence."""


type HeadInspectionMoveResult = (
    HeadInspectionPositionReached
    | HeadInspectionMoveFailed
    | HeadInspectionMoveCancelled
    | HeadInspectionMovePaused
)
