#!/usr/bin/env python3

"""Status GUI for collision monitoring and supervised calibration control."""

from __future__ import annotations

import json
import math
import sys
import time
from typing import Dict

import rclpy
from control_msgs.msg import DynamicJointState
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QApplication,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QDoubleSpinBox,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    QoSProfile,
    ReliabilityPolicy,
    qos_profile_sensor_data,
)
from std_msgs.msg import String
from std_srvs.srv import Trigger


JOINT_NAMES = [f"Joint_{index}" for index in range(1, 7)]
COLUMNS = [
    "Joint",
    "Input",
    "Sensor Nm",
    "Expected Nm",
    "Residual Nm",
    "External Nm",
    "Threshold Nm",
    "Active",
    "Latched",
    "Reason",
]


class CollisionStatusNode(Node):
    def __init__(self) -> None:
        super().__init__("zeroerr_collision_status_gui")
        self.state: Dict[str, Dict[str, float]] = {}
        self.reasons: Dict[str, str] = {}
        self.thresholds: Dict[str, float] = {}
        self.estimator = "unknown"
        self.collision_sensitivity_percent = 100
        self.confirm_duration_ms = 25
        self.dynamic_threshold_max_ratio = 5.0
        self.active_stop_enabled = False
        self.last_state_time = 0.0
        self.calibration = {}
        self.last_calibration_time = 0.0
        self.calibration_request_pending = False
        self.calibration_request_result = ""

        self.create_subscription(
            DynamicJointState,
            "/zeroerr/collision_monitor/state",
            self._on_state,
            qos_profile_sensor_data,
        )
        self.create_subscription(
            String,
            "/zeroerr/collision_monitor/json",
            self._on_json,
            10,
        )
        self.create_subscription(
            String,
            "/zeroerr/collision_monitor/config_state",
            self._on_config,
            10,
        )
        calibration_qos = QoSProfile(depth=1)
        calibration_qos.reliability = ReliabilityPolicy.RELIABLE
        calibration_qos.durability = DurabilityPolicy.TRANSIENT_LOCAL
        self.create_subscription(
            String,
            "/zeroerr_collision_calibration_runner/status",
            self._on_calibration_status,
            calibration_qos,
        )
        self.calibration_start = self.create_client(
            Trigger, "/zeroerr_collision_calibration_runner/start")
        self.collision_test_start = self.create_client(
            Trigger, "/zeroerr_collision_calibration_runner/start_test")
        self.calibration_stop = self.create_client(
            Trigger, "/zeroerr_collision_calibration_runner/stop")
        self.config_publisher = self.create_publisher(
            String, "/zeroerr/collision_monitor/config", 10)

    def _on_state(self, msg: DynamicJointState) -> None:
        latest: Dict[str, Dict[str, float]] = {}
        for joint_name, interfaces in zip(msg.joint_names, msg.interface_values):
            latest[joint_name] = {
                name: float(value)
                for name, value in zip(interfaces.interface_names, interfaces.values)
            }
        self.state = latest
        self.last_state_time = time.monotonic()

    def _on_json(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except (json.JSONDecodeError, TypeError):
            return
        for joint in payload.get("slaves", []):
            joint_name = str(joint.get("joint", ""))
            if not joint_name:
                continue
            dynamics_reason = str(joint.get("dynamics_reason", "")).strip()
            contact_reason = str(joint.get("contact_reason", "")).strip()
            self.reasons[joint_name] = dynamics_reason or contact_reason

    def _on_config(self, msg: String) -> None:
        try:
            payload = json.loads(msg.data)
        except (json.JSONDecodeError, TypeError):
            return
        values = payload.get("external_torque_thresholds", [])
        self.thresholds = {
            joint_name: float(values[index])
            for index, joint_name in enumerate(JOINT_NAMES)
            if index < len(values)
        }
        mode = str(payload.get("dynamics_estimator_mode", "unknown"))
        self.estimator = mode
        sensitivity = payload.get("collision_sensitivity_percent", 100.0)
        try:
            self.collision_sensitivity_percent = int(round(float(sensitivity)))
        except (TypeError, ValueError):
            self.collision_sensitivity_percent = 100
        self.active_stop_enabled = bool(payload.get("active_stop_enabled", False))
        try:
            self.confirm_duration_ms = max(
                0, int(round(float(payload.get("confirm_duration_ms", 25.0)))))
        except (TypeError, ValueError):
            self.confirm_duration_ms = 25
        try:
            self.dynamic_threshold_max_ratio = max(
                1.0,
                min(20.0, float(payload.get("dynamic_threshold_max_ratio", 5.0))),
            )
        except (TypeError, ValueError):
            self.dynamic_threshold_max_ratio = 5.0

    def set_collision_sensitivity(self, percent: int) -> None:
        value = max(50, min(200, int(percent)))
        msg = String()
        msg.data = json.dumps({"collision_sensitivity_percent": value})
        self.config_publisher.publish(msg)

    def set_active_stop_enabled(self, enabled: bool) -> None:
        msg = String()
        msg.data = json.dumps({"active_stop_enabled": bool(enabled)})
        self.config_publisher.publish(msg)

    def set_confirm_duration_ms(self, duration_ms: int) -> None:
        msg = String()
        msg.data = json.dumps({"confirm_duration_ms": max(0, int(duration_ms))})
        self.config_publisher.publish(msg)

    def set_dynamic_threshold_max_ratio(self, ratio: float) -> None:
        msg = String()
        msg.data = json.dumps({
            "dynamic_threshold_max_ratio": max(1.0, min(20.0, float(ratio)))
        })
        self.config_publisher.publish(msg)


    def _on_calibration_status(self, msg: String) -> None:
        try:
            self.calibration = json.loads(msg.data)
            self.last_calibration_time = time.monotonic()
        except (json.JSONDecodeError, TypeError):
            return

    def request_calibration_start(self) -> None:
        self._request_calibration(self.calibration_start, "start")

    def request_calibration_stop(self) -> None:
        self._request_calibration(self.calibration_stop, "stop")

    def request_collision_test_start(self) -> None:
        self._request_calibration(self.collision_test_start, "false-positive test start")

    def _request_calibration(self, client, operation: str) -> None:
        if self.calibration_request_pending:
            return
        if not client.service_is_ready():
            self.calibration_request_result = f"Calibration {operation} service is unavailable"
            return
        self.calibration_request_pending = True
        self.calibration_request_result = f"Requesting calibration {operation}..."
        future = client.call_async(Trigger.Request())
        future.add_done_callback(
            lambda completed, action=operation: self._on_calibration_response(completed, action)
        )

    def _on_calibration_response(self, future, operation: str) -> None:
        self.calibration_request_pending = False
        try:
            result = future.result()
            outcome = "accepted" if result.success else "refused"
            self.calibration_request_result = (
                f"Calibration {operation} {outcome}: {result.message}"
            )
        except Exception as exc:
            self.calibration_request_result = f"Calibration {operation} failed: {exc}"


class CollisionStatusWindow(QMainWindow):
    def __init__(self, node: CollisionStatusNode) -> None:
        super().__init__()
        self.node = node
        self.setWindowTitle("ZeroErr Sensorless Collision Status")
        self.resize(1280, 550)

        root = QWidget()
        layout = QVBoxLayout(root)
        self.banner = QLabel("WAITING FOR COLLISION MONITOR")
        self.banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.banner.setMinimumHeight(58)
        layout.addWidget(self.banner)

        self.detail = QLabel(
            "Waiting for /zeroerr/collision_monitor/state — detector may be disabled"
        )
        self.detail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.detail)

        calibration_group = QGroupBox("Calibration runner")
        calibration_layout = QHBoxLayout(calibration_group)
        self.calibration_status = QLabel("OFFLINE")
        self.calibration_status.setMinimumWidth(700)
        calibration_layout.addWidget(self.calibration_status, 1)
        layout.addWidget(calibration_group)

        sensitivity_group = QGroupBox("Collision sensitivity")
        sensitivity_layout = QHBoxLayout(sensitivity_group)
        sensitivity_layout.addWidget(QLabel("Less sensitive"))
        self.sensitivity_slider = QSlider(Qt.Orientation.Horizontal)
        self.sensitivity_slider.setRange(50, 200)
        self.sensitivity_slider.setSingleStep(5)
        self.sensitivity_slider.setPageStep(10)
        self.sensitivity_slider.setValue(100)
        self.sensitivity_slider.setToolTip(
            "100% is the calibrated baseline. Higher sensitivity lowers collision thresholds."
        )
        self.sensitivity_value = QLabel("100% (calibrated)")
        self.sensitivity_value.setMinimumWidth(150)
        self.sensitivity_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sensitivity_slider.valueChanged.connect(self._preview_sensitivity)
        self.sensitivity_slider.sliderReleased.connect(self._apply_sensitivity)
        sensitivity_layout.addWidget(self.sensitivity_slider, 1)
        sensitivity_layout.addWidget(QLabel("More sensitive"))
        sensitivity_layout.addWidget(self.sensitivity_value)
        self.active_mode_button = QPushButton("PASSIVE — REPORT ONLY")
        self.active_mode_button.setCheckable(True)
        self.active_mode_button.setMinimumWidth(220)
        self.active_mode_button.clicked.connect(self._change_active_mode)
        sensitivity_layout.addWidget(self.active_mode_button)
        layout.addWidget(sensitivity_group)

        confirmation_group = QGroupBox("Detection confirmation")
        confirmation_layout = QHBoxLayout(confirmation_group)
        confirmation_layout.addWidget(QLabel("Threshold exceedance before latching:"))
        self.confirm_duration_spin = QSpinBox()
        self.confirm_duration_spin.setRange(0, 1000)
        self.confirm_duration_spin.setValue(25)
        self.confirm_duration_spin.setSuffix(" ms")
        self.confirm_duration_spin.setToolTip(
            "A joint must continuously exceed its collision threshold for this "
            "measurement-timestamp duration before the detector latches."
        )
        self.confirm_duration_spin.editingFinished.connect(
            self._apply_confirm_duration)
        confirmation_layout.addWidget(self.confirm_duration_spin)
        confirmation_layout.addStretch(1)
        confirmation_layout.addWidget(QLabel(
            "Higher values reject brief spikes but delay collision response."
        ))
        layout.addWidget(confirmation_group)

        dynamic_cap_group = QGroupBox("Fast-motion sensitivity")
        dynamic_cap_layout = QHBoxLayout(dynamic_cap_group)
        dynamic_cap_layout.addWidget(QLabel("Maximum dynamic threshold:"))
        self.dynamic_threshold_max_ratio_spin = QDoubleSpinBox()
        self.dynamic_threshold_max_ratio_spin.setRange(1.0, 20.0)
        self.dynamic_threshold_max_ratio_spin.setDecimals(1)
        self.dynamic_threshold_max_ratio_spin.setSingleStep(0.5)
        self.dynamic_threshold_max_ratio_spin.setValue(5.0)
        self.dynamic_threshold_max_ratio_spin.setSuffix(" × static")
        self.dynamic_threshold_max_ratio_spin.setToolTip(
            "Caps the learned motion-conditioned threshold relative to each joint's "
            "static threshold. Lower values improve collision sensitivity during fast "
            "motion but can increase false detections."
        )
        self.dynamic_threshold_max_ratio_spin.editingFinished.connect(
            self._apply_dynamic_threshold_max_ratio)
        dynamic_cap_layout.addWidget(self.dynamic_threshold_max_ratio_spin)
        dynamic_cap_layout.addStretch(1)
        dynamic_cap_layout.addWidget(QLabel(
            "Lower values limit how much speed and acceleration can mask a collision."
        ))
        layout.addWidget(dynamic_cap_group)

        self.table = QTableWidget(len(JOINT_NAMES), len(COLUMNS))
        self.table.setHorizontalHeaderLabels(COLUMNS)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.setCentralWidget(root)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(100)
        self.refresh()

    @staticmethod
    def _finite(value: float | None) -> bool:
        return value is not None and math.isfinite(value)

    @classmethod
    def _number(cls, value: float | None, decimals: int = 2) -> str:
        return f"{value:.{decimals}f}" if cls._finite(value) else "NO DATA"

    def _set_banner(self, text: str, color: str) -> None:
        self.banner.setText(text)
        self.banner.setStyleSheet(
            f"font-size: 24px; font-weight: bold; color: white; "
            f"background-color: {color}; border-radius: 5px; padding: 8px;"
        )

    def refresh(self) -> None:
        age = time.monotonic() - self.node.last_state_time
        stale = not self.node.state or age > 0.5
        any_active = False
        any_latched = False
        missing_inputs = False
        observer_warming = False

        for row, joint_name in enumerate(JOINT_NAMES):
            state = self.node.state.get(joint_name, {})
            sensor = state.get("torque_sensor")
            expected = state.get("expected_torque")
            residual = state.get("torque_difference")
            external = state.get("external_torque")
            threshold = state.get(
                "external_torque_threshold",
                self.node.thresholds.get(joint_name),
            )
            active = bool(state.get("dynamics_active", 0.0)) or bool(
                state.get("contact_active", 0.0)
            )
            latched = bool(state.get("dynamics_latched", 0.0)) or bool(
                state.get("contact_latched", 0.0)
            )
            observer_ready_value = state.get("observer_ready")
            observer_ready = (
                self._finite(observer_ready_value)
                and float(observer_ready_value) >= 0.5
            )
            joint_warming = self._finite(sensor) and not observer_ready and not stale
            observer_warming |= joint_warming
            input_ok = (
                self._finite(sensor)
                and self._finite(external)
                and observer_ready
                and not stale
            )
            missing_inputs |= not input_ok and not joint_warming
            any_active |= active
            any_latched |= latched

            values = [
                joint_name,
                "OK" if input_ok else "WARMING" if joint_warming else "MISSING",
                self._number(sensor),
                self._number(expected),
                self._number(residual),
                self._number(external),
                self._number(threshold),
                "YES" if active else "NO",
                "YES" if latched else "NO",
                self.node.reasons.get(joint_name, ""),
            ]
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                if column in (1, 7, 8):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                if column == 1:
                    item.setBackground(QColor(
                        "#2e7d32" if input_ok else "#ef6c00" if joint_warming else "#c62828"
                    ))
                    item.setForeground(QColor("white"))
                elif column in (7, 8) and value == "YES":
                    item.setBackground(QColor("#c62828"))
                    item.setForeground(QColor("white"))
                self.table.setItem(row, column, item)

        if stale:
            self._set_banner("MONITOR OFFLINE / STATE STALE", "#616161")
            detail = "No fresh monitor state received"
        elif any_active or any_latched:
            self._set_banner("COLLISION DETECTED", "#c62828")
            detail = "One or more joints are ACTIVE or LATCHED"
        elif observer_warming:
            self._set_banner("DETECTOR WARMING UP — PROTECTION NOT ACTIVE", "#ef6c00")
            detail = "Momentum observer is initializing or waiting for stable drives"
        elif missing_inputs:
            self._set_banner("DETECTOR NOT READY — INPUT MISSING", "#ef6c00")
            detail = "At least one joint lacks valid torque or residual data"
        else:
            self._set_banner("NO COLLISION DETECTED", "#2e7d32")
            detail = "All detector inputs are valid"

        age_text = "never" if not self.node.last_state_time else f"{age:.2f} s ago"
        self.detail.setText(
            f"{detail}  |  estimator: {self.node.estimator}  |  last update: {age_text}"
        )
        self._refresh_calibration()
        if not self.sensitivity_slider.isSliderDown():
            configured = self.node.collision_sensitivity_percent
            if self.sensitivity_slider.value() != configured:
                self.sensitivity_slider.setValue(configured)
        self._refresh_active_mode_button()
        if not self.confirm_duration_spin.hasFocus():
            configured_duration = self.node.confirm_duration_ms
            if self.confirm_duration_spin.value() != configured_duration:
                self.confirm_duration_spin.setValue(configured_duration)
        if not self.dynamic_threshold_max_ratio_spin.hasFocus():
            configured_ratio = self.node.dynamic_threshold_max_ratio
            if self.dynamic_threshold_max_ratio_spin.value() != configured_ratio:
                self.dynamic_threshold_max_ratio_spin.setValue(configured_ratio)

    def _preview_sensitivity(self, value: int) -> None:
        suffix = " (calibrated)" if value == 100 else ""
        threshold_scale = 100.0 / value
        self.sensitivity_value.setText(
            f"{value}%{suffix} — thresholds ×{threshold_scale:.2f}"
        )

    def _apply_sensitivity(self) -> None:
        value = self.sensitivity_slider.value()
        if value < 100:
            answer = QMessageBox.warning(
                self,
                "Reduce collision sensitivity?",
                "This raises collision thresholds and can make lighter collisions harder "
                "to detect. Apply the reduced sensitivity?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self.sensitivity_slider.setValue(
                    self.node.collision_sensitivity_percent)
                return
        self.node.set_collision_sensitivity(value)

    def _apply_confirm_duration(self) -> None:
        self.node.set_confirm_duration_ms(self.confirm_duration_spin.value())

    def _apply_dynamic_threshold_max_ratio(self) -> None:
        ratio = self.dynamic_threshold_max_ratio_spin.value()
        if ratio > self.node.dynamic_threshold_max_ratio:
            answer = QMessageBox.warning(
                self,
                "Increase fast-motion threshold cap?",
                "A higher cap can make collisions during fast motion harder to detect. "
                "Apply the increased cap?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                self.dynamic_threshold_max_ratio_spin.setValue(
                    self.node.dynamic_threshold_max_ratio)
                return
        self.node.set_dynamic_threshold_max_ratio(ratio)

    def _refresh_active_mode_button(self) -> None:
        enabled = self.node.active_stop_enabled
        self.active_mode_button.blockSignals(True)
        self.active_mode_button.setChecked(enabled)
        self.active_mode_button.setText(
            "ACTIVE — STOPS MOTION" if enabled else "PASSIVE — REPORT ONLY")
        self.active_mode_button.setStyleSheet(
            "font-weight: bold; color: white; padding: 7px; "
            f"background-color: {'#c62828' if enabled else '#616161'};"
        )
        self.active_mode_button.blockSignals(False)

    def _change_active_mode(self, requested_active: bool) -> None:
        if requested_active:
            title = "Enable active collision stopping?"
            message = (
                "When a collision is confirmed, the monitor will cancel the active "
                "trajectory, stop Servo jogging, and clear queued motion. The production "
                "process will enter an error state. Enable ACTIVE mode?"
            )
        else:
            title = "Switch collision monitor to passive?"
            message = (
                "Confirmed collisions will only be reported and logged; robot motion will "
                "not be stopped automatically. Enable PASSIVE mode?"
            )
        answer = QMessageBox.question(
            self,
            title,
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            self._refresh_active_mode_button()
            return
        self.node.set_active_stop_enabled(requested_active)


    def _refresh_calibration(self) -> None:
        status_age = time.monotonic() - self.node.last_calibration_time
        online = bool(self.node.calibration) and status_age <= 2.0
        running = bool(self.node.calibration.get("running", False)) if online else False
        dry_run = bool(self.node.calibration.get("dry_run", True)) if online else True
        stage = str(self.node.calibration.get("stage", "unknown")) if online else "offline"
        accepted = int(self.node.calibration.get("accepted_motions", 0)) if online else 0
        rejected = int(self.node.calibration.get("rejected_motions", 0)) if online else 0
        coverage = int(self.node.calibration.get("coverage_points", 0)) if online else 0
        profile = str(self.node.calibration.get("dynamic_profile", "none")) if online else "none"
        drive_fault = str(self.node.calibration.get("drive_fault", "")) if online else ""
        run_type = str(self.node.calibration.get("run_type", "calibration")) if online else "unknown"
        collision_events = int(self.node.calibration.get("collision_events", 0)) if online else 0
        mode = "DRY RUN — NO MOTION" if dry_run else "LIVE ROBOT MOTION"
        text = (
            f"{mode}  |  run: {run_type}  |  stage: {stage}  |  "
            f"detections: {collision_events}  |  accepted: {accepted}  |  "
            f"rejected: {rejected}  |  measured XYZ points: "
            f"{'N/A in dry run' if dry_run else coverage}  |  {profile}"
            if online else "Calibration runner OFFLINE"
        )
        if self.node.calibration_request_result:
            text += f"  |  {self.node.calibration_request_result}"
        if drive_fault:
            text += f"  |  FAULT: {drive_fault}"
        self.calibration_status.setText(text)
        self.calibration_status.setStyleSheet(
            "font-weight: bold; color: #c62828;" if online and not dry_run
            else "font-weight: bold; color: #1565c0;" if online
            else "font-weight: bold; color: #616161;"
        )

    def start_calibration(self) -> None:
        dry_run = bool(self.node.calibration.get("dry_run", True))
        if dry_run:
            title = "Start calibration dry run?"
            message = (
                "This is a validation-only run. MoveIt will check every candidate, "
                "but no controller motion will be sent."
            )
        else:
            title = "Start LIVE robot calibration?"
            message = (
                "This will move the physical robot through the configured calibration sequence.\n\n"
                "Confirm the workspace is clear, the robot is supervised, and the hardware "
                "emergency stop is accessible. The sensorless collision monitor is passive."
            )
        answer = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.node.request_calibration_start()

    def start_collision_test(self) -> None:
        dry_run = bool(self.node.calibration.get("dry_run", True))
        title = "Run collision false-positive test?"
        message = (
            "This runs a compact set of MoveIt-validated, bidirectional joint motions "
            "at the configured velocity and acceleration profiles. Any collision "
            "indication will be recorded with the motion and joint state."
        )
        if not dry_run:
            message += (
                "\n\nThe physical robot will move. Supervise it, clear the workspace, "
                "and keep the hardware emergency stop accessible."
            )
        answer = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.node.request_collision_test_start()

    def stop_calibration(self) -> None:
        self.node.request_calibration_stop()


def main() -> None:
    rclpy.init()
    node = CollisionStatusNode()
    app = QApplication(sys.argv)
    window = CollisionStatusWindow(node)
    window.show()

    spin_timer = QTimer()
    spin_timer.timeout.connect(lambda: rclpy.spin_once(node, timeout_sec=0.0))
    spin_timer.start(10)

    try:
        app.exec()
    finally:
        spin_timer.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
