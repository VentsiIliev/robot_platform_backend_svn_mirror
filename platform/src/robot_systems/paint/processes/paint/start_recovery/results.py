"""Typed outcomes for start/restart recovery."""
from dataclasses import dataclass
from enum import StrEnum

from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome
from .errors import StartRecoveryFailure


class StartRecoveryOutcome(StrEnum):
    NOT_REQUIRED = "not_required"
    RECOVERED = "recovered"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass(frozen=True)
class StartRecoveryResult:
    outcome: StartRecoveryOutcome
    failure: StartRecoveryFailure | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, StartRecoveryOutcome):
            raise TypeError("Recovery outcome must be a StartRecoveryOutcome")
        if (self.outcome is StartRecoveryOutcome.FAILED) != (self.failure is not None):
            raise ValueError("Only failed recovery outcomes must carry a failure")

    @property
    def succeeded(self) -> bool:
        return self.outcome in (StartRecoveryOutcome.NOT_REQUIRED, StartRecoveryOutcome.RECOVERED)

    def to_operation_result(self) -> PaintOperationResult:
        """Adapt to the paint workflow while retaining the typed recovery failure."""
        if self.failure is not None:
            return PaintOperationResult(PaintOutcome.FAILED, self.failure.message, self.failure)
        if self.outcome is StartRecoveryOutcome.CANCELLED:
            return PaintOperationResult(PaintOutcome.CANCELLED, "Start recovery cancelled")
        return PaintOperationResult(PaintOutcome.COMPLETED, "")
