"""Tray return and unchanged startup outside the tray footprint."""
import math
from dataclasses import replace

from src.engine.geometry.planar import unwrap_degrees
from src.engine.robot.motion_sequence import OrderedMotionType, OrderedPositionCommand
from src.robot_systems.paint.processes.paint.tray_dry.plate_layout import validate_plate_passage_gate
from src.robot_systems.paint.processes.paint.tray_dry.return_route import (
    plate_motion_profile, plate_ordered_segment, build_return_segments, read_return_waypoints,
    interpolate_route_rotations,
)
from .contracts import IStartRecoveryStrategy, StartRecoveryRequest
from .errors import (
    BelowTraySurfaceError, InvalidRecoveryClearanceError, InvalidRecoveryExitGateError,
    InvalidRecoveryMotionProfileError, InvalidRecoveryWaypointError,
    MissingRecoveryWaypointsError, RecoveryTargetUnavailableError,
)
from src.robot_systems.paint.processes.paint.tray_dry.return_errors import (
    InvalidPlateMotionProfileError, InvalidReturnWaypointError, MissingReturnWaypointsError,
)


class TrayReturnRecoveryStrategy(IStartRecoveryStrategy):
    """Route every TCP inside the taught XY polygon through the tray return path.

    Height does not exclude a pose from detection. Initial vertical clearance
    preserves orientation; configured gate/return poses then define the route.
    """

    def matches(self, request: StartRecoveryRequest) -> bool:
        x, y = request.pose[:2]
        crosses = []
        for a, b in zip(request.corners, request.corners[1:] + request.corners[:1]):
            crosses.append((b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0]))
        return all(v >= -1e-6 for v in crosses) or all(v <= 1e-6 for v in crosses)

    def build_route(self, request: StartRecoveryRequest) -> list[OrderedPositionCommand]:
        config = request.dropoff
        try:
            target = request.target_provider()
        except Exception as exc:
            raise RecoveryTargetUnavailableError(str(exc)) from exc

        if target is None:
            raise RecoveryTargetUnavailableError()

        gate, error = validate_plate_passage_gate(config.plate_exit_gate_pose)
        if error:
            raise InvalidRecoveryExitGateError(error)
        # Do not silently turn an incomplete return route into a direct magazine move.
        if not config.plate_next_cycle_midpoint_enabled or not config.plate_next_cycle_waypoints:
            raise MissingRecoveryWaypointsError()
        try:
            waypoints = read_return_waypoints(config)
        except MissingReturnWaypointsError as exc:
            raise MissingRecoveryWaypointsError(str(exc)) from exc
        except InvalidReturnWaypointError as exc:
            raise InvalidRecoveryWaypointError(str(exc)) from exc
        try:
            offset = float(config.plate_release_z_offset_mm)
            clearance = float(config.plate_approach_clearance_mm)
        except (TypeError, ValueError) as exc:
            raise InvalidRecoveryClearanceError(str(exc)) from exc
        if not math.isfinite(offset) or not math.isfinite(clearance) or clearance <= 0:
            raise InvalidRecoveryClearanceError()
        surface_z = max(c[2] for c in request.corners) + offset
        if request.pose[2] < min(c[2] for c in request.corners) + offset - 1.0:
            raise BelowTraySurfaceError()
        raised = list(request.pose)
        raised[2] = max(raised[2], surface_z + clearance)
        center = list(raised)
        center[:2] = [sum(c[i] for c in request.corners) / 4.0 for i in range(2)]
        poses = {"exit_center": center, "exit_gate": gate, "next_start": list(target.position)}
        return_poses = [center, gate, *(w.position for w in waypoints), poses["next_start"]]
        if config.plate_distribute_unwind:
            # Unlike normal dropoff, a fresh Start has no trustworthy paint-turn
            # history. Distribute the current-to-taught orientation change; do
            # not infer joint winding from a wrapped Cartesian angle.
            interpolate_route_rotations(
                raised, return_poses,
                end_rotation=float(target.position[5]), rotation_index=5,
            )
        else:
            previous = raised[5]
            for pose in return_poses:
                pose[5] = unwrap_degrees(previous, pose[5])
                previous = pose[5]
        try:
            segments = []
            if raised[2] > request.pose[2] + 1e-6:
                profile = replace(plate_motion_profile(config, "exit_center"), motion_type=OrderedMotionType.LINEAR)
                segments.append(plate_ordered_segment("Tray start recovery: vertical clearance", raised, profile, stop=True))
            segments.extend(build_return_segments(
                config, poses, waypoints, target, use_center_waypoint=True,
            ))
        except InvalidPlateMotionProfileError as exc:
            raise InvalidRecoveryMotionProfileError(str(exc)) from exc
        return segments


class ContinueStartStrategy(IStartRecoveryStrategy):
    """Preserve normal startup when no preceding regional strategy matches."""

    def matches(self, request: StartRecoveryRequest) -> bool:
        return True

    def build_route(self, request: StartRecoveryRequest) -> list[OrderedPositionCommand]:
        return []
