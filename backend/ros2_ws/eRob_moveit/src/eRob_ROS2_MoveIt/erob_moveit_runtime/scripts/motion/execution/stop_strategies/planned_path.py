"""Brake along the previously commanded path; also preserves operator J6 hold."""
import math
import time
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from .base import StopPlan

# TODO - COULD USE TYPED RESULTS, TYPE HINTS, DOCSTRINGS AND TYPED EXCEPTIONS FOR ALL OF THESE STRATEGIES, AND A COMMON BASE CLASS WITH A GENERATOR FACTORY METHOD.

class PlannedPathStop:
    name = 'planned_path'

    def __init__(self, config, *, stop_kind='collision'):
        self.config = config
        self.stop_kind = stop_kind

    def build(self, executor, *, stop_duration_s=None):
        config = self.config
        stop_kind = self.stop_kind
        prefix = 'EXECUTOR_COLLISION_STOP_' if stop_kind == 'collision' else 'EXECUTOR_PATH_STOP_'
        if not bool(getattr(config, prefix + 'ENABLED', True)):
            return None, 'disabled'

        source = executor._last_sent_trajectory
        if source is None or len(getattr(source, 'points', []) or []) < 2:
            return None, 'no active trajectory copy'

        started_at = executor._active_goal_started_monotonic
        if started_at is None:
            return None, 'active trajectory start time unavailable'

        joint_names = list(getattr(source, 'joint_names', []) or [])
        if not joint_names:
            return None, 'active trajectory has no joint names'

        measured_positions = executor._get_latest_joint_state_in_trajectory_order(joint_names)
        if measured_positions is None:
            return None, 'measured joint state unavailable'

        elapsed_s = max(0.0, time.monotonic() - started_at)
        configured_duration_s = (
            getattr(config, prefix + 'DURATION_S', 0.30)
            if stop_duration_s is None
            else stop_duration_s
        )
        duration_s = max(
            0.05,
            float(configured_duration_s),
        )
        sample_period_s = max(
            0.01,
            float(getattr(config, prefix + 'SAMPLE_PERIOD_S', 0.04)),
        )
        tracking_tol = max(
            0.0,
            float(getattr(config, prefix + 'TRACKING_TOL_RAD', 0.20)),
        )

        start_sample = executor._sample_joint_trajectory(source, elapsed_s)
        if start_sample is None:
            return None, 'could not sample active trajectory at stop time'

        path_positions, path_velocities = start_sample
        max_tracking_error = max(
            abs(float(measured) - float(expected))
            for measured, expected in zip(measured_positions, path_positions)
        )
        if max_tracking_error > tracking_tol:
            return None, (
                f'tracking error {max_tracking_error:.4f} rad exceeds '
                f'{tracking_tol:.4f} rad'
            )

        source_end_s = executor._duration_to_sec(source.points[-1].time_from_start)
        remaining_s = max(0.0, source_end_s - elapsed_s)
        forward_window_s = min(remaining_s, duration_s * 0.5)
        point_count = max(2, int(math.ceil(duration_s / sample_period_s)) + 1)
        hold_joint_names = {
            str(name).strip()
            for name in getattr(config, prefix + 'HOLD_JOINT_NAMES', [])
            if str(name).strip()
        }
        hold_joint_indices = [
            index
            for index, name in enumerate(joint_names)
            if name in hold_joint_names
        ]
        hold_joint_positions = {
            index: float(path_positions[index])
            for index in hold_joint_indices
        }

        traj = JointTrajectory()
        traj.joint_names = joint_names
        traj.header.stamp = executor._node.get_clock().now().to_msg()

        points = []
        for index in range(point_count):
            u = index / (point_count - 1)
            # Advance along the original trajectory, but reduce path speed to zero.
            path_offset_s = forward_window_s * (1.0 - (1.0 - u) * (1.0 - u))
            speed_scale = 1.0 - u
            sample = executor._sample_joint_trajectory(source, elapsed_s + path_offset_s)
            if sample is None:
                return None, 'could not sample stop trajectory point'
            positions, velocities = sample
            for held_index in hold_joint_indices:
                positions[held_index] = hold_joint_positions[held_index]
                velocities[held_index] = 0.0

            point = JointTrajectoryPoint()
            point.positions = [float(value) for value in positions]
            point.velocities = [
                float(value) * speed_scale
                for value in velocities
            ]
            point.accelerations = [0.0] * len(joint_names)
            point.time_from_start = executor._sec_to_duration(duration_s * u)
            points.append(point)

        points[-1].velocities = [0.0] * len(joint_names)
        points[-1].accelerations = [0.0] * len(joint_names)
        traj.points = points

        return StopPlan(traj, held_joint_names=frozenset(hold_joint_names)), (
            f'elapsed={elapsed_s:.3f}s forward_window={forward_window_s:.3f}s '
            f'duration={duration_s:.3f}s points={len(points)} '
            f'max_tracking_error={max_tracking_error:.4f}rad '
            f'held_joints={[joint_names[index] for index in hold_joint_indices]} '
            f'held_positions={[round(hold_joint_positions[index], 6) for index in hold_joint_indices]}'
        )
