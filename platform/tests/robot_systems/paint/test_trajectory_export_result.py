"""Optional exports report failures without raising into their motion caller."""
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from src.robot_systems.paint.processes.paint.execute import diagnostics
from src.robot_systems.paint.processes.paint.execute.trajectory_export_result import (
    ExportFailed, ExportFailureCode, ExportSkipped, ExportWritten,
)


class TestTrajectoryExportResult(unittest.TestCase):
    def request(self, **overrides):
        args = dict(command_path=[[0, 1, 2, 3, 4, 5]], vel=10, acc=20,
                    pattern_type="contour", stage="execute_job_1")
        args.update(overrides)
        return diagnostics.write_platform_command_path_csv(**args)

    def test_empty_path_is_explicitly_skipped_without_submission(self):
        with patch.object(diagnostics, "_TRAJECTORY_EXPORT_EXECUTOR") as executor:
            result = self.request(command_path=[]).result()
        self.assertIsInstance(result, ExportSkipped)
        executor.submit.assert_not_called()

    def test_invalid_snapshot_is_a_typed_failure_before_submission(self):
        with patch.object(diagnostics, "_TRAJECTORY_EXPORT_EXECUTOR") as executor:
            with self.assertLogs(diagnostics._logger, level="WARNING"):
                result = self.request(command_path=[["bad"]]).result()
        self.assertIsInstance(result, ExportFailed)
        self.assertIs(result.code, ExportFailureCode.INVALID_INPUT)
        self.assertEqual(result.phase, "snapshot")
        executor.submit.assert_not_called()

    def test_executor_shutdown_does_not_raise_into_motion_caller(self):
        with patch.object(diagnostics, "_TRAJECTORY_EXPORT_EXECUTOR") as executor:
            executor.submit.side_effect = RuntimeError("cannot schedule after shutdown")
            with self.assertLogs(diagnostics._logger, level="WARNING"):
                result = self.request().result()
        self.assertIs(result.code, ExportFailureCode.UNAVAILABLE)
        self.assertEqual(result.phase, "submit")

    def test_unexpected_submission_bug_is_error_level_internal_failure(self):
        with patch.object(diagnostics, "_TRAJECTORY_EXPORT_EXECUTOR") as executor:
            executor.submit.side_effect = AttributeError("broken executor")
            with self.assertLogs(diagnostics._logger, level="ERROR") as logs:
                result = self.request().result()
        self.assertIs(result.code, ExportFailureCode.INTERNAL)
        self.assertIn("AttributeError", logs.output[0])

    def test_directory_permission_failure_is_distinct_from_programming_bug(self):
        with patch.object(diagnostics.Path, "mkdir", side_effect=PermissionError("denied")):
            with self.assertLogs(diagnostics._logger, level="WARNING"):
                result = diagnostics._write_platform_command_path_artifacts(
                    ((0, 1, 2, 3, 4, 5),), 10, 20, "contour", "job", {})
        self.assertIs(result.code, ExportFailureCode.FILESYSTEM)
        self.assertEqual(result.phase, "create_directory")
        self.assertEqual(result.completed_artifacts, ())

    def run_export(self, root, *, plot_failure=None):
        fake_source = root / "a/b/c/d/e/f/diagnostics.py"
        def write_plot(path, _data):
            path.write_bytes(b"test plot")
        with ThreadPoolExecutor(max_workers=1) as executor:
            with patch.object(diagnostics, "__file__", str(fake_source)), \
                 patch.object(diagnostics, "_TRAJECTORY_EXPORT_EXECUTOR", executor), \
                 patch.object(diagnostics, "_write_platform_pose_plot",
                              side_effect=plot_failure or write_plot), \
                 patch.object(diagnostics, "_write_contour_pipeline_plot", side_effect=write_plot), \
                 patch.object(diagnostics, "_write_contour_before_after_plot"):
                return self.request().result(timeout=5)

    def test_plot_bug_reports_csv_already_written_and_preserves_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertLogs(diagnostics._logger, level="ERROR") as logs:
                result = self.run_export(Path(directory), plot_failure=ValueError("plot bug"))
            self.assertIs(result.code, ExportFailureCode.INTERNAL)
            self.assertEqual(result.phase, "command_plot")
            self.assertEqual(len(result.completed_artifacts), 1)
            self.assertTrue(result.completed_artifacts[0].is_file())
            self.assertIn("ValueError: plot bug", logs.output[0])

    def test_success_records_only_artifacts_actually_written(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_export(Path(directory))
            self.assertIsInstance(result, ExportWritten)
            self.assertEqual(result.stage, "execute_job_1")
            self.assertEqual(len(result.artifacts), 4)
            self.assertTrue(all(path.is_file() for path in result.artifacts))
            self.assertIn("point_index", result.artifacts[0].read_text())

    def test_filesystem_failure_after_csv_retains_completed_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertLogs(diagnostics._logger, level="WARNING"):
                result = self.run_export(Path(directory), plot_failure=OSError("disk full"))
            self.assertIs(result.code, ExportFailureCode.FILESYSTEM)
            self.assertEqual(result.phase, "command_plot")
            self.assertEqual(len(result.completed_artifacts), 1)
            self.assertTrue(result.completed_artifacts[0].is_file())

    def test_queued_data_is_detached_from_mutable_caller_inputs(self):
        path = [[0, 1, 2, 3, 4, 5]]
        pipeline = {"source_px": [[1, 2]]}
        with patch.object(diagnostics, "_TRAJECTORY_EXPORT_EXECUTOR") as executor:
            self.request(command_path=path, pipeline_stages=pipeline)
            args = executor.submit.call_args.args
        path[0][0] = 100
        pipeline["source_px"][0][0] = 100
        self.assertEqual(args[1][0][0], 0)
        self.assertEqual(args[6]["source_px"][0][0], 1)

    def test_process_interrupts_are_not_converted_to_optional_failures(self):
        with patch.object(diagnostics, "_TRAJECTORY_EXPORT_EXECUTOR") as executor:
            executor.submit.side_effect = KeyboardInterrupt()
            with self.assertRaises(KeyboardInterrupt):
                self.request()
