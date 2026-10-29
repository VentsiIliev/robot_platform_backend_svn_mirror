"""Errors at the detector's public and configuration boundaries."""

from enum import Enum


class ErrorReason(Enum):
    CONFIGURATION_NOT_FOUND = "configuration_not_found"
    CONFIGURATION_INVALID = "configuration_invalid"
    REFERENCE_UNREADABLE = "reference_unreadable"
    REFERENCE_SIZE_MISMATCH = "reference_size_mismatch"
    REFERENCE_IMAGE_INVALID = "reference_image_invalid"
    IMAGE_TYPE_INVALID = "image_type_invalid"
    IMAGE_UNREADABLE = "image_unreadable"
    IMAGE_DTYPE_INVALID = "image_dtype_invalid"
    IMAGE_SHAPE_INVALID = "image_shape_invalid"
    IMAGE_SIZE_MISMATCH = "image_size_mismatch"
    PROCESSING_FAILED = "processing_failed"
    CAMERA_UNAVAILABLE = "camera_unavailable"
    CAMERA_READ_FAILED = "camera_read_failed"
    CAMERA_CONTROL_FAILED = "camera_control_failed"
    ARTIFACT_WRITE_FAILED = "artifact_write_failed"
    DEVELOPMENT_UI_FAILED = "development_ui_failed"


class PaintHeadError(Exception):
    """Base error with a machine-readable reason and a human-readable message."""

    def __init__(self, reason: ErrorReason, message: str) -> None:
        self.reason = reason
        self.message = message
        super().__init__(message)


class ConfigurationError(PaintHeadError):
    """A required configuration file or value is missing or invalid."""


class CalibrationError(PaintHeadError):
    """Reference images cannot provide a valid calibration."""


class InvalidImageError(PaintHeadError):
    """The supplied image does not satisfy the BGR uint8 input contract."""


class DetectionProcessingError(PaintHeadError):
    """The vision backend failed while processing a valid input image."""


class CameraError(PaintHeadError):
    """Development camera acquisition or control failed."""


class ArtifactError(PaintHeadError):
    """A development capture or report could not be written."""
