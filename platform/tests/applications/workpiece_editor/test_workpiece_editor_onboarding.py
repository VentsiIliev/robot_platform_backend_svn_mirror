import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget

from src.applications.workpiece_editor.view.workpiece_editor_view import WorkpieceEditorView
from src.engine.localization.dict_translator import DictTranslator
from tests.applications.workpiece_editor.test_workpiece_editor_view import _make_view


class TestWorkpieceEditorOnboarding(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.editor = QWidget()
        layout = QVBoxLayout(self.editor)
        self.capture = QPushButton('Capture')
        self.save = QPushButton('Save')
        layout.addWidget(self.capture)
        layout.addWidget(self.save)
        self.editor.topbar = SimpleNamespace(capture_button=self.capture, save_button=self.save)
        with patch.object(WorkpieceEditorView, '_build_editor', return_value=self.editor):
            self.view = _make_view()
        self.view.resize(1280, 900)
        self.view.show()
        self.app.processEvents()

    def tearDown(self):
        self.view.clean_up()
        self.view.close()
        self.view.deleteLater()
        self.app.processEvents()

    def test_navigation_skips_unavailable_controls_and_restarts(self):
        self.view.start_onboarding_tour()
        tour = self.view._onboarding_tour
        self.assertEqual(tour._index, 0)
        tour.next()
        self.assertEqual(tour._overlay._title.text(), 'Capture contours')
        tour.next()
        self.assertEqual(tour._overlay._title.text(), 'Save the workpiece')
        tour.next()
        self.assertIsNone(tour._overlay)
        self.view.start_onboarding_tour()
        self.assertEqual(tour._index, 0)
        self.view.hide()
        self.assertIsNone(tour._overlay)

    def test_localization_initial_display_and_language_switch(self):
        path = Path('src/applications/workpiece_editor/localization/bg.json')
        translator = DictTranslator(json.loads(path.read_text()))
        self.app.installTranslator(translator)
        try:
            self.view.start_onboarding_tour()
            self.assertEqual(self.view._onboarding_tour._overlay._title.text(),
                             'Добре дошли в редактора на детайли')
            self.app.removeTranslator(translator)
            self.view.on_language_changed()
            self.assertIsNone(self.view._onboarding_tour._overlay)
            self.view.start_onboarding_tour()
            self.assertEqual(self.view._onboarding_tour._overlay._title.text(),
                             'Welcome to the Workpiece Editor')
        finally:
            self.app.removeTranslator(translator)

    def test_catalogs_cover_all_tour_strings(self):
        self.view.start_onboarding_tour()
        for language in ('en', 'bg'):
            catalog = json.loads(Path(f'src/applications/workpiece_editor/localization/{language}.json').read_text())['WorkpieceEditorOnboarding']
            for step in self.view._onboarding_tour._steps:
                self.assertTrue(catalog[step.title])
                self.assertTrue(catalog[step.body])

    def test_individual_canvas_redo_and_nudge_targets(self):
        from contour_editor.ui.new_widgets.BottomToolBar import BottomToolBar
        from contour_editor.ui.new_widgets.NudgePointWidget import NudgePointWidget
        toolbar = BottomToolBar()
        nudge = NudgePointWidget()
        redo = QPushButton('Redo')
        self.editor.layout().addWidget(toolbar)
        self.editor.layout().addWidget(nudge)
        self.editor.layout().addWidget(redo)
        self.editor.contourEditor = SimpleNamespace(bottom_toolbar=toolbar)
        self.editor.pointManagerWidget = SimpleNamespace(coordinator=SimpleNamespace(nudge_widget=nudge))
        self.editor.topbar.redo_button = redo
        self.app.processEvents()
        expected = {'point_visibility': toolbar.hide_points_button,
                    'zoom_out': toolbar.zoom_out_button,
                    'reset_zoom': toolbar.reset_zoom_button,
                    'zoom_in': toolbar.zoom_in_button,
                    'pan': toolbar.pan_toggle_button, 'redo': redo,
                    'nudge': nudge.title_label}
        self.view.start_onboarding_tour()
        tour = self.view._onboarding_tour
        visited = []
        while tour._overlay is not None:
            visited.append(tour._steps[tour._index].target())
            tour.next()
        for target_id, widget in expected.items():
            self.assertIs(self.view.onboarding_target(target_id), widget)
            self.assertIn(widget, visited)

    def test_segment_and_layer_buttons_resolve_from_real_list_rows(self):
        from PyQt6.QtWidgets import QListWidget, QListWidgetItem
        from contour_editor.ui.new_widgets.point_manager.list_item_widgets import (
            ExpandableLayerWidget, ExpandableSegmentWidget, PointWidget,
        )
        from contour_editor.ui.new_widgets.LayerButtonsWidget import LayerButtonsWidget
        from contour_editor.ui.new_widgets.SegmentButtonsAndComboWidget import SegmentButtonsAndComboWidget
        listing = QListWidget()
        self.editor.layout().addWidget(listing)
        coordinator = SimpleNamespace(list=listing)
        self.editor.pointManagerWidget = SimpleNamespace(coordinator=coordinator)
        layer_item = QListWidgetItem(listing)
        layer = LayerButtonsWidget('Main', layer_item, lambda *_: None,
                                   lambda *_: None, lambda *_: None)
        layer_row = ExpandableLayerWidget('Main', layer, lambda *_: None)
        layer_item.setSizeHint(layer_row.sizeHint())
        listing.setItemWidget(layer_item, layer_row)
        segment = SegmentButtonsAndComboWidget(0, SimpleNamespace(visible=True), 'Main',
                                               *([lambda *_: None] * 6))
        segment_row = ExpandableSegmentWidget(0, segment, lambda *_: None)
        segment_item = QListWidgetItem(listing)
        segment_item.setSizeHint(segment_row.sizeHint())
        listing.setItemWidget(segment_item, segment_row)
        point = PointWidget('P0', '(0, 0)')
        point_item = QListWidgetItem(listing)
        point_item.setSizeHint(point.sizeHint())
        listing.setItemWidget(point_item, point)
        self.app.processEvents()
        for target_id, target in {
            'layer_expand': layer_row.expand_btn,
            'layer_visibility': layer.visibility_btn,
            'layer_add': layer.add_segment_btn, 'layer_lock': layer.lock_btn,
            'segment_expand': segment_row.expand_btn,
            'segment_activate': segment.index_label,
            'segment_visibility': segment.visibility_btn,
            'segment_delete': segment.delete_btn,
            'segment_settings': segment.settings_btn, 'point_select': point,
        }.items():
            self.assertIs(self.view.onboarding_target(target_id), target)
        listing.clear()
        self.assertIsNone(self.view.onboarding_target('segment_delete'))
