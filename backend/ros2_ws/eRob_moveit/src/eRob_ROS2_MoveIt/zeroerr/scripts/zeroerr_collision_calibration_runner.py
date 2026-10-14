#!/usr/bin/env python3
"""Conservative, MoveIt-validated excitation runner for torque-model data collection.

The node is deliberately idle on startup.  A run must be requested through the
``~/start`` Trigger service, and real controller goals are only sent when
``dry_run`` is false.  Every motion is densely sampled and checked by the live
MoveIt planning scene before and after time parameterization.
"""

import csv
import json
import math
import os
import threading
import time
from pathlib import Path

import rclpy
from control_msgs.action import FollowJointTrajectory
from control_msgs.msg import DynamicJointState
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from std_srvs.srv import Trigger
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from erob_moveit_runtime.srv import ApplyIPP, ValidateTrajectoryStates


def _halton(index, base):
    value = 0.0
    factor = 1.0
    while index:
        factor /= base
        index, digit = divmod(index, base)
        value += factor * digit
    return value


class CalibrationRunner(Node):
    def __init__(self):
        super().__init__('zeroerr_collision_calibration_runner')
        self.declare_parameter('joint_names', [f'Joint_{i}' for i in range(1, 7)])
        self.declare_parameter('planning_group', 'manipulator')
        self.declare_parameter('controller_action', '/manipulator_controller/follow_joint_trajectory')
        self.declare_parameter('validator_service', '/validate_trajectory_states')
        self.declare_parameter('ruckig_service', '/apply_ruckig')
        self.declare_parameter('dry_run', True)
        self.declare_parameter('joint_sweep_amplitudes_rad', [0.15] * 6)
        self.declare_parameter('sweep_levels', 2)
        self.declare_parameter('coupled_sample_count', 48)
        self.declare_parameter('coupled_amplitude_scale', 0.35)
        self.declare_parameter('coupled_return_interval', 4)
        self.declare_parameter('base_rotation_sample_count', 12)
        self.declare_parameter('base_rotation_min_rad', -3.0)
        self.declare_parameter('base_rotation_max_rad', 3.0)
        self.declare_parameter('max_interpolation_step_rad', 0.015)
        self.declare_parameter(
            'velocity_scalings',
            [0.04, 0.10, 0.20, 0.30, 0.40, 0.55, 0.70, 0.85, 1.00])
        self.declare_parameter(
            'acceleration_scalings',
            [0.04, 0.12, 0.30, 0.40, 0.50, 0.65, 0.80, 0.90, 1.00])
        self.declare_parameter(
            'joint_sampling_min_rad', [-3.0, -1.5, -1.8, -2.5, -2.5, -3.0])
        self.declare_parameter(
            'joint_sampling_max_rad', [3.0, 1.5, 1.8, 2.0, 2.5, 3.0])
        self.declare_parameter('settle_time_sec', 0.35)
        self.declare_parameter('service_timeout_sec', 10.0)
        self.declare_parameter('motion_timeout_sec', 90.0)
        self.declare_parameter('coverage_log_period_sec', 0.05)
        self.declare_parameter('coverage_voxel_size_m', 0.05)
        self.declare_parameter(
            'output_directory',
            '/home/ilv/ros2_ws/eRob_moveit/zeroerr_data/collision_detection/calibration_runs')

        self.joint_names = list(self.get_parameter('joint_names').value)
        self.group = str(self.get_parameter('planning_group').value)
        self.dry_run = bool(self.get_parameter('dry_run').value)
        self._lock = threading.RLock()
        self._running = False
        self._stop_requested = False
        self._stage = 'idle'
        self._dynamic_profile = 'none'
        self._positions = None
        self._velocities = None
        self._accelerations = None
        self._joint_state_time = None
        self._collision_thresholds = {}
        self._pose = None
        self._active_goal = None
        self._drive_state_seen = False
        self._drive_fault_reason = ''
        self._csv_file = None
        self._csv_writer = None
        self._last_coverage_write = 0.0
        self._coverage_points = []
        self._joint_coverage_points = []
        self._accepted = 0
        self._rejected = 0
        self._motion_results = []
        self._run_type = 'calibration'
        self._collision_events = []
        self._collision_active_joints = set()
        self._event_csv_file = None
        self._event_csv_writer = None
        self._training_csv_file = None
        self._training_csv_writer = None
        self._last_training_write = 0.0

        self.validator = self.create_client(
            ValidateTrajectoryStates,
            str(self.get_parameter('validator_service').value))
        self.ruckig = self.create_client(
            ApplyIPP, str(self.get_parameter('ruckig_service').value))
        self.controller = ActionClient(
            self, FollowJointTrajectory,
            str(self.get_parameter('controller_action').value))

        self.create_subscription(JointState, '/joint_states', self._on_joint_state, 20)
        self.create_subscription(
            DynamicJointState, '/dynamic_joint_states', self._on_drive_state, 20)
        self.create_subscription(PoseStamped, '/cartesian_position', self._on_pose, 20)
        self.create_subscription(
            DynamicJointState, '/zeroerr/collision_monitor/state',
            self._on_collision_state, 20)
        self.create_subscription(
            String, '/zeroerr/collision_monitor/config_state',
            self._on_collision_config, 10)
        qos = QoSProfile(depth=1)
        qos.reliability = ReliabilityPolicy.RELIABLE
        qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.status_pub = self.create_publisher(String, '~/status', qos)
        self.create_service(Trigger, '~/start', self._on_start)
        self.create_service(Trigger, '~/start_test', self._on_start_test)
        self.create_service(Trigger, '~/start_external', self._on_start_external)
        self.create_service(Trigger, '~/stop', self._on_stop)
        self.create_service(Trigger, '~/write_summary', self._on_write_summary)
        self.create_timer(0.5, self._publish_status)
        self.get_logger().info(
            f'Calibration runner ready (dry_run={self.dry_run}). Start with: '
            'ros2 service call /zeroerr_collision_calibration_runner/start std_srvs/srv/Trigger {}')

    def _on_joint_state(self, msg):
        by_name = {name: i for i, name in enumerate(msg.name)}
        if not all(name in by_name for name in self.joint_names):
            return
        with self._lock:
            now = time.monotonic()
            new_velocities = [
                float(msg.velocity[by_name[n]]) if by_name[n] < len(msg.velocity) else 0.0
                for n in self.joint_names]
            if self._velocities is not None and self._joint_state_time is not None:
                dt = max(now - self._joint_state_time, 1.0e-6)
                self._accelerations = [
                    (new - old) / dt
                    for new, old in zip(new_velocities, self._velocities)]
            else:
                self._accelerations = [0.0] * len(self.joint_names)
            self._positions = [float(msg.position[by_name[n]]) for n in self.joint_names]
            self._velocities = new_velocities
            self._joint_state_time = now

    def _on_collision_config(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
            thresholds = list(payload.get('external_torque_thresholds', []))
        except (json.JSONDecodeError, TypeError, ValueError):
            return
        with self._lock:
            self._collision_thresholds = {
                name: float(thresholds[index])
                for index, name in enumerate(self.joint_names)
                if index < len(thresholds)
            }

    def _on_pose(self, msg):
        now = time.monotonic()
        with self._lock:
            self._pose = msg.pose
            if ((self.dry_run and self._run_type != 'external_motion')
                    or not self._running or self._csv_writer is None):
                return
            period = float(self.get_parameter('coverage_log_period_sec').value)
            if now - self._last_coverage_write < period or self._positions is None:
                return
            self._last_coverage_write = now
            p = msg.pose.position
            row = [time.time(), self._stage, p.x, p.y, p.z] + list(self._positions)
            self._csv_writer.writerow(row)
            self._csv_file.flush()
            self._coverage_points.append((float(p.x), float(p.y), float(p.z)))
            self._joint_coverage_points.append(tuple(float(v) for v in self._positions))

    def _on_drive_state(self, msg: DynamicJointState) -> None:
        faults = []
        all_operation_enabled = True
        for joint_name, values in zip(msg.joint_names, msg.interface_values):
            interfaces = {
                name: value
                for name, value in zip(values.interface_names, values.values)
            }
            error_code = int(round(interfaces.get('error_code', 0.0)))
            statusword = int(round(interfaces.get('statusword', 0.0)))
            if error_code:
                faults.append(f'{joint_name}=0x{error_code:04X}')
            if (statusword & 0x006F) != 0x0027:
                all_operation_enabled = False
        with self._lock:
            self._drive_state_seen = bool(msg.joint_names)
            self._drives_operation_enabled = all_operation_enabled
            if not faults or self._drive_fault_reason:
                return
            self._drive_fault_reason = 'drive fault: ' + ', '.join(faults)
            if not self._running:
                return
            self._stop_requested = True
            self._stage = 'fault:' + self._drive_fault_reason
            goal = self._active_goal
        self.get_logger().error(
            f'Calibration cancelling active motion immediately: {self._drive_fault_reason}')
        if goal is not None:
            goal.cancel_goal_async()

    def _on_collision_state(self, msg: DynamicJointState) -> None:
        """Record observer samples or rising indications for the active run."""
        with self._lock:
            if not self._running:
                return
            if self._run_type == 'external_motion':
                self._append_external_training_sample(msg)
                return
            if self._run_type != 'false_positive_test':
                return
            stage = self._stage
            profile = self._dynamic_profile
            positions = list(self._positions or [])
            velocities = list(self._velocities or [])
            accelerations = list(self._accelerations or [])
            thresholds = dict(self._collision_thresholds)
            previously_active = set(self._collision_active_joints)

        currently_active = set()
        events = []
        for joint_name, values in zip(msg.joint_names, msg.interface_values):
            interfaces = dict(zip(values.interface_names, values.values))
            active = bool(interfaces.get('dynamics_active', 0.0)) or bool(
                interfaces.get('contact_active', 0.0))
            if not active:
                continue
            currently_active.add(joint_name)
            if joint_name in previously_active:
                continue
            events.append({
                'unix_time': time.time(),
                'motion': stage,
                'profile': profile,
                'joint': joint_name,
                'external_torque_nm': float(interfaces.get('external_torque', math.nan)),
                'expected_torque_nm': float(interfaces.get('expected_torque', math.nan)),
                'measured_torque_nm': float(interfaces.get('measured_torque', math.nan)),
                'threshold_nm': float(interfaces.get(
                    'external_torque_threshold',
                    thresholds.get(joint_name, math.nan))),
                'positions_rad': positions,
                'velocities_rad_s': velocities,
                'accelerations_rad_s2': accelerations,
            })
        with self._lock:
            self._collision_active_joints = currently_active
            for event in events:
                self._collision_events.append(event)
                if self._event_csv_writer is not None:
                    self._event_csv_writer.writerow([
                        event['unix_time'], event['motion'], event['profile'],
                        event['joint'], event['external_torque_nm'],
                        event['threshold_nm'], event['expected_torque_nm'],
                        event['measured_torque_nm'],
                        json.dumps(event['positions_rad']),
                        json.dumps(event['velocities_rad_s']),
                        json.dumps(event['accelerations_rad_s2']),
                    ])
                    self._event_csv_file.flush()

    def _on_start(self, request, response):
        del request
        return self._begin_run(response, 'calibration')

    def _on_start_test(self, request, response):
        del request
        return self._begin_run(response, 'false_positive_test')

    def _on_start_external(self, request, response):
        """Start passive recording; the caller owns all robot motion."""
        del request
        return self._begin_run(response, 'external_motion')

    def _begin_run(self, response, run_type):
        with self._lock:
            if self._running:
                response.success = False
                response.message = 'calibration is already running'
                return response
            if self._positions is None:
                response.success = False
                response.message = 'no complete /joint_states sample received'
                return response
            if any(abs(v) > 0.03 for v in (self._velocities or [])):
                response.success = False
                response.message = 'robot is moving; wait until it is stationary'
                return response
            live_run = run_type == 'external_motion' or not self.dry_run
            if live_run and (
                    not self._drive_state_seen
                    or not getattr(self, '_drives_operation_enabled', False)):
                response.success = False
                response.message = 'all drives must report operation_enabled before a live run'
                return response
            self._running = True
            self._stop_requested = False
            self._drive_fault_reason = ''
            self._accepted = 0
            self._rejected = 0
            self._coverage_points = []
            self._joint_coverage_points = []
            self._motion_results = []
            self._run_type = run_type
            self._collision_events = []
            self._collision_active_joints = set()
            self._last_training_write = 0.0
        threading.Thread(target=self._run, daemon=True).start()
        response.success = True
        response.message = f'{run_type} started (dry_run={self.dry_run and not live_run})'
        return response

    def _on_stop(self, request, response):
        del request
        with self._lock:
            self._stop_requested = True
            goal = self._active_goal
        if goal is not None:
            goal.cancel_goal_async()
        response.success = True
        response.message = 'stop requested; active controller goal cancellation requested'
        return response

    def _on_write_summary(self, request, response):
        del request
        path = self._write_summary()
        response.success = path is not None
        response.message = str(path) if path else 'no run data available'
        return response

    def _publish_status(self):
        with self._lock:
            payload = {
                'running': self._running, 'dry_run': self.dry_run,
                'run_type': self._run_type,
                'stop_requested': self._stop_requested, 'stage': self._stage,
                'dynamic_profile': self._dynamic_profile,
                'accepted_motions': self._accepted, 'rejected_motions': self._rejected,
                'coverage_points': len(self._coverage_points),
                'drive_fault': self._drive_fault_reason,
                'collision_events': len(self._collision_events),
                'run_directory': str(getattr(self, '_run_directory', '')),
            }
        msg = String()
        msg.data = json.dumps(payload, separators=(',', ':'))
        self.status_pub.publish(msg)

    def _wait_future(self, future, timeout):
        event = threading.Event()
        future.add_done_callback(lambda _: event.set())
        if not event.wait(timeout):
            raise TimeoutError(f'ROS operation timed out after {timeout:.1f}s')
        return future.result()

    def _dense_path(self, start, target):
        step = max(0.001, float(self.get_parameter('max_interpolation_step_rad').value))
        count = max(2, int(math.ceil(max(abs(b - a) for a, b in zip(start, target)) / step)) + 1)
        return [[a + (b - a) * i / (count - 1) for a, b in zip(start, target)]
                for i in range(count)]

    def _validate(self, states):
        req = ValidateTrajectoryStates.Request()
        req.joint_names = self.joint_names
        req.positions = [value for state in states for value in state]
        req.state_count = len(states)
        req.group_name = self.group
        req.check_collisions = True
        req.max_workers = 0
        timeout = float(self.get_parameter('service_timeout_sec').value)
        if not self.validator.wait_for_service(timeout_sec=timeout):
            raise RuntimeError('MoveIt trajectory validator service is unavailable')
        result = self._wait_future(self.validator.call_async(req), timeout)
        return bool(result.success and result.valid), result.message

    def _parameterize(self, states, velocity_scaling, acceleration_scaling):
        raw = JointTrajectory()
        raw.joint_names = self.joint_names
        # The dense samples exist for planning-scene validation. Passing all of
        # them to Ruckig creates hundreds of collinear micro-segments and can
        # trigger its maximum-duration fallback. A calibration leg is a single
        # straight joint-space motion, so only its endpoints need timing.
        for state in (states[0], states[-1]):
            point = JointTrajectoryPoint()
            point.positions = state
            raw.points.append(point)
        req = ApplyIPP.Request()
        req.trajectory = raw
        req.max_velocity_scaling = float(velocity_scaling)
        req.max_acceleration_scaling = float(acceleration_scaling)
        timeout = float(self.get_parameter('service_timeout_sec').value)
        if not self.ruckig.wait_for_service(timeout_sec=timeout):
            raise RuntimeError('Ruckig service is unavailable')
        result = self._wait_future(self.ruckig.call_async(req), timeout)
        trajectory = result.trajectory.joint_trajectory
        if len(trajectory.points) < 2:
            raise RuntimeError('Ruckig returned an empty trajectory')
        return trajectory

    def _execute(self, trajectory):
        timeout = float(self.get_parameter('motion_timeout_sec').value)
        with self._lock:
            actual = list(self._positions) if self._positions is not None else None
            drive_fault = self._drive_fault_reason
            drives_enabled = getattr(self, '_drives_operation_enabled', False)
        if drive_fault or not drives_enabled:
            raise RuntimeError(drive_fault or 'one or more drives are not operation_enabled')
        expected = list(trajectory.points[0].positions)
        if actual is None or max(abs(a - b) for a, b in zip(actual, expected)) > 0.03:
            raise RuntimeError(
                'robot moved after validation; refusing to dispatch stale trajectory')
        if not self.controller.wait_for_server(timeout_sec=min(timeout, 10.0)):
            raise RuntimeError('FollowJointTrajectory action server is unavailable')
        goal = FollowJointTrajectory.Goal()
        goal.trajectory = trajectory
        handle = self._wait_future(self.controller.send_goal_async(goal), 10.0)
        if not handle.accepted:
            raise RuntimeError('controller rejected trajectory')
        with self._lock:
            self._active_goal = handle
            drive_fault = self._drive_fault_reason
        if drive_fault:
            handle.cancel_goal_async()
            raise RuntimeError(drive_fault)
        result_future = handle.get_result_async()
        try:
            result = self._wait_future(result_future, timeout)
        except TimeoutError:
            self.get_logger().error(
                'Controller result timeout; cancelling unresolved calibration goal')
            cancel_future = handle.cancel_goal_async()
            try:
                self._wait_future(cancel_future, 3.0)
            except TimeoutError:
                self.get_logger().error('Controller goal cancellation acknowledgement timed out')
            raise
        with self._lock:
            self._active_goal = None
            drive_fault = self._drive_fault_reason
        if drive_fault:
            raise RuntimeError(drive_fault)
        if int(result.result.error_code) != 0:
            raise RuntimeError(
                f'controller error {result.result.error_code}: {result.result.error_string}')

    def _targets(self, anchor):
        amplitudes = list(self.get_parameter('joint_sweep_amplitudes_rad').value)
        if len(amplitudes) != len(anchor):
            raise RuntimeError('joint_sweep_amplitudes_rad must match joint_names')
        levels = max(1, int(self.get_parameter('sweep_levels').value))
        velocity_profiles = list(self.get_parameter('velocity_scalings').value)
        acceleration_profiles = list(self.get_parameter('acceleration_scalings').value)
        if not velocity_profiles or len(velocity_profiles) != len(acceleration_profiles):
            raise RuntimeError('velocity_scalings and acceleration_scalings must be equal nonzero lengths')
        profiles = [
            (f'profile_{i + 1}', float(velocity), float(acceleration))
            for i, (velocity, acceleration) in enumerate(
                zip(velocity_profiles, acceleration_profiles))
        ]

        # Explicitly rotate a known-valid arm shape around the base. Unlike the
        # coupled samples, this guarantees candidates in every J1 sector while
        # keeping J2..J6 at the starting configuration.
        rotation_count = max(0, int(self.get_parameter('base_rotation_sample_count').value))
        rotation_min = float(self.get_parameter('base_rotation_min_rad').value)
        rotation_max = float(self.get_parameter('base_rotation_max_rad').value)
        if rotation_count > 0 and rotation_max <= rotation_min:
            raise RuntimeError('base_rotation_max_rad must exceed base_rotation_min_rad')
        for sample in range(rotation_count):
            fraction = sample / max(1, rotation_count - 1)
            target = list(anchor)
            target[0] = rotation_min + (rotation_max - rotation_min) * fraction
            profile_name, velocity, acceleration = profiles[sample % len(profiles)]
            yield (f'base_ring_{sample + 1:03d}', target,
                   profile_name, velocity, acceleration)
        if rotation_count:
            profile_name, velocity, acceleration = profiles[0]
            yield ('base_ring_return', list(anchor), profile_name, velocity, acceleration)

        # Repeat controlled single-axis excitation at each dynamic profile.
        for profile_name, velocity, acceleration in profiles:
            for joint in range(len(anchor)):
                for level in range(1, levels + 1):
                    delta = float(amplitudes[joint]) * level / levels
                    for sign in (1.0, -1.0):
                        target = list(anchor)
                        target[joint] += sign * delta
                        yield (f'{profile_name}_joint_{joint + 1}_{sign * delta:+.3f}',
                               target, profile_name, velocity, acceleration)
                yield (f'{profile_name}_joint_{joint + 1}_return', list(anchor),
                       profile_name, velocity, acceleration)

        lower = list(self.get_parameter('joint_sampling_min_rad').value)
        upper = list(self.get_parameter('joint_sampling_max_rad').value)
        if len(lower) != len(anchor) or len(upper) != len(anchor):
            raise RuntimeError('joint sampling limits must match joint_names')
        bases = [2, 3, 5, 7, 11, 13]
        count = max(0, int(self.get_parameter('coupled_sample_count').value))
        coupled_scale = max(
            0.0, min(1.0, float(self.get_parameter('coupled_amplitude_scale').value)))
        return_interval = max(
            0, int(self.get_parameter('coupled_return_interval').value))
        for sample in range(1, count + 1):
            # Conservative low-discrepancy multi-joint excitation around the
            # run's known-valid anchor.  The previous full-range workspace
            # sampler found configurations whose physical Link_4/Link_6
            # clearance was not represented accurately by the meshes.  Clamp
            # to configured bounds, then let MoveIt validate the dense path and
            # timed trajectory with collision padding before execution.
            target = [
                min(hi, max(lo, anchor[i] +
                    float(amplitudes[i]) * coupled_scale *
                    (2.0 * _halton(sample, bases[i]) - 1.0)))
                for i, (lo, hi) in enumerate(zip(lower, upper))
            ]
            profile_name, velocity, acceleration = profiles[(sample - 1) % len(profiles)]
            yield (f'coupled_{sample:03d}', target,
                   profile_name, velocity, acceleration)
            if return_interval and sample % return_interval == 0:
                yield (f'coupled_{sample:03d}_return', list(anchor),
                       profile_name, velocity, acceleration)
        # Every base-ring and single-joint sequence already returns to anchor.
        # A final return is only required after coupled workspace samples.  Do
        # not send a redundant near-zero trajectory to Ruckig when count is 0.
        if count and not (return_interval and count % return_interval == 0):
            profile_name, velocity, acceleration = profiles[0]
            yield 'return_to_anchor', list(anchor), profile_name, velocity, acceleration

    def _test_targets(self, anchor):
        """Compact bidirectional/profile matrix for finding false positives."""
        amplitudes = list(self.get_parameter('joint_sweep_amplitudes_rad').value)
        velocities = list(self.get_parameter('velocity_scalings').value)
        accelerations = list(self.get_parameter('acceleration_scalings').value)
        if len(amplitudes) != len(anchor):
            raise RuntimeError('joint_sweep_amplitudes_rad must match joint_names')
        if not velocities or len(velocities) != len(accelerations):
            raise RuntimeError('velocity and acceleration profiles must match')
        for profile_index, (velocity, acceleration) in enumerate(
                zip(velocities, accelerations), start=1):
            profile = f'test_profile_{profile_index}'
            for joint, amplitude in enumerate(amplitudes):
                for sign in (1.0, -1.0):
                    target = list(anchor)
                    target[joint] += sign * float(amplitude)
                    yield (f'test_joint_{joint + 1}_{sign:+.0f}', target,
                           profile, float(velocity), float(acceleration))
                yield (f'test_joint_{joint + 1}_return', list(anchor),
                       profile, float(velocity), float(acceleration))

    def _open_run_log(self):
        output = Path(os.path.expanduser(str(self.get_parameter('output_directory').value)))
        output.mkdir(parents=True, exist_ok=True)
        run_id = time.strftime('%Y%m%d-%H%M%S')
        self._run_directory = output / run_id
        self._run_directory.mkdir()
        self._csv_file = open(self._run_directory / 'coverage_points.csv', 'w', newline='')
        self._csv_writer = csv.writer(self._csv_file)
        self._csv_writer.writerow(['unix_time', 'stage', 'x_m', 'y_m', 'z_m'] + self.joint_names)
        if self._run_type == 'external_motion':
            self._training_csv_file = open(
                self._run_directory / 'collision_training.csv', 'w', newline='')
            self._training_csv_writer = csv.writer(self._training_csv_file)
            self._training_csv_writer.writerow([
                'timestamp', 'joint', 'position_rad', 'velocity_rad_s',
                'acceleration_rad_s2', 'torque_sensor_nm', 'measured_torque_nm',
                'expected_torque_nm', 'external_torque_nm',
                'following_error_actual',
            ])
        if self._run_type == 'false_positive_test':
            self._event_csv_file = open(
                self._run_directory / 'false_positive_events.csv', 'w', newline='')
            self._event_csv_writer = csv.writer(self._event_csv_file)
            self._event_csv_writer.writerow([
                'unix_time', 'motion', 'profile', 'joint',
                'external_torque_nm', 'threshold_nm', 'expected_torque_nm',
                'measured_torque_nm', 'positions_rad', 'velocities_rad_s',
                'accelerations_rad_s2'])

    def _write_summary(self):
        with self._lock:
            points = list(self._coverage_points)
            joint_points = list(self._joint_coverage_points)
            run_dir = getattr(self, '_run_directory', None)
            accepted, rejected = self._accepted, self._rejected
            motion_results = list(self._motion_results)
            run_type = self._run_type
            collision_events = list(self._collision_events)
        if run_dir is None:
            return None
        voxel = max(0.001, float(self.get_parameter('coverage_voxel_size_m').value))
        occupied = {tuple(math.floor(v / voxel) for v in p) for p in points}
        summary = {
            'dry_run': self.dry_run, 'run_type': run_type,
            'accepted_motions': accepted,
            'rejected_motions': rejected, 'point_count': len(points),
            'voxel_size_m': voxel, 'occupied_voxel_count': len(occupied),
            'axis_bounds_m': ({axis: {'min': min(p[i] for p in points),
                                      'max': max(p[i] for p in points),
                                      'span': max(p[i] for p in points) - min(p[i] for p in points)}
                               for i, axis in enumerate(('x', 'y', 'z'))} if points else {}),
            'xy_quadrant_point_counts': ({
                'x_pos_y_pos': sum(1 for x, y, _ in points if x >= 0.0 and y >= 0.0),
                'x_neg_y_pos': sum(1 for x, y, _ in points if x < 0.0 and y >= 0.0),
                'x_neg_y_neg': sum(1 for x, y, _ in points if x < 0.0 and y < 0.0),
                'x_pos_y_neg': sum(1 for x, y, _ in points if x >= 0.0 and y < 0.0),
            } if points else {}),
            'joint_space_bounds_rad': ({
                name: {
                    'min': min(q[i] for q in joint_points),
                    'max': max(q[i] for q in joint_points),
                    'span': max(q[i] for q in joint_points) - min(q[i] for q in joint_points),
                }
                for i, name in enumerate(self.joint_names)
            } if joint_points else {}),
            # A 0.02 rad bin suppresses encoder noise while retaining genuinely
            # different calibration postures.
            'unique_joint_configurations_0_02rad': len({
                tuple(round(value / 0.02) for value in q) for q in joint_points
            }),
            'motion_results': motion_results,
            'collision_event_count': len(collision_events),
            'collision_events': collision_events,
        }
        path = run_dir / 'coverage_summary.json'
        path.write_text(json.dumps(summary, indent=2) + '\n')
        return path

    def _run(self):
        try:
            self._open_run_log()
            if self._run_type == 'external_motion':
                with self._lock:
                    self._stage = 'recording_external_motion'
                    self._dynamic_profile = 'paint_process'
                while True:
                    with self._lock:
                        if self._stop_requested:
                            break
                    time.sleep(0.05)
                with self._lock:
                    self._stage = 'stopped'
                    self._dynamic_profile = 'none'
                return
            with self._lock:
                anchor = list(self._positions)
            planned_start = list(anchor)
            target_source = (
                self._test_targets(anchor)
                if self._run_type == 'false_positive_test'
                else self._targets(anchor))
            for label, target, profile_name, velocity, acceleration in target_source:
                with self._lock:
                    if self._stop_requested:
                        break
                    actual = list(self._positions) if not self.dry_run else planned_start
                    self._stage = f'validating:{label}'
                    self._dynamic_profile = (
                        f'{profile_name}: velocity={velocity:.3f}, acceleration={acceleration:.3f}')
                max_delta = max(abs(target_value - actual_value)
                                for actual_value, target_value in zip(actual, target))
                # The real controller commonly settles a few tenths of a
                # milliradian away from the commanded endpoint.  Such a move is
                # below useful calibration resolution and can collapse to an
                # empty Ruckig trajectory after duplicate-point filtering.
                if max_delta <= 1.0e-3:
                    with self._lock:
                        self._accepted += 1
                        self._stage = f'noop:{label}'
                        self._motion_results.append({
                            'motion': label, 'profile': profile_name,
                            'velocity_scaling': velocity,
                            'acceleration_scaling': acceleration,
                            'accepted': True, 'validation_stage': 'noop',
                            'reason': 'already at target',
                        })
                    planned_start = list(target)
                    continue
                dense = self._dense_path(actual, target)
                valid, reason = self._validate(dense)
                if not valid:
                    with self._lock:
                        self._rejected += 1
                        self._motion_results.append({
                            'motion': label, 'profile': profile_name,
                            'velocity_scaling': velocity,
                            'acceleration_scaling': acceleration,
                            'accepted': False, 'validation_stage': 'pre_timing',
                            'reason': reason,
                        })
                    self.get_logger().warning(f'Skipping {label}: MoveIt rejected path: {reason}')
                    continue
                trajectory = self._parameterize(dense, velocity, acceleration)
                timed_states = [list(point.positions) for point in trajectory.points]
                # Densify every returned segment so timing cannot hide a collision gap.
                post_states = []
                for a, b in zip(timed_states, timed_states[1:]):
                    segment = self._dense_path(a, b)
                    post_states.extend(segment[:-1])
                post_states.append(timed_states[-1])
                valid, reason = self._validate(post_states)
                if not valid:
                    with self._lock:
                        self._rejected += 1
                        self._motion_results.append({
                            'motion': label, 'profile': profile_name,
                            'velocity_scaling': velocity,
                            'acceleration_scaling': acceleration,
                            'accepted': False, 'validation_stage': 'post_timing',
                            'reason': reason,
                        })
                    self.get_logger().warning(f'Skipping {label}: timed path rejected: {reason}')
                    continue
                with self._lock:
                    self._accepted += 1
                    self._motion_results.append({
                        'motion': label, 'profile': profile_name,
                        'velocity_scaling': velocity,
                        'acceleration_scaling': acceleration,
                        'accepted': True, 'validation_stage': 'both',
                        'reason': '',
                    })
                    self._stage = ('dry_run:' if self.dry_run else 'executing:') + label
                if self.dry_run:
                    planned_start = list(target)
                else:
                    self._execute(trajectory)
                    time.sleep(max(0.0, float(self.get_parameter('settle_time_sec').value)))
            with self._lock:
                self._stage = 'stopped' if self._stop_requested else 'complete'
                self._dynamic_profile = 'none'
        except Exception as exc:
            self.get_logger().error(f'Calibration aborted: {exc}')
            with self._lock:
                self._stage = f'error:{exc}'
        finally:
            if self._csv_file is not None:
                self._csv_file.flush()
                self._csv_file.close()
                self._csv_file = None
                self._csv_writer = None
            if self._event_csv_file is not None:
                self._event_csv_file.flush()
                self._event_csv_file.close()
                self._event_csv_file = None
                self._event_csv_writer = None
            if self._training_csv_file is not None:
                self._training_csv_file.flush()
                self._training_csv_file.close()
                self._training_csv_file = None
                self._training_csv_writer = None
            path = self._write_summary()
            if path:
                self.get_logger().info(f'Calibration coverage summary: {path}')
            with self._lock:
                self._active_goal = None
                self._running = False

    def _append_external_training_sample(self, msg: DynamicJointState) -> None:
        """Write one synchronized, model-ready sample for every reported joint."""
        writer = self._training_csv_writer
        handle = self._training_csv_file
        if writer is None or handle is None:
            return
        timestamp = time.time()
        period = max(0.0, float(self.get_parameter('coverage_log_period_sec').value))
        if timestamp - self._last_training_write < period:
            return
        positions = dict(zip(self.joint_names, self._positions or []))
        velocities = dict(zip(self.joint_names, self._velocities or []))
        accelerations = dict(zip(self.joint_names, self._accelerations or []))
        for joint_name, values in zip(msg.joint_names, msg.interface_values):
            fields = dict(zip(values.interface_names, values.values))
            writer.writerow([
                f'{timestamp:.9f}', joint_name,
                positions.get(joint_name, fields.get('position', math.nan)),
                velocities.get(joint_name, fields.get('velocity', math.nan)),
                accelerations.get(joint_name, math.nan),
                fields.get('torque_sensor', math.nan),
                fields.get('measured_torque', math.nan),
                fields.get('expected_torque', math.nan),
                fields.get('external_torque', math.nan),
                fields.get('following_error_actual', math.nan),
            ])
        handle.flush()
        self._last_training_write = timestamp


def main(args=None):
    rclpy.init(args=args)
    node = CalibrationRunner()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
