"""Immutable values consumed by policies, without camera or detector imports."""

from dataclasses import dataclass
from enum import Enum, StrEnum, auto
from math import isfinite

from src.robot_systems.paint.component_ids import MovementGroupID

from .errors import PaintHeadConfigurationError, PaintHeadContractError
from .guidance import PaintHeadCorrection


class PaintHeadState(Enum):
    PRESENT = auto()
    MISSING = auto()
    MISALIGNED = auto()
    UNKNOWN = auto()


class PaintHeadObservationReason(Enum):
    ALIGNED = auto()
    MISALIGNED = auto()
    EMPTY_MOUNT = auto()
    INSUFFICIENT_EVIDENCE = auto()
    CONFLICTING_EVIDENCE = auto()
    POSE_UNDETERMINED = auto()
    TOO_DARK = auto()
    OVEREXPOSED = auto()
    LOW_CONTRAST = auto()
    CONFIRMING_STATUS = auto()
    RECHECKING_POSITION = auto()


class PaintHeadAction(StrEnum):
    REPORT_ONLY = auto()
    CONTINUE = auto()
    RETRY = auto()
    PAUSE = auto()
    STOP = auto()
    REJECT = auto()


class HeadCheckScheduleDecision(Enum):
    DUE = auto()
    NOT_DUE = auto()


class HeadCheckOperatingMode(Enum):
    PRODUCTION = auto()
    DRY_RUN = auto()
    ADJUSTMENT = auto()
    PICKUP_ONLY = auto()


@dataclass(frozen=True, slots=True)
class HeadCheckPolicyId:
    """Extensible typed identity; string conversion is confined to persistence/UI."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value or self.value.strip() != self.value:
            raise PaintHeadConfigurationError("Head-check policy ID must be a non-empty identifier")


@dataclass(frozen=True, slots=True)
class HeadCheckPolicyDescription:
    policy_id: HeadCheckPolicyId
    label: str
    uses_interval: bool


@dataclass(frozen=True, slots=True)
class HeadInspectionWindow:
    """Monotonic times and frame freshness supplied explicitly by the caller."""

    started_at: float
    deadline_at: float
    max_frame_age_seconds: float

    def __post_init__(self) -> None:
        if not all(
            isfinite(value)
            for value in (
                self.started_at,
                self.deadline_at,
                self.max_frame_age_seconds,
            )
        ):
            raise PaintHeadConfigurationError("Inspection time limits must be finite")
        if self.deadline_at <= self.started_at or self.max_frame_age_seconds <= 0:
            raise PaintHeadConfigurationError(
                "Inspection requires a positive duration and maximum frame age",
            )


class HeadInspectionMotionType(Enum):
    POINT_TO_POINT = auto()
    LINEAR = auto()
    FAST_LINEAR = auto()


type HeadInspectionPose = tuple[float, float, float, float, float, float]


@dataclass(frozen=True, slots=True)
class HeadInspectionPositionTolerance:
    translation_mm: float
    rotation_degrees: float

    def __post_init__(self) -> None:
        if not all(
            type(value) in (int, float) and isfinite(value) and value > 0
            for value in (self.translation_mm, self.rotation_degrees)
        ):
            raise PaintHeadConfigurationError(
                "Inspection position tolerances must be positive and finite"
            )


@dataclass(frozen=True, slots=True)
class HeadInspectionTarget:
    """An explicit configured target; no pose or motion defaults are provided."""

    group_id: MovementGroupID
    position: HeadInspectionPose
    velocity_percent: float
    acceleration_percent: float
    motion_type: HeadInspectionMotionType


@dataclass(frozen=True, slots=True)
class PaintHeadAlignment:
    """Placement in image units; this is not a robot correction command."""

    aligned: bool
    translation_pixels: float
    rotation_degrees: float
    max_translation_pixels: float
    max_rotation_degrees: float
    recovery_pixel_limit: float
    recovery_degree_limit: float
    recovering: bool


@dataclass(frozen=True, slots=True)
class PaintHeadObservation:
    """One distinct frame, retaining confirmation and acquisition freshness."""

    state: PaintHeadState
    observed_state: PaintHeadState
    reason: PaintHeadObservationReason
    frame_sequence: int
    frame_captured_at: float
    frame_received_at: float
    evaluated_at: float
    calibration_revision: int
    alignment: PaintHeadAlignment | None
    held_warning: bool
    correction: PaintHeadCorrection | None = None


@dataclass(frozen=True, slots=True)
class HeadCheckProgress:
    """Completed painted workpieces in the current accepted Start session."""

    completed_workpieces: int

    def __post_init__(self) -> None:
        if type(self.completed_workpieces) is not int or self.completed_workpieces < 0:
            raise PaintHeadContractError(
                "Completed workpieces must be a non-negative integer",
            )


@dataclass(frozen=True, slots=True)
class HeadCheckContext:
    progress: HeadCheckProgress
    attempt_number: int
    elapsed_seconds: float
    previous_observation: PaintHeadObservation | None

    def __post_init__(self) -> None:
        if type(self.attempt_number) is not int or self.attempt_number < 1:
            raise PaintHeadContractError("Inspection attempt number must be positive")
        if not isfinite(self.elapsed_seconds) or self.elapsed_seconds < 0:
            raise PaintHeadContractError(
                "Inspection elapsed time must be finite and non-negative",
            )


@dataclass(frozen=True, slots=True)
class PaintHeadStateReactions:
    """Every state has an explicit action; no operational defaults are assumed."""

    present: PaintHeadAction
    missing: PaintHeadAction
    misaligned: PaintHeadAction
    unknown: PaintHeadAction

    def __post_init__(self) -> None:
        actions = (self.present, self.missing, self.misaligned, self.unknown)
        if not all(isinstance(action, PaintHeadAction) for action in actions):
            raise PaintHeadConfigurationError("Head-state reactions require typed actions")


@dataclass(frozen=True, slots=True)
class PaintHeadCheckConfiguration:
    """Run snapshot; all operational choices are explicit at the boundary."""

    enabled: bool
    policy_id: HeadCheckPolicyId
    interval_cycles: int
    timeout_seconds: float
    state_reactions: PaintHeadStateReactions
    failure_action: PaintHeadAction
    timeout_action: PaintHeadAction
    report_until_confirmed: bool

    def __post_init__(self) -> None:
        if type(self.interval_cycles) is not int or self.interval_cycles < 1:
            raise PaintHeadConfigurationError("Head-check interval must be a positive integer")
        if (
            type(self.timeout_seconds) not in (int, float)
            or not isfinite(self.timeout_seconds)
            or self.timeout_seconds <= 0
        ):
            raise PaintHeadConfigurationError("Head-check timeout must be finite and positive")
        if not isinstance(self.policy_id, HeadCheckPolicyId):
            raise PaintHeadConfigurationError("Head-check policy requires a typed identity")
        if not isinstance(self.state_reactions, PaintHeadStateReactions):
            raise PaintHeadConfigurationError("Head-state reactions require typed configuration")
        if not all(
            type(value) is bool
            for value in (
                self.enabled,
                self.report_until_confirmed,
            )
        ):
            raise PaintHeadConfigurationError("Head-check switches must be boolean values")
        if not isinstance(self.failure_action, PaintHeadAction):
            raise PaintHeadConfigurationError("Head-check failure response must be a typed action")
        if not isinstance(self.timeout_action, PaintHeadAction):
            raise PaintHeadConfigurationError("Head-check timeout response must be a typed action")
        if self.timeout_action is PaintHeadAction.RETRY:
            raise PaintHeadConfigurationError("An expired inspection timeout cannot be retried")
