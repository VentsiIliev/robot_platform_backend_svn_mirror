import json
import unittest
from pathlib import Path
from threading import Event
from unittest.mock import MagicMock

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QPushButton

from src.applications.tool_settings.service.stub_tool_settings_service import StubToolSettingsService
from src.applications.tool_settings.tool_settings_factory import ToolSettingsFactory
from src.engine.localization.dict_translator import DictTranslator
from src.engine.robot.tool_changer import ToolChangeStep


class SequenceTeachingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        self.service = StubToolSettingsService()
        self.service.update_slot_sequences = MagicMock(return_value=(True, 'Saved'))
        self.view = ToolSettingsFactory().build(self.service)
        self.view.resize(1280, 900)
        self.view.show()
        self.ctrl = self.view._controller
        self.ctrl._on_edit_sequences(10)
        self.editor = self.view._sequence_editor

    def tearDown(self):
        self.ctrl.stop()
        self.view.close()
        self.view.deleteLater()
        self.app.processEvents()

    def _capture(self):
        self.editor._capture.click()
        for _ in range(200):
            QTest.qWait(5)
            if self.ctrl._capture_page is None and not self.ctrl._active:
                break
        self.assertIsNone(self.ctrl._capture_page)

    def test_teaching_is_inline_and_jog_remains_enabled(self):
        self.assertIsNone(self.app.activeModalWidget())
        self.assertTrue(self.view._drawer._btn.isEnabled())
        self.assertTrue(self.view._jog_widget.isEnabled())
        self.assertTrue(self.editor.isVisible())
        self.assertFalse(self.view._tabs.isVisible())
        labels = {button.text() for button in self.editor.findChildren(QPushButton, options=Qt.FindChildOption.FindDirectChildrenOnly)}
        self.assertEqual(labels, {'Capture position', 'Remove selected', 'Cancel', 'Save sequences',
                                  'Reverse pickup into drop-off', 'Run pickup', 'Run drop-off', 'Stop'})

    def test_capture_order_and_pickup_dropoff_saved_independently(self):
        poses = [[float(i)] * 6 for i in (1, 2, 3)]
        self.service.get_current_motion_pose = MagicMock(side_effect=[(True, '', pose) for pose in poses])
        self._capture()
        self._capture()
        self.editor._tabs.setCurrentIndex(1)
        self._capture()
        self.editor._save.click()
        slot, pickup, dropoff = self.service.update_slot_sequences.call_args.args
        self.assertEqual(slot, 10)
        self.assertEqual([step['pose'] for step in pickup], poses[:2])
        self.assertEqual([step['pose'] for step in dropoff], poses[2:])
        self.assertTrue(all(step['kind'] == 'motion' for step in pickup + dropoff))
        self.assertFalse(self.editor.isVisible())
        self.assertTrue(self.view._tabs.isVisible())

    def test_capture_failure_keeps_draft_and_reports_error(self):
        self.service.get_current_motion_pose = MagicMock(return_value=(False, 'Disconnected', []))
        self._capture()
        self.assertEqual(self.editor._tables[0].rowCount(), 0)
        self.assertEqual(self.editor._message.text(), 'Disconnected')
        self.assertTrue(self.editor._capture.isEnabled())

    def test_capture_is_nonblocking_and_cannot_change_destination_while_pending(self):
        ready, release = Event(), Event()

        def pose():
            ready.set()
            release.wait(3)
            return True, '', [1] * 6

        self.service.get_current_motion_pose = pose
        self.editor._capture.click()
        try:
            self.assertTrue(ready.wait(1))
            self.app.processEvents()
            self.assertFalse(self.editor._tabs.isEnabled())
            self.assertFalse(self.editor._save.isEnabled())
            self.assertTrue(self.view._jog_widget.isEnabled())
        finally:
            release.set()
            for _ in range(200):
                QTest.qWait(5)
                if not self.ctrl._active:
                    break
        self.assertEqual(self.editor._tables[0].rowCount(), 1)

    def test_cancel_discards_captures(self):
        self._capture()
        self.editor._cancel.click()
        self.service.update_slot_sequences.assert_not_called()
        self.ctrl._on_edit_sequences(10)
        self.assertEqual(self.editor._tables[0].rowCount(), 0)

    def test_existing_actions_are_preserved_until_explicitly_removed(self):
        actions = [ToolChangeStep(kind='attach'), ToolChangeStep(kind='operator_confirm')]
        self.service._slots[0].pickup_sequence = actions
        self.ctrl._on_edit_sequences(10)
        self.editor._save.click()
        self.assertEqual(self.service.update_slot_sequences.call_args.args[1], [s.to_dict() for s in actions])

    def test_save_failure_leaves_draft_open(self):
        self._capture()
        self.service.update_slot_sequences.return_value = False, 'Save failed'
        self.editor._save.click()
        self.assertTrue(self.editor.isVisible())
        self.assertEqual(self.editor._tables[0].rowCount(), 1)
        self.assertEqual(self.editor._message.text(), 'Save failed')

    def test_remove_only_changes_selected_sequence_and_renumbers(self):
        self._capture()
        self._capture()
        self.editor._tables[0].selectRow(0)
        self.editor._remove.click()
        self.assertEqual(self.editor._tables[0].rowCount(), 1)
        self.assertEqual(self.editor._tables[0].item(0, 0).text(), '1')
        self.assertEqual(self.editor._tables[1].rowCount(), 0)

    def test_initial_bulgarian_and_runtime_language_switch(self):
        catalog = Path('src/applications/tool_settings/localization/bg.json')
        translator = DictTranslator(json.loads(catalog.read_text()))
        self.app.installTranslator(translator)
        try:
            from src.applications.tool_settings.view.sequence_editor import SequenceEditor
            editor = SequenceEditor()
            self.assertEqual(editor._capture.text(), 'Запиши позиция')
            self.app.sendEvent(self.editor, QEvent(QEvent.Type.LanguageChange))
            self.assertEqual(self.editor._tabs.tabText(0), 'Вземане')
            editor.deleteLater()
        finally:
            self.app.removeTranslator(translator)
        self.app.sendEvent(self.editor, QEvent(QEvent.Type.LanguageChange))
        self.assertEqual(self.editor._capture.text(), 'Capture position')

    def test_reverse_pickup_populates_dropoff_without_changing_pickup(self):
        steps = [{'kind': 'motion', 'pose': [i] * 6} for i in (1, 2)]
        steps.insert(1, {'kind': 'attach', 'label': 'Attach tool'})
        for step in steps:
            self.editor.append_step(0, step)
        self.editor._reverse.click()
        self.assertEqual(self.editor._tabs.currentIndex(), 1)
        dropoff = self.editor._values(1)
        self.assertEqual(dropoff[0]['pose'], [2] * 6)
        self.assertEqual(dropoff[1]['kind'], 'detach')
        self.assertEqual(dropoff[2]['pose'], [1] * 6)
        self.assertEqual(self.editor._values(0), steps)
        self.service.update_slot_sequences.assert_not_called()

    def test_run_buttons_execute_the_selected_draft_without_saving(self):
        self.service.execute_sequence = MagicMock(return_value=(True, 'Sequence completed'))
        for page, button in ((0, self.editor._run_pickup), (1, self.editor._run_dropoff)):
            self.editor._tabs.setCurrentIndex(page)
            step = {'kind': 'motion', 'pose': [page + 1] * 6}
            self.editor.append_step(page, step)
            button.click()
            for _ in range(200):
                QTest.qWait(5)
                if not self.ctrl._active:
                    break
            self.assertEqual(self.service.execute_sequence.call_args.args[:2], (10, [step]))
            self.assertTrue(self.view._jog_widget.isEnabled())
        self.service.update_slot_sequences.assert_not_called()

    def test_stop_cancels_execution_and_restores_controls_after_worker_finishes(self):
        started = Event()

        def run(slot, steps, cancelled):
            started.set()
            cancelled.wait(3)
            return False, 'Sequence stopped'

        self.service.execute_sequence = run
        self.service.stop_sequence_motion = MagicMock(return_value=(True, 'Stop requested'))
        self.editor.append_step(0, {'kind': 'motion', 'pose': [1] * 6})
        self.editor._run_pickup.click()
        self.assertTrue(started.wait(1))
        self.assertFalse(self.view._jog_widget.isEnabled())
        self.assertFalse(self.editor._capture.isEnabled())
        self.assertTrue(self.editor._stop.isEnabled())
        self.editor._stop.click()
        for _ in range(200):
            QTest.qWait(5)
            if not self.ctrl._active:
                break
        self.service.stop_sequence_motion.assert_called_once()
        self.assertTrue(self.view._jog_widget.isEnabled())
        self.assertTrue(self.editor._capture.isEnabled())
        self.assertFalse(self.editor._stop.isEnabled())

    def test_capture_uses_visible_velocity_and_acceleration(self):
        self.editor._velocity.setValue(24.5)
        self.editor._acceleration.setValue(35.0)
        self._capture()
        step = self.editor._values(0)[0]
        self.assertEqual(step['velocity'], 24.5)
        self.assertEqual(step['acceleration'], 35.0)
        table = self.editor._tables[0]
        self.assertEqual(table.item(0, 1).text(), '24.5')
        self.assertEqual(table.item(0, 2).text(), '35')

    def test_edit_selected_motion_is_saved_and_used_for_run(self):
        self._capture()
        self.editor._velocity.setValue(15.0)
        self.editor._acceleration.setValue(25.0)
        self.service.execute_sequence = MagicMock(return_value=(True, 'Sequence completed'))
        self.editor._run_pickup.click()
        for _ in range(200):
            QTest.qWait(5)
            if not self.ctrl._active:
                break
        step = self.service.execute_sequence.call_args.args[1][0]
        self.assertEqual((step['velocity'], step['acceleration']), (15.0, 25.0))
        self.editor._save.click()
        self.assertEqual(self.service.update_slot_sequences.call_args.args[1][0], step)

    def test_selecting_saved_position_loads_its_settings_without_modifying_other_steps(self):
        steps = [dict(kind='motion', pose=[i] * 6, velocity=v, acceleration=a)
                 for i, v, a in ((1, 12.5, 22.5), (2, 32.5, 42.5))]
        for step in steps:
            self.editor.append_step(0, step)
        self.editor._tables[0].selectRow(0)
        self.assertEqual(self.editor._velocity.value(), 12.5)
        self.assertEqual(self.editor._acceleration.value(), 22.5)
        self.editor._velocity.setValue(16.0)
        self.assertEqual(self.editor._values(0)[0]['velocity'], 16.0)
        self.assertEqual(self.editor._values(0)[1], steps[1])
        self.editor._reverse.click()
        self.assertEqual(self.editor._values(1)[1]['velocity'], 16.0)

    def test_motion_fields_disabled_for_saved_actions_and_running_sequence(self):
        self.editor.append_step(0, {'kind': 'attach'})
        self.assertFalse(self.editor._velocity.isEnabled())
        self.assertFalse(self.editor._acceleration.isEnabled())
        self.editor.append_step(0, {'kind': 'motion', 'pose': [1] * 6})
        self.assertTrue(self.editor._velocity.isEnabled())
        self.editor.set_executing(True)
        self.assertFalse(self.editor._velocity.isEnabled())
        self.editor.set_executing(False)
        self.assertTrue(self.editor._velocity.isEnabled())

    def test_endpoint_options_default_off_and_are_independent_per_sequence(self):
        for page in (0, 1):
            self.assertFalse(self.editor._start_at_tool_changer[page].isChecked())
            self.assertFalse(self.editor._finish_at_tool_changer[page].isChecked())
        self.editor.append_step(0, {'kind': 'motion', 'pose': [1] * 6})
        self.editor.append_step(1, {'kind': 'motion', 'pose': [2] * 6})
        self.editor._start_at_tool_changer[0].setChecked(True)
        self.editor._finish_at_tool_changer[1].setChecked(True)
        self.editor._save.click()
        _, pickup, dropoff = self.service.update_slot_sequences.call_args.args
        self.assertEqual([s['kind'] for s in pickup], ['start_at_tool_changer', 'motion'])
        self.assertEqual([s['kind'] for s in dropoff], ['motion', 'finish_at_tool_changer'])

    def test_reload_endpoint_options_and_switching_them_off_preserves_taught_steps(self):
        slot = self.service.get_slots()[0]
        slot.pickup_sequence = [ToolChangeStep(kind='start_at_tool_changer'),
                                ToolChangeStep(pose=[1]*6), ToolChangeStep(kind='finish_at_tool_changer')]
        self.editor.set_slot(slot)
        self.assertTrue(self.editor._start_at_tool_changer[0].isChecked())
        self.assertTrue(self.editor._finish_at_tool_changer[0].isChecked())
        self.assertEqual(self.editor._tables[0].rowCount(), 1)
        self.editor._start_at_tool_changer[0].setChecked(False)
        self.editor._finish_at_tool_changer[0].setChecked(False)
        self.assertEqual([s['kind'] for s in self.editor._values(0)], ['motion'])
        self.editor.set_slot(slot)
        self.assertEqual([s['kind'] for s in self.editor._values(0)],
                         ['start_at_tool_changer', 'motion', 'finish_at_tool_changer'])
        self.assertEqual(self.editor._tables[0].rowCount(), 1)

    def test_run_emits_current_unsaved_endpoint_settings_without_saving(self):
        self.editor.append_step(0, {'kind': 'motion', 'pose': [1] * 6})
        self.editor._start_at_tool_changer[0].setChecked(True)
        self.editor._finish_at_tool_changer[0].setChecked(True)
        calls = []
        def capture_execution(page, steps):
            calls.append((page, steps))
        self.editor.execute_requested.connect(capture_execution)
        self.editor._run_pickup.click()
        self.assertEqual([s['kind'] for s in calls[0][1]],
                         ['start_at_tool_changer', 'motion', 'finish_at_tool_changer'])
        self.service.update_slot_sequences.assert_not_called()
        for _ in range(200):
            QTest.qWait(5)
            if not self.ctrl._active:
                break

    def test_reverse_swaps_endpoint_options_as_well_as_taught_steps(self):
        self.editor.append_step(0, {'kind': 'motion', 'pose': [1] * 6})
        self.editor._start_at_tool_changer[0].setChecked(True)
        self.editor._reverse.click()
        self.assertFalse(self.editor._start_at_tool_changer[1].isChecked())
        self.assertTrue(self.editor._finish_at_tool_changer[1].isChecked())
        self.assertEqual([s['kind'] for s in self.editor._values(1)], ['motion', 'finish_at_tool_changer'])

    def test_endpoint_options_cannot_change_during_execution(self):
        self.editor.set_executing(True)
        for page in (0, 1):
            self.assertFalse(self.editor._start_at_tool_changer[page].isEnabled())
            self.assertFalse(self.editor._finish_at_tool_changer[page].isEnabled())
        self.editor.set_executing(False)
        self.assertTrue(self.editor._start_at_tool_changer[0].isEnabled())

    def test_endpoint_options_translate_initially_and_on_language_change(self):
        from src.applications.tool_settings.view.sequence_editor import SequenceEditor
        translator = DictTranslator(json.loads(Path('src/applications/tool_settings/localization/bg.json').read_text()))
        self.app.installTranslator(translator)
        editor = None
        try:
            editor = SequenceEditor()
            self.assertEqual(editor._start_at_tool_changer[0].text(), 'Начало от позицията за смяна на инструменти')
            self.app.sendEvent(self.editor, QEvent(QEvent.Type.LanguageChange))
            self.assertEqual(self.editor._finish_at_tool_changer[0].text(), 'Край на позицията за смяна на инструменти')
        finally:
            self.app.removeTranslator(translator)
            if editor is not None:
                editor.deleteLater()
        self.app.sendEvent(self.editor, QEvent(QEvent.Type.LanguageChange))
        self.assertEqual(self.editor._start_at_tool_changer[0].text(), 'Start from Tool Changer')

    def test_inactive_dropoff_cannot_run_with_visible_pickup_options(self):
        self.service.execute_sequence = MagicMock(return_value=(True, 'Sequence completed'))
        self.editor.append_step(0, {'kind': 'motion', 'pose': [1] * 6})
        self.editor.append_step(1, {'kind': 'motion', 'pose': [2] * 6})
        self.editor._start_at_tool_changer[0].setChecked(True)
        self.editor._finish_at_tool_changer[0].setChecked(True)
        self.assertTrue(self.editor._run_pickup.isEnabled())
        self.assertFalse(self.editor._run_dropoff.isEnabled())
        self.editor._run_dropoff.click()
        self.editor._on_run_dropoff()
        self.service.execute_sequence.assert_not_called()
        self.editor._tabs.setCurrentIndex(1)
        self.assertFalse(self.editor._run_pickup.isEnabled())
        self.assertTrue(self.editor._run_dropoff.isEnabled())
        self.assertFalse(self.editor._finish_at_tool_changer[1].isChecked())

    def test_dropoff_run_includes_its_own_enabled_start_and_finish_moves(self):
        self.service.execute_sequence = MagicMock(return_value=(True, 'Sequence completed'))
        self.editor.append_step(1, {'kind': 'motion', 'pose': [2] * 6})
        self.editor._tabs.setCurrentIndex(1)
        self.editor._start_at_tool_changer[1].setChecked(True)
        self.editor._finish_at_tool_changer[1].setChecked(True)
        self.editor._run_dropoff.click()
        for _ in range(200):
            QTest.qWait(5)
            if not self.ctrl._active:
                break
        self.assertEqual([step['kind'] for step in self.service.execute_sequence.call_args.args[1]],
                         ['start_at_tool_changer', 'motion', 'finish_at_tool_changer'])
        self.assertTrue(self.editor._run_dropoff.isEnabled())
        self.assertFalse(self.editor._run_pickup.isEnabled())
