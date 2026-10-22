import json
import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.engine.diagnostics.config import DiagnosticsConfig
from src.engine.diagnostics.events import is_recording, observe
from src.engine.diagnostics.evidence import publish_snapshot
from src.engine.diagnostics.service import build_diagnostics_service, NullDiagnosticsService
from src.bootstrap.build_engine import EngineContext


class DiagnosticsServiceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name) / 'history'

    def test_disabled_or_omitted_service_creates_no_storage_or_workers(self):
        for config in (None, DiagnosticsConfig(enabled=False)):
            with self.subTest(config=config), patch('src.engine.diagnostics.runtime.DiagnosticsRuntime') as runtime:
                service = build_diagnostics_service(config, directory=self.directory)
                self.assertIsInstance(service, NullDiagnosticsService)
                self.assertFalse(service.start())
                self.assertEqual(service.status['state'], 'disabled')
                observe(logging.getLogger(__name__), 'component.completed', result=True)
                with patch('src.engine.diagnostics.evidence.PrimitiveSnapshot') as copy:
                    reference = publish_snapshot('component.settings', object())
                copy.assert_not_called()
                self.assertEqual(reference['reason'], 'recorder_inactive')
                service.close()
                runtime.assert_not_called()
                self.assertFalse(self.directory.exists())

    def test_enabled_service_captures_once_and_stops_without_restarting(self):
        service = build_diagnostics_service(DiagnosticsConfig(capture_logs=False), directory=self.directory)
        self.addCleanup(service.close)
        ctx = EngineContext.build(diagnostics_service=service)
        self.assertIs(ctx.diagnostics_service, service)
        handlers = tuple(logging.getLogger().handlers)
        self.assertTrue(service.start())
        self.assertTrue(service.start())
        self.assertTrue(is_recording())
        self.assertEqual(service.status['state'], 'recording')
        self.assertEqual(tuple(logging.getLogger().handlers), handlers)
        observe(logging.getLogger(__name__), 'component.completed', result=True)
        self.assertIsNone(service._runtime._console._thread.ident)
        service.close()
        service.close()
        self.assertFalse(service.start())
        self.assertFalse(is_recording())
        self.assertEqual(service.status['state'], 'stopped')
        records = [json.loads(line) for line in (self.directory / 'events.jsonl').read_text().splitlines()]
        self.assertEqual([record['event'] for record in records],
                         ['diagnostics.capture.started', 'component.completed'])
        before = (self.directory / 'events.jsonl').read_bytes()
        observe(logging.getLogger(__name__), 'after.close')
        self.assertEqual((self.directory / 'events.jsonl').read_bytes(), before)

    def test_compatibility_capture_can_be_disabled_without_losing_structured_events(self):
        logger = logging.getLogger('test.optional_diagnostics')
        previous = logger.level
        logger.setLevel(logging.INFO)
        self.addCleanup(logger.setLevel, previous)
        for capture in (False, True):
            directory = self.directory / str(capture)
            service = build_diagnostics_service(DiagnosticsConfig(capture_logs=capture), directory=directory)
            self.addCleanup(service.close)
            self.assertTrue(service.start())
            logger.info('ordinary compatibility message')
            observe(logger, 'typed.observation')
            service.close()
            rows = [json.loads(line) for line in (directory / 'events.jsonl').read_text().splitlines()]
            self.assertEqual(sum(row['event'] is None for row in rows), int(capture))
            self.assertEqual(sum(row['event'] == 'typed.observation' for row in rows), 1)

    def test_unavailable_storage_is_not_a_machine_startup_failure(self):
        self.directory.write_text('not a directory')
        service = build_diagnostics_service(DiagnosticsConfig(), directory=self.directory)
        self.addCleanup(service.close)
        with patch('sys.stderr'):
            self.assertFalse(service.start())
        self.assertEqual(service.status['state'], 'unavailable')
        self.assertTrue(service.status['last_error'])
        self.assertFalse(is_recording())
        self.assertFalse(service.start())

    def test_optional_start_and_cleanup_exceptions_do_not_escape(self):
        service = build_diagnostics_service(DiagnosticsConfig(), directory=self.directory)
        with patch('src.engine.diagnostics.runtime.DiagnosticsRuntime') as runtime:
            runtime.return_value.start.side_effect = OSError('startup failed')
            runtime.return_value.close.side_effect = OSError('cleanup failed')
            self.assertFalse(service.start())
            self.assertEqual(service.status['last_error'], 'startup failed')
            service.close()

    def test_paint_evidence_does_not_inspect_or_copy_when_recorder_absent(self):
        from src.robot_systems.paint.diagnostics.cycle_evidence import (
            publish_cycle_settings, publish_workpiece, publish_execution_plan)
        class Untouchable:
            def __getattribute__(self, name):
                raise AssertionError('disabled evidence touched domain state')
        self.assertEqual(publish_cycle_settings(Untouchable()), {})
        publish_workpiece(Untouchable())
        publish_execution_plan(Untouchable())


class DiagnosticsConfigTests(unittest.TestCase):
    def test_default_preserves_history_and_skips_extra_console_work(self):
        self.assertEqual(DiagnosticsConfig.from_mapping(environ={}), DiagnosticsConfig())
        self.assertTrue(DiagnosticsConfig().enabled)
        self.assertFalse(DiagnosticsConfig().console_events)

    def test_environment_override_and_explicit_policies(self):
        config = DiagnosticsConfig.from_mapping(
            {'enabled': True, 'capture_logs': False, 'console_events': True},
            environ={'ROBOT_PLATFORM_DIAGNOSTICS_ENABLED': '0'})
        self.assertEqual(config, DiagnosticsConfig(enabled=False, capture_logs=False, console_events=True))
        self.assertTrue(DiagnosticsConfig.from_mapping({'enabled': False},
            environ={'ROBOT_PLATFORM_DIAGNOSTICS_ENABLED': '1'}).enabled)

    def test_invalid_flags_are_not_silently_treated_as_truthy(self):
        for field in ('enabled', 'capture_logs', 'console_events'):
            for invalid in ('false', 0, None, []):
                with self.subTest(field=field, invalid=invalid), self.assertRaisesRegex(RuntimeError, field):
                    DiagnosticsConfig.from_mapping({field: invalid}, environ={})
        with self.assertRaisesRegex(RuntimeError, 'JSON object'):
            DiagnosticsConfig.from_mapping([], environ={})
        with self.assertRaisesRegex(RuntimeError, 'must be 0 or 1'):
            DiagnosticsConfig.from_mapping(environ={'ROBOT_PLATFORM_DIAGNOSTICS_ENABLED': 'false'})
