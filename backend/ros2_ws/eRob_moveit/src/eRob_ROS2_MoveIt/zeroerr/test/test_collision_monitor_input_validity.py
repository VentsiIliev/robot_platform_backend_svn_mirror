import unittest
from types import SimpleNamespace

from scripts.zeroerr_collision_monitor import ZeroErrCollisionMonitor


class _Clock:
    def __init__(self, seconds):
        self._nanoseconds = int(seconds * 1e9)

    def now(self):
        return SimpleNamespace(nanoseconds=self._nanoseconds)


class _MonitorState:
    def __init__(self, now=10.0):
        self._joint_sample_complete = True
        self._dynamic_sample_complete = True
        self._last_joint_sample_time = 9.95
        self._last_dynamic_sample_time = 9.96
        self._clock = _Clock(now)
        self._parameters = {
            "input_timeout_sec": 0.25,
            "input_sync_tolerance_sec": 0.10,
        }

    def get_clock(self):
        return self._clock

    def get_parameter(self, name):
        return SimpleNamespace(value=self._parameters[name])


class CollisionMonitorInputValidityTests(unittest.TestCase):
    def test_accepts_recent_complete_synchronized_samples(self):
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

    def test_rejects_unsynchronized_streams(self):
        state = _MonitorState()
        state._last_joint_sample_time = 9.80
        state._last_dynamic_sample_time = 9.95

        valid, reason = ZeroErrCollisionMonitor._input_validity(state)

        self.assertFalse(valid)
        self.assertIn("unsynchronized", reason)

    def test_rejects_incomplete_sample(self):
        state = _MonitorState()
        state._joint_sample_complete = False

        valid, reason = ZeroErrCollisionMonitor._input_validity(state)

        self.assertFalse(valid)
        self.assertIn("incomplete", reason)


if __name__ == "__main__":
    unittest.main()
