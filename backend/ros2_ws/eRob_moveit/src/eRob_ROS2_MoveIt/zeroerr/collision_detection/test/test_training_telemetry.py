"""Exercise recording against the C++ producer's actual telemetry field contract."""
import csv
import importlib.util
import io
import math
from pathlib import Path
import re
from types import SimpleNamespace
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'calibration/data_collection' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


runner = load_module('training_runner', 'zeroerr_collision_calibration_runner.py')
peak = load_module('training_peak_recorder', 'zeroerr_peak_recorder.py')


class TrainingTelemetryTests(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.warnings = []
        self.state = SimpleNamespace(
            _training_csv_writer=csv.writer(self.output), _training_csv_file=self.output,
            _last_training_write=0.0, _last_training_flush=0.0,
            _training_samples=0, _training_rejected_samples=0,
            _training_rejection_reason='', joint_names=[f'Joint_{i}' for i in range(1, 7)],
            get_parameter=lambda name: SimpleNamespace(value=0.0),
            get_logger=lambda: SimpleNamespace(warning=self.warnings.append),
        )
        source = (ROOT / 'runtime/src/realtime_collision_controller.cpp').read_text()
        contract = source.split('state_publisher_->msg_.interface_values.resize')[1]
        names = contract.split('interfaces.interface_names = {')[1].split('};')[0]
        self.names = re.findall(r'"([^"]+)"', names)

    def message(self, remove=None, change=None):
        interfaces = []
        for index in range(6):
            fields = {name: float(index + 1) for name in self.names}
            fields['observer_ready'] = 1.0
            # Deliberately distinct: full inverse dynamics must not become auxiliary torque.
            fields['expected_torque'] = 13.0
            fields['observer_auxiliary_torque'] = -2.0
            if remove:
                fields.pop(remove, None)
            if change:
                fields.update(change)
            interfaces.append(SimpleNamespace(interface_names=list(fields), values=list(fields.values())))
        return SimpleNamespace(
            header=SimpleNamespace(stamp=SimpleNamespace(sec=123, nanosec=500000000)),
            joint_names=self.state.joint_names, interface_values=interfaces)

    def record(self, message):
        runner.CalibrationRunner._append_external_training_sample(self.state, message)
        return list(csv.reader(io.StringIO(self.output.getvalue())))

    def test_actual_producer_contract_records_six_synchronized_rows_without_following_error(self):
        rows = self.record(self.message())
        self.assertEqual(len(rows), 6)
        self.assertEqual({row[0] for row in rows}, {'123.500000000'})
        self.assertEqual([row[1] for row in rows], self.state.joint_names)
        self.assertEqual([float(row[2]) for row in rows], list(range(1, 7)))
        self.assertTrue(all(float(row[7]) == 13.0 and float(row[8]) == -2.0 for row in rows))
        self.assertTrue(all(math.isnan(float(row[10])) for row in rows))
        self.assertEqual(self.state._training_samples, 1)

    def test_missing_torque_rejects_entire_batch_and_reports_reason(self):
        self.assertEqual(self.record(self.message(remove='expected_torque')), [])
        self.assertEqual(self.state._training_rejected_samples, 1)
        self.assertIn('expected_torque', self.state._training_rejection_reason)
        self.assertEqual(len(self.warnings), 1)

    def test_legacy_readiness_only_message_is_diagnosed(self):
        msg = self.message()
        for values in msg.interface_values:
            values.interface_names = ['observer_ready']
            values.values = [1.0]
        self.assertEqual(self.record(msg), [])
        self.assertIn('position', self.state._training_rejection_reason)

    def test_unready_or_nonfinite_joint_never_writes_partial_batch(self):
        for change in ({'observer_ready': 0.0}, {'measured_torque': math.nan}):
            with self.subTest(change=change):
                self.assertEqual(self.record(self.message(change=change)), [])
        self.assertEqual(self.state._training_samples, 0)

    def test_missing_joint_rejects_entire_batch(self):
        msg = self.message()
        msg.joint_names = msg.joint_names[:-1]
        self.assertEqual(self.record(msg), [])
        self.assertIn('Joint_6', self.state._training_rejection_reason)

    def test_recovery_clears_reason_and_writes_again(self):
        self.record(self.message(remove='acceleration'))
        self.assertEqual(len(self.record(self.message())), 6)
        self.assertEqual(self.state._training_rejection_reason, '')

    def test_recording_period_decimates_without_counting_as_rejection(self):
        self.state.get_parameter = lambda name: SimpleNamespace(value=3600.0)
        self.state._last_training_write = runner.time.monotonic()
        self.assertEqual(self.record(self.message()), [])
        self.assertEqual(self.state._training_rejected_samples, 0)

    def test_peak_recorder_distinguishes_source_span_from_lifetime(self):
        state = SimpleNamespace(
            _first_source_timestamp=None, _last_source_timestamp=None,
            _max_source_gap_sec=0.0, _last_received=None, _max_receive_gap_sec=0.0,
            _writer=csv.writer(self.output), _session_id='test', _sequence=0,
            _rows=0, _last_flush=peak.time.monotonic(), _handle=self.output)
        msg = self.message()
        # Timing diagnostics do not depend on accepting a row.
        peak.PeakRecorder._on_sample(state, msg)
        msg.header.stamp.sec += 2
        peak.PeakRecorder._on_sample(state, msg)
        self.assertEqual(state._last_source_timestamp - state._first_source_timestamp, 2.0)
        self.assertEqual(state._max_source_gap_sec, 2.0)


if __name__ == '__main__':
    unittest.main()
