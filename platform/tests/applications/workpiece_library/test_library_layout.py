import json
import unittest
from pathlib import Path

from PyQt6.QtCore import QCoreApplication, QEvent, Qt
from PyQt6.QtWidgets import QApplication

from src.applications.workpiece_library.domain.workpiece_schema import WorkpieceRecord
from src.applications.workpiece_library.domain.geometry_summary import summarize_geometry
from src.applications.workpiece_library.view.workpiece_library_view import WorkpieceLibraryView
from src.robot_systems.paint.domain.workpieces.paint_workpiece_library_service import build_paint_workpiece_library_schema
from src.engine.localization.dict_translator import DictTranslator


class TestLibraryLayout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.view = WorkpieceLibraryView(build_paint_workpiece_library_schema(), selection_enabled=True)
        self.records = [
            WorkpieceRecord(dict(id='a', name='Zulu', description='First', date='2026-01-02', height_mm=2)),
            WorkpieceRecord(dict(id='b', name='Alpha', description='Second', date='2026-01-03', height_mm=10)),
        ]
        self.view.set_available_ids(['a', 'b'])
        self.view.set_records(self.records)
        self.view.resize(1000, 780)
        self.view.show()
        self.app.processEvents()

    def tearDown(self):
        self.view.clean_up()
        self.view.close()
        self.view.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)

    def test_sorting_and_grid_keep_action_bound_to_selected_record(self):
        self.assertEqual(self.view._table.item(0, 2).data(Qt.ItemDataRole.UserRole).get('id'), 'b')
        self.view._table.selectRow(0)
        self.view._sort_buttons['height'].click()
        self.assertEqual(self.view._table.item(0, 2).data(Qt.ItemDataRole.UserRole).get('id'), 'a')
        self.assertEqual(self.view.selected_record().get('id'), 'b')
        self.view._grid_button.click()
        opened = []
        self.view.open_in_editor_requested.connect(opened.append)
        self.view._btn_open.click()
        self.assertEqual(opened[0].get('id'), 'b')
        self.view._grid.setCurrentRow(0)
        self.view._list_button.click()
        self.assertEqual(self.view.selected_record().get('id'), 'a')

    def test_dirty_save_and_numeric_height(self):
        self.view._table.selectRow(0)
        self.assertFalse(self.view._btn_save.isEnabled())
        self.view._edit_widgets['name'].setText('Changed')
        self.view._edit_widgets['height_mm'].setValue(12.5)
        saved = []
        self.view.edit_requested.connect(lambda record, updates: saved.append((record, updates)))
        self.view._btn_save.click()
        self.assertEqual(saved[0][0].get('id'), 'b')
        self.assertEqual(saved[0][1]['name'], 'Changed')
        self.assertEqual(saved[0][1]['height_mm'], 12.5)
        self.view.set_detail(None)
        for button in (self.view._btn_open, self.view._btn_save, self.view._btn_delete, self.view._btn_duplicate):
            self.assertFalse(button.isEnabled())

    def test_language_switch_preserves_unsaved_values(self):
        self.view._table.selectRow(0)
        self.view._edit_widgets['name'].setText('Unsaved')
        translator = DictTranslator(json.loads(Path('src/applications/workpiece_library/localization/bg.json').read_text()))
        self.app.installTranslator(translator)
        try:
            self.view.retranslateUi()
            self.assertEqual(self.view._btn_open.text(), 'Отвори в редактора')
            self.assertEqual(self.view._edit_widgets['name'].text(), 'Unsaved')
            self.assertTrue(self.view._btn_save.isEnabled())
        finally:
            self.app.removeTranslator(translator)

    def test_select_mode_and_grid_checks_preserve_storage_ids(self):
        applied = []
        self.view.selection_requested.connect(applied.append)
        self.view.set_selection(())
        self.view._select_button.click()
        self.view._grid_button.click()
        self.view._grid.item(0).setCheckState(Qt.CheckState.Checked)
        self.assertEqual(applied[-1], ('b',))
        self.view.set_records([self.records[0]])
        self.assertEqual(self.view.checked_ids(), {'b'})
        self.view._grid.item(0).setCheckState(Qt.CheckState.Checked)
        self.assertIsNone(applied[-1])


class TestGeometrySummary(unittest.TestCase):
    def test_separate_paths_are_not_joined_and_nested_points_are_supported(self):
        summary = summarize_geometry({'contour': [[[0, 0]], [[10, 0]], [[10, 10]]],
            'sprayPattern': {'Contour': [{'contour': [[0, 0], [3, 4]]}, {'contour': [[100, 0], [100, 2]]}]}})
        self.assertEqual(summary['points'], 7)
        self.assertEqual(summary['path_length'], 7)
        self.assertEqual(summary['dimensions'], '100.0 × 10.0 mm')
        self.assertIsNone(summarize_geometry(None))
        self.assertIsNone(summarize_geometry({'contour': ['bad', [float('inf'), 0]]}))
