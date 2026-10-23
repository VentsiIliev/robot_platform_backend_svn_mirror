import logging
from threading import Event
from functools import partial

from PyQt6.QtCore import QObject, QThread, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QLabel, QVBoxLayout,
)

from src.applications.base.app_dialog import (
    AppDialog, DIALOG_COMBO_STYLE, DIALOG_INPUT_STYLE,
)
from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.styled_message_box import show_warning, ask_yes_no
from pl_gui.settings.settings_view.styles import LABEL_STYLE
from src.applications.base.widgets.custom_virtual_keyboard import (
    KeyboardLineEdit,
)
from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField
from ..model.tool_settings_model import ToolSettingsModel
from ..view.tool_settings_view import ToolSettingsView

_logger = logging.getLogger(__name__)


class _Worker(QObject):
    finished = pyqtSignal(object)

    def __init__(self, fn):
        super().__init__()
        self._fn = fn

    def run(self):
        try:
            self.finished.emit(self._fn())
        except Exception as exc:
            self.finished.emit((False, str(exc)))


def _lbl(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(LABEL_STYLE)
    return lbl


class ToolSettingsController(IApplicationController):

    def __init__(self, model: ToolSettingsModel, view: ToolSettingsView):
        self._model = model
        self._view  = view
        self._active = []
        self._reference_captured = False
        self._candidate_samples = 0
        self._teaching_slot_id = None
        self._capture_page = None
        self._capture_settings = {}
        self._sequence_cancelled = None
        self._sequence_stop_pending = False

    def load(self) -> None:
        self._connect_signals()
        self._refresh()
        self._update_calibration_progress()

    def has_active_operations(self) -> bool:
        return bool(self._active)

    def stop(self) -> None:
        if self._sequence_cancelled is not None:
            self._sequence_cancelled.set()
            self._model.stop_sequence_motion()
        for thread, _worker in list(self._active):
            thread.quit()
            if not thread.wait(1000):
                thread.wait()
        self._active.clear()

    def _connect_signals(self) -> None:
        self._view.add_tool_requested.connect(self._on_add)
        self._view.edit_tool_requested.connect(self._on_edit)
        self._view.remove_tool_requested.connect(self._on_remove)
        self._view.add_slot_requested.connect(self._on_add_slot)
        self._view.remove_slot_requested.connect(self._on_remove_slot)
        self._view.save_slots_requested.connect(self._on_save_slots)
        self._view.edit_slot_requested.connect(self._on_edit_slot)
        self._view.edit_geometry_requested.connect(self._on_edit_geometry)
        self._view.activate_tool_requested.connect(self._on_activate_tool)
        self._view.capture_reference_requested.connect(self._on_capture_reference)
        self._view.capture_candidate_requested.connect(self._on_capture_candidate)
        self._view.reset_calibration_requested.connect(self._on_reset_calibration)
        self._view.solve_calibration_requested.connect(self._on_solve_calibration)
        self._view.edit_sequences_requested.connect(self._on_edit_sequences)
        self._view.sequence_capture_requested.connect(self._on_capture_sequence_pose)
        self._view.sequence_save_requested.connect(self._on_save_sequences)
        self._view.sequence_cancel_requested.connect(self._on_cancel_sequences)
        self._view.sequence_reverse_requested.connect(self._on_reverse_pickup)
        self._view.sequence_execute_requested.connect(self._on_execute_sequence)
        self._view.sequence_stop_requested.connect(self._on_stop_sequence)

    def _refresh(self) -> None:
        tools = self._model.get_tools()
        slots = self._model.get_slots()
        self._view.set_tools(tools)
        self._view.set_slots(slots, tools)
        self._view.set_status(f"{len(tools)} tool(s), {len(slots)} slot(s)")

    def _on_add(self) -> None:
        dialog = _ToolDialog(parent=self._view)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        tool_id, name = dialog.get_values()
        ok, msg = self._model.add_tool(tool_id, name)
        self._view.set_status(msg)
        if ok:
            self._refresh()
        else:
            show_warning(self._view, "Add Tool", msg)

    def _on_edit(self, tool_id: int, current_name: str) -> None:
        dialog = _ToolDialog(tool_id=tool_id, name=current_name, parent=self._view)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        _, name = dialog.get_values()
        ok, msg = self._model.update_tool(tool_id, name)
        self._view.set_status(msg)
        if ok:
            self._refresh()
        else:
            show_warning(self._view, "Edit Tool", msg)

    def _on_remove(self, tool_id: int) -> None:
        if not ask_yes_no(self._view, "Remove Tool", f"Remove tool ID {tool_id}?"):
            return
        ok, msg = self._model.remove_tool(tool_id)
        self._view.set_status(msg)
        if ok:
            self._refresh()
        else:
            show_warning(self._view, "Remove Tool", msg)

    def _on_add_slot(self) -> None:
        tools = self._model.get_tools()
        if not tools:
            show_warning(self._view, "Add Slot", "Add at least one tool first.")
            return
        dialog = _SlotDialog(tools=tools, parent=self._view)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        slot_id, tool_id = dialog.get_values()
        ok, msg = self._model.add_slot(slot_id, tool_id)
        self._view.set_status(msg)
        if ok:
            self._refresh()
        else:
            show_warning(self._view, "Add Slot", msg)

    def _on_remove_slot(self, slot_id: int) -> None:
        if not ask_yes_no(self._view, "Remove Slot", f"Remove slot {slot_id}?"):
            return
        ok, msg = self._model.remove_slot(slot_id)
        self._view.set_status(msg)
        if ok:
            self._refresh()
        else:
            show_warning(self._view, "Remove Slot", msg)

    def _on_save_slots(self, assignments: list) -> None:
        errors = []
        for slot_id, tool_id in assignments:
            ok, msg = self._model.update_slot(slot_id, tool_id)
            if not ok:
                errors.append(msg)
        if errors:
            show_warning(self._view, "Save Slots", "\n".join(errors))
        else:
            self._view.set_status("Slots saved")
            self._refresh()

    def _on_edit_slot(self, slot_id: int, current_tool_id) -> None:
        tools = self._model.get_tools()
        if not tools:
            show_warning(self._view, "Edit Slot", "No tools defined.")
            return
        dialog = _SlotDialog(tools=tools, slot_id=slot_id, current_tool_id=current_tool_id, parent=self._view)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        _, tool_id = dialog.get_values()
        ok, msg = self._model.update_slot(slot_id, tool_id)
        self._view.set_status(msg)
        if ok:
            self._refresh()
        else:
            show_warning(self._view, "Edit Slot", msg)

    def _on_edit_geometry(self, tool_id: int) -> None:
        tool = next((item for item in self._model.get_tools() if item.id == tool_id), None)
        if tool is None:
            return
        if tool.reference_tool_id is None:
            show_warning(self._view, "Tool Offsets", "Backend geometry is unavailable. Reconnect and reload before editing.")
            return
        dialog = _ToolGeometryDialog(tool, parent=self._view)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
        transform, collision_profile = dialog.get_values()
        ok, msg = self._model.update_tool_geometry(tool_id, transform, collision_profile)
        self._view.set_status(msg)
        if ok:
            self._refresh()
        else:
            show_warning(self._view, "Tool Offsets", msg)

    def _on_capture_reference(self) -> None:
        self._run_blocking(
            self._model.capture_reference_contact, self._show_reference_result
        )

    def _on_capture_candidate(self) -> None:
        self._run_blocking(
            self._model.capture_tool_contact, self._show_candidate_result
        )

    def _on_reset_calibration(self) -> None:
        self._reference_captured = False
        self._candidate_samples = 0
        self._update_calibration_progress()

    def _on_solve_calibration(self, tool_id: int) -> None:
        self._run_blocking(
            lambda: self._model.solve_tool_calibration(tool_id),
            self._show_calibration_result,
        )

    def _on_activate_tool(self, tool_id: int) -> None:
        self._run_blocking(lambda: self._model.activate_tool(tool_id), self._show_simple_result)

    def _on_edit_sequences(self, slot_id: int) -> None:
        slot = next((item for item in self._model.get_slots() if item.id == slot_id), None)
        if slot is None:
            return
        self._teaching_slot_id = slot_id
        self._view.show_sequence_editor(slot)

    def _on_capture_sequence_pose(self, page: int, settings: dict) -> None:
        if self._teaching_slot_id is None or self._capture_page is not None or self._sequence_cancelled is not None or self._sequence_stop_pending:
            return
        self._capture_page = page
        self._capture_settings = dict(settings)
        self._view.set_sequence_capture_busy(True)
        self._run_blocking(self._model.get_current_motion_pose, self._show_sequence_pose)

    def _show_sequence_pose(self, result) -> None:
        page = self._capture_page
        self._capture_page = None
        self._view.set_sequence_capture_busy(False)
        ok, message = result[:2]
        if not ok:
            self._view.set_sequence_message(message)
            return
        self._view.append_sequence_step(page, {
            "kind": "motion", "label": "", "pose": list(result[2]),
            "motion_type": "linear", "velocity": self._capture_settings["velocity"],
            "acceleration": self._capture_settings["acceleration"], "blend_radius": 0.0,
        })

    def _on_save_sequences(self, pickup: list, dropoff: list) -> None:
        if self._teaching_slot_id is None or self._capture_page is not None or self._sequence_cancelled is not None or self._sequence_stop_pending:
            return
        ok, msg = self._model.update_slot_sequences(self._teaching_slot_id, pickup, dropoff)
        if not ok:
            self._view.set_sequence_message(msg)
            return
        self._on_cancel_sequences()
        self._refresh()
        self._view.set_status(msg)

    def _on_cancel_sequences(self) -> None:
        if self._capture_page is not None or self._sequence_cancelled is not None or self._sequence_stop_pending:
            return
        self._teaching_slot_id = None
        self._view.hide_sequence_editor()

    def _on_reverse_pickup(self, steps: list) -> None:
        if not steps:
            return
        self._view.set_sequence_dropoff(self._model.reverse_pickup(steps))

    def _on_execute_sequence(self, page: int, steps: list) -> None:
        if self._teaching_slot_id is None or self._capture_page is not None or self._sequence_cancelled is not None or self._sequence_stop_pending:
            return
        cancelled = Event()
        self._sequence_cancelled = cancelled
        slot_id = self._teaching_slot_id
        self._view.set_sequence_executing(True)
        self._view.set_sequence_message(self._sequence_t("Running pickup…") if page == 0 else self._sequence_t("Running drop-off…"))
        self._run_blocking(
            lambda: self._model.execute_sequence(slot_id, steps, cancelled),
            self._show_sequence_execution,
        )

    def _show_sequence_execution(self, result) -> None:
        self._sequence_cancelled = None
        if not self._sequence_stop_pending:
            self._view.set_sequence_executing(False)
        self._view.set_sequence_message(self._sequence_t(result[1]))

    def _on_stop_sequence(self) -> None:
        if self._sequence_cancelled is None or self._sequence_stop_pending:
            return
        self._sequence_cancelled.set()
        self._sequence_stop_pending = True
        self._run_blocking(self._model.stop_sequence_motion, self._show_sequence_stop)

    def _show_sequence_stop(self, result) -> None:
        self._sequence_stop_pending = False
        if self._sequence_cancelled is None:
            self._view.set_sequence_executing(False)
        if not result[0]:
            self._view.set_sequence_message(self._sequence_t(result[1]))

    @staticmethod
    def _sequence_t(text):
        from PyQt6.QtCore import QCoreApplication
        return QCoreApplication.translate("SequenceEditor", text) or text

    def _show_simple_result(self, result) -> None:
        ok, msg = result[:2]
        self._view.set_status(msg)
        if not ok:
            show_warning(self._view, "Tools & Magazine", msg)
        else:
            self._refresh()

    def _show_reference_result(self, result) -> None:
        ok, msg = result[:2]
        self._view.set_status(msg)
        if not ok:
            show_warning(self._view, "Tool Calibration", msg)
            return
        self._reference_captured = True
        self._candidate_samples = 0
        self._update_calibration_progress()

    def _show_candidate_result(self, result) -> None:
        ok, msg = result[:2]
        self._view.set_status(msg)
        if not ok:
            show_warning(self._view, "Tool Calibration", msg)
            return
        self._candidate_samples += 1
        self._update_calibration_progress()

    def _update_calibration_progress(self) -> None:
        self._view.set_calibration_progress(
            reference_captured=self._reference_captured,
            candidate_samples=self._candidate_samples,
        )

    def _show_calibration_result(self, result) -> None:
        ok, msg = result[:2]
        payload = result[2] if len(result) > 2 else {}
        if ok and payload.get("sample_count"):
            msg = (
                f"{msg}; samples={payload['sample_count']}, "
                f"spread={float(payload.get('max_spread_mm', 0.0)):.3f} mm"
            )
        self._view.set_status(msg)
        if not ok:
            show_warning(self._view, "Tool Calibration", msg)
        else:
            self._refresh()

    def _run_blocking(self, fn, on_done) -> None:
        thread = QThread(self._view)
        worker = _Worker(fn)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(on_done)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(partial(self._release_worker, thread, worker))
        self._active.append((thread, worker))
        thread.start()

    def _release_worker(self, thread, worker) -> None:
        try:
            self._active.remove((thread, worker))
        except ValueError:
            pass
        thread.deleteLater()


# ── Dialogs ───────────────────────────────────────────────────────────────────

class _ToolDialog(AppDialog):

    def __init__(self, tool_id=None, name: str = "", parent=None):
        title = "Edit Tool" if tool_id is not None else "Add Tool"
        super().__init__(title, min_width=360, parent=parent)
        self._fixed_id = tool_id

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(12)

        root.addWidget(_lbl("Tool ID"))
        self._id_spin = KeyboardNumberField()
        self._id_spin.setRange(0, 9999)
        self._id_spin.setCursor(Qt.CursorShape.PointingHandCursor)
        if tool_id is not None:
            self._id_spin.setValue(tool_id)
            self._id_spin.setEnabled(False)
        root.addWidget(self._id_spin)

        root.addWidget(_lbl("Name"))
        self._name_edit = KeyboardLineEdit(name)
        self._name_edit.setPlaceholderText("e.g. Single Gripper")
        self._name_edit.setStyleSheet(DIALOG_INPUT_STYLE)
        root.addWidget(self._name_edit)

        root.addStretch()
        ok_label = "Save" if tool_id is not None else "Add"
        root.addWidget(self._build_button_row(ok_label=ok_label))

    def get_values(self):
        return self._id_spin.value(), self._name_edit.text().strip()


class _SlotDialog(AppDialog):

    def __init__(self, tools, slot_id=None, current_tool_id=None, parent=None):
        title = "Edit Slot" if slot_id is not None else "Add Slot"
        super().__init__(title, min_width=360, parent=parent)

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(12)

        root.addWidget(_lbl("Slot ID"))
        self._slot_spin = KeyboardNumberField()
        self._slot_spin.setRange(0, 9999)
        self._slot_spin.setCursor(Qt.CursorShape.PointingHandCursor)
        if slot_id is not None:
            self._slot_spin.setValue(slot_id)
            self._slot_spin.setEnabled(False)
        root.addWidget(self._slot_spin)

        root.addWidget(_lbl("Tool"))
        self._tool_combo = QComboBox()
        self._tool_combo.setStyleSheet(DIALOG_COMBO_STYLE)
        self._tool_combo.addItem("— Unassigned —", None)
        for t in tools:
            self._tool_combo.addItem(f"{t.name}  (ID {t.id})", t.id)
        idx = self._tool_combo.findData(current_tool_id)
        self._tool_combo.setCurrentIndex(idx if idx >= 0 else 0)
        root.addWidget(self._tool_combo)

        root.addStretch()
        ok_label = "Save" if slot_id is not None else "Add"
        root.addWidget(self._build_button_row(ok_label=ok_label))

    def get_values(self):
        return self._slot_spin.value(), self._tool_combo.currentData()


class _ToolGeometryDialog(AppDialog):
    def __init__(self, tool, parent=None):
        super().__init__("Tool TCP Offsets", min_width=420, parent=parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)
        root.setSpacing(10)
        root.addWidget(_lbl(f"{tool.name} (Tool {tool.id}) — relative to calibration tool"))
        transform = list(getattr(tool, "relative_transform", [0, 0, 0, 0, 0, 0]))
        self._offsets = []
        for index, axis in enumerate(("X offset (mm)", "Y offset (mm)", "Z offset (mm)")):
            root.addWidget(_lbl(axis))
            field = KeyboardNumberField(decimal=True)
            field.setRange(-2000.0, 2000.0)
            field.setDecimals(3)
            field.setValue(float(transform[index]))
            self._offsets.append(field)
            root.addWidget(field)
        root.addWidget(_lbl("Collision profile"))
        self._collision = KeyboardLineEdit(str(getattr(tool, "collision_profile", "")))
        self._collision.setPlaceholderText("e.g. vacuum_gripper")
        self._collision.setStyleSheet(DIALOG_INPUT_STYLE)
        root.addWidget(self._collision)
        root.addWidget(self._build_button_row(ok_label="Save Offsets"))

    def get_values(self):
        xyz = [field.value() for field in self._offsets]
        return xyz + [0.0, 0.0, 0.0], self._collision.text().strip()
