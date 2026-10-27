import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import numpy as np

from PyQt6.QtCore import QEvent
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtTest import QTest

from src.applications.workpiece_editor.view.workpiece_editor_view import WorkpieceEditorView
from src.engine.localization.dict_translator import DictTranslator
from src.applications.workpiece_editor.controller.workpiece_editor_controller import WorkpieceEditorController
from src.applications.workpiece_editor.model.workpiece_editor_model import WorkpieceEditorModel
from src.applications.workpiece_editor.service.workpiece_editor_service import (
    WorkpieceEditorService, WorkpieceEditorServices, WorkpieceEditorStorage,
)
from src.applications.workpiece_editor.editor_core.config import SegmentEditorConfig
from src.robot_systems.paint.domain.contour_editor_schema import (
    build_paint_contour_form_schema, build_paint_segment_settings_schema,
)
from src.robot_systems.paint.domain.paint_workpiece_editor_adapter import PaintWorkpieceEditorAdapter
from src.robot_systems.paint.domain.paint_capture_contour_preparation import PaintCaptureContourPreparation


class TestCapturePreparationView(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_editor_waits_for_processed_geometry_and_retranslates_status(self):
        inner = SimpleNamespace(verification_contours=[[[1, 2], [3, 4]]],
                                set_verification_contours=MagicMock(), workpiece_manager=object())
        editor = QWidget()
        editor.contourEditor = SimpleNamespace(editor_with_rulers=SimpleNamespace(editor=inner))
        with patch.object(WorkpieceEditorView, "_build_editor", return_value=editor):
            view = WorkpieceEditorView(MagicMock(), MagicMock(), MagicMock())
        original_manager = inner.workpiece_manager
        view.set_capture_busy(True)
        self.assertFalse(editor.isEnabled())
        self.assertEqual("Processing captured contour…", view._capture_status_label.text())
        inner.set_verification_contours.assert_not_called()
        self.assertIs(original_manager, inner.workpiece_manager)

        catalog = Path(__file__).resolve().parents[3] / "src/applications/workpiece_editor/localization/bg.json"
        translator = DictTranslator(json.loads(catalog.read_text()))
        self.app.installTranslator(translator)
        try:
            self.app.sendEvent(view, QEvent(QEvent.Type.LanguageChange))
            self.assertEqual("Обработка на заснетия контур…", view._capture_status_label.text())
        finally:
            self.app.removeTranslator(translator)
            view.set_capture_busy(False)
            self.assertTrue(editor.isEnabled())
            self.assertTrue(view._capture_status_label.isHidden())
            view.close()

    def test_capture_loads_editable_processed_points_and_saves_original_only_for_matching(self):
        original = [[100., 100.], [200., 100.], [200., 200.], [100., 200.]]
        processed = [[100.1, 100.1], [150., 100.2], [199.9, 100.1], [199.9, 199.9], [100.1, 199.9]]
        preparation = MagicMock()
        preparation.build_execution_plan.return_value = SimpleNamespace(
            raw_pixel_paths=[original], raw_paths=[original], prepared_paths=[processed])
        vision = MagicMock()
        vision.get_latest_contours.return_value = [original]
        save = MagicMock(return_value=(True, "saved"))
        adapter = PaintWorkpieceEditorAdapter()
        schema = build_paint_contour_form_schema()
        config = SegmentEditorConfig(schema=build_paint_segment_settings_schema())
        service = WorkpieceEditorService(
            storage=WorkpieceEditorStorage(save_fn=save, update_fn=MagicMock()),
            services=WorkpieceEditorServices(
                vision_service=vision, workpiece_data_adapter=adapter,
                capture_workpiece_preparer=PaintCaptureContourPreparation(preparation)),
            form_schema=schema, segment_config=config)
        view = WorkpieceEditorView(schema, config, adapter)
        controller = WorkpieceEditorController(WorkpieceEditorModel(service), view, MagicMock())
        controller._active = True
        controller._save_pickup_debug_image = MagicMock()
        try:
            controller._on_capture()
            for _ in range(100):
                QTest.qWait(10)
                if not controller.has_running_workers():
                    break
            self.assertFalse(controller.has_running_workers())
            self.assertTrue(view._editor.isEnabled())
            inner = view._editor.contourEditor.editor_with_rulers.editor
            self.assertEqual([], inner.verification_contours)
            segments = inner.manager.get_segments()
            self.assertGreaterEqual(len(segments), 2)
            for segment in segments:
                self.assertFalse(segment.layer.locked)
                actual = [[point.x(), point.y()] for point in segment.points]
                np.testing.assert_allclose(processed, actual, atol=1e-4)

            main = next(s for s in segments if s.layer.name == "Workpiece")
            main.points[1].setX(153.0)
            # The settings dialog replaces visible settings. Hidden processing
            # metadata must still survive saving and later execution.
            main.set_settings({"velocity": 12})
            ok, message = controller._on_form_submit({"workpieceId": "processed-part"})
            self.assertTrue(ok, message)
            stored = save.call_args.args[0]
            self.assertEqual(original, stored["matchingContour"])
            self.assertTrue(stored["paint_contour_prepared"])
            self.assertAlmostEqual(153.0, np.asarray(stored["contour"]).reshape(-1, 2)[1, 0])
        finally:
            controller.stop()
            view.close()
