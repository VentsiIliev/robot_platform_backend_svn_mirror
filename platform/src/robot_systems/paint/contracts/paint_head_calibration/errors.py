"""Expected calibration failures; messages never select operational behavior."""

from dataclasses import dataclass
from enum import StrEnum, auto


class CalibrationFailureCode(StrEnum):
    INVALID_DATA = auto()
    INVALID_CALIBRATION = auto()
    PROFILE_NOT_FOUND = auto()
    REVISION_NOT_FOUND = auto()
    DRAFT_NOT_FOUND = auto()
    CONFLICT = auto()
    REVISION_SELECTED = auto()
    REVISION_IN_USE = auto()
    PROCESS_ACTIVE = auto()
    SELECTION_MISSING = auto()
    STORAGE_LOAD_FAILED = auto()
    STORAGE_SAVE_FAILED = auto()
    ASSET_INVALID = auto()
    ASSET_NOT_FOUND = auto()
    ASSET_CLEANUP_FAILED = auto()
    CAMERA_UNAVAILABLE = auto()
    FRAME_INVALID = auto()
    FRAME_STALE = auto()
    EVALUATION_FAILED = auto()
    CANCELLED = auto()


@dataclass(frozen=True, slots=True)
class CalibrationFailure:
    code: CalibrationFailureCode
    detail: str
    published: bool = False


class PaintHeadCalibrationError(Exception):
    def __init__(self, failure: CalibrationFailure) -> None:
        self._failure = failure
        super().__init__(failure.detail)

    @property
    def failure(self) -> CalibrationFailure:
        return self._failure


class CalibrationValidationError(PaintHeadCalibrationError, ValueError):
    def __init__(self, detail: str) -> None:
        super().__init__(CalibrationFailure(CalibrationFailureCode.INVALID_DATA, detail))


class CalibrationConflictError(PaintHeadCalibrationError):
    def __init__(self, detail: str) -> None:
        super().__init__(CalibrationFailure(CalibrationFailureCode.CONFLICT, detail))


class CalibrationPersistenceError(PaintHeadCalibrationError):
    """A repository load/save failure retaining whether a replacement was visible."""


@dataclass(frozen=True, slots=True)
class CalibrationSucceeded[T]:
    value: T
    warnings: tuple[CalibrationFailure, ...] = ()


@dataclass(frozen=True, slots=True)
class CalibrationFailed:
    failure: CalibrationFailure


type CalibrationResult[T] = CalibrationSucceeded[T] | CalibrationFailed
