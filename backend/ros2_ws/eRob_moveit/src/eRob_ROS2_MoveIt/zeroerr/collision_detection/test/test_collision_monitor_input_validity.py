import unittest
from types import SimpleNamespace

from collision_detection.runtime.legacy.zeroerr_collision_monitor import (
    ZeroErrCollisionMonitor,
)


class _Clock:
    def __init__(self, seconds):
        self._nanoseconds = int(seconds * 1e9)

    def now(self):
        return SimpleNamespace(nanoseconds=self._nanoseconds)


class _MonitorState:
    def __init__(self, now=10.0):
        self._dynamic_sample_complete = True
        self._last_dynamic_sample_time = 9.96
        self._clock = _Clock(now)
        self._parameters = {
            "input_timeout_sec": 0.25,
        }

    def get_clock(self):
        return self._clock

    def get_parameter(self, name):
        return SimpleNamespace(value=self._parameters[name])


class CollisionMonitorInputValidityTests(unittest.TestCase):
    def test_reset_confirmation_windows_breaks_all_joint_continuity(self):
        state = SimpleNamespace(
            _slave_count=2,
            _dynamics_cycles={"Joint_1": 8, "Joint_2": 4},
            _dynamics_exceedance_since={"Joint_1": 1.0, "Joint_2": 2.0},
            _contact_cycles={"Joint_1": 3, "Joint_2": 2},
            _contact_exceedance_since={"Joint_1": 1.5, "Joint_2": 2.5},
        )

        ZeroErrCollisionMonitor._reset_confirmation_windows(state)

        self.assertEqual({"Joint_1": 0, "Joint_2": 0}, state._dynamics_cycles)
        self.assertEqual(
            {"Joint_1": None, "Joint_2": None},
            state._dynamics_exceedance_since,
        )
        self.assertEqual({"Joint_1": 0, "Joint_2": 0}, state._contact_cycles)
        self.assertEqual(
            {"Joint_1": None, "Joint_2": None},
            state._contact_exceedance_since,
        )

    def test_exceedance_duration_uses_measurement_timestamps(self):
        self.assertAlmostEqual(
            0.025,
            ZeroErrCollisionMonitor._exceedance_duration_sec(10.0, 10.025),
        )

    def test_exceedance_duration_is_zero_without_active_window(self):
        self.assertEqual(
            0.0,
            ZeroErrCollisionMonitor._exceedance_duration_sec(None, 10.025),
        )

    def test_message_timestamp_uses_source_header(self):
        message = SimpleNamespace(
            header=SimpleNamespace(stamp=SimpleNamespace(sec=12, nanosec=345_000_000))
        )

        timestamp = ZeroErrCollisionMonitor._message_timestamp(message)

        self.assertAlmostEqual(12.345, timestamp)

    def test_message_timestamp_rejects_unset_header(self):
        message = SimpleNamespace(
            header=SimpleNamespace(stamp=SimpleNamespace(sec=0, nanosec=0))
        )

        with self.assertRaisesRegex(ValueError, "timestamp"):
            ZeroErrCollisionMonitor._message_timestamp(message)

    def test_accepts_recent_complete_atomic_sample(self):
        state = _MonitorState()

        valid, reason = ZeroErrCollisionMonitor._input_validity(state)

        self.assertTrue(valid)
        self.assertEqual("", reason)

    def test_rejects_stale_stream(self):
        state = _MonitorState()
        state._last_dynamic_sample_time = 9.0

        valid, reason = ZeroErrCollisionMonitor._input_validity(state)

        self.assertFalse(valid)
        self.assertIn("stale", reason)

    def test_rejects_incomplete_sample(self):
        state = _MonitorState()
        state._dynamic_sample_complete = False

        valid, reason = ZeroErrCollisionMonitor._input_validity(state)

        self.assertFalse(valid)
        self.assertIn("incomplete", reason)


if __name__ == "__main__":
    unittest.main()
