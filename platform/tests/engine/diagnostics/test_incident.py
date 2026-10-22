import copy
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from src.engine.diagnostics.evidence import publish_snapshot
from src.engine.diagnostics.incident import export_incident, reconstruct_evidence


class IncidentEvidenceTests(unittest.TestCase):
    def publish(self, payload, name='welding.settings', **options):
        events = []
        def observe(_logger, event, **fields):
            events.append({'timestamp': '2026-10-21T08:00:00+00:00', 'level': 'INFO',
                           'event': event, 'fields': fields, 'context': {'operation_id': 'op-1'}})
        with (patch('src.engine.diagnostics.evidence.observe', side_effect=observe),
              patch('src.engine.diagnostics.evidence.is_recording', return_value=True)):
            reference = publish_snapshot(name, payload, **options)
        return reference, events

    def test_snapshot_is_detached_generic_and_reassembled_without_loss(self):
        payload = {str(i): {'speed': i, 'description': 'setting'} for i in range(100)}
        expected = copy.deepcopy(payload)
        reference, events = self.publish(payload)
        self.assertEqual(reference['availability'], 'submitted')
        payload['0']['speed'] = 999
        rebuilt = reconstruct_evidence(events)
        self.assertEqual(rebuilt[0]['status'], 'complete')
        self.assertEqual(rebuilt[0]['payload'], expected)
        self.assertEqual(rebuilt[0]['name'], 'welding.settings')
        self.assertTrue(all(len(event['fields'].get('data', '')) <= 2048 for event in events))

    def test_opted_in_dataclasses_use_bounded_copy_without_deepcopy_hooks(self):
        @dataclass
        class Settings:
            speed: float
            points: list
        source = Settings(12.5, [[1, 2], [3, 4]])
        expected = asdict(source)
        _, events = self.publish(source, expand_dataclasses=True)
        source.points[0][0] = 999
        self.assertEqual(reconstruct_evidence(events)[0]['payload'], expected)
        class Unsafe:
            def __deepcopy__(self, memo):
                raise AssertionError('unbounded deepcopy must never run')
        _, events = self.publish(Settings(12.5, [Unsafe()] * 100000), expand_dataclasses=True)
        result = reconstruct_evidence(events)[0]
        self.assertEqual(result['status'], 'partial')
        self.assertLessEqual(len(result['payload']['points']), 128)
        # Dataclass expansion is opt-in, never implicit for compatibility logs.
        _, events = self.publish(source)
        self.assertEqual(reconstruct_evidence(events)[0]['status'], 'unavailable')

    def test_missing_or_conflicting_parts_never_report_complete(self):
        _, events = self.publish({'description': 'x' * 3000})
        self.assertEqual(reconstruct_evidence(events[:-1])[0]['status'], 'incomplete')
        repeated = copy.deepcopy(events[-1])
        repeated['fields']['data'] = 'conflicting'
        result = reconstruct_evidence(events + [repeated])[0]
        self.assertEqual(result['status'], 'incomplete')
        self.assertIn('conflicting', result['reason'])
        self.assertEqual(reconstruct_evidence(events + events)[0]['status'], 'complete')
        corrupt = copy.deepcopy(events)
        corrupt[-1]['fields']['data'] = '!' + corrupt[-1]['fields']['data'][1:]
        self.assertEqual(reconstruct_evidence(corrupt)[0]['reason'], 'invalid_payload_or_digest')

    def test_partial_optional_data_is_explicit_and_never_formats_unknown_objects(self):
        class Unsafe:
            def __str__(self):
                raise AssertionError('format hook must not run')
        _, events = self.publish({'value': 42, 'nan': float('nan'), 'object': Unsafe()})
        result = reconstruct_evidence(events)[0]
        self.assertEqual(result['status'], 'partial')
        self.assertGreaterEqual(result['snapshot_omitted_fields'], 2)
        self.assertEqual(result['payload'], {'value': 42})

    def test_missing_source_and_size_limit_are_explicit_without_producer_failure(self):
        reference, events = self.publish(None)
        self.assertEqual(reference['availability'], 'unavailable')
        self.assertEqual(reconstruct_evidence(events)[0]['status'], 'unavailable')
        reference, events = self.publish({str(i): '\x00' * 4096 for i in range(20)})
        self.assertEqual(reference['availability'], 'unavailable')
        self.assertEqual(reconstruct_evidence(events)[0]['status'], 'unavailable')

    def test_future_snapshot_schema_is_not_assumed_compatible(self):
        _, events = self.publish({'speed': 42})
        events[0]['fields']['schema_version'] = 2
        self.assertEqual(reconstruct_evidence(events)[0]['reason'], 'unsupported_snapshot_schema')

    def test_archive_is_reviewable_exclusive_and_discloses_missing_capture(self):
        _, events = self.publish({'speed': 42})
        events.insert(0, {'timestamp': '2026-10-21T07:59:59+00:00', 'level': 'INFO',
            'event': 'operation.requested', 'fields': {'expected_evidence': ['welding.settings', 'welding.part']}})
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'incident.zip'
            export_incident({'events': events, 'matched': len(events), 'warnings': [], 'limited': False},
                            destination, filters={'operation_id': 'op-1'})
            before = destination.read_bytes()
            with ZipFile(destination) as archive:
                manifest = json.loads(archive.read('manifest.json'))
                self.assertEqual(manifest['expected_evidence_not_captured'], ['welding.part'])
                self.assertEqual(manifest['evidence'][0]['status'], 'complete')
                self.assertIn('events.jsonl', archive.namelist())
                self.assertIn('timeline.txt', archive.namelist())
                evidence = next(name for name in archive.namelist() if name.startswith('evidence/'))
                self.assertEqual(json.loads(archive.read(evidence)), {'speed': 42})
            with self.assertRaises(FileExistsError):
                export_incident({'events': events}, destination, filters={})
            self.assertEqual(destination.read_bytes(), before)
            self.assertEqual(list(Path(directory).iterdir()), [destination])

    def test_export_does_not_claim_complete_range_after_budget_or_selection_limits(self):
        with tempfile.TemporaryDirectory() as directory:
            path = export_incident({'events': [], 'matched': 1000, 'limited': True,
                'warnings': ['scan budget reached']}, Path(directory) / 'limited.zip', filters={})
            with ZipFile(path) as archive:
                manifest = json.loads(archive.read('manifest.json'))
            self.assertTrue(manifest['scan_limited'])
            self.assertTrue(manifest['warnings'])
            self.assertEqual(manifest['recorder_commit_acknowledgement'], 'not_available')

    def test_failed_export_cleans_staging_without_publishing_partial_archive(self):
        _, events = self.publish({'speed': 42})
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / 'incident.zip'
            with patch('src.engine.diagnostics.incident.ZipFile.writestr', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    export_incident({'events': events}, destination, filters={})
            self.assertEqual(list(Path(directory).iterdir()), [])
