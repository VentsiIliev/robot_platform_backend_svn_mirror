import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.diagnostics.failure_register import (
    append_paint_failure_record, summarize_failure_workpiece,
)
from src.robot_systems.paint.processes.paint.configuration.models import PaintProcessConfig
from src.robot_systems.paint.processes.paint.paint_process import PaintProcess
from src.robot_systems.paint.processes.paint.production.cycle_runner import PaintCycleExecution
from src.robot_systems.paint.processes.paint.production.service import PaintProductionService
from src.robot_systems.paint.processes.paint.results import PaintFailureCode, PaintOperationResult, PaintOutcome
from src.shared_contracts.events.process_events import ProcessState


class TestPaintFailureRegister(unittest.TestCase):
    def setUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.production = PaintProductionService(
            workpiece_preparation_service=MagicMock(),
            capture_snapshot_service=MagicMock(),
            path_preparation_service=MagicMock(),
            path_executor=SimpleNamespace(set_cycle_dropoff_strategy=MagicMock()),
            failure_artifact_root=self.root / "paint_failures",
        )
        self.config = PaintProcessConfig(enable_dry_run_mode=True)

    def run_cycle(self, result, index=1):
        with patch(
            "src.robot_systems.paint.processes.paint.production.service.run_paint_cycle",
            return_value=PaintCycleExecution(result),
        ):
            return self.production.run_cycle_result(
                lambda: False, process_config=self.config, magazine_config=None, cycle_index=index,
            )

    def fail_run(self, *, collision=None):
        failure = PaintOperationResult.failed(PaintFailureCode.MOTION, "pickup", "Motor rejected\nНеуспешно")
        self.production.run_once_result = lambda *args: self.run_cycle(failure, index=4)
        process = PaintProcess(self.production, MagicMock())
        process._state = ProcessState.RUNNING
        process._diagnostic_run_id = "test-run"
        with patch.object(process, "_request_hardware_stop"), patch.object(
            process, "_collision_event_since", return_value=collision,
        ):
            process._run_in_background_impl()
        self.assertEqual(process.state, ProcessState.ERROR)
        return process

    def records(self):
        return [json.loads(line) for line in (self.root / "failure_register.jsonl").read_text().splitlines()]

    def test_failed_run_records_pre_reset_streak_reason_and_evidence_once(self):
        for _ in range(3):
            self.run_cycle(PaintOperationResult(PaintOutcome.COMPLETED, "Completed"))
        self.fail_run()
        records = self.records()
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["consecutive_completed_cycles"], 3)
        self.assertEqual(record["failure"]["stage"], "pickup")
        self.assertEqual(record["failure"]["code"], "motion")
        self.assertEqual(record["message"], "Motor rejected\nНеуспешно")
        self.assertEqual(record["run_id"], "test-run")
        self.assertEqual(record["cycle_index"], 4)
        bundle = json.loads(Path(record["failure_bundle"]).read_text())
        self.assertEqual(record["cycle_id"], bundle["cycle_id"])
        self.assertEqual(self.production.consecutive_completed_cycles, 0)

    def test_collision_preserves_backend_details_and_original_cycle_failure(self):
        collision = {"joint": "Joint_6", "detector": "cpp_realtime_dynamics", "timestamp": 123.0}
        self.fail_run(collision=collision)
        record, = self.records()
        self.assertEqual(record["failure"]["stage"], "collision_monitor")
        self.assertEqual(record["collision_event"], collision)
        self.assertEqual(record["cycle_failure"]["stage"], "pickup")
        self.assertIn("Joint_6", record["message"])

    def test_external_fault_logged_once_and_writing_does_not_hold_process_lock(self):
        self.run_cycle(PaintOperationResult(PaintOutcome.COMPLETED, "Completed"))
        process = PaintProcess(self.production, MagicMock())
        writer = self.production.write_failure_record

        def write(record):
            self.assertFalse(process._lock.locked())
            writer(record)

        with patch.object(process, "_request_hardware_stop"), patch.object(
            self.production, "write_failure_record", side_effect=write,
        ):
            process.set_error("Robot disconnected")
            process.set_error("Robot disconnected")
        record, = self.records()
        self.assertEqual(record["consecutive_completed_cycles"], 1)
        self.assertEqual(record["message"], "Robot disconnected")

    def test_append_preserves_existing_records_and_storage_errors_are_best_effort(self):
        append_paint_failure_record(self.root, {"message": "First"})
        append_paint_failure_record(self.root, {"message": "Second"})
        self.assertEqual([r["message"] for r in self.records()], ["First", "Second"])
        with patch("pathlib.Path.open", side_effect=OSError("Disk full")):
            with self.assertLogs("src.robot_systems.paint.diagnostics.failure_register", level="ERROR"):
                append_paint_failure_record(self.root, {"message": "Third"})

    def test_expected_stop_does_not_create_failure_record(self):
        self.production.run_once_result = lambda *args: PaintOperationResult(PaintOutcome.NO_WORKPIECE, "Empty")
        process = PaintProcess(self.production, MagicMock())
        process._state = ProcessState.RUNNING
        with patch.object(process, "_request_hardware_stop"):
            process._run_in_background_impl()
        self.assertEqual(process.state, ProcessState.STOPPED)
        self.assertFalse((self.root / "failure_register.jsonl").exists())

    def test_missing_bundle_does_not_prevent_register_entry(self):
        with patch(
            "src.robot_systems.paint.diagnostics.failure_bundle.write_paint_failure_bundle",
            return_value=None,
        ):
            self.fail_run()
        record, = self.records()
        self.assertIsNone(record["failure_bundle"])
        self.assertEqual(record["failure"]["stage"], "pickup")

    def test_register_identifies_dry_run_part_instead_of_generic_captured_id(self):
        failed = PaintOperationResult.failed(PaintFailureCode.MOTION, "pickup", "Rejected")

        def fail_cycle(context, **kwargs):
            context.workpiece_description = "Executed captured contour"
            context.raw_workpiece = {"workpieceId": "captured", "name": "Captured contour"}
            context.dry_run_metadata = {"paint": {
                "dataset_index": 20, "dataset_manifest": "/dataset/manifest.json",
                "workpiece": {"id": "0022_ellipse", "shape_type": "ellipse", "contour_normalized": [[1, 2]]},
                "angle_deg": 196.2, "contour_mm": [[3, 4]],
            }}
            return PaintCycleExecution(failed)

        self.production.run_once_result = lambda *args: self.production.run_cycle_result(
            lambda: False, process_config=self.config, magazine_config=None, cycle_index=21,
        )
        process = PaintProcess(self.production, MagicMock())
        process._state = ProcessState.RUNNING
        with patch.object(process, "_request_hardware_stop"), patch(
            "src.robot_systems.paint.processes.paint.production.service.run_paint_cycle",
            side_effect=fail_cycle,
        ):
            process._run_in_background_impl()
        record, = self.records()
        part = record["workpiece"]
        self.assertEqual(part["id"], "0022_ellipse")
        self.assertEqual(part["prepared_workpiece_id"], "captured")
        self.assertEqual(part["dry_run_placements"]["paint"]["dataset_index"], 20)
        self.assertEqual(part["dry_run_placements"]["paint"]["angle_deg"], 196.2)
        self.assertNotIn("contour_normalized", json.dumps(part))
        self.assertNotIn("contour_mm", json.dumps(part))

    def test_identity_for_real_part_magazine_only_and_unknown_part(self):
        real = summarize_failure_workpiece("Matched part", {"workpieceId": "part-7", "name": "Panel"}, None)
        self.assertEqual(real["id"], "part-7")
        self.assertEqual(real["name"], "Panel")
        magazine = summarize_failure_workpiece("", None, {"magazine": {"workpiece": {"id": "dry-part"}}})
        self.assertEqual(magazine["id"], "dry-part")
        self.assertIsNone(summarize_failure_workpiece("", None, None))
