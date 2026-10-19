#!/usr/bin/env python3
"""Deprecated Python observer retained only for offline comparison and tests.

Production launch files use ``zeroerr/RealtimeCollisionController`` exclusively.
Do not run both observers at the same time.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import rclpy
from control_msgs.msg import DynamicJointState, InterfaceValue
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import JointState
from std_msgs.msg import String

JOINT_NAMES = [f"Joint_{index}" for index in range(1, 7)]
INTERFACE_DEFAULTS = {
    "motor_actual_current": None,
    "following_error_actual": None,
    "torque_sensor": None,
    "statusword": None,
    "error_code": None,
    "mode_display": None,
}

PLOT_METRICS = {
    "zero_reference": lambda self, slave: 0.0,
    "position": lambda self, slave: slave.get("position"),
    "velocity": lambda self, slave: slave.get("velocity"),
    "following_error_actual": lambda self, slave: slave.get("following_error_actual"),
    "torque_sensor": lambda self, slave: slave.get("torque_sensor"),
    "friction_torque": lambda self, slave: self._friction_torque_by_joint.get(str(slave["joint"])),
    "measured_torque": lambda self, slave: self._measured_torque_by_joint.get(str(slave["joint"])),
    "expected_torque": lambda self, slave: self._expected_torque_by_joint.get(str(slave["joint"])),
    "observer_auxiliary_torque": lambda self, slave: self._observer_auxiliary_torque_by_joint.get(str(slave["joint"])),
    "torque_difference": lambda self, slave: self._torque_difference_by_joint.get(str(slave["joint"])),
    "external_torque": lambda self, slave: self._external_torque_by_joint.get(str(slave["joint"])),
    "external_torque_threshold": lambda self, slave: self._current_external_torque_thresholds.get(str(slave["joint"])),
    "negative_external_torque_threshold": lambda self, slave: -self._current_external_torque_thresholds.get(
        str(slave["joint"]), 0.0
    ),
    "contact_active": lambda self, slave: 1.0 if self._contact_active[str(slave["joint"])] else 0.0,
    "contact_latched": lambda self, slave: 1.0 if self._contact_latched[str(slave["joint"])] else 0.0,
    "dynamics_active": lambda self, slave: 1.0 if self._dynamics_active[str(slave["joint"])] else 0.0,
    "dynamics_latched": lambda self, slave: 1.0 if self._dynamics_latched[str(slave["joint"])] else 0.0,
}

DEFAULT_EFFORT_THRESHOLDS = [20.0, 20.0, 15.0, 8.0, 6.0, 4.0]
DEFAULT_FOLLOWING_ERROR_THRESHOLDS = [4000.0, 4000.0, 3500.0, 2000.0, 1500.0, 1200.0]
DEFAULT_COLLISION_CONFIG_PATH = str(
    Path(__file__).resolve().parents[2] / "config" / "collision_monitor_config.json"
)


class ZeroErrCollisionMonitor(Node):
    def __init__(self) -> None:
        super().__init__("zeroerr_collision_monitor")
        self.get_logger().warning(
            "DEPRECATED: use zeroerr/RealtimeCollisionController; "
            "the Python collision observer is not a production fallback"
        )

        self.declare_parameter("slave_count", 6)
        self.declare_parameter("poll_period_sec", 2.0)
        self.declare_parameter("input_sample_period_sec", 0.0)
        self.declare_parameter("input_timeout_sec", 0.25)
        self.declare_parameter("print_table", False)
        self.declare_parameter("confirm_duration_ms", 25.0)
        self.declare_parameter("expected_input_rate_hz", 2000.0)
        self.declare_parameter("late_sample_threshold_ms", 2.0)
        self.declare_parameter("confirmation_max_sample_gap_ms", 2.0)
        self.declare_parameter("dynamic_threshold_max_ratio", 5.0)
        self.declare_parameter("effort_thresholds", DEFAULT_EFFORT_THRESHOLDS)
        self.declare_parameter(
            "following_error_thresholds",
            DEFAULT_FOLLOWING_ERROR_THRESHOLDS,
        )
        self.declare_parameter("friction_coulomb_nm", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.declare_parameter("friction_viscous_nm_per_rad_s", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.declare_parameter("friction_velocity_deadband_rad_s", 0.01)
        self.declare_parameter("urdf_path", "")
        self.declare_parameter("base_link", "base_link")
        self.declare_parameter("tip_link", "tool0")
        self.declare_parameter("num_joints", 6)
        self.declare_parameter("external_torque_thresholds", [12.0, 12.0, 10.0, 8.0, 6.0, 5.0])
        self.declare_parameter("filter_alpha", 0.7)
        self.declare_parameter("include_gravity", False)
        self.declare_parameter("static_torque_bias_nm", [0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
        self.declare_parameter("warmup_sec", 8.0)
        self.declare_parameter("warmup_vel_threshold_rad_s", 0.02)
        self.declare_parameter("warmup_min_samples", 20)
        self.declare_parameter("observer_gain", 10.0)
        self.declare_parameter("drive_stable_sec", 2.0)
        self.declare_parameter("collision_config_path", DEFAULT_COLLISION_CONFIG_PATH)
        self.declare_parameter("torque_log_enabled", False)
        self.declare_parameter(
            "torque_log_path",
            str(Path(__file__).resolve().parents[1] / "data" / "torque_sensor_log.csv"),
        )
        self.declare_parameter("torque_log_min_velocity_rad_s", 0.01)
        self.declare_parameter("torque_log_min_acceleration_rad_s2", 0.05)
        self.declare_parameter("torque_log_idle_timeout_s", 2.0)
        self.declare_parameter("torque_log_period_sec", 0.05)

        self._slave_count = int(self.get_parameter("slave_count").value)
        self._print_table = bool(self.get_parameter("print_table").value)
        self._confirm_duration_sec = max(
            0.0,
            float(self.get_parameter("confirm_duration_ms").value) * 1.0e-3,
        )
        self._expected_input_rate_hz = max(
            1.0, float(self.get_parameter("expected_input_rate_hz").value))
        self._expected_input_period_sec = 1.0 / self._expected_input_rate_hz
        self._late_sample_threshold_sec = max(
            0.0,
            float(self.get_parameter("late_sample_threshold_ms").value) * 1.0e-3,
        )
        self._confirmation_max_sample_gap_sec = max(
            self._expected_input_period_sec,
            float(self.get_parameter("confirmation_max_sample_gap_ms").value)
            * 1.0e-3,
        )
        friction_coulomb_nm = list(self.get_parameter("friction_coulomb_nm").value)
        friction_viscous_nm_per_rad_s = list(
            self.get_parameter("friction_viscous_nm_per_rad_s").value
        )
        self._friction_velocity_deadband_rad_s = float(
            self.get_parameter("friction_velocity_deadband_rad_s").value
        )
        period = float(self.get_parameter("poll_period_sec").value)
        self._input_sample_period_sec = max(
            0.0,
            float(self.get_parameter("input_sample_period_sec").value),
        )
        self._last_dynamic_sample_time: Optional[float] = None
        self._last_dynamic_source_timestamp: Optional[float] = None
        self._dynamic_sample_complete = False
        self._timing_started_monotonic = time.monotonic()
        self._received_sample_count = 0
        self._processed_sample_count = 0
        self._rejected_sample_count = 0
        self._throttled_sample_count = 0
        self._out_of_order_sample_count = 0
        self._late_sample_count = 0
        self._estimated_missing_sample_count = 0
        self._last_callback_arrival_monotonic: Optional[float] = None
        self._source_intervals_sec = deque(maxlen=20000)
        self._arrival_intervals_sec = deque(maxlen=20000)
        self._sample_ages_sec = deque(maxlen=20000)
        self._observer_update_durations_sec = deque(maxlen=20000)
        self._kdl_model_durations_sec = deque(maxlen=20000)
        self._observer_non_model_durations_sec = deque(maxlen=20000)
        self._callback_durations_sec = deque(maxlen=20000)
        self._cached_timing_snapshot: Dict[str, object] = {}
        self._last_timing_snapshot_monotonic: Optional[float] = None
        self._observer_inputs_valid = False
        self._last_input_invalid_reason = ""
        self._all_drives_op_since: Optional[float] = None
        effort_thresholds = list(self.get_parameter("effort_thresholds").value)
        following_error_thresholds = list(
            self.get_parameter("following_error_thresholds").value
        )
        external_torque_thresholds = list(
            self.get_parameter("external_torque_thresholds").value
        )
        self._effort_thresholds = {
            joint_name: float(effort_thresholds[index])
            for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count])
        }
        self._following_error_thresholds = {
            joint_name: float(following_error_thresholds[index])
            for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count])
        }
        self._external_torque_thresholds = {
            joint_name: float(external_torque_thresholds[index])
            for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count])
        }
        self._dynamic_threshold_enabled = False
        self._dynamic_threshold_coefficients = {
            joint_name: np.zeros(9, dtype=float)
            for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._dynamic_threshold_training_limits = {
            joint_name: np.array([np.inf, np.inf], dtype=float)
            for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._dynamic_threshold_decay_sec = 0.35
        self._dynamic_threshold_max_ratio = max(
            1.0,
            float(self.get_parameter("dynamic_threshold_max_ratio").value),
        )
        self._dynamic_threshold_envelope = {
            joint_name: np.zeros(4, dtype=float)
            for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._dynamic_threshold_last_timestamp = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._current_external_torque_thresholds = dict(self._external_torque_thresholds)
        self._collision_sensitivity_percent = 100.0
        self._active_stop_enabled = False
        self._detection_enabled = True
        self._effort_following_error_detection_enabled = False
        self._diagnostics_enabled = False
        self._detection_suppressed = False
        self._stop_request_armed = True
        self._friction_coulomb_nm = {
            joint_name: float(friction_coulomb_nm[index])
            for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count])
        }
        self._friction_viscous_nm_per_rad_s = {
            joint_name: float(friction_viscous_nm_per_rad_s[index])
            for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count])
        }
        self._position_correction_coefficients = {
            joint_name: np.zeros(9, dtype=float)
            for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._motion_residual_correction_coefficients = {
            joint_name: np.zeros(6, dtype=float)
            for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._motion_residual_correction_limits = {
            joint_name: np.array([np.inf, np.inf], dtype=float)
            for joint_name in JOINT_NAMES[: self._slave_count]
        }

        self._latest_payload: Dict[str, Dict[str, Optional[float]]] = {
            joint_name: {
                "position": None,
                "velocity": None,
                "effort": None,
                **INTERFACE_DEFAULTS,
            }
            for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._dynamic_state_seen = False
        self._dynamic_state_warned = False
        self._contact_cycles = {joint_name: 0 for joint_name in JOINT_NAMES[: self._slave_count]}
        self._contact_latched = {joint_name: False for joint_name in JOINT_NAMES[: self._slave_count]}
        self._dynamics_cycles = {joint_name: 0 for joint_name in JOINT_NAMES[: self._slave_count]}
        self._contact_exceedance_since = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._dynamics_exceedance_since = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._dynamics_latched = {joint_name: False for joint_name in JOINT_NAMES[: self._slave_count]}
        self._contact_active = {joint_name: False for joint_name in JOINT_NAMES[: self._slave_count]}
        self._dynamics_active = {joint_name: False for joint_name in JOINT_NAMES[: self._slave_count]}
        self._contact_reason = {joint_name: "" for joint_name in JOINT_NAMES[: self._slave_count]}
        self._dynamics_reason = {joint_name: "" for joint_name in JOINT_NAMES[: self._slave_count]}
        self._expected_torque_by_joint = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._observer_auxiliary_torque_by_joint = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._friction_torque_by_joint = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._measured_torque_by_joint = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._torque_difference_by_joint = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._external_torque_by_joint = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._last_velocity_vector: Optional[np.ndarray] = None
        self._last_velocity_timestamp: Optional[float] = None
        self._acceleration_by_joint = {
            joint_name: 0.0 for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._last_logged_velocity_by_joint = {
            joint_name: None for joint_name in JOINT_NAMES[: self._slave_count]
        }
        self._last_logged_timestamp: Optional[float] = None
        self._estimator: Optional[object] = None
        self._dynamics_enabled = False

        self._init_inverse_dynamics_model()

        self._collision_config_path = Path(
            str(self.get_parameter("collision_config_path").value)
        )
        self._load_persisted_config()
        self._filter_alpha = float(self.get_parameter("filter_alpha").value)
        self._torque_log_enabled = bool(self.get_parameter("torque_log_enabled").value)
        self._torque_log_path = Path(str(self.get_parameter("torque_log_path").value))
        self._torque_log_min_velocity_rad_s = float(
            self.get_parameter("torque_log_min_velocity_rad_s").value
        )
        self._torque_log_min_acceleration_rad_s2 = float(
            self.get_parameter("torque_log_min_acceleration_rad_s2").value
        )
        self._torque_log_idle_timeout_s = float(
            self.get_parameter("torque_log_idle_timeout_s").value
        )
        self._torque_log_period_sec = max(
            0.0, float(self.get_parameter("torque_log_period_sec").value)
        )
        self._torque_log_header_written = False
        self._last_substantial_motion_timestamp: Optional[float] = None
        if self._torque_log_enabled:
            self._init_torque_log()

        self._json_pub = self.create_publisher(String, "/zeroerr/collision_monitor/json", 10)
        self._table_pub = self.create_publisher(String, "/zeroerr/collision_monitor/table", 10)
        self._state_pub = self.create_publisher(
            DynamicJointState,
            "/zeroerr/collision_monitor/state",
            10,
        )
        self._plot_publishers = {
            metric: self.create_publisher(
                JointState,
                f"/zeroerr/collision_monitor/plot/{metric}",
                qos_profile_sensor_data,
            )
            for metric in PLOT_METRICS
        }
        self._config_pub = self.create_publisher(
            String,
            "/zeroerr/collision_monitor/config_state",
            10,
        )
        self._stop_request_pub = self.create_publisher(
            String,
            "/zeroerr/collision_monitor/stop_request",
            10,
        )

        self.create_subscription(
            DynamicJointState,
            "/dynamic_joint_states",
            self._on_dynamic_joint_states,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            String,
            "/zeroerr/collision_monitor/config",
            self._on_config,
            10,
        )
        self.create_subscription(
            String,
            "/zeroerr/collision_monitor/acknowledged",
            self._on_collision_acknowledged,
            10,
        )
        self.create_timer(period, self._publish_snapshot)

        self.get_logger().info(
            "[ZeroErrCollisionMonitor] Using atomic PDO-backed position, velocity, "
            "and torque samples from /dynamic_joint_states"
        )
        if self._dynamics_enabled:
            self.get_logger().info(
                "[ZeroErrCollisionMonitor] Inverse dynamics enabled with explicit ZeroErr model"
            )
        if self._input_sample_period_sec > 0.0:
            self.get_logger().info(
                "[ZeroErrCollisionMonitor] Input state processing throttled to "
                f"{1.0 / self._input_sample_period_sec:.1f} Hz"
            )

    def _on_dynamic_joint_states(self, msg: DynamicJointState) -> None:
        callback_started = time.perf_counter()
        arrival_monotonic = time.monotonic()
        self._received_sample_count += 1
        if self._last_callback_arrival_monotonic is not None:
            self._arrival_intervals_sec.append(
                max(0.0, arrival_monotonic - self._last_callback_arrival_monotonic))
        self._last_callback_arrival_monotonic = arrival_monotonic
        processed_before = self._processed_sample_count
        try:
            self._process_dynamic_joint_states(msg)
        finally:
            if self._processed_sample_count == processed_before:
                self._rejected_sample_count += 1
            self._callback_durations_sec.append(
                max(0.0, time.perf_counter() - callback_started))

    def _process_dynamic_joint_states(self, msg: DynamicJointState) -> None:
        now = self.get_clock().now().nanoseconds * 1e-9
        if (
            self._input_sample_period_sec > 0.0
            and self._last_dynamic_sample_time is not None
            and now - self._last_dynamic_sample_time < self._input_sample_period_sec
        ):
            self._throttled_sample_count += 1
            return
        by_name = {
            joint_name: index for index, joint_name in enumerate(msg.joint_names)
        }
        required_interfaces = {
            "position", "velocity", "torque_sensor", "statusword", "error_code",
        }
        if self._effort_following_error_detection_enabled:
            required_interfaces.add("following_error_actual")
        updates = {}
        for joint_name in JOINT_NAMES[: self._slave_count]:
            index = by_name.get(joint_name)
            if index is None or index >= len(msg.interface_values):
                self._dynamic_sample_complete = False
                return
            interface_value = msg.interface_values[index]
            values = dict(zip(interface_value.interface_names, interface_value.values))
            if any(
                name not in values or not np.isfinite(values[name])
                for name in required_interfaces
            ):
                self._dynamic_sample_complete = False
                return
            updates[joint_name] = {
                name: float(value)
                for name, value in values.items()
                if name in INTERFACE_DEFAULTS and np.isfinite(value)
            }
            updates[joint_name]["position"] = float(values["position"])
            updates[joint_name]["velocity"] = float(values["velocity"])
            updates[joint_name]["effort"] = (
                float(values["effort"])
                if "effort" in values and np.isfinite(values["effort"])
                else None
            )

        try:
            source_timestamp = self._message_timestamp(msg)
        except ValueError as exc:
            self._dynamic_sample_complete = False
            self._invalidate_observer_inputs(str(exc))
            return
        previous_timestamp = self._last_dynamic_source_timestamp
        if previous_timestamp is not None and source_timestamp <= previous_timestamp:
            self._out_of_order_sample_count += 1
            self.get_logger().warning(
                "[ZeroErrCollisionMonitor] Ignoring duplicate/out-of-order dynamic "
                f"sample timestamp={source_timestamp:.9f} previous={previous_timestamp:.9f}"
            )
            return

        sample_age = now - source_timestamp
        if np.isfinite(sample_age):
            self._sample_ages_sec.append(sample_age)
            if sample_age > self._late_sample_threshold_sec:
                self._late_sample_count += 1
        if previous_timestamp is not None:
            source_interval = source_timestamp - previous_timestamp
            self._source_intervals_sec.append(source_interval)
            if source_interval > 1.5 * self._expected_input_period_sec:
                self._estimated_missing_sample_count += max(
                    0,
                    int(round(source_interval / self._expected_input_period_sec)) - 1,
                )
            if source_interval > self._confirmation_max_sample_gap_sec:
                self._reset_confirmation_windows()

        timeout = max(0.01, float(self.get_parameter("input_timeout_sec").value))
        if (
            previous_timestamp is not None
            and source_timestamp - previous_timestamp > timeout
        ):
            self._invalidate_observer_inputs(
                "dynamic input source gap "
                f"dt={source_timestamp - previous_timestamp:.6f}s "
                f"limit={timeout:.6f}s"
            )
        for joint_name, values in updates.items():
            self._latest_payload[joint_name].update(values)
        self._last_dynamic_sample_time = now
        self._last_dynamic_source_timestamp = source_timestamp
        self._dynamic_sample_complete = True
        self._dynamic_state_seen = True

        slaves = self._build_atomic_slaves()
        self._observer_inputs_valid = True
        self._last_input_invalid_reason = ""
        observer_started = time.perf_counter()
        if self._estimator is not None:
            self._estimator.last_model_duration_sec = 0.0
            self._estimator.last_update_duration_sec = 0.0
        self._update_external_torque_estimate(slaves, source_timestamp)
        self._observer_update_durations_sec.append(
            max(0.0, time.perf_counter() - observer_started))
        model_duration = float(getattr(
            self._estimator, "last_model_duration_sec", 0.0))
        update_duration = float(getattr(
            self._estimator, "last_update_duration_sec", 0.0))
        if update_duration > 0.0 and np.isfinite(model_duration):
            self._kdl_model_durations_sec.append(max(0.0, model_duration))
        if update_duration > 0.0 and np.isfinite(update_duration):
            self._observer_non_model_durations_sec.append(
                max(0.0, update_duration - model_duration))
        self._evaluate_collisions(slaves, source_timestamp)
        self._processed_sample_count += 1

    @staticmethod
    def _message_timestamp(msg: DynamicJointState) -> float:
        stamp = msg.header.stamp
        timestamp = float(stamp.sec) + float(stamp.nanosec) * 1e-9
        if timestamp <= 0.0 or not np.isfinite(timestamp):
            raise ValueError("dynamic input source timestamp is missing or non-finite")
        return timestamp

    def _build_atomic_slaves(self) -> List[Dict[str, Optional[float]]]:
        slaves = []
        for slave_index, joint_name in enumerate(JOINT_NAMES[: self._slave_count]):
            state = dict(self._latest_payload[joint_name])
            state["joint"] = joint_name
            state["slave"] = slave_index
            state["friction_torque"] = self._compute_friction_torque(
                joint_name, state.get("velocity"))
            self._friction_torque_by_joint[joint_name] = state["friction_torque"]
            state["measured_torque"] = self._compute_measured_torque(
                state.get("torque_sensor"))
            self._measured_torque_by_joint[joint_name] = state["measured_torque"]
            slaves.append(state)
        return slaves

    def _on_config(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except json.JSONDecodeError as exc:
            self.get_logger().warning(
                f"[ZeroErrCollisionMonitor] Ignoring invalid config JSON: {exc}"
            )
            return

        updated = self._apply_runtime_config(payload)
        if updated:
            try:
                self._collision_config_path.parent.mkdir(parents=True, exist_ok=True)
                self._collision_config_path.write_text(
                    json.dumps(
                        {
                            "confirm_duration_ms": self._confirm_duration_sec * 1000.0,
                            "effort_thresholds": [
                                self._effort_thresholds[joint_name]
                                for joint_name in JOINT_NAMES[: self._slave_count]
                            ],
                            "following_error_thresholds": [
                                self._following_error_thresholds[joint_name]
                                for joint_name in JOINT_NAMES[: self._slave_count]
                            ],
                            "external_torque_thresholds": [
                                self._external_torque_thresholds[joint_name]
                                for joint_name in JOINT_NAMES[: self._slave_count]
                            ],
                            "collision_sensitivity_percent": self._collision_sensitivity_percent,
                            "active_stop_enabled": self._active_stop_enabled,
                            "detection_enabled": self._detection_enabled,
                            "effort_following_error_detection_enabled":
                                self._effort_following_error_detection_enabled,
                            "diagnostics_enabled": self._diagnostics_enabled,
                            "dynamic_threshold_enabled": self._dynamic_threshold_enabled,
                            "dynamic_threshold_feature_names": [
                                "bias", "positive_velocity", "negative_velocity",
                                "positive_acceleration", "negative_acceleration",
                                "positive_velocity_squared", "negative_velocity_squared",
                                "positive_acceleration_squared", "negative_acceleration_squared",
                            ],
                            "dynamic_threshold_coefficients": {
                                joint_name: self._dynamic_threshold_coefficients[joint_name].tolist()
                                for joint_name in JOINT_NAMES[: self._slave_count]
                            },
                            "dynamic_threshold_training_limits": {
                                joint_name: self._dynamic_threshold_training_limits[joint_name].tolist()
                                for joint_name in JOINT_NAMES[: self._slave_count]
                            },
                            "dynamic_threshold_decay_sec": self._dynamic_threshold_decay_sec,
                            "dynamic_threshold_max_ratio": self._dynamic_threshold_max_ratio,
                            "friction_coulomb_nm": [
                                self._friction_coulomb_nm[joint_name]
                                for joint_name in JOINT_NAMES[: self._slave_count]
                            ],
                            "friction_viscous_nm_per_rad_s": [
                                self._friction_viscous_nm_per_rad_s[joint_name]
                                for joint_name in JOINT_NAMES[: self._slave_count]
                            ],
                            "position_correction_coefficients": {
                                joint_name: self._position_correction_coefficients[
                                    joint_name].tolist()
                                for joint_name in JOINT_NAMES[: self._slave_count]
                                if np.any(self._position_correction_coefficients[joint_name])
                            },
                            "motion_residual_correction_coefficients": {
                                joint_name: self._motion_residual_correction_coefficients[
                                    joint_name].tolist()
                                for joint_name in JOINT_NAMES[: self._slave_count]
                                if np.any(self._motion_residual_correction_coefficients[joint_name])
                            },
                            "motion_residual_correction_limits": {
                                joint_name: self._motion_residual_correction_limits[
                                    joint_name].tolist()
                                for joint_name in JOINT_NAMES[: self._slave_count]
                                if np.all(np.isfinite(
                                    self._motion_residual_correction_limits[joint_name]))
                            },
                            "friction_velocity_deadband_rad_s": self._friction_velocity_deadband_rad_s,
                        },
                        indent=2,
                        sort_keys=True,
                    ),
                    encoding="utf-8",
                )
            except Exception as exc:
                self.get_logger().warning(
                    f"[ZeroErrCollisionMonitor] Failed to persist config to {self._collision_config_path}: {exc}"
                )
            self.get_logger().info(
                "[ZeroErrCollisionMonitor] Runtime config updated"
            )

    def _apply_runtime_config(self, payload: Dict[str, object]) -> bool:
        updated = False
        confirm_duration_ms = payload.get("confirm_duration_ms")
        if confirm_duration_ms is not None:
            value = float(confirm_duration_ms)
            if np.isfinite(value):
                self._confirm_duration_sec = float(np.clip(value, 0.0, 1000.0)) * 1.0e-3
                updated = True
        elif payload.get("confirm_cycles") is not None:
            # Read-only migration for older persisted configurations. New API
            # clients must send an explicit duration so behavior is independent
            # of callback/update frequency. The old detector evaluated at
            # 200 Hz, so preserve its historical 5 ms-per-cycle semantics.
            self._confirm_duration_sec = (
                max(1, int(payload["confirm_cycles"]))
                * 0.005
            )
            updated = True

        updated |= self._apply_threshold_update(
            payload.get("effort_thresholds"),
            self._effort_thresholds,
        )
        updated |= self._apply_threshold_update(
            payload.get("following_error_thresholds"),
            self._following_error_thresholds,
        )
        updated |= self._apply_threshold_update(
            payload.get("external_torque_thresholds"),
            self._external_torque_thresholds,
        )
        sensitivity = payload.get("collision_sensitivity_percent")
        if sensitivity is not None:
            sensitivity_value = float(sensitivity)
            if np.isfinite(sensitivity_value):
                self._collision_sensitivity_percent = float(
                    np.clip(sensitivity_value, 50.0, 200.0))
                updated = True
        active_stop_enabled = payload.get("active_stop_enabled")
        if active_stop_enabled is not None:
            self._active_stop_enabled = bool(active_stop_enabled)
            updated = True
        detection_enabled = payload.get("detection_enabled")
        if detection_enabled is not None:
            self._detection_enabled = bool(detection_enabled)
            updated = True
        secondary_enabled = payload.get(
            "effort_following_error_detection_enabled")
        if secondary_enabled is not None:
            self._effort_following_error_detection_enabled = bool(
                secondary_enabled)
            updated = True
        diagnostics_enabled = payload.get("diagnostics_enabled")
        if diagnostics_enabled is not None:
            requested = bool(diagnostics_enabled)
            if requested != self._diagnostics_enabled:
                self._diagnostics_enabled = requested
                self.get_logger().info(
                    "[ZeroErrCollisionMonitor] Live observer diagnostics %s"
                    % ("enabled" if requested else "disabled")
                )
            updated = True
        detection_suppressed = payload.get("collision_detection_suppressed")
        if detection_suppressed is not None:
            requested = bool(detection_suppressed)
            if requested != self._detection_suppressed:
                self._detection_suppressed = requested
                self.get_logger().warning(
                    "[ZeroErrCollisionMonitor] collision detection %s for recovery jog"
                    % ("SUPPRESSED" if requested else "restored")
                )
        dynamic_threshold_enabled = payload.get("dynamic_threshold_enabled")
        if dynamic_threshold_enabled is not None:
            self._dynamic_threshold_enabled = bool(dynamic_threshold_enabled)
            updated = True
        dynamic_coefficients = payload.get("dynamic_threshold_coefficients")
        if isinstance(dynamic_coefficients, dict):
            for joint_name, values in dynamic_coefficients.items():
                if joint_name not in self._dynamic_threshold_coefficients:
                    continue
                if isinstance(values, list) and len(values) == 9:
                    coefficients = np.asarray(values, dtype=float)
                    if np.all(np.isfinite(coefficients)):
                        self._dynamic_threshold_coefficients[joint_name] = coefficients
                        updated = True
        dynamic_limits = payload.get("dynamic_threshold_training_limits")
        if isinstance(dynamic_limits, dict):
            for joint_name, values in dynamic_limits.items():
                if joint_name not in self._dynamic_threshold_training_limits:
                    continue
                if isinstance(values, list) and len(values) == 2:
                    limits = np.asarray(values, dtype=float)
                    if np.all(np.isfinite(limits)) and np.all(limits > 0.0):
                        self._dynamic_threshold_training_limits[joint_name] = limits
                        updated = True
        dynamic_decay = payload.get("dynamic_threshold_decay_sec")
        if dynamic_decay is not None:
            self._dynamic_threshold_decay_sec = max(0.01, float(dynamic_decay))
            updated = True
        dynamic_max_ratio = payload.get("dynamic_threshold_max_ratio")
        if dynamic_max_ratio is not None:
            ratio = float(dynamic_max_ratio)
            if np.isfinite(ratio):
                self._dynamic_threshold_max_ratio = float(np.clip(ratio, 1.0, 20.0))
                updated = True
        updated |= self._apply_threshold_update(
            payload.get("friction_coulomb_nm"),
            self._friction_coulomb_nm,
        )
        updated |= self._apply_threshold_update(
            payload.get("friction_viscous_nm_per_rad_s"),
            self._friction_viscous_nm_per_rad_s,
        )
        position_corrections = payload.get("position_correction_coefficients")
        if isinstance(position_corrections, dict):
            for joint_name, values in position_corrections.items():
                if joint_name not in self._position_correction_coefficients:
                    continue
                if isinstance(values, list) and len(values) == 9:
                    self._position_correction_coefficients[joint_name] = np.asarray(
                        values, dtype=float)
                    updated = True
        motion_corrections = payload.get("motion_residual_correction_coefficients")
        if isinstance(motion_corrections, dict):
            for joint_name, values in motion_corrections.items():
                if joint_name not in self._motion_residual_correction_coefficients:
                    continue
                if isinstance(values, list) and len(values) == 6:
                    coefficients = np.asarray(values, dtype=float)
                    if np.all(np.isfinite(coefficients)):
                        self._motion_residual_correction_coefficients[joint_name] = coefficients
                        updated = True
        motion_limits = payload.get("motion_residual_correction_limits")
        if isinstance(motion_limits, dict):
            for joint_name, values in motion_limits.items():
                if joint_name not in self._motion_residual_correction_limits:
                    continue
                if isinstance(values, list) and len(values) == 2:
                    limits = np.asarray(values, dtype=float)
                    if np.all(np.isfinite(limits)) and np.all(limits > 0.0):
                        self._motion_residual_correction_limits[joint_name] = limits
                        updated = True
        friction_velocity_deadband_rad_s = payload.get("friction_velocity_deadband_rad_s")
        if friction_velocity_deadband_rad_s is not None:
            self._friction_velocity_deadband_rad_s = max(
                0.0,
                float(friction_velocity_deadband_rad_s),
            )
            updated = True

        return updated

    def _clear_dynamics_collision_state(self) -> None:
        for joint_name in JOINT_NAMES[: self._slave_count]:
            self._dynamics_cycles[joint_name] = 0
            self._dynamics_exceedance_since[joint_name] = None
            self._dynamics_latched[joint_name] = False
            self._dynamics_active[joint_name] = False
            self._dynamics_reason[joint_name] = ""
            self._dynamic_threshold_envelope[joint_name].fill(0.0)
            self._dynamic_threshold_last_timestamp[joint_name] = None

    def _reset_confirmation_windows(self) -> None:
        """Break continuity when source samples contain an unobserved gap."""
        for joint_name in JOINT_NAMES[: self._slave_count]:
            self._dynamics_cycles[joint_name] = 0
            self._dynamics_exceedance_since[joint_name] = None
            self._contact_cycles[joint_name] = 0
            self._contact_exceedance_since[joint_name] = None

    def _on_collision_acknowledged(self, _msg: String) -> None:
        self._clear_dynamics_collision_state()
        for joint_name in JOINT_NAMES[: self._slave_count]:
            self._contact_cycles[joint_name] = 0
            self._contact_exceedance_since[joint_name] = None
            self._contact_latched[joint_name] = False
            self._contact_active[joint_name] = False
        # Do not immediately re-arm against the same residual that caused the
        # stop. Restart bias learning and expose observer_ready=False while the
        # runtime keeps its collision-recovery hold active.
        self._stop_request_armed = False
        self._all_drives_op_since = None
        self._last_velocity_vector = None
        self._last_velocity_timestamp = None
        restart = getattr(self._estimator, "restart_warmup", None)
        if callable(restart):
            restart()
        for joint_name in JOINT_NAMES[: self._slave_count]:
            self._external_torque_by_joint[joint_name] = None
            self._expected_torque_by_joint[joint_name] = None
            self._observer_auxiliary_torque_by_joint[joint_name] = None
            self._torque_difference_by_joint[joint_name] = None
        self.get_logger().warning(
            "[ZeroErrCollisionMonitor] Collision latch cleared; observer warm-up restarted")

    def _load_persisted_config(self) -> None:
        path = self._collision_config_path
        if not path.exists():
            return
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.get_logger().warning(
                f"[ZeroErrCollisionMonitor] Failed to load persisted config from {path}: {exc}"
            )
            return
        # Backend selection is a startup safety decision owned by runtime.yaml.
        # Do not let a stale GUI-generated JSON file silently replace the
        # momentum observer with the learned model on the next launch.
        if self._apply_runtime_config(payload):
            self.get_logger().info(
                f"[ZeroErrCollisionMonitor] Loaded persisted config from {path}"
            )

    def _apply_threshold_update(
        self,
        values: Optional[List[float]],
        target: Dict[str, float],
    ) -> bool:
        if values is None:
            return False
        changed = False
        for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count]):
            if index >= len(values):
                break
            target[joint_name] = float(values[index])
            changed = True
        return changed

    def _publish_snapshot(self) -> None:
        if not self._dynamic_state_seen and not self._dynamic_state_warned:
            self.get_logger().warning(
                "[ZeroErrCollisionMonitor] Waiting for /dynamic_joint_states..."
            )
            self._dynamic_state_warned = True

        stamp = self.get_clock().now().to_msg()
        payload = {
            "stamp": {
                "sec": stamp.sec,
                "nanosec": stamp.nanosec,
                "iso": datetime.now(UTC).isoformat(timespec="seconds"),
            },
            "timing": self._timing_snapshot(),
            "slaves": [],
        }

        inputs_valid, invalid_reason = self._input_validity()
        if not inputs_valid:
            self._invalidate_observer_inputs(invalid_reason)
        else:
            self._observer_inputs_valid = True
            self._last_input_invalid_reason = ""

        payload["slaves"] = self._build_atomic_slaves()
        self._inject_reasons(payload["slaves"])

        json_msg = String()
        json_msg.data = json.dumps(payload, sort_keys=True)
        self._json_pub.publish(json_msg)

        table_msg = String()
        table_msg.data = self._format_table(payload["slaves"])
        self._table_pub.publish(table_msg)
        self._state_pub.publish(self._build_state_msg(payload["slaves"]))
        if self._diagnostics_enabled:
            self._publish_plot_topics(payload["slaves"], stamp)
        self._publish_config_state()

        if self._print_table:
            self.get_logger().info("\n" + table_msg.data)

        if self._torque_log_enabled:
            self._append_torque_log(payload["slaves"], stamp)

    @staticmethod
    def _distribution_ms(values) -> Dict[str, Optional[float]]:
        if not values:
            return {"max": None, "p99": None, "p99_9": None}
        samples = np.asarray(values, dtype=float) * 1000.0
        samples = samples[np.isfinite(samples)]
        if samples.size == 0:
            return {"max": None, "p99": None, "p99_9": None}
        return {
            "max": float(np.max(samples)),
            "p99": float(np.percentile(samples, 99.0)),
            "p99_9": float(np.percentile(samples, 99.9)),
        }

    def _timing_snapshot(self) -> Dict[str, object]:
        now = time.monotonic()
        if (
            self._last_timing_snapshot_monotonic is not None
            and now - self._last_timing_snapshot_monotonic < 1.0
        ):
            return dict(self._cached_timing_snapshot)
        elapsed = max(1.0e-9, now - self._timing_started_monotonic)
        source_intervals = list(self._source_intervals_sec)
        median_source_interval = (
            float(np.median(source_intervals)) if source_intervals else None
        )
        snapshot = {
            "expected_input_rate_hz": self._expected_input_rate_hz,
            "delivered_callback_rate_hz": self._received_sample_count / elapsed,
            "processed_rate_hz": self._processed_sample_count / elapsed,
            "received_samples": self._received_sample_count,
            "processed_samples": self._processed_sample_count,
            "rejected_samples": self._rejected_sample_count,
            "throttled_samples": self._throttled_sample_count,
            "out_of_order_samples": self._out_of_order_sample_count,
            "late_samples": self._late_sample_count,
            "estimated_missing_source_samples": self._estimated_missing_sample_count,
            "source_rate_hz_from_median": (
                None
                if median_source_interval is None or median_source_interval <= 0.0
                else 1.0 / median_source_interval
            ),
            "source_interval_ms": self._distribution_ms(source_intervals),
            "arrival_interval_ms": self._distribution_ms(self._arrival_intervals_sec),
            "sample_age_ms": self._distribution_ms(self._sample_ages_sec),
            "observer_update_ms": self._distribution_ms(
                self._observer_update_durations_sec),
            "kdl_model_ms": self._distribution_ms(self._kdl_model_durations_sec),
            "observer_non_model_ms": self._distribution_ms(
                self._observer_non_model_durations_sec),
            "callback_total_ms": self._distribution_ms(self._callback_durations_sec),
        }
        self._cached_timing_snapshot = snapshot
        self._last_timing_snapshot_monotonic = now
        return dict(snapshot)

    def _input_validity(self) -> tuple[bool, str]:
        if not self._dynamic_sample_complete:
            return False, "dynamic joint state sample is incomplete or non-finite"
        if self._last_dynamic_sample_time is None:
            return False, "dynamic input stream has not produced a complete sample"
        now = self.get_clock().now().nanoseconds * 1e-9
        timeout = max(0.01, float(self.get_parameter("input_timeout_sec").value))
        dynamic_age = now - self._last_dynamic_sample_time
        if dynamic_age > timeout:
            return False, (
                f"dynamic input stream stale age={dynamic_age:.3f}s "
                f"timeout={timeout:.3f}s"
            )
        return True, ""

    def _invalidate_observer_inputs(self, reason: str) -> None:
        previous_reason = self._last_input_invalid_reason
        repeated_stale_stream = (
            reason.startswith("dynamic input stream stale")
            and previous_reason.startswith("dynamic input stream stale")
        )
        if (
            self._observer_inputs_valid
            or (reason != previous_reason and not repeated_stale_stream)
        ):
            self.get_logger().warning(
                f"[ZeroErrCollisionMonitor] Observer unavailable: {reason}"
            )
        self._observer_inputs_valid = False
        self._last_input_invalid_reason = reason
        self._all_drives_op_since = None
        self._last_velocity_vector = None
        self._last_velocity_timestamp = None
        restart = getattr(self._estimator, "restart_warmup", None)
        if callable(restart):
            restart()
        for joint_name in JOINT_NAMES[: self._slave_count]:
            self._expected_torque_by_joint[joint_name] = None
            self._observer_auxiliary_torque_by_joint[joint_name] = None
            self._torque_difference_by_joint[joint_name] = None
            self._external_torque_by_joint[joint_name] = None

    def _evaluate_collisions(
        self,
        slaves: List[Dict[str, Optional[float]]],
        sample_timestamp: Optional[float] = None,
    ) -> None:
        observer_ready = (
            self._dynamics_enabled
            and self._estimator is not None
            and bool(getattr(self._estimator, "ready", False))
        )
        timestamp = (
            self.get_clock().now().nanoseconds * 1.0e-9
            if sample_timestamp is None else float(sample_timestamp)
        )
        for slave in slaves:
            joint_name = slave["joint"]
            effort = (
                abs(float(self._measured_torque_by_joint[joint_name]))
                if self._measured_torque_by_joint[joint_name] is not None
                else 0.0
            )
            following_error = (
                abs(float(slave["following_error_actual"]))
                if slave.get("following_error_actual") is not None
                else 0.0
            )
            external_torque = abs(self._external_torque_by_joint[joint_name]) if self._external_torque_by_joint[joint_name] is not None else 0.0
            dynamic_threshold = self._compute_external_torque_threshold(
                joint_name,
                slave.get("velocity"),
                self._acceleration_by_joint.get(joint_name),
                sample_timestamp,
            )
            self._current_external_torque_thresholds[joint_name] = dynamic_threshold
            self._contact_reason[joint_name] = (
                f"meas_tau {effort:.1f} > {self._effort_thresholds[joint_name]:.1f} and "
                f"foll_err {following_error:.0f} > {self._following_error_thresholds[joint_name]:.0f}"
            )
            self._dynamics_reason[joint_name] = (
                f"ext_tau {external_torque:.2f} > {dynamic_threshold:.2f} dynamic"
            )

            if not self._detection_enabled or self._detection_suppressed:
                self._dynamics_active[joint_name] = False
                self._dynamics_cycles[joint_name] = 0
                self._dynamics_exceedance_since[joint_name] = None
                self._contact_active[joint_name] = False
                self._contact_cycles[joint_name] = 0
                self._contact_exceedance_since[joint_name] = None
                reason = (
                    "sensorless detection disabled"
                    if not self._detection_enabled
                    else "suppressed by recovery jog"
                )
                self._dynamics_reason[joint_name] = reason
                self._contact_reason[joint_name] = reason
                continue

            # The momentum observer must never assert a collision while the
            # slaves are starting, settling, or its stationary bias is being
            # initialized.  _update_external_torque_estimate() restarts that
            # initialization whenever any drive leaves operation-enabled.
            if not observer_ready:
                self._dynamics_active[joint_name] = False
                self._dynamics_cycles[joint_name] = 0
                self._dynamics_exceedance_since[joint_name] = None
                self._contact_active[joint_name] = False
                self._contact_cycles[joint_name] = 0
                self._contact_exceedance_since[joint_name] = None
                if not (self._active_stop_enabled and not self._stop_request_armed):
                    self._dynamics_latched[joint_name] = False
                    self._contact_latched[joint_name] = False
                continue

            # Both estimator backends produce external torque. The learned
            # model does not set _dynamics_enabled (that flag only describes
            # the KDL backend), so gating detection on it made learned-model
            # threshold crossings visible in the GUI without ever asserting
            # ACTIVE/LATCHED.
            if self._external_torque_by_joint[joint_name] is not None:
                dynamics_active = external_torque >= dynamic_threshold
                self._dynamics_active[joint_name] = dynamics_active
                if dynamics_active:
                    self._dynamics_cycles[joint_name] += 1
                    if self._dynamics_exceedance_since[joint_name] is None:
                        self._dynamics_exceedance_since[joint_name] = timestamp
                else:
                    self._dynamics_cycles[joint_name] = 0
                    self._dynamics_exceedance_since[joint_name] = None
                    if not (self._active_stop_enabled and not self._stop_request_armed):
                        self._dynamics_latched[joint_name] = False

                if (
                    dynamics_active
                    and self._exceedance_duration_sec(
                        self._dynamics_exceedance_since[joint_name], timestamp
                    ) >= self._confirm_duration_sec
                    and not self._dynamics_latched[joint_name]
                ):
                    self._dynamics_latched[joint_name] = True
                    self.get_logger().warning(
                        "[ZeroErrCollisionMonitor] dynamics collision suspect on "
                        f"{joint_name}: external_torque={external_torque:.2f} >= "
                        f"{dynamic_threshold:.2f} for "
                        f"{self._exceedance_duration_sec(self._dynamics_exceedance_since[joint_name], timestamp) * 1000.0:.2f} ms"
                    )
                    self._request_motion_stop(joint_name, "dynamics")
            else:
                self._dynamics_active[joint_name] = False
                self._dynamics_cycles[joint_name] = 0
                self._dynamics_exceedance_since[joint_name] = None
                if not (self._active_stop_enabled and not self._stop_request_armed):
                    self._dynamics_latched[joint_name] = False

            if self._effort_following_error_detection_enabled:
                exceeds_contact_thresholds = (
                    effort >= self._effort_thresholds[joint_name]
                    and following_error >= self._following_error_thresholds[joint_name]
                )
                self._contact_active[joint_name] = exceeds_contact_thresholds
                if exceeds_contact_thresholds:
                    self._contact_cycles[joint_name] += 1
                    if self._contact_exceedance_since[joint_name] is None:
                        self._contact_exceedance_since[joint_name] = timestamp
                else:
                    self._contact_cycles[joint_name] = 0
                    self._contact_exceedance_since[joint_name] = None
                    if not (self._active_stop_enabled and not self._stop_request_armed):
                        self._contact_latched[joint_name] = False

                if (
                    exceeds_contact_thresholds
                    and self._exceedance_duration_sec(
                        self._contact_exceedance_since[joint_name], timestamp
                    ) >= self._confirm_duration_sec
                    and not self._contact_latched[joint_name]
                ):
                    self._contact_latched[joint_name] = True
                    self.get_logger().warning(
                        "[ZeroErrCollisionMonitor] secondary collision suspect on "
                        f"{joint_name}: effort={effort:.1f} >= "
                        f"{self._effort_thresholds[joint_name]:.1f}, "
                        f"following_error={following_error:.1f} >= "
                        f"{self._following_error_thresholds[joint_name]:.1f}"
                    )
                    self._request_motion_stop(joint_name, "effort/following-error")
            else:
                self._contact_active[joint_name] = False
                self._contact_cycles[joint_name] = 0
                self._contact_exceedance_since[joint_name] = None
                if not (self._active_stop_enabled and not self._stop_request_armed):
                    self._contact_latched[joint_name] = False
                self._contact_reason[joint_name] = "secondary detector disabled"

        if not any(
            self._dynamics_active[name]
            or self._dynamics_latched[name]
            or self._contact_active[name]
            or self._contact_latched[name]
            for name in JOINT_NAMES[: self._slave_count]
        ):
            self._stop_request_armed = True

    @staticmethod
    def _exceedance_duration_sec(started_at: Optional[float], now: float) -> float:
        if started_at is None:
            return 0.0
        return max(0.0, float(now) - float(started_at))

    def _request_motion_stop(self, joint_name: str, detector: str) -> None:
        if not self._active_stop_enabled or not self._stop_request_armed:
            return
        self._stop_request_armed = False
        message = String()
        message.data = json.dumps({
            "timestamp": time.time(),
            "joint": joint_name,
            "detector": detector,
            "mode": "active",
        })
        self._stop_request_pub.publish(message)
        self.get_logger().error(
            "[ZeroErrCollisionMonitor] ACTIVE mode requested motion stop: "
            f"joint={joint_name} detector={detector}"
        )

    def _inject_reasons(self, slaves: List[Dict[str, Optional[float]]]) -> None:
        for slave in slaves:
            joint_name = str(slave["joint"])
            slave["contact_reason"] = self._contact_reason[joint_name]
            slave["dynamics_reason"] = self._dynamics_reason[joint_name]

    def _init_inverse_dynamics_model(self) -> None:
        support = self._load_inverse_dynamics_support()
        if support is None:
            return
        momentum_estimator_class, model_class = support

        urdf_path = str(self.get_parameter("urdf_path").value)
        base_link = str(self.get_parameter("base_link").value)
        tip_link = str(self.get_parameter("tip_link").value)
        num_joints = int(self.get_parameter("num_joints").value)
        filter_alpha = float(self.get_parameter("filter_alpha").value)
        include_gravity = bool(self.get_parameter("include_gravity").value)
        static_torque_bias_nm = list(self.get_parameter("static_torque_bias_nm").value)
        warmup_sec = float(self.get_parameter("warmup_sec").value)
        warmup_vel_threshold_rad_s = float(self.get_parameter("warmup_vel_threshold_rad_s").value)
        warmup_min_samples = int(self.get_parameter("warmup_min_samples").value)
        observer_gain = float(self.get_parameter("observer_gain").value)

        if not urdf_path:
            self.get_logger().warning(
                "[ZeroErrCollisionMonitor] Inverse dynamics disabled: missing urdf_path"
            )
            return

        try:
            model = model_class(
                urdf_path=urdf_path,
                base_link=base_link,
                tip_link=tip_link,
                num_joints=num_joints,
                include_gravity=include_gravity,
                logger=self.get_logger(),
            )
            self._estimator = momentum_estimator_class(
                model,
                filter_alpha=filter_alpha,
                observer_gain=observer_gain,
                static_torque_bias_nm=np.array(static_torque_bias_nm, dtype=float),
                warmup_sec=warmup_sec,
                warmup_vel_threshold_rad_s=warmup_vel_threshold_rad_s,
                warmup_min_samples=warmup_min_samples,
            )
            self._dynamics_enabled = True
            self.get_logger().info(
                "[ZeroErrCollisionMonitor] Dynamics estimator mode: momentum_observer"
            )
        except Exception as exc:
            self._dynamics_enabled = False
            self.get_logger().warning(
                f"[ZeroErrCollisionMonitor] Inverse dynamics disabled: {exc}"
            )

    def _reinitialize_estimator(self) -> None:
        self._estimator = None
        self._dynamics_enabled = False
        self._last_velocity_vector = None
        self._last_velocity_timestamp = None
        for joint_name in JOINT_NAMES[: self._slave_count]:
            self._expected_torque_by_joint[joint_name] = None
            self._observer_auxiliary_torque_by_joint[joint_name] = None
            self._torque_difference_by_joint[joint_name] = None
            self._external_torque_by_joint[joint_name] = None
        self._init_inverse_dynamics_model()

    def _load_inverse_dynamics_support(self):
        try:
            from erob_moveit_runtime.safety.collision_detection.external_torque_estimator import (
                MomentumObserverEstimator as momentum_estimator_class,
            )
            from erob_moveit_runtime.safety.collision_detection.inverse_dynamics_model import (
                KDLInverseDynamicsModel as model_class,
            )

            return momentum_estimator_class, model_class
        except ModuleNotFoundError:
            pass

        # erob_moveit_runtime is an ament_cmake package whose Python safety
        # modules are installed below lib/<package>, not site-packages.
        try:
            from ament_index_python.packages import get_package_prefix

            module_root = Path(get_package_prefix("erob_moveit_runtime")) / \
                "lib" / "erob_moveit_runtime"
            module_root_text = str(module_root)
            if module_root_text not in sys.path:
                sys.path.insert(0, module_root_text)
            from safety.collision_detection.external_torque_estimator import (
                MomentumObserverEstimator as momentum_estimator_class,
            )
            from safety.collision_detection.inverse_dynamics_model import (
                KDLInverseDynamicsModel as model_class,
            )

            return momentum_estimator_class, model_class
        except (ImportError, ModuleNotFoundError):
            pass

        self._dynamics_enabled = False
        self.get_logger().warning(
            "[ZeroErrCollisionMonitor] Inverse dynamics disabled: erob_moveit_runtime collision modules not importable"
        )
        return None

    def _update_external_torque_estimate(
        self,
        slaves: List[Dict[str, Optional[float]]],
        sample_timestamp: Optional[float] = None,
    ) -> None:
        if not self._dynamics_enabled or self._estimator is None:
            return

        # Do not initialize from transient torque while EtherCAT/CiA402 drives
        # are passing through PREOP, SAFEOP, fault reset, or switched-on.  Bit
        # 2 of the CiA402 statusword is "operation enabled".
        drives_operational = all(
            slave.get("statusword") is not None
            and (int(slave["statusword"]) & 0x0004) != 0
            and slave.get("error_code") is not None
            and int(slave["error_code"]) == 0
            for slave in slaves
        )
        now_s = (
            self.get_clock().now().nanoseconds / 1e9
            if sample_timestamp is None else float(sample_timestamp)
        )
        if not drives_operational:
            self._all_drives_op_since = None
            self._reset_estimator_after_drive_interruption()
            for joint_name in JOINT_NAMES[: self._slave_count]:
                self._expected_torque_by_joint[joint_name] = None
                self._observer_auxiliary_torque_by_joint[joint_name] = None
                self._torque_difference_by_joint[joint_name] = None
                self._external_torque_by_joint[joint_name] = None
            return
        if self._all_drives_op_since is None:
            self._all_drives_op_since = now_s
        stable_sec = max(0.0, float(self.get_parameter("drive_stable_sec").value))
        if now_s - self._all_drives_op_since < stable_sec:
            self._reset_estimator_after_drive_interruption()
            for joint_name in JOINT_NAMES[: self._slave_count]:
                self._expected_torque_by_joint[joint_name] = None
                self._observer_auxiliary_torque_by_joint[joint_name] = None
                self._torque_difference_by_joint[joint_name] = None
                self._external_torque_by_joint[joint_name] = None
            return

        positions: List[float] = []
        velocities: List[float] = []
        measured_torques: List[float] = []
        for slave in slaves:
            if (
                slave.get("position") is None
                or slave.get("velocity") is None
            ):
                return
            measured_torque = self._measured_torque_by_joint.get(
                str(slave["joint"]))
            if measured_torque is None:
                return
            positions.append(float(slave["position"]))
            velocities.append(float(slave["velocity"]))
            measured_torques.append(float(measured_torque))

        velocity_vector = np.array(velocities, dtype=float)
        timestamp = now_s
        if self._last_velocity_vector is None or self._last_velocity_timestamp is None:
            acceleration_vector = np.zeros_like(velocity_vector)
        else:
            dt = max(timestamp - self._last_velocity_timestamp, 1e-6)
            acceleration_vector = (velocity_vector - self._last_velocity_vector) / dt

        for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count]):
            self._acceleration_by_joint[joint_name] = float(acceleration_vector[index])

        self._last_velocity_vector = velocity_vector
        self._last_velocity_timestamp = timestamp

        # The momentum observer equations expect commanded/measured joint
        # torque with internal drivetrain friction removed.  Previously these
        # coefficients were published in the GUI but never affected the
        # observer, causing normal bidirectional motion to look like contact.
        friction_torques = np.array([
            self._compute_friction_torque(joint_name, velocities[index])
            for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count])
        ], dtype=float)
        position_corrections = np.array([
            self._compute_position_correction(joint_name, positions)
            for joint_name in JOINT_NAMES[: self._slave_count]
        ], dtype=float)
        motion_residual_corrections = np.array([
            self._compute_motion_residual_correction(
                joint_name,
                velocities[index],
                acceleration_vector[index],
            )
            for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count])
        ], dtype=float)
        compensated_measured_torques = (
            np.array(measured_torques, dtype=float)
            - friction_torques
            - position_corrections
            - motion_residual_corrections
        )
        try:
            self._estimator.update(
                compensated_measured_torques,
                np.array(positions, dtype=float),
                velocity_vector,
                acceleration_vector,
                timestamp=timestamp,
            )
        except (ValueError, FloatingPointError, RuntimeError) as exc:
            self._invalidate_observer_inputs(f"invalid observer data: {exc}")
            return

        filtered = self._estimator.filtered
        observer_ready = bool(getattr(self._estimator, "ready", False))
        expected = self._estimator.expected_torque_history[-1] if self._estimator.expected_torque_history else None
        auxiliary_history = getattr(self._estimator, "observer_auxiliary_history", ())
        observer_auxiliary = auxiliary_history[-1] if auxiliary_history else None
        for index, joint_name in enumerate(JOINT_NAMES[: self._slave_count]):
            # Present expected torque in the original sensor domain. External
            # torque itself comes from the friction-compensated observer.
            expected_torque = (
                float(expected[index])
                + float(friction_torques[index])
                + float(position_corrections[index])
                + float(motion_residual_corrections[index])
                if expected is not None else None
            )
            self._expected_torque_by_joint[joint_name] = expected_torque
            self._observer_auxiliary_torque_by_joint[joint_name] = (
                float(observer_auxiliary[index])
                + float(friction_torques[index])
                + float(position_corrections[index])
                + float(motion_residual_corrections[index])
                if observer_auxiliary is not None else None
            )
            self._torque_difference_by_joint[joint_name] = (
                float(measured_torques[index]) - expected_torque if expected_torque is not None else None
            )
            # The observer deliberately keeps its internal output at zero
            # during initial bias learning. A drive interruption also makes
            # the estimate unavailable until the drive-stability gate passes.
            # Publishing that zero as a valid estimate makes consumers think
            # collision protection is active when it is not.
            self._external_torque_by_joint[joint_name] = (
                float(filtered[index]) if observer_ready else None
            )

    def _reset_estimator_after_drive_interruption(self) -> None:
        """Reset observer transients without discarding a completed bias calibration."""
        self._last_velocity_vector = None
        self._last_velocity_timestamp = None
        if self._estimator is None:
            return
        if bool(getattr(self._estimator, "ready", False)):
            reset = getattr(self._estimator, "reset", None)
            if reset is not None:
                reset()
            return
        restart = getattr(self._estimator, "restart_warmup", None)
        if restart is not None:
            restart()

    def _compute_external_torque_threshold(
        self,
        joint_name: str,
        velocity: Optional[float],
        acceleration: Optional[float],
        sample_timestamp: Optional[float] = None,
    ) -> float:
        """Return the motion-conditioned threshold, never below its static floor."""
        floor = float(self._external_torque_thresholds[joint_name])
        if not self._dynamic_threshold_enabled:
            return floor * (100.0 / self._collision_sensitivity_percent)
        velocity_f = 0.0 if velocity is None else float(velocity)
        acceleration_f = 0.0 if acceleration is None else float(acceleration)
        if not np.isfinite(velocity_f) or not np.isfinite(acceleration_f):
            return floor * (100.0 / self._collision_sensitivity_percent)
        limits = self._dynamic_threshold_training_limits[joint_name]
        velocity_f = float(np.clip(velocity_f, -limits[0], limits[0]))
        acceleration_f = float(np.clip(acceleration_f, -limits[1], limits[1]))
        velocity_positive = max(velocity_f, 0.0)
        velocity_negative = max(-velocity_f, 0.0)
        acceleration_positive = max(acceleration_f, 0.0)
        acceleration_negative = max(-acceleration_f, 0.0)
        now = (
            self.get_clock().now().nanoseconds / 1e9
            if sample_timestamp is None else float(sample_timestamp)
        )
        last = self._dynamic_threshold_last_timestamp[joint_name]
        dt = 0.0 if last is None else max(0.0, now - float(last))
        decay = float(np.exp(-dt / self._dynamic_threshold_decay_sec))
        instantaneous = np.array([
            velocity_positive,
            velocity_negative,
            acceleration_positive,
            acceleration_negative,
        ], dtype=float)
        envelope = np.maximum(
            instantaneous,
            self._dynamic_threshold_envelope[joint_name] * decay,
        )
        self._dynamic_threshold_envelope[joint_name] = envelope
        self._dynamic_threshold_last_timestamp[joint_name] = now
        velocity_positive, velocity_negative = envelope[0], envelope[1]
        acceleration_positive, acceleration_negative = envelope[2], envelope[3]
        features = np.array([
            1.0,
            velocity_positive,
            velocity_negative,
            acceleration_positive,
            acceleration_negative,
            velocity_positive * velocity_positive,
            velocity_negative * velocity_negative,
            acceleration_positive * acceleration_positive,
            acceleration_negative * acceleration_negative,
        ], dtype=float)
        fitted = float(self._dynamic_threshold_coefficients[joint_name] @ features)
        base_threshold = max(floor, fitted) if np.isfinite(fitted) else floor
        base_threshold = min(
            base_threshold,
            floor * self._dynamic_threshold_max_ratio,
        )
        return base_threshold * (100.0 / self._collision_sensitivity_percent)

    def _format_table(self, slaves: List[Dict[str, Optional[float]]]) -> str:
        lines = [
            "slv joint     sens_tau(Nm) fric_tau(Nm) meas_tau(Nm) exp_tau(Nm) diff_tau(Nm) ext_tau(Nm) foll_err",
        ]
        for slave in slaves:
            joint_name = slave.get("joint", "")
            external_torque = self._external_torque_by_joint.get(slave.get("joint", ""))
            lines.append(
                "{slave:>3} {joint:<7} {torque_sensor:>12} {friction_torque:>12} "
                "{measured_torque:>12} {expected_torque:>11} {torque_difference:>12} {external_torque:>11} {following_error_actual:>8}".format(
                    slave=slave.get("slave", "NA"),
                    joint=joint_name or "NA",
                    torque_sensor=self._fmt_float(slave.get("torque_sensor"), 2),
                    friction_torque=self._fmt_float(self._friction_torque_by_joint.get(joint_name), 2),
                    measured_torque=self._fmt_float(self._measured_torque_by_joint.get(joint_name), 2),
                    expected_torque=self._fmt_float(self._expected_torque_by_joint.get(joint_name), 2),
                    torque_difference=self._fmt_float(self._torque_difference_by_joint.get(joint_name), 2),
                    external_torque=self._fmt_float(external_torque, 2),
                    following_error_actual=self._fmt_float(
                        slave.get("following_error_actual"),
                        0,
                    ),
                )
            )
        return "\n".join(lines)

    def _init_torque_log(self) -> None:
        self._torque_log_path.parent.mkdir(parents=True, exist_ok=True)
        self._torque_log_header_written = self._torque_log_path.exists() and self._torque_log_path.stat().st_size > 0
        self.get_logger().info(
            f"[ZeroErrCollisionMonitor] Torque logging enabled -> {self._torque_log_path}"
        )

    def _append_torque_log(self, slaves: List[Dict[str, Optional[float]]], stamp) -> None:
        timestamp = f"{stamp.sec}.{stamp.nanosec:09d}"
        timestamp_s = float(stamp.sec) + float(stamp.nanosec) / 1e9
        if (
            self._torque_log_period_sec > 0.0
            and self._last_logged_timestamp is not None
            and timestamp_s - self._last_logged_timestamp < self._torque_log_period_sec
        ):
            return
        acceleration_by_joint: Dict[str, Optional[float]] = {}
        for slave in slaves:
            joint_name = str(slave["joint"])
            acceleration_by_joint[joint_name] = self._compute_joint_acceleration(
                joint_name,
                slave.get("velocity"),
                timestamp_s,
            )

        if not self._torque_log_motion_window_active(slaves, acceleration_by_joint, timestamp_s):
            self._last_logged_timestamp = timestamp_s
            for slave in slaves:
                joint_name = str(slave["joint"])
                velocity = slave.get("velocity")
                self._last_logged_velocity_by_joint[joint_name] = (
                    None if velocity is None else float(velocity)
                )
            return

        with self._torque_log_path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            if not self._torque_log_header_written:
                writer.writerow(
                    [
                        "timestamp",
                        "joint",
                        "position_rad",
                        "velocity_rad_s",
                        "acceleration_rad_s2",
                        "torque_sensor_nm",
                        "measured_torque_nm",
                        "expected_torque_nm",
                        "observer_auxiliary_torque_nm",
                        "external_torque_nm",
                        "following_error_actual",
                    ]
                )
                self._torque_log_header_written = True

            for slave in slaves:
                joint_name = str(slave["joint"])
                position = slave.get("position")
                velocity = slave.get("velocity")
                acceleration = acceleration_by_joint.get(joint_name)
                torque_sensor = slave.get("torque_sensor")
                following_error = slave.get("following_error_actual")
                if not self._torque_log_sample_is_valid(
                    position=position,
                    velocity=velocity,
                    acceleration=acceleration,
                    torque_sensor=torque_sensor,
                    following_error=following_error,
                ):
                    continue
                writer.writerow(
                    [
                        timestamp,
                        joint_name,
                        self._csv_value(position),
                        self._csv_value(velocity),
                        self._csv_value(acceleration),
                        self._csv_value(torque_sensor),
                        self._csv_value(self._measured_torque_by_joint.get(joint_name)),
                        self._csv_value(self._expected_torque_by_joint.get(joint_name)),
                        self._csv_value(self._observer_auxiliary_torque_by_joint.get(joint_name)),
                        self._csv_value(self._external_torque_by_joint.get(joint_name)),
                        self._csv_value(following_error),
                    ]
                )

        self._last_logged_timestamp = timestamp_s
        for slave in slaves:
            joint_name = str(slave["joint"])
            velocity = slave.get("velocity")
            self._last_logged_velocity_by_joint[joint_name] = (
                None if velocity is None else float(velocity)
            )

    def _compute_joint_acceleration(
        self,
        joint_name: str,
        velocity: Optional[float],
        timestamp_s: float,
    ) -> Optional[float]:
        if velocity is None:
            return None
        previous_velocity = self._last_logged_velocity_by_joint.get(joint_name)
        if previous_velocity is None or self._last_logged_timestamp is None:
            return None
        dt = timestamp_s - self._last_logged_timestamp
        if dt <= 1e-6:
            return None
        return (float(velocity) - previous_velocity) / dt

    def _csv_value(self, value: Optional[float]) -> str:
        if value is None:
            return ""
        value_f = float(value)
        if not np.isfinite(value_f):
            return ""
        return f"{value_f:.9f}"

    def _torque_log_sample_is_valid(
        self,
        *,
        position: Optional[float],
        velocity: Optional[float],
        acceleration: Optional[float],
        torque_sensor: Optional[float],
        following_error: Optional[float],
    ) -> bool:
        required_values = [position, velocity, acceleration, torque_sensor, following_error]
        return all(value is not None and np.isfinite(float(value)) for value in required_values)

    def _torque_log_motion_window_active(
        self,
        slaves: List[Dict[str, Optional[float]]],
        acceleration_by_joint: Dict[str, Optional[float]],
        timestamp_s: float,
    ) -> bool:
        motion_detected = False
        for slave in slaves:
            joint_name = str(slave["joint"])
            velocity = slave.get("velocity")
            acceleration = acceleration_by_joint.get(joint_name)
            velocity_ok = (
                velocity is not None
                and np.isfinite(float(velocity))
                and abs(float(velocity)) >= self._torque_log_min_velocity_rad_s
            )
            acceleration_ok = (
                acceleration is not None
                and np.isfinite(float(acceleration))
                and abs(float(acceleration)) >= self._torque_log_min_acceleration_rad_s2
            )
            if velocity_ok or acceleration_ok:
                motion_detected = True
                break

        if motion_detected:
            self._last_substantial_motion_timestamp = timestamp_s
            return True

        if self._last_substantial_motion_timestamp is None:
            return False

        return (timestamp_s - self._last_substantial_motion_timestamp) <= self._torque_log_idle_timeout_s

    def _build_state_msg(self, slaves: List[Dict[str, Optional[float]]]) -> DynamicJointState:
        msg = DynamicJointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "base_link"
        msg.joint_names = [str(slave["joint"]) for slave in slaves]

        for slave in slaves:
            interface_value = InterfaceValue()
            interface_value.interface_names = [
                "position",
                "velocity",
                "acceleration",
                "torque_sensor",
                "friction_torque",
                "measured_torque",
                "expected_torque",
                "observer_auxiliary_torque",
                "torque_difference",
                "external_torque",
                "external_torque_threshold",
                "following_error_actual",
                "error_code",
                "statusword",
                "mode_display",
                "contact_active",
                "contact_cycles",
                "contact_latched",
                "dynamics_active",
                "dynamics_cycles",
                "dynamics_latched",
                "observer_ready",
            ]
            interface_value.values = [
                self._state_value(slave.get("position")),
                self._state_value(slave.get("velocity")),
                self._state_value(self._acceleration_by_joint.get(str(slave["joint"]))),
                self._state_value(slave.get("torque_sensor")),
                self._state_value(self._friction_torque_by_joint.get(str(slave["joint"]))),
                self._state_value(self._measured_torque_by_joint.get(str(slave["joint"]))),
                self._state_value(self._expected_torque_by_joint.get(str(slave["joint"]))),
                self._state_value(self._observer_auxiliary_torque_by_joint.get(str(slave["joint"]))),
                self._state_value(self._torque_difference_by_joint.get(str(slave["joint"]))),
                self._state_value(self._external_torque_by_joint.get(str(slave["joint"]))),
                self._state_value(self._current_external_torque_thresholds.get(str(slave["joint"]))),
                self._state_value(slave.get("following_error_actual")),
                self._state_value(slave.get("error_code")),
                self._state_value(slave.get("statusword")),
                self._state_value(slave.get("mode_display")),
                self._state_value(1.0 if self._contact_active[str(slave["joint"])] else 0.0),
                self._state_value(float(self._contact_cycles[str(slave["joint"])])),
                self._state_value(1.0 if self._contact_latched[str(slave["joint"])] else 0.0),
                self._state_value(1.0 if self._dynamics_active[str(slave["joint"])] else 0.0),
                self._state_value(float(self._dynamics_cycles[str(slave["joint"])])),
                self._state_value(1.0 if self._dynamics_latched[str(slave["joint"])] else 0.0),
                self._state_value(
                    1.0
                    if self._dynamics_enabled
                    and self._estimator is not None
                    and bool(getattr(self._estimator, "ready", False))
                    and self._external_torque_by_joint.get(str(slave["joint"])) is not None
                    else 0.0
                ),
            ]
            msg.interface_values.append(interface_value)

        return msg

    def _state_value(self, value: Optional[float]) -> float:
        if value is None:
            return float("nan")
        return float(value)

    def _publish_config_state(self) -> None:
        msg = String()
        msg.data = json.dumps(
            {
                "confirm_duration_ms": self._confirm_duration_sec * 1000.0,
                "expected_input_rate_hz": self._expected_input_rate_hz,
                "effort_thresholds": [
                    self._effort_thresholds[joint_name]
                    for joint_name in JOINT_NAMES[: self._slave_count]
                ],
                "following_error_thresholds": [
                    self._following_error_thresholds[joint_name]
                    for joint_name in JOINT_NAMES[: self._slave_count]
                ],
                "external_torque_thresholds": [
                    self._external_torque_thresholds[joint_name]
                    for joint_name in JOINT_NAMES[: self._slave_count]
                ],
                "current_external_torque_thresholds": [
                    self._current_external_torque_thresholds[joint_name]
                    for joint_name in JOINT_NAMES[: self._slave_count]
                ],
                "collision_sensitivity_percent": self._collision_sensitivity_percent,
                "active_stop_enabled": self._active_stop_enabled,
                "detection_enabled": self._detection_enabled,
                "effort_following_error_detection_enabled":
                    self._effort_following_error_detection_enabled,
                "diagnostics_enabled": self._diagnostics_enabled,
                "collision_detection_suppressed": self._detection_suppressed,
                "dynamic_threshold_enabled": self._dynamic_threshold_enabled,
                "dynamic_threshold_feature_names": [
                    "bias", "positive_velocity", "negative_velocity",
                    "positive_acceleration", "negative_acceleration",
                    "positive_velocity_squared", "negative_velocity_squared",
                    "positive_acceleration_squared", "negative_acceleration_squared",
                ],
                "dynamic_threshold_coefficients": {
                    joint_name: self._dynamic_threshold_coefficients[joint_name].tolist()
                    for joint_name in JOINT_NAMES[: self._slave_count]
                },
                "dynamic_threshold_training_limits": {
                    joint_name: self._dynamic_threshold_training_limits[joint_name].tolist()
                    for joint_name in JOINT_NAMES[: self._slave_count]
                },
                "dynamic_threshold_decay_sec": self._dynamic_threshold_decay_sec,
                "dynamic_threshold_max_ratio": self._dynamic_threshold_max_ratio,
                "motion_residual_correction_coefficients": {
                    joint_name: self._motion_residual_correction_coefficients[
                        joint_name].tolist()
                    for joint_name in JOINT_NAMES[: self._slave_count]
                    if np.any(self._motion_residual_correction_coefficients[joint_name])
                },
                "motion_residual_correction_limits": {
                    joint_name: self._motion_residual_correction_limits[
                        joint_name].tolist()
                    for joint_name in JOINT_NAMES[: self._slave_count]
                    if np.all(np.isfinite(
                        self._motion_residual_correction_limits[joint_name]))
                },
                "dynamics_estimator_mode": "momentum_observer",
                "use_inverse_dynamics": True,
                "friction_coulomb_nm": [
                    self._friction_coulomb_nm[joint_name]
                    for joint_name in JOINT_NAMES[: self._slave_count]
                ],
                "friction_viscous_nm_per_rad_s": [
                    self._friction_viscous_nm_per_rad_s[joint_name]
                    for joint_name in JOINT_NAMES[: self._slave_count]
                ],
                "friction_velocity_deadband_rad_s": self._friction_velocity_deadband_rad_s,
            },
            sort_keys=True,
        )
        self._config_pub.publish(msg)

    def _publish_plot_topics(self, slaves: List[Dict[str, Optional[float]]], stamp) -> None:
        joint_names = [str(slave["joint"]) for slave in slaves]
        for metric, publisher in self._plot_publishers.items():
            msg = JointState()
            msg.header.stamp = stamp
            msg.name = joint_names
            msg.position = [
                self._state_value(PLOT_METRICS[metric](self, slave))
                for slave in slaves
            ]
            publisher.publish(msg)

    def _compute_friction_torque(
        self,
        joint_name: str,
        velocity: Optional[float],
    ) -> Optional[float]:
        if velocity is None:
            return None
        velocity_f = float(velocity)
        if abs(velocity_f) < self._friction_velocity_deadband_rad_s:
            sign = 0.0
        else:
            sign = 1.0 if velocity_f > 0.0 else -1.0
        return (
            self._friction_coulomb_nm[joint_name] * sign
            + self._friction_viscous_nm_per_rad_s[joint_name] * velocity_f
        )

    def _compute_position_correction(
        self, joint_name: str, positions: List[float]
    ) -> float:
        """Physics-shaped residual correction identified from free motion.

        The feature angles represent the principal gravity lever arms of the
        serial chain. Keeping this correction small and structured avoids a
        workspace lookup table and permits interpolation to unseen poses.
        """
        coefficients = self._position_correction_coefficients.get(joint_name)
        if coefficients is None or len(positions) < 4 or not np.any(coefficients):
            return 0.0
        q2, q3, q4 = (float(positions[i]) for i in (1, 2, 3))
        q23 = q2 + q3
        q234 = q23 + q4
        features = np.array([
            1.0,
            np.sin(q2), np.cos(q2),
            np.sin(q23), np.cos(q23),
            np.sin(q234), np.cos(q234),
            np.sin(q3), np.cos(q3),
        ], dtype=float)
        return float(coefficients @ features)

    def _compute_motion_residual_correction(
        self,
        joint_name: str,
        velocity: float,
        acceleration: float,
    ) -> float:
        """Predict repeatable directional motion residual from clean data."""
        coefficients = self._motion_residual_correction_coefficients.get(joint_name)
        limits = self._motion_residual_correction_limits.get(joint_name)
        if coefficients is None or limits is None or not np.any(coefficients):
            return 0.0
        velocity = float(np.clip(float(velocity), -limits[0], limits[0]))
        acceleration = float(np.clip(float(acceleration), -limits[1], limits[1]))
        velocity_positive = max(velocity, 0.0)
        velocity_negative = max(-velocity, 0.0)
        features = np.array([
            velocity_positive,
            velocity_negative,
            velocity_positive * velocity_positive,
            velocity_negative * velocity_negative,
            max(acceleration, 0.0),
            max(-acceleration, 0.0),
        ], dtype=float)
        return float(coefficients @ features)

    def _compute_measured_torque(
        self,
        torque_sensor: Optional[float],
    ) -> Optional[float]:
        if torque_sensor is None or not np.isfinite(torque_sensor):
            return None
        return float(torque_sensor)

    def _fmt_float(self, value: Optional[float], decimals: int) -> str:
        if value is None:
            return "NA"
        return f"{value:.{decimals}f}"

    def _fmt_hex(self, value: Optional[float]) -> str:
        if value is None:
            return "NA"
        return f"0x{int(value):04X}"


def main(args=None) -> None:
    rclpy.init(args=args)
    node = ZeroErrCollisionMonitor()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
