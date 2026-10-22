import json
import logging
import sqlite3
import threading
import tempfile
import time
import unittest
from enum import Enum
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from src.engine.diagnostics.events import diagnostic_context, observe, current_context
from src.engine.diagnostics.runtime import DiagnosticsRuntime
from src.engine.diagnostics.report import read_summary, export_support_bundle


class DiagnosticsRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / 'diagnostics'
        self.logger = logging.getLogger('test.machine')

    def start(self, **options):
        runtime = DiagnosticsRuntime(self.directory, **options)
        self.addCleanup(runtime.close)
        self.assertTrue(runtime.start(), runtime.status)
        return runtime

    def wait_error(self, runtime):
        deadline = time.monotonic() + 2
        while runtime.status['last_error'] is None and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertIsNotNone(runtime.status['last_error'])

    def test_counters_survive_restart_and_keep_expected_outcomes_separate(self):
        first = self.start()
        observe(self.logger, 'cycle.ended', metrics={'paint.cycle.outcome.unmatched': 1})
        first.close()
        second = self.start()
        observe(self.logger, 'cycle.ended', metrics={'paint.cycle.outcome.completed': 1})
        second.close()
        metrics = read_summary(self.directory)['metrics']
        self.assertEqual(metrics['paint.cycle.outcome.unmatched']['total'], 1)
        self.assertEqual(metrics['paint.cycle.outcome.completed']['total'], 1)
        self.assertEqual(metrics['diagnostics.sessions']['total'], 2)
        self.assertNotIn('paint.failure.internal', metrics)

    def test_repeated_on_does_not_inflate_activations_or_duration(self):
        runtime = self.start(checkpoint_seconds=60)
        base = time.monotonic()
        for offset, state in ((0, True), (2, True), (5, False)):
            with patch('src.engine.diagnostics.events.monotonic', return_value=base + offset):
                observe(self.logger, 'output.written', output=('vacuum_pump', state))
        runtime.close()
        metrics = read_summary(self.directory)['metrics']
        self.assertEqual(metrics['vacuum_pump.commanded_on_intervals']['total'], 1)
        self.assertEqual(metrics['vacuum_pump.commanded_on_seconds']['total'], 5)

    def test_failed_off_marks_unknown_and_does_not_assume_physical_shutdown(self):
        runtime = self.start(checkpoint_seconds=60)
        base = time.monotonic()
        for offset, state in ((0, True), (4, None)):
            with patch('src.engine.diagnostics.events.monotonic', return_value=base + offset):
                observe(self.logger, 'output.written', output=('fan', state))
        runtime.close()
        metrics = read_summary(self.directory)['metrics']
        self.assertEqual(metrics['fan.commanded_on_seconds']['total'], 4)
        self.assertEqual(metrics['fan.unknown_state_events']['total'], 1)

    def test_unclean_previous_session_does_not_credit_downtime(self):
        runtime = self.start()
        runtime.close()
        db = sqlite3.connect(self.directory / 'statistics.sqlite3')
        db.execute("INSERT INTO sessions(id,started) VALUES('crashed','2020-01-01')")
        db.execute("INSERT INTO outputs(name,state) VALUES('pump',1)")
        db.commit()
        db.close()
        restarted = self.start()
        restarted.close()
        summary = read_summary(self.directory)
        self.assertEqual(summary['metrics']['diagnostics.interrupted_sessions']['total'], 1)
        self.assertEqual(summary['metrics']['pump.unconfirmed_intervals']['total'], 1)
        self.assertNotIn('pump.commanded_on_seconds', summary['metrics'])

    def test_context_is_scoped_and_tracebacks_are_persisted(self):
        runtime = self.start()
        original = self.logger.level
        self.logger.setLevel(logging.INFO)
        self.addCleanup(self.logger.setLevel, original)
        with diagnostic_context(cycle_id='cycle-123'):
            try:
                raise RuntimeError('device failed')
            except RuntimeError:
                self.logger.exception('command failed')
        self.assertEqual(current_context(), {})
        runtime.close()
        record = json.loads((self.directory / 'events.jsonl').read_text().splitlines()[0])
        self.assertEqual(record['context']['cycle_id'], 'cycle-123')
        self.assertIn('RuntimeError: device failed', record['traceback'])
        self.assertEqual(record['session_id'], runtime.session_id)

    def test_metrics_are_collected_when_component_logging_is_disabled(self):
        runtime = self.start()
        with patch.object(self.logger, 'level', logging.CRITICAL):
            observe(self.logger, 'command', metrics={'command.count': 1})
        runtime.close()
        self.assertEqual(read_summary(self.directory)['metrics']['command.count']['total'], 1)

    def test_direct_exception_capture_preserves_bounded_cause_chain(self):
        runtime = self.start()
        try:
            try:
                raise ValueError('root failure')
            except ValueError as cause:
                raise RuntimeError('operation failed') from cause
        except RuntimeError:
            observe(self.logger, 'operation.failed', level=logging.ERROR)
        runtime.close()
        record = json.loads((self.directory / 'events.jsonl').read_text().splitlines()[0])
        self.assertIn('ValueError: root failure', record['traceback'])
        self.assertIn('RuntimeError: operation failed', record['traceback'])
        self.assertLessEqual(len(record['traceback']), 4096)

    def test_invalid_metric_is_rejected_atomically_without_stopping_writer(self):
        runtime = self.start(checkpoint_seconds=60)
        observe(self.logger, 'invalid', metrics={'must_not_persist': 2, 'bad': -1})
        observe(self.logger, 'valid', metrics={'valid': 1})
        runtime.close()
        metrics = read_summary(self.directory)['metrics']
        self.assertEqual(metrics['valid']['total'], 1)
        self.assertNotIn('must_not_persist', metrics)
        self.assertNotIn('bad', metrics)
        self.assertEqual(runtime.status['dropped_events'], 1)
        self.assertIsNone(runtime.status['last_error'])

    def test_invalid_optional_field_does_not_discard_off_transition(self):
        runtime = self.start(checkpoint_seconds=60)
        base = time.monotonic()
        for offset, state, fields in ((0, True, {}), (4, False, {'detail': float('nan')}),
                                      (10, False, {})):
            with patch('src.engine.diagnostics.events.monotonic', return_value=base + offset):
                observe(self.logger, 'output', output=('pump', state), **fields)
        runtime.close()
        metrics = read_summary(self.directory)['metrics']
        self.assertEqual(metrics['pump.commanded_on_seconds']['total'], 4)
        self.assertEqual(runtime.status['omitted_fields'], 1)
        self.assertEqual(runtime.status['dropped_events'], 0)
        records = [json.loads(line) for line in (self.directory / 'events.jsonl').read_text().splitlines()]
        self.assertEqual(records[1]['omitted_fields'], 1)

    def test_optional_objects_are_not_formatted_and_success_history_is_retained(self):
        class Unsafe:
            def __str__(self):
                raise AssertionError('diagnostics must not format arbitrary objects')
        runtime = self.start()
        observe(self.logger, 'cycle.completed', detail=Unsafe(), outcome='success')
        runtime.close()
        record = json.loads((self.directory / 'events.jsonl').read_text().splitlines()[0])
        self.assertEqual(record['fields']['outcome'], 'success')
        self.assertNotIn('detail', record['fields'])
        self.assertEqual(record['omitted_fields'], 1)

    def test_rejected_record_invalidates_output_before_next_off(self):
        runtime = self.start(checkpoint_seconds=60)
        base = time.monotonic()
        with patch('src.engine.diagnostics.events.monotonic', return_value=base):
            observe(self.logger, 'on', output=('pump', True))
        with patch('src.engine.diagnostics.events.monotonic', return_value=base + 4):
            observe(self.logger, 'invalid.off', output=('pump', False), metrics={'bad': -1})
        with patch('src.engine.diagnostics.events.monotonic', return_value=base + 10):
            observe(self.logger, 'off', output=('pump', False))
        runtime.close()
        metrics = read_summary(self.directory)['metrics']
        self.assertEqual(metrics.get('pump.commanded_on_seconds', {}).get('total', 0), 0)
        self.assertEqual(metrics['pump.unconfirmed_intervals']['total'], 1)
        self.assertEqual(metrics['diagnostics.dropped_events']['total'], 1)

    def test_writer_rejection_rolls_back_prior_record_effects_and_continues(self):
        runtime = self.start(checkpoint_seconds=60)
        original = runtime._metric
        def metric(db, name, value):
            if name == 'reject_at_writer':
                raise ValueError('invalid producer data')
            original(db, name, value)
        with patch.object(runtime, '_metric', side_effect=metric):
            observe(self.logger, 'invalid', metrics={'rolled_back': 2, 'reject_at_writer': 1})
            observe(self.logger, 'valid', metrics={'valid': 1})
            runtime.close()
        metrics = read_summary(self.directory)['metrics']
        self.assertNotIn('rolled_back', metrics)
        self.assertEqual(metrics['valid']['total'], 1)
        self.assertEqual(runtime.status['rejections']['writer_rejection'], 1)
        self.assertIsNone(runtime.status['last_error'])

    def test_lost_off_is_invalidated_before_later_off_after_queue_saturation(self):
        entered, release, queued_written = threading.Event(), threading.Event(), threading.Event()
        from logging.handlers import RotatingFileHandler
        original = RotatingFileHandler.shouldRollover
        def blocked(handler, record):
            event = json.loads(record.msg).get('event')
            if event == 'on':
                entered.set()
                release.wait(2)
            if event == 'queued':
                queued_written.set()
            return original(handler, record)
        runtime = self.start(queue_size=1, checkpoint_seconds=60)
        base = time.monotonic()
        with patch('src.engine.diagnostics.runtime.RotatingFileHandler.shouldRollover', blocked):
            try:
                with patch('src.engine.diagnostics.events.monotonic', return_value=base):
                    observe(self.logger, 'on', output=('pump', True))
                self.assertTrue(entered.wait(1))
                observe(self.logger, 'queued')
                with patch('src.engine.diagnostics.events.monotonic', return_value=base + 4):
                    observe(self.logger, 'lost.off', output=('pump', False))
                self.assertEqual(runtime.status['rejections']['queue_full'], 1)
                release.set()
                self.assertTrue(queued_written.wait(1))
                with patch('src.engine.diagnostics.events.monotonic', return_value=base + 10):
                    observe(self.logger, 'off', output=('pump', False))
                runtime.close()
            finally:
                release.set()
        metrics = read_summary(self.directory)['metrics']
        self.assertEqual(metrics.get('pump.commanded_on_seconds', {}).get('total', 0), 0)
        self.assertEqual(metrics['pump.unconfirmed_intervals']['total'], 1)

    def test_compatibility_input_does_not_invoke_arbitrary_formatting(self):
        class Unsafe:
            def __str__(self):
                raise AssertionError('unexpected formatting hook')
        runtime = self.start()
        record = logging.LogRecord('legacy', logging.INFO, '', 0, '%s', (Unsafe(),), None)
        runtime._handler.emit(record)
        record = logging.LogRecord('legacy', logging.INFO, '', 0, '%1000000000s', ('x',), None)
        runtime._handler.emit(record)
        runtime.close()
        records = [json.loads(line) for line in (self.directory / 'events.jsonl').read_text().splitlines()]
        self.assertEqual(len(records), 2)
        self.assertTrue(all(record['omitted_fields'] > 0 for record in records))

    def test_context_depth_and_size_are_bounded_before_serialization(self):
        runtime = self.start()
        nested = 'x'
        for _ in range(100):
            nested = [nested]
        with diagnostic_context(deep=nested, large='x' * 1000000):
            observe(self.logger, 'bounded', path=[1, float('nan'), 3])
        runtime.close()
        line = (self.directory / 'events.jsonl').read_text().splitlines()[0]
        record = json.loads(line)
        self.assertLess(len(line), 20000)
        self.assertGreater(record['omitted_fields'], 0)
        self.assertEqual(record['fields']['path'], [1, None, 3])

    def test_large_configuration_preserves_correlation_and_source_envelope(self):
        runtime = self.start()
        with diagnostic_context(cycle_id='cycle-1', action_id='action-1', actor={'user_id': '42'}):
            observe(self.logger, 'cycle.started', configuration={
                str(index): list(range(64)) for index in range(64)})
        runtime.close()
        record = json.loads((self.directory / 'events.jsonl').read_text().splitlines()[0])
        self.assertEqual(record['context']['cycle_id'], 'cycle-1')
        self.assertEqual(record['context']['actor']['user_id'], '42')
        self.assertEqual(record['logger'], self.logger.name)
        self.assertEqual(record['source'], self.logger.name)
        self.assertEqual(record['message'], 'cycle.started')
        self.assertNotIn('traceback', record)
        self.assertGreater(record['omitted_fields'], 0)

    def test_enum_fields_and_known_path_message_arguments_are_preserved(self):
        class Failure(Enum):
            REJECTED = 'rejected'
        runtime = self.start()
        observe(self.logger, 'cycle.failed', code=Failure.REJECTED)
        runtime._handler.emit(logging.LogRecord('legacy', logging.INFO, '', 0,
            'Outcome %s; artifact %s', (Failure.REJECTED, Path('/tmp/capture.png')), None))
        runtime.close()
        records = [json.loads(line) for line in (self.directory / 'events.jsonl').read_text().splitlines()]
        self.assertEqual(records[0]['fields']['code'], 'rejected')
        self.assertEqual(records[1]['message'], 'Outcome rejected; artifact /tmp/capture.png')
        self.assertTrue(all(record['omitted_fields'] == 0 for record in records))

    def test_rotation_is_bounded_and_export_is_consistent(self):
        runtime = self.start(max_bytes=500, backups=2)
        for index in range(25):
            observe(self.logger, 'cycle.ended', metrics={'cycles': 1}, index=index)
        runtime.close()
        self.assertLessEqual(len(list(self.directory.glob('events.jsonl*'))), 3)
        archive_path = export_support_bundle(self.directory, Path(self.temp.name) / 'support.zip')
        with ZipFile(archive_path) as archive:
            summary = json.loads(archive.read('summary.json'))
            self.assertEqual(summary['metrics']['cycles']['total'], 25)
            self.assertIn('statistics.sqlite3', archive.namelist())
            self.assertTrue(json.loads(archive.read('manifest.json'))['log_files'])
        with self.assertRaises(FileExistsError):
            export_support_bundle(self.directory, archive_path)

    def test_corrupt_database_is_visible_without_breaking_logging(self):
        self.directory.mkdir()
        (self.directory / 'statistics.sqlite3').write_bytes(b'not sqlite')
        runtime = DiagnosticsRuntime(self.directory)
        self.addCleanup(runtime.close)
        self.assertFalse(runtime.start())
        self.assertIsNotNone(runtime.status['last_error'])
        observe(self.logger, 'hardware.command.finished')

    def test_disk_failure_is_visible_and_does_not_escape_to_producer(self):
        runtime = self.start()
        with patch('src.engine.diagnostics.runtime.RotatingFileHandler.shouldRollover', side_effect=OSError('disk full')):
            observe(self.logger, 'hardware.command.finished')
            self.wait_error(runtime)
        self.assertIn('disk full', runtime.status['last_error'])

    def test_second_writer_cannot_modify_live_sessions(self):
        first = self.start()
        second = DiagnosticsRuntime(self.directory)
        self.addCleanup(second.close)
        self.assertFalse(second.start())
        self.assertIsNotNone(second.status['last_error'])
        first.close()
        self.assertEqual(read_summary(self.directory)['metrics']['diagnostics.sessions']['total'], 1)

    def test_queue_overload_is_counted(self):
        # Freeze file I/O while the first record is being handled; producers
        # must remain nonblocking and the bounded queue must report the loss.
        import threading
        entered, release = threading.Event(), threading.Event()
        from logging.handlers import RotatingFileHandler
        original = RotatingFileHandler.shouldRollover
        def blocked(handler, record):
            entered.set()
            release.wait(2)
            return original(handler, record)
        runtime = self.start(queue_size=1)
        with patch('src.engine.diagnostics.runtime.RotatingFileHandler.shouldRollover', blocked):
            observe(self.logger, 'first')
            self.assertTrue(entered.wait(1))
            observe(self.logger, 'queued')
            with (patch('src.engine.diagnostics.runtime.prepare') as snapshot,
                  patch('src.engine.diagnostics.runtime.exception_snapshot') as traceback):
                for _ in range(10):
                    observe(self.logger, 'overloaded', level=logging.ERROR)
                snapshot.assert_not_called()
                traceback.assert_not_called()
            self.assertGreater(runtime.status['dropped_events'], 0)
            release.set()
            runtime.close()
        metrics = read_summary(self.directory)['metrics']
        self.assertEqual(metrics['diagnostics.dropped_events']['total'], runtime.status['dropped_events'])

class DeviceObservationTests(unittest.TestCase):
    def test_stalled_console_does_not_block_pump_commands_or_writer_shutdown(self):
        from unittest.mock import MagicMock
        from src.engine.hardware.vacuum_pump.vacuum_pump_controller import VacuumPumpController
        entered, release, completed = threading.Event(), threading.Event(), threading.Event()
        class StalledHandler(logging.Handler):
            def emit(self, record):
                entered.set()
                release.wait(3)
        logger = logging.getLogger('diagnostics.events')
        handler = StalledHandler()
        logger.addHandler(handler)
        results = []
        with tempfile.TemporaryDirectory() as temp:
            runtime = DiagnosticsRuntime(temp)
            self.assertTrue(runtime.start())
            controller = VacuumPumpController(MagicMock())
            def command():
                try:
                    results.extend([controller.turn_on(), controller.turn_off()])
                finally:
                    completed.set()
            worker = threading.Thread(target=command, daemon=True)
            try:
                worker.start()
                self.assertTrue(completed.wait(0.5), 'command waited for the console')
                self.assertTrue(entered.wait(1))
                started = time.monotonic()
                runtime.close()
                self.assertLess(time.monotonic() - started, 1)
                self.assertEqual(results, [True, True])
                self.assertEqual(read_summary(temp)['metrics']['vacuum_pump.commands.off']['total'], 1)
            finally:
                release.set()
                worker.join(1)
                logger.removeHandler(handler)
                runtime.close()

    def test_recorder_adapter_failure_preserves_original_device_results(self):
        from unittest.mock import MagicMock
        from src.engine.hardware.vacuum_pump.vacuum_pump_controller import VacuumPumpController
        from src.engine.hardware.fan.modbus.modbus_fan_control import ModbusFanControl
        with tempfile.TemporaryDirectory() as temp:
            runtime = DiagnosticsRuntime(temp)
            self.assertTrue(runtime.start())
            try:
                with patch.object(runtime, 'record_observation', side_effect=RuntimeError('recorder broken')):
                    self.assertTrue(VacuumPumpController(MagicMock()).turn_on())
                    transport = MagicMock()
                    original = OSError('original device failure')
                    transport.write_register.side_effect = original
                    with self.assertRaises(OSError) as caught:
                        ModbusFanControl(transport).turn_on()
                    self.assertIs(caught.exception, original)
                    transport.write_register.assert_called_once()
            finally:
                runtime.close()

    def test_successful_off_is_counted_even_when_blowoff_fails(self):
        from unittest.mock import MagicMock
        from src.engine.hardware.vacuum_pump.vacuum_pump_controller import VacuumPumpController
        from src.engine.hardware.vacuum_pump.models.vacuum_pump_config import VacuumPumpConfig
        with tempfile.TemporaryDirectory() as temp:
            runtime = DiagnosticsRuntime(temp)
            self.assertTrue(runtime.start())
            try:
                transport = MagicMock()
                controller = VacuumPumpController(transport, VacuumPumpConfig(
                    pump_register='Y0', blow_off_register='Y2', blow_off_pulse_seconds=0))
                self.assertTrue(controller.turn_on())
                transport.write_register.side_effect = [None, RuntimeError('blowoff failed')]
                self.assertFalse(controller.turn_off())
            finally:
                runtime.close()
            metrics = read_summary(temp)['metrics']
            self.assertEqual(metrics['vacuum_pump.commands.off']['total'], 1)
            self.assertEqual(metrics['vacuum_pump.commanded_on_intervals']['total'], 1)
            self.assertNotIn('vacuum_pump.unknown_state_events', metrics)

    def test_fans_keep_distinct_usage_and_preserve_failed_command_exception(self):
        from unittest.mock import MagicMock
        from src.engine.hardware.fan.modbus.modbus_fan_control import ModbusFanControl
        with tempfile.TemporaryDirectory() as temp:
            runtime = DiagnosticsRuntime(temp)
            self.assertTrue(runtime.start())
            try:
                fan = ModbusFanControl(MagicMock(), diagnostic_name='fan')
                failed_transport = MagicMock()
                failed_transport.write_register.side_effect = OSError('disconnected')
                tray_fan = ModbusFanControl(failed_transport, diagnostic_name='tray_fan')
                fan.turn_on()
                fan.turn_off()
                with self.assertRaisesRegex(OSError, 'disconnected'):
                    tray_fan.turn_on()
            finally:
                runtime.close()
            metrics = read_summary(temp)['metrics']
            self.assertEqual(metrics['fan.commanded_on_intervals']['total'], 1)
            self.assertEqual(metrics['tray_fan.command_failures']['total'], 1)
            self.assertNotIn('tray_fan.commanded_on_intervals', metrics)

class OutputTransitionTests(unittest.TestCase):
    def test_known_off_to_on_is_distinct_from_unknown_start(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = DiagnosticsRuntime(temp, checkpoint_seconds=60)
            self.assertTrue(runtime.start())
            try:
                logger = logging.getLogger('test.output')
                observe(logger, 'write', output=('pump', True))
                observe(logger, 'write', output=('pump', False))
                observe(logger, 'write', output=('pump', True))
                observe(logger, 'write', output=('pump', True))
                observe(logger, 'write', output=('pump', False))
            finally:
                runtime.close()
            metrics = read_summary(temp)['metrics']
            self.assertEqual(metrics['pump.commanded_on_intervals']['total'], 2)
            self.assertEqual(metrics['pump.off_to_on_transitions']['total'], 1)
