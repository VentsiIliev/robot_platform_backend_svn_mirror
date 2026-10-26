"""Pure tray return-route construction shared by dropoff and startup."""
from dataclasses import dataclass
from collections.abc import Mapping, Sequence
import math
from typing import Any
from src.engine.robot.motion_sequence import (
    OrderedMotionType, OrderedPositionCommand, OrderedMotionProfile, OrderedMotionMetadata,
)
from src.robot_systems.paint.contracts.next_cycle_target import NextCycleTarget
from src.robot_systems.paint.processes.paint.configuration.models import PaintDropoffConfig
from .return_errors import (
    InvalidPlateMotionProfileError, InvalidReturnWaypointError, MissingReturnWaypointsError,
)
from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import validate_plate_passage_gate

@dataclass(frozen=True)
class PlateMotionProfile:
    velocity_percent: float
    acceleration_percent: float
    blend_radius: float
    motion_type: OrderedMotionType


@dataclass
class PlateNextWaypoint:
    position: list[float]
    profile: PlateMotionProfile


def plate_motion_profile(dropoff: PaintDropoffConfig, key: str) -> PlateMotionProfile:
    """Read one named profile or raise its specific configuration error."""
    for raw in dropoff.plate_motion_profiles:
        if not isinstance(raw, dict) or raw.get("key") != key:
            continue
        required = {"key", "vel_percent", "acc_percent", "blendR", "motion_type"}
        missing = required.difference(raw)
        if missing:
            raise InvalidPlateMotionProfileError(key, f"missing {sorted(missing)}")
        try:
            return _parse_profile(raw)
        except (TypeError, ValueError) as exc:
            raise InvalidPlateMotionProfileError(key, str(exc)) from exc
    raise InvalidPlateMotionProfileError(key, "profile is missing")


def _parse_profile(raw: Mapping[str, Any]) -> PlateMotionProfile:
    velocity = float(raw["vel_percent"])
    acceleration = float(raw["acc_percent"])
    blend = float(raw["blendR"])
    if not all(math.isfinite(v) for v in (velocity, acceleration, blend)):
        raise ValueError("motion limits must be finite")
    if velocity <= 0 or acceleration <= 0:
        raise ValueError("velocity and acceleration must be positive")
    return PlateMotionProfile(
        velocity_percent=velocity, acceleration_percent=acceleration,
        blend_radius=max(0.0, blend),
        motion_type=OrderedMotionType.parse(raw["motion_type"]),
    )


def plate_ordered_segment(
    label: str,
    pose: Sequence[float],
    profile: PlateMotionProfile,
    *,
    stop: bool = False,
) -> OrderedPositionCommand:
    return OrderedPositionCommand(
        label=label,
        position=tuple(float(value) for value in pose),
        motion_type=profile.motion_type,
        profile=OrderedMotionProfile(
            profile.velocity_percent, profile.acceleration_percent,
            0.0 if stop else profile.blend_radius,
        ),
        metadata=OrderedMotionMetadata(protected=True),
    )


def read_return_waypoints(dropoff: PaintDropoffConfig) -> list[PlateNextWaypoint]:
    """Parse fresh waypoint copies or raise a typed configuration error."""
    if not dropoff.plate_next_cycle_midpoint_enabled:
        return []
    if not dropoff.plate_next_cycle_waypoints:
        raise MissingReturnWaypointsError()
    waypoints: list[PlateNextWaypoint] = []
    for index, raw in enumerate(dropoff.plate_next_cycle_waypoints):
        if not isinstance(raw, dict):
            raise InvalidReturnWaypointError(index, "expected a mapping")
        required = {"position", "vel_percent", "acc_percent", "motion_type", "blendR"}
        missing = required.difference(raw)
        if missing:
            raise InvalidReturnWaypointError(index, f"missing {sorted(missing)}")
        pose, error = validate_plate_passage_gate(raw["position"])
        if error:
            raise InvalidReturnWaypointError(index, error)
        try:
            profile = _parse_profile(raw)
        except (TypeError, ValueError) as exc:
            raise InvalidReturnWaypointError(index, str(exc)) from exc
        waypoints.append(PlateNextWaypoint(pose, profile))
    return waypoints


def build_return_segments(
    dropoff: PaintDropoffConfig,
    route_poses: Mapping[str, Sequence[float]],
    next_waypoints: Sequence[PlateNextWaypoint],
    next_cycle_start: NextCycleTarget | None,
    *, use_center_waypoint: bool,
) -> list[OrderedPositionCommand]:
    """Build return motion only; the last destination is always an exact stop."""
    exit_segments = []
    if use_center_waypoint:
        exit_segments.append(plate_ordered_segment(
            "Plate exit: dropoff to plate center",
            route_poses["exit_center"],
            plate_motion_profile(dropoff, "exit_center"),
        ))
    exit_segments.append(plate_ordered_segment(
        (
            "Plate exit: plate center to passage gate"
            if use_center_waypoint
            else "Plate exit: dropoff to passage gate"
        ),
        route_poses["exit_gate"],
        plate_motion_profile(dropoff, "exit_gate"),
        stop=next_cycle_start is None,
    ))
    if next_cycle_start is not None:
        for index, waypoint in enumerate(next_waypoints):
            exit_segments.append(plate_ordered_segment(
                f"Plate exit: next-cycle waypoint {index + 1}/{len(next_waypoints)}",
                waypoint.position,
                waypoint.profile,
            ))
        exit_segments.append(plate_ordered_segment(
            (
                f"Plate exit: last waypoint to next-cycle start '{next_cycle_start.group_id}'"
                if next_waypoints
                else f"Plate exit: passage gate to next-cycle start '{next_cycle_start.group_id}'"
            ),
            route_poses["next_start"],
            plate_motion_profile(dropoff, "gate_to_next_start"),
            stop=True,
        ))

    return exit_segments


def interpolate_route_rotations(
    start_pose: list[float],
    route_poses: list[list[float]],
    *,
    end_rotation: float,
    rotation_index: int,
) -> None:
    """Interpolate one rotation axis at a constant rate over route distance."""
    if not route_poses:
        return

    route = [start_pose, *route_poses]
    segment_lengths = [
        math.dist(route[index - 1][:3], route[index][:3])
        for index in range(1, len(route))
    ]
    total_distance = sum(segment_lengths)
    start_rotation = float(start_pose[rotation_index])
    travelled = 0.0
    for index, pose in enumerate(route_poses):
        travelled += segment_lengths[index]
        if total_distance > 1e-6:
            progress = travelled / total_distance
        else:
            progress = (index + 1) / len(route_poses)
        pose[rotation_index] = start_rotation + progress * (end_rotation - start_rotation)
