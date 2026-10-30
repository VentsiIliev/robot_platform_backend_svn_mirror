"""Catalog coverage, initial translation and live retranslation of the actual MVC screen."""

import ast
import json
from pathlib import Path
from time import monotonic
from unittest import TestCase

from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QLabel, QPushButton

from src.engine.localization.dict_translator import DictTranslator
from src.robot_systems.paint.applications.paint_head_detector_setup.controller.paint_head_detector_setup_controller import (
    PaintHeadDetectorSetupController,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.model.paint_head_detector_setup_model import (
    PaintHeadDetectorSetupModel,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.service.stub_paint_head_detector_setup_service import (
    StubPaintHeadDetectorSetupService,
)
from src.robot_systems.paint.applications.paint_head_detector_setup.view.paint_head_detector_setup_view import (
    PaintHeadDetectorSetupView,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import Region

_ROOT = Path(__file__).resolve().parents[3]
_APP_ROOT = _ROOT / "src/robot_systems/paint/applications/paint_head_detector_setup"
_APP = QApplication.instance() or QApplication(["paint-head-localization-tests"])


def _strings(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {node.value}
    if isinstance(node, ast.IfExp):
        return _strings(node.body) | _strings(node.orelse)
    return set()


def source_strings():
    values = {"Confirm"}
    paths = [
        *_APP_ROOT.glob("view/**/*.py"),
        _APP_ROOT / "controller/paint_head_detector_setup_controller.py",
        _APP_ROOT / "tuning_fields.py",
    ]
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Call):
                name = node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id if isinstance(node.func, ast.Name) else ""
                if name in {"translate", "_label", "_button", "_card", "_field", "action_button", "SetupDialog", "finish_layout", "__init__"} and node.args:
                    values.update(_strings(node.args[0]))
                if name == "IconActionButton" and len(node.args) > 1:
                    values.update(_strings(node.args[1]))
                if name == "TuningParameter" and len(node.args) > 1:
                    values.update(_strings(node.args[1]))
            if isinstance(node, ast.Tuple) and len(node.elts) > 1:
                if all(isinstance(item, ast.Constant) and isinstance(item.value, str) for item in node.elts):
                    values.update(item.value for item in node.elts)
                elif len(node.elts) == 2:
                    first, second = node.elts
                    if isinstance(first, ast.Attribute) and isinstance(first.value, ast.Name) and first.value.id in {"SetupPage", "EditorTool", "TuningSection"}:
                        values.update(_strings(second))
                    if isinstance(second, ast.Attribute) and isinstance(second.value, ast.Name) and second.value.id == "self":
                        values.update(_strings(first))
            if isinstance(node, ast.Dict):
                for key, value in zip(node.keys, node.values):
                    if isinstance(key, ast.Attribute) and isinstance(key.value, ast.Name) and key.value.id in {"PaintHeadState", "PaintHeadObservationReason"}:
                        values.update(_strings(value))
    values.discard("PaintHeadDetectorSetup")
    return values


class CalibrationLocalizationTests(TestCase):
    def catalog(self, system, language):
        path = _ROOT / "src/robot_systems" / system / "storage/translations" / (language + ".json")
        return json.loads(path.read_text())

    def install(self, language):
        translator = DictTranslator(self.catalog("paint", language))
        _APP.installTranslator(translator)
        self.addCleanup(_APP.removeTranslator, translator)
        return translator

    def wait_for(self, predicate):
        deadline = monotonic() + 3
        while monotonic() < deadline:
            _APP.processEvents()
            if predicate():
                return
            QTest.qWait(5)
        self.fail("Timed out waiting for language/UI update")

    def test_every_static_source_exists_in_both_languages_for_all_paint_variants(self):
        sources = source_strings()
        self.assertGreater(len(sources), 180)
        for system in ("paint", "paint_tray_dry", "paint_auto_dry"):
            for language in ("en", "bg"):
                with self.subTest(system=system, language=language):
                    values = self.catalog(system, language)["PaintHeadDetectorSetup"]
                    self.assertEqual(sources - values.keys(), set())
                    self.assertTrue(all(values[source] for source in sources))

    def test_initial_bulgarian_render_uses_the_active_translator(self):
        translator = self.install("bg")
        view = PaintHeadDetectorSetupView()
        self.addCleanup(view.close)
        self.assertEqual(view.findChild(QPushButton, "saveCalibrationDraft").text(), "Запиши чернова")
        self.assertEqual(view.findChild(QPushButton, "saveCalibrationRevision").text(), "Запиши калибрация")
        self.assertIsNotNone(translator)

    def test_runtime_language_switch_preserves_draft_and_translates_dynamic_labels(self):
        service = StubPaintHeadDetectorSetupService()
        model = PaintHeadDetectorSetupModel(service)
        view = PaintHeadDetectorSetupView()
        controller = PaintHeadDetectorSetupController(model, view)
        self.addCleanup(view.close)
        self.addCleanup(controller.stop)
        controller.load()
        self.wait_for(lambda: model.snapshot.catalog is not None)
        self.wait_for(lambda: not controller.has_active_operations())
        from dataclasses import replace

        model.update_definition(replace(model.snapshot.definition, inspection_region=Region(150, 50, 340, 380)))
        before = model.snapshot.definition
        translator = self.install("bg")
        self.wait_for(lambda: "Незаписана чернова" in view.findChild(QLabel, "calibrationDraftStatus").text())
        self.assertEqual(model.snapshot.definition, before)
        self.assertTrue(model.snapshot.dirty)
        self.assertIn("Процес:", view.findChild(QLabel, "calibrationRuntimeSelection").text())
        self.assertIn("Standard", view.findChild(QLabel, "calibrationRuntimeSelection").text())
        self.wait_for(lambda: any('Камера на живо' in label.text() for label in view.findChildren(QLabel)))
        self.assertIsNotNone(translator)
