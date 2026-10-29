"""Jerk-limited brake from measured position, velocity and filtered acceleration."""
import math
import time
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from .base import StopPlan
from .ruckig_generator import CollisionBrake

# TODO - COULD USE TYPED RESULTS, TYPE HINTS, DOCSTRINGS AND TYPED EXCEPTIONS FOR ALL OF THESE STRATEGIES, AND A COMMON BASE CLASS WITH A GENERATOR FACTORY METHOD.

class MeasuredRuckigStop:
    name = 'measured_ruckig'

    def __init__(self, config):
        self.config = config
        self.generator = CollisionBrake.from_config(config)

    def build(self, executor, *, stop_duration_s=None):
        config = self.config
        if not bool(getattr(config, 'EXECUTOR_COLLISION_STOP_ENABLED', True)):
            return None, 'collision brake disabled'
        generator = self.generator
        try:
            state = executor._node.state_store.get_braking_state()
            max_age = float(getattr(config, 'EXECUTOR_COLLISION_STOP_STATE_MAX_AGE_S', 0.05))
            source_age = 0.0
            if state is not None and state.stamp_s > 0:
                source_age = executor._node.get_clock().now().nanoseconds*1e-9 - state.stamp_s
                if not -0.005 <= source_age <= max_age:
                    raise ValueError('joint state source timestamp is stale or in the future')
            rows = generator.generate(
                state, max_age_s=max_age,
                max_duration_s=float(getattr(config, 'EXECUTOR_COLLISION_STOP_MAX_DURATION_S', 0.6)),
                max_travel_rad=float(getattr(config, 'EXECUTOR_COLLISION_STOP_MAX_TRAVEL_RAD', 0.35)),
                sample_period_s=float(getattr(config, 'EXECUTOR_COLLISION_STOP_SAMPLE_PERIOD_S', 0.01)))
            age = time.monotonic() - state.received_at
            if state.stamp_s > 0:
                source_age = executor._node.get_clock().now().nanoseconds*1e-9 - state.stamp_s
            if age > max_age or source_age > max_age:
                raise ValueError('joint state aged out during collision brake generation')
            dispatch_deadline = time.monotonic() + max_age - max(age, source_age)
            traj = JointTrajectory()
            # The real controller treats this as a bounded collision request and
            # regenerates from its outgoing command at the RT takeover cycle.
            # The measured preview remains the dispatch/freshness guard only.
            traj.header.frame_id = "zeroerr_command_brake_v1"
            traj.joint_names = list(generator.names)
            # Zero header stamp: start on receipt, without a past absolute timestamp.
            for row in rows:
                point = JointTrajectoryPoint()
                point.positions = list(row[1:7])
                point.velocities = list(row[7:13])
                point.accelerations = list(row[13:19])
                point.time_from_start = executor._sec_to_duration(row[0])
                traj.points.append(point)
            travel = [max(abs(row[i+1]-rows[0][i+1]) for row in rows) for i in range(6)]
            velocity_tolerance = float(getattr(config, 'EXECUTOR_COLLISION_STOP_GOAL_VELOCITY_TOL_RAD_S', 0.02))
            if not math.isfinite(velocity_tolerance) or velocity_tolerance <= 0:
                raise ValueError('invalid standstill velocity tolerance')
            return StopPlan(traj, server_timeout_s=0.0, dispatch_deadline=dispatch_deadline,
                            goal_velocity_tolerance=velocity_tolerance), (
                f'generator=measured_ruckig_preview takeover=controller_command state_age_s={age:.4f} duration={rows[-1][0]:.4f}s '
                f'points={len(rows)} initial_positions={list(rows[0][1:7])} '
                f'initial_velocities={list(rows[0][7:13])} '
                f'initial_accelerations={list(rows[0][13:19])} travel_rad={travel} held_joints=[]')
        except Exception as exc:
            return None, f'measured collision brake refused: {exc}'
