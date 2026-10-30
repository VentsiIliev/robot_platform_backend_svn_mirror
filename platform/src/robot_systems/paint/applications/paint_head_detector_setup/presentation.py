"""Immutable presentation snapshots shared across MVC without model/view imports."""

from dataclasses import dataclass

from src.robot_systems.paint.contracts.paint_head_calibration.errors import CalibrationFailure
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationCatalog,
    CalibrationDefinition,
    CalibrationEvaluation,
    ImageFrame,
    ProfileId,
    RevisionRef,
)


@dataclass(frozen=True, slots=True)
class SetupSnapshot:
    catalog: CalibrationCatalog | None
    profile_id: ProfileId | None
    definition: CalibrationDefinition | None
    base_revision: int | None
    dirty: bool
    generation: int
    frozen: bool
    live: bool
    in_use_revisions: tuple[RevisionRef, ...] = ()


@dataclass(frozen=True, slots=True)
class PreviewUpdate:
    generation: int
    frame: ImageFrame | None
    evaluation: CalibrationEvaluation | None
    failure: CalibrationFailure | None = None
