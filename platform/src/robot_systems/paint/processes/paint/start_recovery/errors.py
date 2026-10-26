"""Stable recovery failures and the exceptions raised by their producers."""
from dataclasses import dataclass
from enum import StrEnum

from src.robot_systems.paint.processes.paint.results import (
    PaintFailure, PaintFailureCode, PaintOperationError,
)


class StartRecoveryFailureCode(StrEnum):
    INVALID_TRAY_GEOMETRY = "invalid_tray_geometry"
    FRAME_MISMATCH = "frame_mismatch"
    POSE_UNAVAILABLE = "pose_unavailable"
    NO_STRATEGY = "no_strategy"
    TARGET_UNAVAILABLE = "target_unavailable"
    INVALID_EXIT_GATE = "invalid_exit_gate"
    MISSING_RETURN_WAYPOINTS = "missing_return_waypoints"
    INVALID_RETURN_WAYPOINT = "invalid_return_waypoint"
    INVALID_MOTION_PROFILE = "invalid_motion_profile"
    INVALID_CLEARANCE = "invalid_clearance"
    BELOW_TRAY_SURFACE = "below_tray_surface"
    MOTION_FAILED = "motion_failed"
    INTERNAL = "internal"


@dataclass(frozen=True)
class StartRecoveryFailure(PaintFailure):
    """Paint-compatible failure retaining the specific recovery reason in diagnostics."""

    recovery_code: StartRecoveryFailureCode = StartRecoveryFailureCode.INTERNAL


class StartRecoveryError(PaintOperationError):
    """Base for expected recovery failures; consumers inspect failure codes."""

    recovery_code = StartRecoveryFailureCode.INTERNAL
    category = PaintFailureCode.INTERNAL
    description = "Unexpected start recovery failure"
    failure: StartRecoveryFailure

    def __init__(self, detail: str = "") -> None:
        message = f"{self.description}: {detail}" if detail else self.description
        super().__init__(StartRecoveryFailure(
            code=self.category, stage="start_recovery", message=message,
            recovery_code=self.recovery_code,
        ))


class InvalidTrayGeometryError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.INVALID_TRAY_GEOMETRY
    category = PaintFailureCode.INVALID_CONFIGURATION
    description = "Tray recovery requires valid taught tray corners"


class TrayFrameMismatchError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.FRAME_MISMATCH
    category = PaintFailureCode.INVALID_CONFIGURATION
    description = "Tray recovery requires corners taught with the active tool and user frame"


class RecoveryPoseUnavailableError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.POSE_UNAVAILABLE
    category = PaintFailureCode.UNAVAILABLE
    description = "Cannot read a fresh robot pose for start recovery"


class NoRecoveryStrategyError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.NO_STRATEGY
    category = PaintFailureCode.PLANNING
    description = "No start recovery strategy accepts the current position"


class RecoveryTargetUnavailableError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.TARGET_UNAVAILABLE
    category = PaintFailureCode.UNAVAILABLE
    description = "Cannot resolve the production start pose for tray recovery"


class InvalidRecoveryExitGateError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.INVALID_EXIT_GATE
    category = PaintFailureCode.INVALID_CONFIGURATION
    description = "Tray recovery exit gate is invalid"


class MissingRecoveryWaypointsError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.MISSING_RETURN_WAYPOINTS
    category = PaintFailureCode.INVALID_CONFIGURATION
    description = "Tray recovery requires enabled dropoff return waypoints"


class InvalidRecoveryWaypointError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.INVALID_RETURN_WAYPOINT
    category = PaintFailureCode.INVALID_CONFIGURATION
    description = "Tray recovery return waypoint is invalid"


class InvalidRecoveryMotionProfileError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.INVALID_MOTION_PROFILE
    category = PaintFailureCode.INVALID_CONFIGURATION
    description = "Tray recovery motion profile is invalid"


class InvalidRecoveryClearanceError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.INVALID_CLEARANCE
    category = PaintFailureCode.INVALID_CONFIGURATION
    description = "Tray recovery requires a positive finite approach clearance and finite surface offset"


class BelowTraySurfaceError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.BELOW_TRAY_SURFACE
    category = PaintFailureCode.PLANNING
    description = "Robot is below the taught tray surface; manual positioning required"


class RecoveryMotionFailedError(StartRecoveryError):
    recovery_code = StartRecoveryFailureCode.MOTION_FAILED
    category = PaintFailureCode.MOTION
    description = "Tray return failed; direct production navigation is prohibited"


class RecoveryInternalError(StartRecoveryError):
    """Unexpected implementation/runtime error; also blocks production."""
