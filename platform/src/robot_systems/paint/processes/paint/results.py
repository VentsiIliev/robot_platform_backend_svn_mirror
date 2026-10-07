"""Paint operation outcomes. Messages describe outcomes; codes drive decisions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Generic, TypeVar


class PaintFailureCode(StrEnum):
    UNAVAILABLE = "unavailable"
    INVALID_CONFIGURATION = "invalid_configuration"
    PLANNING = "planning"
    STORAGE = "storage"
    MATCHING = "matching"
    VACUUM = "vacuum"
    MOTION = "motion"
    INTERNAL = "internal"


@dataclass(frozen=True)
class PaintFailure:
    code: PaintFailureCode
    stage: str
    message: str
    secondary_failures: tuple[PaintFailure, ...] = ()
    backend_code: int | None = None


class PaintOperationError(RuntimeError):
    """Actionable operation failure raised at a lower-level boundary."""

    def __init__(self, failure: PaintFailure) -> None:
        super().__init__(failure.message)
        self.failure = failure


class PaintPlanningError(PaintOperationError):
    def __init__(self, message: str, *, stage: str = "pickup_planning") -> None:
        super().__init__(PaintFailure(PaintFailureCode.PLANNING, stage, message))


class PaintConfigurationError(PaintOperationError, ValueError):
    """Invalid settings; also compatible with existing ValueError validation callers."""

    def __init__(self, message: str, *, stage: str) -> None:
        super().__init__(PaintFailure(PaintFailureCode.INVALID_CONFIGURATION, stage, message))


T = TypeVar("T")


@dataclass(frozen=True)
class Ready(Generic[T]):
    value: T


@dataclass(frozen=True)
class Failed:
    failure: PaintFailure


class PaintOutcome(StrEnum):
    COMPLETED = "completed"
    NO_WORKPIECE = "no_workpiece"
    UNMATCHED = "unmatched"
    CANCELLED = "cancelled"
    NOT_APPLICABLE = "not_applicable"
    TRAY_FULL = "tray_full"
    WORK_AREA_FULL = "work_area_full"
    FAILED = "failed"


@dataclass(frozen=True)
class PaintOperationResult:
    outcome: PaintOutcome
    message: str
    failure: PaintFailure | None = None
    planned_waypoints: int = 0
    stop_reason: PaintOutcome | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, PaintOutcome):
            raise TypeError("Paint outcome must be a PaintOutcome")
        if (self.outcome is PaintOutcome.FAILED) != (self.failure is not None):
            raise ValueError("Only failed outcomes must carry a failure")
        if self.stop_reason is not None and (
            self.outcome is not PaintOutcome.COMPLETED
            or self.stop_reason not in {PaintOutcome.NO_WORKPIECE, PaintOutcome.TRAY_FULL}
        ):
            raise ValueError("Only completed cycles may carry an expected loop stop reason")
        if self.planned_waypoints < 0:
            raise ValueError("Planned waypoint count cannot be negative")

    @classmethod
    def failed(cls, code: PaintFailureCode, stage: str, message: str,
               *, planned_waypoints: int = 0, backend_code: int | None = None) -> PaintOperationResult:
        return cls(PaintOutcome.FAILED, message,
                   PaintFailure(code, stage, message, backend_code=backend_code),
                   planned_waypoints)

    @property
    def completed(self) -> bool:
        return self.outcome is PaintOutcome.COMPLETED

    def as_legacy_pair(self) -> tuple[bool, str]:
        """Adapter for existing editor/service interfaces; internal callers use outcome."""
        return self.completed, self.message

    def as_legacy_triple(self) -> tuple[bool, str, int] | None:
        if self.outcome is PaintOutcome.NOT_APPLICABLE:
            return None
        return self.completed, self.message, self.planned_waypoints
