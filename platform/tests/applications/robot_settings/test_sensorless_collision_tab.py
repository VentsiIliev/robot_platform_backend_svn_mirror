import sys
import unittest

from PyQt6.QtWidgets import QApplication

from src.applications.robot_settings.view.sensorless_collision_tab import (
    SensorlessCollisionTab,
)


class SensorlessCollisionTabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication(sys.argv)

    def test_round_trip_operational_configuration(self):
        tab = SensorlessCollisionTab()
        config = {
            "detection_enabled": True,
            "active_stop_enabled": True,
            "effort_following_error_detection_enabled": True,
            "dynamic_threshold_enabled": True,
            "diagnostics_enabled": True,
            "collision_sensitivity_percent": 135.0,
            "confirm_duration_ms": 25.0,
            "dynamic_threshold_max_ratio": 2.5,
            "dynamic_threshold_decay_sec": 0.4,
            "external_torque_thresholds": [1, 2, 3, 4, 5, 6],
            "effort_thresholds": [10, 20, 30, 40, 50, 60],
            "following_error_thresholds": [100, 200, 300, 400, 500, 600],
        }

        tab.load_config(config)
        result = tab.values()

        for key, expected in config.items():
            self.assertEqual(result[key], expected)

    def test_save_signal_contains_current_values(self):
        tab = SensorlessCollisionTab()
        emitted = []
        tab.save_requested.connect(emitted.append)

        tab._emit_save()

        self.assertEqual(len(emitted), 1)
        self.assertIn("detection_enabled", emitted[0])
