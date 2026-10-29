"""Strict settings boundary for the mandatory paint shaft-alignment group."""

import json
from collections.abc import Callable
from math import isfinite
from typing import NoReturn

from src.engine.robot.configuration.movement_group_settings import MovementGroupSettings
from src.robot_systems.paint.component_ids import MovementGroupID
from src.robot_systems.paint.contracts.paint_head_check.errors import (
    HeadInspectionFailure,
    HeadInspectionFailureCode,
    PaintHeadInspectionTargetError,
)
from src.robot_systems.paint.contracts.paint_head_check.interfaces import (
    IHeadInspectionTargetProvider,
)
from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionMotionType,
    HeadInspectionPose,
    HeadInspectionTarget,
)


class ShaftAlignmentInspectionTargetProvider(IHeadInspectionTargetProvider):
    """Read configured values on each resolution; never teach or repair settings."""

    def __init__(self, settings_provider: Callable[[], MovementGroupSettings]) -> None:
        self._settings_provider = settings_provider

    def resolve(self) -> HeadInspectionTarget:
        settings = self._settings_provider()
        group_id = MovementGroupID.VERTICAL_SHAFT_ALIGNMENT
        group = settings.movement_groups.get(group_id.value)
        if group is None:
            _fail(HeadInspectionFailureCode.INSPECTION_GROUP_MISSING, "group is not configured")

        position = _position(group.position)
        velocity = _percentage(
            group.velocity,
            HeadInspectionFailureCode.INSPECTION_VELOCITY_INVALID,
            "velocity",
        )
        acceleration = _percentage(
            group.acceleration,
            HeadInspectionFailureCode.INSPECTION_ACCELERATION_INVALID,
            "acceleration",
        )
        if group.has_trajectory_execution is not True:
            _fail(
                HeadInspectionFailureCode.INSPECTION_MOVEMENT_DISABLED,
                "trajectory execution is not enabled",
            )
        motion_type = _motion_type(group.motion_type)
        return HeadInspectionTarget(group_id, position, velocity, acceleration, motion_type)


def _position(raw: str | None) -> HeadInspectionPose:
    if not isinstance(raw, str) or not raw.strip():
        _fail(HeadInspectionFailureCode.INSPECTION_POSITION_INVALID, "position is not configured")
    try:
        decoded: object = json.loads(raw)
    except (ValueError, TypeError) as error:
        raise _target_error(
            HeadInspectionFailureCode.INSPECTION_POSITION_INVALID,
            "position must be a JSON array of six finite numbers",
        ) from error
    if not isinstance(decoded, list) or len(decoded) != 6:
        _fail(
            HeadInspectionFailureCode.INSPECTION_POSITION_INVALID,
            "position must contain exactly six coordinates",
        )
    coordinates: list[float] = []
    for value in decoded:
        if type(value) not in (int, float):
            _fail(
                HeadInspectionFailureCode.INSPECTION_POSITION_INVALID,
                "position coordinates must be numbers, without boolean or string coercion",
            )
        try:
            coordinate = float(value)
        except OverflowError as error:
            raise _target_error(
                HeadInspectionFailureCode.INSPECTION_POSITION_INVALID,
                "position coordinates must be finite",
            ) from error
        if not isfinite(coordinate):
            _fail(
                HeadInspectionFailureCode.INSPECTION_POSITION_INVALID,
                "position coordinates must be finite",
            )
        coordinates.append(coordinate)
    x, y, z, rx, ry, rz = coordinates
    return x, y, z, rx, ry, rz


def _percentage(raw: int | float, code: HeadInspectionFailureCode, field: str) -> float:
    if type(raw) not in (int, float):
        _fail(
            code,
            f"{field} must be numeric, finite, greater than 0 and at most 100 percent",
        )
    try:
        value = float(raw)
    except OverflowError as error:
        raise _target_error(code, f"{field} must be finite") from error
    if not isfinite(value) or not 0 < value <= 100:
        _fail(code, f"{field} must be in the range (0, 100] percent")
    return value


def _motion_type(raw: str) -> HeadInspectionMotionType:
    # String conversion belongs only to this external settings boundary.
    match raw:
        case "ptp":
            return HeadInspectionMotionType.POINT_TO_POINT
        case "linear":
            return HeadInspectionMotionType.LINEAR
        case "fast_lin":
            return HeadInspectionMotionType.FAST_LINEAR
        case _:
            _fail(
                HeadInspectionFailureCode.INSPECTION_MOTION_TYPE_INVALID,
                "motion type is invalid",
            )


def _target_error(code: HeadInspectionFailureCode, detail: str) -> PaintHeadInspectionTargetError:
    group_id = MovementGroupID.VERTICAL_SHAFT_ALIGNMENT
    return PaintHeadInspectionTargetError(
        HeadInspectionFailure(
            code,
            f"Paint-head inspection requires movement group '{group_id.value}': {detail}. "
            "Configure the group in Robot Settings; no fallback inspection pose is permitted.",
        )
    )


def _fail(code: HeadInspectionFailureCode, detail: str) -> NoReturn:
    raise _target_error(code, detail)
