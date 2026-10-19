#!/usr/bin/env python3
"""Record peak-preserving C++ collision samples without loading the RT loop."""

from __future__ import annotations

import csv
import json
import math
import time
from pathlib import Path

import rclpy
from control_msgs.msg import DynamicJointState
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data


class PeakRecorder(Node):
    def __init__(self) -> None:
        super().__init__("zeroerr_peak_recorder")
        self.declare_parameter(
            "output_root",
            str(Path.home() / "zeroerr_data/collision_detection/peak_sessions"),
        )
        session_id = time.strftime("%Y%m%d-%H%M%S")
        self._directory = Path(
            str(self.get_parameter("output_root").value)
        ).expanduser() / session_id
        self._directory.mkdir(parents=True)
        self._path = self._directory / "peak_samples.csv"
        self._handle = self._path.open("w", newline="", encoding="utf-8")
        self._writer = csv.writer(self._handle)
        self._writer.writerow([
            "session_id", "sequence", "timestamp", "joint",
            "position_1", "position_2", "position_3",
            "position_4", "position_5", "position_6",
            "velocity_rad_s", "acceleration_rad_s2",
            "measured_torque_nm", "expected_torque_nm",
            "external_torque_nm", "threshold_nm",
        ])
        self._session_id = session_id
        self._sequence = 0
        self._rows = 0
        self._started = time.time()
        self._last_flush = time.monotonic()
        self.create_subscription(
            DynamicJointState,
            "/zeroerr/collision_rt/peak_samples",
            self._on_sample,
            qos_profile_sensor_data,
        )
        self.get_logger().info(f"Peak-preserving recording -> {self._path}")

    def _on_sample(self, message: DynamicJointState) -> None:
        timestamp = float(message.header.stamp.sec) + 1.0e-9 * float(
            message.header.stamp.nanosec)
        for joint, interfaces in zip(message.joint_names, message.interface_values):
            fields = dict(zip(interfaces.interface_names, interfaces.values))
            required = [
                *(f"position_{index}" for index in range(1, 7)),
                "velocity", "acceleration", "measured_torque",
                "expected_torque", "external_torque", "threshold",
            ]
            values = [float(fields.get(name, math.nan)) for name in required]
            if not all(math.isfinite(value) for value in values):
                continue
            self._writer.writerow([
                self._session_id, self._sequence, f"{timestamp:.9f}", joint,
                *values,
            ])
            self._rows += 1
        self._sequence += 1
        now = time.monotonic()
        if now - self._last_flush >= 1.0:
            self._handle.flush()
            self._last_flush = now

    def close(self) -> None:
        if self._handle.closed:
            return
        self._handle.flush()
        self._handle.close()
        metadata = {
            "session_id": self._session_id,
            "started_unix": self._started,
            "stopped_unix": time.time(),
            "messages": self._sequence,
            "rows": self._rows,
            "source_topic": "/zeroerr/collision_rt/peak_samples",
            "source_semantics": "largest absolute C++ observer residual per joint per 10 ms window",
        }
        (self._directory / "metadata.json").write_text(
            json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        # Ctrl+C may already have invalidated the ROS context.  Report the
        # completed filesystem cleanup without publishing another rosout
        # message through that context.
        print(
            f"Recorded {self._sequence} peak windows "
            f"({self._rows} rows) in {self._directory}",
            flush=True,
        )


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PeakRecorder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.close()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
