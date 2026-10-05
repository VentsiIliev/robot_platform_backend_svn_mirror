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
        self.start_calibration_button = QPushButton("Start calibration")
        self.start_test_button = QPushButton("Run false-positive test")
        self.stop_calibration_button = QPushButton("Stop calibration")
        self.start_calibration_button.clicked.connect(self.start_calibration)
        self.start_test_button.clicked.connect(self.start_collision_test)
        self.stop_calibration_button.clicked.connect(self.stop_calibration)
        calibration_layout.addWidget(self.calibration_status, 1)
        calibration_layout.addWidget(self.start_calibration_button)
        calibration_layout.addWidget(self.start_test_button)
        calibration_layout.addWidget(self.stop_calibration_button)
        layout.addWidget(calibration_group)

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
            input_ok = self._finite(sensor) and self._finite(external) and not stale
            missing_inputs |= not input_ok
            any_active |= active
            any_latched |= latched

            values = [
                joint_name,
                "OK" if input_ok else "MISSING",
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
                    item.setBackground(QColor("#2e7d32" if input_ok else "#c62828"))
                    item.setForeground(QColor("white"))
                elif column in (7, 8) and value == "YES":
                    item.setBackground(QColor("#c62828"))
                    item.setForeground(QColor("white"))
                self.table.setItem(row, column, item)

        if stale:
            self._set_banner("MONITOR OFFLINE / STATE STALE", "#616161")
            detail = "No fresh monitor state received"
        elif missing_inputs:
            self._set_banner("DETECTOR NOT READY — INPUT MISSING", "#ef6c00")
            detail = "At least one joint lacks valid torque or residual data"
        elif any_active or any_latched:
            self._set_banner("COLLISION DETECTED", "#c62828")
            detail = "One or more joints are ACTIVE or LATCHED"
        else:
            self._set_banner("NO COLLISION DETECTED", "#2e7d32")
            detail = "All detector inputs are valid"

        age_text = "never" if not self.node.last_state_time else f"{age:.2f} s ago"
        self.detail.setText(
            f"{detail}  |  estimator: {self.node.estimator}  |  last update: {age_text}"
        )
        self._refresh_calibration()

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
        pending = self.node.calibration_request_pending
        self.start_calibration_button.setEnabled(
            online and not running and not pending and self.node.calibration_start.service_is_ready()
        )
        self.start_test_button.setEnabled(
            online and not running and not pending
            and self.node.collision_test_start.service_is_ready()
        )
        self.stop_calibration_button.setEnabled(
            online and running and not pending and self.node.calibration_stop.service_is_ready()
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
