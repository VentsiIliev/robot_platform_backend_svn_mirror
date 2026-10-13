"""Preview behavior can be replaced independently of production execution."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from src.robot_systems.paint.processes.paint.adapters.workpiece_editor import PaintWorkpiecePathExecutor
from src.robot_systems.paint.visualization.i_paint_preview_geometry import IPaintPreviewGeometry
from src.robot_systems.paint.visualization.paint_preview_geometry import PaintPreviewGeometry


class _AlternatePreview(IPaintPreviewGeometry):
    def get_projected_pivot_paths(self, execution_plan):
        return execution_plan.paths, [1, 2, 3, 0, 0, 0]

    def get_pivot_motion_snapshots(self, execution_plan):
        return execution_plan.snapshots, [1, 2, 3, 0, 0, 0]


class TestPreviewProvider(unittest.TestCase):
    def test_alternate_provider_changes_preview_without_calling_runtime(self):
        runtime = MagicMock()
        plan = SimpleNamespace(paths=[[[1, 2, 3, 0, 0, 0]]], snapshots=[[]])
        adapter = PaintWorkpiecePathExecutor(runtime, preview=_AlternatePreview())

        self.assertEqual((plan.paths, [1, 2, 3, 0, 0, 0]), adapter.get_pivot_preview_paths(plan))
        self.assertEqual((plan.snapshots, [1, 2, 3, 0, 0, 0]), adapter.get_pivot_motion_preview(plan))
        self.assertEqual([], runtime.mock_calls)

        runtime.execute_paint_process.return_value = (True, "Completed")
        self.assertEqual((True, "Completed"), adapter.execute_process_action(plan, "paint_process"))
        runtime.execute_paint_process.assert_called_once_with(plan)

    def test_default_provider_skips_projection_when_pivot_is_unavailable(self):
        for pose in (None, [1, 2]):
            with self.subTest(pose=pose):
                context_provider = MagicMock(return_value=SimpleNamespace(base_pivot_pose=pose))
                preview = PaintPreviewGeometry(context_provider)
                plan = object()
                with patch('src.robot_systems.paint.visualization.paint_preview_geometry.project_paint_contact_motion_continuous') as project:
                    self.assertEqual(([], pose), preview.get_projected_pivot_paths(plan))
                    self.assertEqual(([], pose), preview.get_pivot_motion_snapshots(plan))
                    project.assert_not_called()
                self.assertEqual(2, context_provider.call_count)

    def test_process_implementation_does_not_import_visualization(self):
        root = Path(__file__).resolve().parents[3] / 'src/robot_systems/paint/processes/paint'
        # The editor adapter is the intentional visualization consumer.
        for package in ('production', 'workflow', 'operations', 'planning'):
            for path in (root / package).rglob('*.py'):
                for node in ast.walk(ast.parse(path.read_text())):
                    modules = ([node.module or ''] if isinstance(node, ast.ImportFrom) else
                               [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
                    for module in modules:
                        self.assertNotIn('paint.visualization', module, str(path))
