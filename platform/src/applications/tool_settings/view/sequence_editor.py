"""Inline sequence teaching controls; robot access belongs to the controller."""

from copy import deepcopy

from PyQt6.QtCore import QCoreApplication, QEvent, QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView, QHBoxLayout, QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField

from pl_gui.settings.settings_view.styles import (
    ACTION_BTN_STYLE, APP_PHASE_TAB_STYLE, GHOST_BTN_STYLE, LABEL_STYLE,
)


class SequenceEditor(QWidget):
    capture_requested = pyqtSignal(int, dict)
    save_requested = pyqtSignal(list, list)
    cancel_requested = pyqtSignal()
    reverse_requested = pyqtSignal(list)
    execute_requested = pyqtSignal(int, list)
    stop_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._slot_id = None
        self._busy = False
        self._executing = False
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        self._title = QLabel()
        self._title.setStyleSheet(LABEL_STYLE)
        root.addWidget(self._title)
        self._instructions = QLabel()
        self._instructions.setWordWrap(True)
        root.addWidget(self._instructions)
        settings = QHBoxLayout()
        self._velocity_label = QLabel()
        self._acceleration_label = QLabel()
        self._velocity = self._motion_field()
        self._acceleration = self._motion_field()
        for widget in (self._velocity_label, self._velocity, self._acceleration_label, self._acceleration):
            settings.addWidget(widget)
        settings.addStretch()
        root.addLayout(settings)
        self._settings_hint = QLabel()
        self._settings_hint.setWordWrap(True)
        root.addWidget(self._settings_hint)
        self._velocity.valueChanged.connect(self._on_motion_settings_changed)
        self._acceleration.valueChanged.connect(self._on_motion_settings_changed)
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(APP_PHASE_TAB_STYLE)
        self._tables = []
        for _ in range(2):
            table = QTableWidget(0, 4)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            table.horizontalHeader().setStretchLastSection(True)
            table.setColumnWidth(0, 55)
            table.setColumnWidth(1, 110)
            table.setColumnWidth(2, 140)
            table.verticalHeader().hide()
            table.verticalHeader().setDefaultSectionSize(44)
            table.itemSelectionChanged.connect(self._on_selection_changed)
            self._tables.append(table)
            self._tabs.addTab(table, "")
        self._tabs.currentChanged.connect(self._on_selection_changed)
        root.addWidget(self._tabs, 1)
        actions = QHBoxLayout()
        self._reverse = self._button(False, self._on_reverse)
        self._run_pickup = self._button(True, self._on_run_pickup)
        self._run_dropoff = self._button(True, self._on_run_dropoff)
        self._stop = self._button(False, self._on_stop)
        self._stop.setEnabled(False)
        for button in (self._reverse, self._run_pickup, self._run_dropoff, self._stop):
            actions.addWidget(button)
        actions.addStretch()
        root.addLayout(actions)
        self._message = QLabel()
        self._message.setWordWrap(True)
        root.addWidget(self._message)
        row = QHBoxLayout()
        self._capture = self._button(True, self._on_capture)
        self._remove = self._button(False, self._on_remove)
        self._cancel = self._button(False, self._on_cancel)
        self._save = self._button(True, self._on_save)
        row.addWidget(self._capture)
        row.addWidget(self._remove)
        row.addWidget(self._cancel)
        row.addWidget(self._save)
        row.addStretch()
        root.addLayout(row)
        self.retranslateUi()

    @staticmethod
    def _motion_field():
        field = KeyboardNumberField(decimal=True)
        field.setRange(0.1, 100.0)
        field.setDecimals(1)
        field.setSingleStep(1.0)
        field.setSuffix(" %")
        field.setValue(10.0)
        field.setFixedWidth(220)
        return field

    def _on_selection_changed(self) -> None:
        table = self._tables[self._tabs.currentIndex()]
        row = table.currentRow()
        item = table.item(row, 3) if row >= 0 else None
        step = item.data(Qt.ItemDataRole.UserRole) if item is not None else None
        motion = step is None or step.get("kind", "motion") == "motion"
        self._velocity.setEnabled(motion and not self._busy)
        self._acceleration.setEnabled(motion and not self._busy)
        if step and motion:
            with QSignalBlocker(self._velocity), QSignalBlocker(self._acceleration):
                self._velocity.setValue(step.get("velocity", 10.0))
                self._acceleration.setValue(step.get("acceleration", 10.0))

    def _on_motion_settings_changed(self, _value) -> None:
        table = self._tables[self._tabs.currentIndex()]
        row = table.currentRow()
        if row < 0 or self._busy:
            return
        item = table.item(row, 3)
        step = item.data(Qt.ItemDataRole.UserRole)
        if step.get("kind", "motion") != "motion":
            return
        step.update(velocity=self._velocity.value(), acceleration=self._acceleration.value())
        item.setData(Qt.ItemDataRole.UserRole, step)
        self._render_step(item)

    @staticmethod
    def _button(primary, callback):
        button = QPushButton()
        button.setStyleSheet(ACTION_BTN_STYLE if primary else GHOST_BTN_STYLE)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(callback)
        return button

    def set_slot(self, slot) -> None:
        self._slot_id = slot.id
        with QSignalBlocker(self._velocity), QSignalBlocker(self._acceleration):
            self._velocity.setValue(10.0)
            self._acceleration.setValue(10.0)
        for page, steps in enumerate((slot.pickup_sequence, slot.dropoff_sequence)):
            self._tables[page].setRowCount(0)
            for step in steps:
                self.append_step(page, step.to_dict() if hasattr(step, "to_dict") else step)
        self._tabs.setCurrentIndex(0)
        self.set_message("")
        self.retranslateUi()

    def append_step(self, page: int, step: dict) -> None:
        table = self._tables[page]
        row = table.rowCount()
        table.insertRow(row)
        table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
        item = QTableWidgetItem()
        item.setData(Qt.ItemDataRole.UserRole, deepcopy(step))
        table.setItem(row, 3, item)
        self._render_step(item)
        table.selectRow(row)
        self._on_selection_changed()
        table.scrollToBottom()
        self.set_message("")

    def _render_step(self, item) -> None:
        step = item.data(Qt.ItemDataRole.UserRole)
        table = item.tableWidget()
        row = item.row()
        motion = step.get("kind", "motion") == "motion"
        table.setItem(row, 1, QTableWidgetItem(f"{step.get('velocity', 10.0):g}" if motion else "—"))
        table.setItem(row, 2, QTableWidgetItem(f"{step.get('acceleration', 10.0):g}" if motion else "—"))
        if step.get("kind", "motion") == "motion":
            item.setText(
                "X {:.3f}, Y {:.3f}, Z {:.3f} | RX {:.3f}, RY {:.3f}, RZ {:.3f}".format(*step["pose"])
            )
        else:
            # Keep existing explicit TCP changes/waits/confirmations intact.
            labels = {"attach": self._t("Attach tool"), "detach": self._t("Detach tool"),
                      "operator_confirm": self._t("Operator confirmation"), "wait": self._t("Wait")}
            item.setText(f"{labels.get(step['kind'], step['kind'])} | {step.get('label', '')}")

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        for widget in (self._tabs, self._capture, self._remove, self._save, self._cancel,
                       self._reverse, self._run_pickup, self._run_dropoff):
            widget.setEnabled(not busy)
        self._on_selection_changed()
        self._capture.setText(self._t("Capturing…") if busy and not self._executing else self._t("Capture position"))

    def set_executing(self, executing: bool) -> None:
        self._executing = executing
        self.set_busy(executing)
        self._capture.setText(self._t("Capture position"))
        self._stop.setEnabled(executing)

    def set_dropoff(self, steps: list) -> None:
        self._tables[1].setRowCount(0)
        for step in steps:
            self.append_step(1, step)
        self._tabs.setCurrentIndex(1)

    def _on_reverse(self) -> None:
        self.reverse_requested.emit(self._values(0))

    def _on_run_pickup(self) -> None:
        self.execute_requested.emit(0, self._values(0))

    def _on_run_dropoff(self) -> None:
        self.execute_requested.emit(1, self._values(1))

    def _on_stop(self) -> None:
        self.stop_requested.emit()

    def set_message(self, message: str) -> None:
        self._message.setText(message)

    def _values(self, page):
        table = self._tables[page]
        return [deepcopy(table.item(row, 3).data(Qt.ItemDataRole.UserRole))
                for row in range(table.rowCount())]

    def _on_capture(self) -> None:
        self.capture_requested.emit(self._tabs.currentIndex(), {
            "velocity": self._velocity.value(), "acceleration": self._acceleration.value(),
        })

    def _on_remove(self) -> None:
        table = self._tables[self._tabs.currentIndex()]
        row = table.currentRow()
        if row >= 0:
            table.removeRow(row)
            for index in range(table.rowCount()):
                table.item(index, 0).setText(str(index + 1))

    def _on_save(self) -> None:
        self.save_requested.emit(self._values(0), self._values(1))

    def _on_cancel(self) -> None:
        self.cancel_requested.emit()

    @staticmethod
    def _t(text):
        return QCoreApplication.translate("SequenceEditor", text) or text

    def retranslateUi(self) -> None:
        self._title.setText(self._t("Teach slot {slot_id}").format(slot_id=self._slot_id))
        self._instructions.setText(self._t(
            "Choose Pickup or Drop-off. Jog the robot to each position, stop, then capture it. Positions run in the order shown."
        ))
        self._velocity_label.setText(self._t("Velocity (%)"))
        self._acceleration_label.setText(self._t("Acceleration (%)"))
        self._settings_hint.setText(self._t("Values apply to the selected position and new captures. Save sequences to keep changes."))
        self._tabs.setTabText(0, self._t("Pickup"))
        self._tabs.setTabText(1, self._t("Drop-off"))
        for table in self._tables:
            table.setHorizontalHeaderLabels([
                self._t("Step"), self._t("Velocity (%)"), self._t("Acceleration (%)"),
                self._t("Position (mm / degrees) or saved action"),
            ])
            for row in range(table.rowCount()):
                self._render_step(table.item(row, 3))
        self._capture.setText(self._t("Capturing…") if self._busy and not self._executing else self._t("Capture position"))
        self._remove.setText(self._t("Remove selected"))
        self._cancel.setText(self._t("Cancel"))
        self._save.setText(self._t("Save sequences"))
        self._reverse.setText(self._t("Reverse pickup into drop-off"))
        self._run_pickup.setText(self._t("Run pickup"))
        self._run_dropoff.setText(self._t("Run drop-off"))
        self._stop.setText(self._t("Stop"))

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
