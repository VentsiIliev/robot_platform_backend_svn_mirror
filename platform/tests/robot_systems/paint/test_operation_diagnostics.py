"""Operator-to-worker-to-export acceptance, with no real hardware transports."""
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

import numpy as np

from src.applications.diagnostics.service.diagnostics_application_service import DiagnosticsApplicationService
from src.engine.auth.user_session import UserSession
from src.engine.diagnostics.actions import ActionRecorder
from src.engine.diagnostics.events import current_context, diagnostic_context
from src.engine.diagnostics.runtime import DiagnosticsRuntime
from src.engine.process.process_requirements import ProcessRequirements
from src.engine.common_service_ids import CommonServiceID
from src.engine.vision.i_capture_snapshot_service import VisionCaptureSnapshot
from src.robot_systems.paint.applications.dashboard.controller.paint_dashboard_controller import PaintDashboardController
from src.robot_systems.paint.applications.dashboard.model.paint_dashboard_model import PaintDashboardModel
from src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service import PaintDashboardService
from src.robot_systems.paint.processes.paint.configuration.models import PaintProcessConfig, PaintMagazineLoadConfig, scale_paint_process_accelerations
from src.robot_systems.paint.processes.paint.match.results import PreparedWorkpiece
from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
from src.robot_systems.paint.processes.paint.production.service import PaintProductionService
from src.robot_systems.paint.processes.paint.results import PaintOperationResult, PaintOutcome, Ready
from src.robot_systems.paint.processes.paint.tray_dry.errors import TrayUnavailableError


class OperationDiagnosticsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        self.runtime = DiagnosticsRuntime(self.directory)
        self.assertTrue(self.runtime.start())
        self.addCleanup(self.runtime.close)
        self.session = UserSession()
        self.session.login(SimpleNamespace(user_id='42', role='Engineer'))
        self.actions = ActionRecorder(self.session, authentication_mode='authenticated')
        self.actions.session_changed(True)

    def setup_pipeline(self, success=True):
        config = PaintProcessConfig(run_while_workpiece_found=False, enable_workpiece_matching=False,
                                    magazine_load=PaintMagazineLoadConfig(enabled=False),
                                    paint_process_acceleration_scale_percent=20)
        settings = MagicMock()
        settings.get_snapshot.return_value = config
        executor = MagicMock()
        executor.supports_paint_motion_states = False
        executor._robot_service.unwind_joint6.return_value = True
        executor._robot_service.get_execution_status.return_value = {'is_executing': False}
        executor.execute_paint_process.return_value = (success, 'painted' if success else 'simulated motion rejection')
        preparation, planning, camera = MagicMock(), MagicMock(), MagicMock()
        raw = {'workpieceId': 'part-17', 'name': 'Bracket', 'velocity': 25.0, 'acceleration': 30.0,
               'offset': 2.0, 'contour': [[[0, 0]], [[10, 0]], [[10, 10]]], 'settings': {'colour': 'blue'}}
        preparation.prepare_result.return_value = Ready(PreparedWorkpiece(raw, 'Bracket part-17'))
        planning.build_execution_plan.return_value = SimpleNamespace(workpiece=raw, execution_jobs=[
            {'vel': 25.0, 'acc': 6.0, 'workpiece_height_mm': 2.0, 'path': [[0.0] * 6]}], total_spline_pts=3)
        camera.capture_snapshot.return_value = VisionCaptureSnapshot(
            frame=np.zeros((4, 4, 3), dtype=np.uint8),
            contours=[np.array([[[0, 0]], [[10, 0]], [[10, 10]]], dtype=np.float32)], source='paint_process')
        production = PaintProductionService(workpiece_preparation_service=preparation,
            capture_snapshot_service=camera, path_preparation_service=planning,
            path_executor=executor, paint_process_config_service=settings)
        production._move_to_calibration_before_manual_cycle = MagicMock(return_value=PaintOperationResult(PaintOutcome.COMPLETED, ""))
        process = PaintProcess(production, MagicMock(), paint_process_config_service=settings)
        def stop_workers():
            for worker in (process._thread, process._stop_thread):
                if worker:
                    worker.join(3)
        self.addCleanup(stop_workers)
        dashboard = PaintDashboardService(process, paint_process_config_service=settings,
                                           diagnostic_actions=self.actions)
        controller = PaintDashboardController.__new__(PaintDashboardController)
        controller._model = PaintDashboardModel(dashboard)
        controller._view = MagicMock()
        controller._production_start_pending = False
        return config, settings, production, process, dashboard, controller, camera

    def events(self):
        self.runtime.close()
        return [json.loads(line) for line in (self.directory / 'events.jsonl').read_text().splitlines()]

    def test_success_and_failure_export_explain_one_cycle_with_original_actor_and_settings(self):
        # One failure fixture proves the full real state-machine path; the success
        # fixture verifies terminal outcomes are recorded without requiring an issue.
        for success in (True, False):
            with self.subTest(success=success):
                if not success:
                    self.runtime = DiagnosticsRuntime(self.directory)
                    self.assertTrue(self.runtime.start())
                    self.addCleanup(self.runtime.close)
                config, settings, production, process, dashboard, controller, camera = self.setup_pipeline(success)
                if self.session.current_user is None:
                    self.session.login(SimpleNamespace(user_id='42', role='Engineer'))
                entered, release = threading.Event(), threading.Event()
                snapshot = camera.capture_snapshot.return_value
                def capture(**kwargs):
                    entered.set()
                    if not release.wait(3):
                        raise TimeoutError('test capture not released')
                    return snapshot
                camera.capture_snapshot.side_effect = capture
                self.addCleanup(release.set)
                controller._on_start()
                token = controller._start_action_context
                self.assertTrue(entered.wait(2))
                self.session.logout()  # Worker must retain the initiating actor.
                release.set()
                process._thread.join(3)
                if process._stop_thread:
                    process._stop_thread.join(3)
                self.assertFalse(process._thread.is_alive())
                self.assertEqual(process.last_result.outcome, PaintOutcome.COMPLETED if success else PaintOutcome.FAILED)
                self.runtime.close()
                destination = self.directory / f'incident-{success}.zip'
                result = DiagnosticsApplicationService().export_incident({
                    'directory': str(self.directory), 'selected_operation_id': token['operation_id'],
                    'level': 'ERROR', 'search': 'a filter that must be cleared for full operation export'}, str(destination))
                self.assertFalse(result['scan_limited'])
                with ZipFile(destination) as archive:
                    manifest = json.loads(archive.read('manifest.json'))
                    events = [json.loads(line) for line in archive.read('events.jsonl').splitlines()]
                    self.assertEqual(manifest['expected_evidence_not_captured'], [])
                    payloads = {item['name']: json.loads(archive.read(f"evidence/{item['snapshot_id']}.json"))
                                for item in manifest['evidence'] if item['status'] == 'complete'}
                    self.assertEqual(payloads['paint.raw_process_settings'], asdict(config))
                    self.assertEqual(payloads['paint.effective_process_settings'], asdict(scale_paint_process_accelerations(config)))
                    self.assertEqual(payloads['paint.workpiece']['workpieceId'], 'part-17')
                    self.assertEqual(payloads['paint.execution_plan']['job_metadata'][0]['acc'], 6.0)
                    self.assertTrue(all(event['context']['actor']['user_id'] == '42' for event in events))
                    cycle = next(event for event in events if event.get('event') == 'paint.cycle.started')
                    final = next(event for event in events if event.get('event') == 'paint.cycle.ended')
                    self.assertEqual(cycle['context']['cycle_id'], final['context']['cycle_id'])
                    self.assertEqual(cycle['context']['operation_id'], token['operation_id'])
                    self.assertTrue(any(event.get('event') == 'paint.stage.ended' for event in events))
                    self.assertTrue(any(event.get('event') == 'paint.run.ended' for event in events))
                    self.assertEqual(sum(event.get('event') == 'paint.start.requested' for event in events), 1)
                    self.assertEqual(final['fields']['outcome'], 'completed' if success else 'failed')
                    self.assertEqual(current_context(), {})

    def test_dashboard_configuration_failure_is_identified_before_process_or_capture(self):
        _, settings, _, process, dashboard, controller, camera = self.setup_pipeline()
        original = ValueError('corrupt process settings')
        settings.get_snapshot.side_effect = original
        with self.assertRaises(ValueError) as caught:
            controller._on_start()
        self.assertIs(caught.exception, original)
        camera.capture_snapshot.assert_not_called()
        self.assertIsNone(process._thread)
        events = [event for event in self.events() if (event.get('event') or '').startswith('paint.start.')]
        self.assertEqual(len(events), 2)
        self.assertEqual(events[-1]['fields']['outcome'], 'failed')
        self.assertEqual(events[0]['context']['operation_id'], events[-1]['context']['operation_id'])
        self.assertIn('corrupt process settings', events[-1]['traceback'])

    def test_cycle_preparation_failure_has_identity_and_does_not_reuse_previous_part(self):
        config, settings, production, process, dashboard, controller, camera = self.setup_pipeline()
        production._last_execution_context = SimpleNamespace(diagnostic_cycle_id='old-cycle',
            diagnostic_context={'operation_id': 'old-operation'}, raw_workpiece={'workpieceId': 'old-part'})
        settings.get_snapshot.side_effect = ValueError('unreadable cycle settings')
        token = self.actions.operation_context()
        with diagnostic_context(**token):
            result = production.run_cycle_result(lambda: False, process_config=config, magazine_config=None, cycle_index=1)
            record = production.prepare_failure_record(message=result.message, failure=result.failure)
        self.assertEqual(record['context']['operation_id'], token['operation_id'])
        self.assertIsNone(record['workpiece'])
        self.assertTrue(record['cycle_id'])
        events = self.events()
        terminal = next(event for event in events if event.get('event') == 'paint.cycle.request_result')
        self.assertEqual(record['cycle_id'], terminal['context']['cycle_id'])
        self.assertTrue(terminal['context']['cycle_id'])
        self.assertEqual(terminal['fields']['evidence']['workpiece'], 'not_captured')

    def test_tray_rejection_keeps_original_exception_and_does_not_start_worker(self):
        _, _, production, process, dashboard, _, _ = self.setup_pipeline()
        original = TrayUnavailableError()
        production.ensure_tray_ready_for_start = MagicMock(side_effect=original)
        with self.assertRaises(TrayUnavailableError) as caught:
            dashboard.start()
        self.assertIs(caught.exception, original)
        self.assertIsNone(process._thread)
        final = [event for event in self.events() if event.get('event') == 'paint.start.result'][-1]
        self.assertEqual(final['fields']['outcome'], 'rejected')
        self.assertEqual(final['context']['actor']['user_id'], '42')

    def test_missing_service_is_rejected_without_claiming_acceptance(self):
        _, _, _, process, dashboard, _, camera = self.setup_pipeline()
        process._requirements = ProcessRequirements.requires(CommonServiceID.ROBOT)
        process._service_checker = lambda service_id: False
        dashboard.start()
        self.assertIsNone(process._thread)
        camera.capture_snapshot.assert_not_called()
        final = [event for event in self.events() if event.get('event') == 'paint.start.result'][-1]
        self.assertEqual(final['fields']['outcome'], 'rejected')
        self.assertIsNone(final['fields']['run_id'])

    def test_preparation_worker_exception_has_original_traceback_and_failure_signal(self):
        from src.robot_systems.paint.applications.dashboard.controller.paint_dashboard_controller import _Worker
        _, _, _, _, dashboard, _, camera = self.setup_pipeline()
        original = OSError('destination prepare failed')
        dashboard._production_start_guard = MagicMock()
        dashboard._production_start_guard.prepare.side_effect = original
        token = dashboard.begin_start_request()
        worker = _Worker(lambda: dashboard.prepare_production_start('auto', token))
        errors, successes = [], []
        worker.failed.connect(errors.append)
        worker.finished.connect(successes.append)
        worker.run()
        self.assertEqual(errors, ['destination prepare failed'])
        self.assertEqual(successes, [])
        camera.capture_snapshot.assert_not_called()
        final = [event for event in self.events() if event.get('event') == 'paint.start.result'][-1]
        self.assertEqual(final['context']['operation_id'], token['operation_id'])
        self.assertIn('OSError: destination prepare failed', final['traceback'])

    def test_absent_recorder_preserves_successful_machine_path_without_snapshot_work(self):
        self.runtime.close()
        before = (self.directory / 'events.jsonl').read_bytes()
        _, _, _, process, _, controller, _ = self.setup_pipeline()
        with patch('src.robot_systems.paint.diagnostics.cycle_evidence.publish_snapshot') as snapshot:
            controller._on_start()
            process._thread.join(3)
            if process._stop_thread:
                process._stop_thread.join(3)
        self.assertEqual(process.last_result.outcome, PaintOutcome.COMPLETED)
        snapshot.assert_not_called()
        self.assertEqual((self.directory / 'events.jsonl').read_bytes(), before)

    def test_evidence_adapter_failure_cannot_change_successful_machine_result(self):
        _, _, _, process, dashboard, controller, _ = self.setup_pipeline()
        with patch('src.robot_systems.paint.processes.paint.production.cycle_runner.publish_cycle_settings',
                   side_effect=RuntimeError('evidence adapter failed')):
            controller._on_start()
            process._thread.join(3)
            if process._stop_thread:
                process._stop_thread.join(3)
        self.assertEqual(process.last_result.outcome, PaintOutcome.COMPLETED)
        events = self.events()
        final = next(event for event in events if event.get('event') == 'paint.cycle.ended')
        self.assertNotIn('raw_process_settings', final['fields']['evidence'])
