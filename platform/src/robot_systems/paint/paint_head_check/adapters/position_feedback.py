"""Read-only validation shared by stopped inspection feedback adapters."""

from math import isfinite, sqrt

from src.robot_systems.paint.contracts.paint_head_check.models import (
    HeadInspectionPose,
    HeadInspectionPositionTolerance,
)


def inspection_pose_matches(
    actual: HeadInspectionPose,
    expected: HeadInspectionPose,
    tolerance: HeadInspectionPositionTolerance,
) -> bool:
    translation = sqrt(sum((actual[index] - expected[index]) ** 2 for index in range(3)))
    rotation = max(
        abs((actual[index] - expected[index] + 180.0) % 360.0 - 180.0) for index in range(3, 6)
    )
    return translation <= tolerance.translation_mm and rotation <= tolerance.rotation_degrees


def parse_inspection_pose(raw: list[float] | None) -> HeadInspectionPose | None:
    if raw is None or len(raw) != 6:
        return None
    try:
        if not all(type(value) in (int, float) and isfinite(value) for value in raw):
            return None
    except OverflowError:
        return None
    x, y, z, rx, ry, rz = raw
    return float(x), float(y), float(z), float(rx), float(ry), float(rz)


def robot_is_stationary(status: object) -> bool:
    if not isinstance(status, dict) or status.get("is_executing") is not False:
        return False
    active_states = {"running", "executing", "active", "moving", "queued"}
    for item in (status, status.get("ordered_motion_chain")):
        if not isinstance(item, dict):
            continue
        if item.get("is_executing") is True or item.get("queued") is True:
            return False
        for key in ("state", "status"):
            value = item.get(key)
            if value is not None and (not isinstance(value, str) or value.lower() in active_states):
                return False
    return True
