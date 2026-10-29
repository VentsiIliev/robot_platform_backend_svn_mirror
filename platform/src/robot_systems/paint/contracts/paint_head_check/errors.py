"""Typed inspection failures; messages provide detail and never drive decisions."""

from dataclasses import dataclass
from enum import StrEnum, auto


class HeadInspectionFailureCode(StrEnum):
    CONFIGURATION_INVALID = auto()
    CAMERA_UNAVAILABLE = auto()
    CAMERA_READ_FAILED = auto()
    CALIBRATION_INVALID = auto()
    IMAGE_INVALID = auto()
    PROCESSING_FAILED = auto()
    FRAME_STALE = auto()
    TIMEOUT = auto()
    INSPECTION_GROUP_MISSING = auto()
    INSPECTION_POSITION_INVALID = auto()
    INSPECTION_POSITION_CHANGED = auto()
    INSPECTION_VELOCITY_INVALID = auto()
    INSPECTION_ACCELERATION_INVALID = auto()
    INSPECTION_MOTION_TYPE_INVALID = auto()
    INSPECTION_MOVEMENT_DISABLED = auto()
    INSPECTION_MOTION_FAILED = auto()
    RETURN_TARGET_INVALID = auto()
    RETURN_MOTION_FAILED = auto()
    SERVICE_UNAVAILABLE = auto()
    STATE_REJECTED = auto()


@dataclass(frozen=True, slots=True)
class HeadInspectionFailure:
    code: HeadInspectionFailureCode
    message: str


class PaintHeadContractError(ValueError):
    """A caller violated a domain invariant; this is not a camera failure."""


class PaintHeadCheckError(Exception):
    """Expected boundary failure, adapted to a result by its owning integration."""

    def __init__(self, failure: HeadInspectionFailure) -> None:
        self._failure = failure
        super().__init__(failure.message)

    @property
    def failure(self) -> HeadInspectionFailure:
        return self._failure


class PaintHeadConfigurationError(PaintHeadCheckError, ValueError):
    def __init__(self, message: str) -> None:
        super().__init__(
            HeadInspectionFailure(
                HeadInspectionFailureCode.CONFIGURATION_INVALID,
                message,
            )
        )


class PaintHeadInspectionTargetError(PaintHeadCheckError, ValueError):
    """The mandatory shaft-alignment target cannot be used; never substitute a pose."""


class PaintHeadCameraUnavailableError(PaintHeadCheckError):
    def __init__(self, message: str) -> None:
        super().__init__(
            HeadInspectionFailure(
                HeadInspectionFailureCode.CAMERA_UNAVAILABLE,
                message,
            )
        )


class PaintHeadCameraReadError(PaintHeadCheckError):
    def __init__(self, message: str) -> None:
        super().__init__(
            HeadInspectionFailure(
                HeadInspectionFailureCode.CAMERA_READ_FAILED,
                message,
            )
        )


class PaintHeadCalibrationError(PaintHeadCheckError):
    def __init__(self, message: str) -> None:
        super().__init__(
            HeadInspectionFailure(
                HeadInspectionFailureCode.CALIBRATION_INVALID,
                message,
            )
        )


class PaintHeadImageError(PaintHeadCheckError):
    def __init__(self, message: str) -> None:
        super().__init__(
            HeadInspectionFailure(
                HeadInspectionFailureCode.IMAGE_INVALID,
                message,
            )
        )


class PaintHeadProcessingError(PaintHeadCheckError):
    def __init__(self, message: str) -> None:
        super().__init__(
            HeadInspectionFailure(
                HeadInspectionFailureCode.PROCESSING_FAILED,
                message,
            )
        )
