"""Normalize paint projection settings."""
from src.robot_systems.paint.processes.paint.configuration.models import PaintSimulationConfig

def _normalize_contact_motion_config(
    *,
    motion_plane: str = "xy_z_rz",
    translation_axis: str = "x",
    pivot_side: str = "negative",
    translation_direction: str = "forward",
    apply_camera_to_tcp_for_pickup: bool = False,
    camera_to_tcp_x_offset: float = 0.0,
    camera_to_tcp_y_offset: float = 0.0,
    rotation_direction_sign: float = 1.0,
    closed_contour_overlap_mm: float = 0.0,
) -> PaintSimulationConfig:
    """Normalize user-facing pivot settings into a validated simulation config."""
    rules = PaintSimulationConfig().rules
    default_plane = rules.default_motion_plane
    plane_key = str(motion_plane or default_plane).strip().lower()
    axis_key = str(translation_axis or "x").strip().lower()
    side_key = str(pivot_side or rules.default_paint_side).strip().lower()
    direction_key = str(translation_direction or rules.default_translation_direction).strip().lower()
    plane_spec = rules.motion_plane_specs.get(plane_key, rules.motion_plane_specs[default_plane])
    valid_axes = tuple(plane_spec.axis_offsets_deg.keys())
    return PaintSimulationConfig(
        motion_plane=plane_key if plane_key in rules.motion_plane_specs else default_plane,
        translation_axis=axis_key if axis_key in valid_axes else valid_axes[0],
        paint_side=side_key if side_key in rules.side_signs else rules.default_paint_side,
        translation_direction=(
            direction_key if direction_key in rules.translation_direction_signs else rules.default_translation_direction
        ),
        apply_camera_to_tcp_for_pickup=bool(apply_camera_to_tcp_for_pickup),
        camera_to_tcp_x_offset=float(camera_to_tcp_x_offset),
        camera_to_tcp_y_offset=float(camera_to_tcp_y_offset),
        rotation_direction_sign=-1.0 if float(rotation_direction_sign) < 0.0 else 1.0,
        closed_contour_overlap_mm=max(0.0, float(closed_contour_overlap_mm)),
    )


def _xz_ry_projection_rotation_sign(motion_plane: str, mirror_execution_rotation: bool) -> float:
    """Return the planar rotation sign used during projection, before command generation."""
    if motion_plane == "xz_y_ry" and mirror_execution_rotation:
        return -1.0
    return 1.0
