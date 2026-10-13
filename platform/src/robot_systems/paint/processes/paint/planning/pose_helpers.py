"""Pure pose transformations shared by paint planning and adjustment."""
from __future__ import annotations
import math
from src.engine.geometry.planar import unwrap_degrees
from src.engine.geometry.planar import rotate_xy
from src.robot_systems.paint.processes.paint.configuration.models import PaintSimulationConfig

def _camera_to_tcp_delta(
    x_offset: float,
    y_offset: float,
    current_rz: float,
    reference_rz: float = 0.0,
) -> tuple[float, float]:
    """Return the tool-frame TCP sweep delta between the reference and current pickup angles."""
    cur_x, cur_y = rotate_xy(x_offset, y_offset, current_rz)
    ref_x, ref_y = rotate_xy(x_offset, y_offset, reference_rz)
    return cur_x - ref_x, cur_y - ref_y


def _paint_axis_staging_offset_pose(
    contact_pose: list[float],
    pivot_config: PaintSimulationConfig,
    *,
    z_offset_mm: float = 0.0,
    paint_axis_offset_mm: float = 0.0,
    perpendicular_axis_offset_mm: float = 0.0,
) -> list[float]:
    """Return the pre-paint staging pose below and behind the first pivot contact."""
    offset_pose = list(contact_pose)
    if len(offset_pose) > 2:
        offset_pose[2] = float(offset_pose[2]) + float(z_offset_mm)

    try:
        axis_position = pivot_config.planar_axes.index(pivot_config.translation_axis)
    except ValueError:
        return offset_pose

    axis_index = pivot_config.planar_coordinate_indices[axis_position]
    perpendicular_axis_position = 1 - axis_position
    perpendicular_axis_index = pivot_config.planar_coordinate_indices[perpendicular_axis_position]
    if len(offset_pose) > perpendicular_axis_index:
        offset_pose[perpendicular_axis_index] = (
            float(offset_pose[perpendicular_axis_index]) + float(perpendicular_axis_offset_mm)
        )
    if len(offset_pose) <= axis_index or abs(float(paint_axis_offset_mm)) <= 1e-9:
        return offset_pose

    offset_pose[axis_index] = (
        float(offset_pose[axis_index])
        - float(pivot_config.direction_sign) * float(paint_axis_offset_mm)
    )
    return offset_pose


def _finite_pose(pose) -> list[float] | None:
    if pose is None:
        return None
    try:
        values = [float(value) for value in list(pose)[:6]]
    except (TypeError, ValueError):
        return None
    if len(values) != 6 or not all(math.isfinite(value) for value in values):
        return None
    return values


def calculate_workpiece_dropoff_pose(
    calibration_pose: list[float] | tuple[float, ...],
    plate_dropoff_pose: list[float] | tuple[float, ...],
    workpiece_rz_at_calibration_deg: float,
) -> list[float]:
    """Return a plate pose preserving workpiece orientation across plane rotation.

    ``workpiece_rz_at_calibration_deg`` is the resolved robot/tool RZ holding the
    workpiece at the calibration pose, not the raw contour angle.  XYZ, RX, and
    RY come from the plate pose; RZ also includes the taught rotation from the
    calibration pose to the plate pose.
    """
    calibration = _finite_pose(calibration_pose)
    dropoff = _finite_pose(plate_dropoff_pose)
    try:
        workpiece_rz = float(workpiece_rz_at_calibration_deg)
    except (TypeError, ValueError) as exc:
        raise ValueError("Workpiece calibration RZ must be finite") from exc
    if calibration is None:
        raise ValueError("Calibration pose must contain six finite values")
    if dropoff is None:
        raise ValueError("Plate dropoff pose must contain six finite values")
    if not math.isfinite(workpiece_rz):
        raise ValueError("Workpiece calibration RZ must be finite")

    calibration_to_plate_rz = dropoff[5] - calibration[5]
    mapped_workpiece_rz = workpiece_rz + calibration_to_plate_rz
    dropoff[5] = unwrap_degrees(dropoff[5], mapped_workpiece_rz)
    return dropoff
