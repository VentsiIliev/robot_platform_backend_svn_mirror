import json
from hashlib import sha256
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import MagicMock
from zipfile import ZipFile

from PyQt6.QtWidgets import QApplication

from src.applications.diagnostics.controller.diagnostics_controller import DiagnosticsController
from src.applications.diagnostics.diagnostics_application_factory import DiagnosticsApplicationFactory
from src.applications.diagnostics.model.diagnostics_model import DiagnosticsModel
from src.applications.diagnostics.service.diagnostics_application_service import DiagnosticsApplicationService
from src.applications.diagnostics.service.stub_diagnostics_service import StubDiagnosticsService
from src.applications.diagnostics.view.diagnostics_view import DiagnosticsView
from src.engine.localization.dict_translator import DictTranslator


class DiagnosticsReaderTests(unittest.TestCase):
    def test_transport_parts_are_hidden_in_table_but_kept_for_operation_export(self):
        payload = '{"speed":42}'
        records = [self.event(event='evidence.snapshot', context={'operation_id': 'op-1'}, fields={
            'snapshot_id': 'snap-1', 'name': 'generic.settings', 'availability': 'submitted',
            'sha256': sha256(payload.encode()).hexdigest(), 'parts': 1}),
            self.event(event='evidence.snapshot.part', context={'operation_id': 'op-1'},
                       fields={'snapshot_id': 'snap-1', 'index': 0, 'data': payload})]
        self.write('events.jsonl', records)
        self.assertEqual(len(self.query()['events']), 1)
        destination = self.directory / 'export.zip'
        self.service.export_incident({'directory': str(self.directory), 'selected_operation_id': 'op-1'}, str(destination))
        with ZipFile(destination) as archive:
            self.assertEqual(len(archive.read('events.jsonl').splitlines()), 2)
            manifest = json.loads(archive.read('manifest.json'))
            self.assertEqual(manifest['evidence'][0]['status'], 'complete')

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.service = DiagnosticsApplicationService()

    def query(self, **filters):
        return self.service.query({'directory': str(self.directory), **filters})

    def write(self, name, records):
        (self.directory / name).write_text(''.join(json.dumps(record) + '\n' for record in records))

    @staticmethod
    def event(hour=10, level='INFO', **kwargs):
        return {'timestamp': f'2026-10-21T{hour:02}:00:00+00:00', 'level': level,
                'event': 'cycle.started', 'message': 'operation started', **kwargs}

    def test_merges_rotations_and_filters_severity_time_and_context(self):
        self.write('events.jsonl.1', [self.event(9), self.event(10, 'ERROR', context={'cycle_id': 'wanted'})])
        self.write('events.jsonl', [self.event(11, 'ERROR', context={'cycle_id': 'other'})])
        result = self.query(since='2026-10-21T10:00:00+00:00', until='2026-10-21T10:30:00+00:00',
                            level='ERROR', search='wanted')
        self.assertEqual(len(result['events']), 1)
        self.assertEqual(result['events'][0]['context']['cycle_id'], 'wanted')
        self.assertEqual(result['warnings'], [])

    def test_corrupt_nonfinite_bad_timestamp_and_partial_records_are_disclosed(self):
        valid = json.dumps(self.event()) + '\n'
        (self.directory / 'events.jsonl').write_text(
            'bad json\n{"timestamp": false}\n' + valid.replace('"INFO"', 'NaN') + valid + valid[:-1])
        result = self.query()
        self.assertEqual(len(result['events']), 1)
        self.assertTrue(any('Invalid record' in warning for warning in result['warnings']))
        self.assertTrue(any('Incomplete' in warning for warning in result['warnings']))

    def test_only_latest_bounded_events_returned_in_time_order(self):
        self.service.MAX_EVENTS = 2
        self.write('events.jsonl', [self.event(10), self.event(11), self.event(12)])
        result = self.query()
        self.assertEqual(result['matched'], 3)
        self.assertEqual([record['timestamp'][11:13] for record in result['events']], ['11', '12'])

    def test_scan_budget_and_missing_directory_are_explicit(self):
        self.write('events.jsonl', [self.event()] * 20)
        self.service.MAX_BYTES = 256
        result = self.query()
        self.assertLessEqual(result['bytes_read'], 256)
        self.assertTrue(result['limited'])
        missing = self.service.query({'directory': str(self.directory / 'missing')})
        self.assertEqual(missing['events'], [])
        self.assertTrue(missing['warnings'])

    def test_reads_legacy_failure_index_without_modifying_files(self):
        self.write('failure_register.jsonl', [{
            'recorded_at_utc': '2026-10-21T10:00:00+00:00', 'cycle_id': 'cycle-1',
            'failure_bundle': '/not/available/failure.json'}])
        path = self.directory / 'failure_register.jsonl'
        before = path.read_bytes()
        result = self.query(search='cycle-1')
        self.assertEqual(result['events'][0]['event'], 'operation.failed')
        self.assertEqual(path.read_bytes(), before)

    def test_custom_reversed_interval_is_rejected(self):
        with self.assertRaises(ValueError):
            self.query(since='2026-10-21T11:00:00+00:00', until='2026-10-21T10:00:00+00:00')


class DiagnosticsControllerTests(unittest.TestCase):
    def test_export_runs_through_worker_and_does_not_replace_timeline(self):
        model, view = MagicMock(), MagicMock()
        controller = DiagnosticsController(model, view)
        jobs = []
        controller._run_in_thread = lambda **job: jobs.append(job)
        controller.export_incident({'selected_operation_id': 'op-1'}, '/tmp/incident.zip')
        controller.export_incident({}, '/tmp/duplicate.zip')
        self.assertEqual(len(jobs), 1)
        jobs[0]['fn']()
        model.export_incident.assert_called_once_with({'selected_operation_id': 'op-1'}, '/tmp/incident.zip')
        result = {'path': '/tmp/incident.zip', 'event_count': 10}
        jobs[0]['on_done'](result)
        view.set_export_result.assert_called_once_with(result)
        view.set_result.assert_not_called()
        controller.stop()

    def test_filter_changes_during_read_are_coalesced_without_stale_display(self):
        model, view = MagicMock(), MagicMock()
        view.filters.side_effect = [{'search': 'old'}, {'search': 'new'}]
        controller = DiagnosticsController(model, view)
        jobs = []
        controller._run_in_thread = lambda **job: jobs.append(job)
        controller.refresh()
        controller.refresh()
        controller.refresh()
        self.assertEqual(len(jobs), 1)
        jobs[0]['on_done']({'events': ['old']})
        self.assertEqual(len(jobs), 2)
        view.set_result.assert_not_called()
        jobs[1]['fn']()
        model.query.assert_called_once_with({'search': 'new'})
        jobs[1]['on_done']({'events': ['new']})
        view.set_result.assert_called_once_with({'events': ['new']})
        controller.stop()

    def test_stop_ignores_late_results_and_model_is_read_only(self):
        view = MagicMock()
        controller = DiagnosticsController(MagicMock(), view)
        controller.stop()
        controller._on_done({'events': []})
        view.set_result.assert_not_called()
        with self.assertRaises(PermissionError):
            DiagnosticsModel(StubDiagnosticsService()).save({})


class DiagnosticsViewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def widget(self):
        widget = DiagnosticsApplicationFactory().build(StubDiagnosticsService())
        self.addCleanup(widget.deleteLater)
        self.addCleanup(widget.clean_up)
        deadline = time.monotonic() + 3
        while (widget._controller._busy or widget._controller.has_running_workers()) and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(.005)
        self.assertFalse(widget._controller.has_running_workers())
        return widget

    def test_factory_reads_off_thread_and_presents_raw_event_details(self):
        widget = self.widget()
        self.assertEqual(widget._table.rowCount(), 1)
        self.assertIn('active_stop_enabled', widget._details.toPlainText())
        self.assertIn('"persisted": false', widget._details.toPlainText())
        widget._range.setCurrentIndex(5)
        self.assertIsNotNone(widget.filters()['since'])
        self.assertIsNotNone(widget.filters()['until'])

    def test_initial_bulgarian_and_runtime_english_retranslation_preserve_data(self):
        catalog = Path('src/applications/diagnostics/localization/bg.json')
        translator = DictTranslator(json.loads(catalog.read_text()))
        self.app.installTranslator(translator)
        try:
            widget = self.widget()
            self.assertEqual(widget._title.text(), 'Диагностика на машината')
            self.assertEqual(widget._table.horizontalHeaderItem(0).text(), 'Време')
            raw = widget._details.toPlainText()
            self.app.removeTranslator(translator)
            self.app.processEvents()
            self.assertEqual(widget._title.text(), 'Machine diagnostics')
            self.assertEqual(widget._range.itemText(0), 'Last 15 minutes')
            self.assertEqual(widget._details.toPlainText(), raw)
        finally:
            self.app.removeTranslator(translator)

    def test_partial_scan_and_omission_metadata_are_visible(self):
        widget = DiagnosticsView()
        self.addCleanup(widget.deleteLater)
        self.addCleanup(widget.clean_up)
        result = StubDiagnosticsService().query({})
        result['limited'] = True
        result['warnings'] = ['Invalid record skipped: events.jsonl']
        result['events'][0]['omitted_fields'] = 3
        widget.set_result(result)
        self.assertIn('Scan incomplete', widget._status.text())
        self.assertIn('Invalid record', widget._warnings.text())
        self.assertIn('"omitted_fields": 3', widget._details.toPlainText())
