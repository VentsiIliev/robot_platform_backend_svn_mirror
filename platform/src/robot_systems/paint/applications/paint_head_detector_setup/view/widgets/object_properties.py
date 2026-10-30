"""Presentation-only editor fields using the platform's shared input widgets."""

from PyQt6.QtCore import QEvent, pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QLabel, QVBoxLayout, QWidget

from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit
from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    Landmark,
    LandmarkRole,
    LandmarkSupport,
)

from ...editor_contracts import EditorKind, EditorObject, ObjectPropertiesEdit
from .forms import action_button, translate


class ObjectPropertiesPanel(QWidget):
    apply_requested = pyqtSignal(object)
    remove_requested = pyqtSignal(object)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._object: EditorObject | None = None
        self._labels: list[tuple[QLabel, str]] = []
        layout = QVBoxLayout(self)
        self._heading = QLabel()
        layout.addWidget(self._heading)
        form = QFormLayout()
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self._name = KeyboardLineEdit()
        self._x, self._y, self._width, self._height = (
            KeyboardNumberField(button_width=32) for _ in range(4)
        )
        for number in (self._x, self._y, self._width, self._height):
            number.setRange(0, 1_000_000)
        self._width.setMinimum(2)
        self._height.setMinimum(2)
        self._threshold = KeyboardNumberField(decimal=True, button_width=32)
        self._threshold.setRange(0, 1)
        self._threshold.setDecimals(4)
        self._threshold.setSingleStep(0.01)
        self._rotation = KeyboardNumberField(decimal=True, button_width=32)
        self._rotation.setRange(0, 180)
        self._rotation.setDecimals(2)
        self._roles = QComboBox()
        for role in LandmarkRole:
            self._roles.addItem("", role)
        self._supports = QComboBox()
        for support in LandmarkSupport:
            self._supports.addItem("", support)
        self._required = QCheckBox()
        self._invariant = QCheckBox()
        self._limit_rotation = QCheckBox()
        self._limit_rotation.toggled.connect(self._on_rotation_limit_changed)
        for source, field in (
            ("Name", self._name),
            ("X (px)", self._x),
            ("Y (px)", self._y),
            ("Width (px)", self._width),
            ("Height (px)", self._height),
            ("Landmark role", self._roles),
            ("Support shape", self._supports),
            ("Match threshold", self._threshold),
            ("Required landmark", self._required),
            ("Orientation invariant", self._invariant),
            ("Limit template rotation", self._limit_rotation),
            ("Template rotation limit (degrees)", self._rotation),
        ):
            label = QLabel()
            label.setWordWrap(True)
            self._labels.append((label, source))
            form.addRow(label, field)
        layout.addLayout(form)
        self._apply = action_button("Apply changes", primary=True)
        self._remove = action_button("Remove object")
        self._apply.clicked.connect(self._on_apply)
        self._remove.clicked.connect(self._on_remove)
        layout.addWidget(self._apply)
        layout.addWidget(self._remove)
        layout.addStretch()
        self.set_object(None, None)
        self.retranslateUi()

    def set_object(self, value: EditorObject | None, landmark: Landmark | None) -> None:
        self._object = value
        self.setEnabled(value is not None)
        if value is None:
            self._name.clear()
            return
        region = value.region
        self._name.setText(value.name)
        self._name.setEnabled(value.target.kind in (EditorKind.EXCLUDED, EditorKind.LANDMARK))
        for field, coordinate in (
            (self._x, region.x),
            (self._y, region.y),
            (self._width, region.width),
            (self._height, region.height),
        ):
            field.setMaximum(max(1_000_000, coordinate))
            field.setValue(coordinate)
        fields = (
            self._roles,
            self._supports,
            self._threshold,
            self._required,
            self._invariant,
            self._limit_rotation,
            self._rotation,
        )
        for field in fields:
            field.setEnabled(landmark is not None)
        if landmark is not None:
            self._roles.setCurrentIndex(self._roles.findData(landmark.role))
            self._supports.setCurrentIndex(self._supports.findData(landmark.support))
            self._threshold.setValue(landmark.threshold)
            self._required.setChecked(landmark.required)
            self._invariant.setChecked(landmark.orientation_invariant)
            self._limit_rotation.setChecked(landmark.max_template_rotation is not None)
            self._rotation.setValue(landmark.max_template_rotation or 0)
            self._rotation.setEnabled(landmark.max_template_rotation is not None)

    def _on_rotation_limit_changed(self, checked: bool) -> None:
        self._rotation.setEnabled(checked)

    def _on_apply(self) -> None:
        if self._object is None:
            return
        self.apply_requested.emit(
            ObjectPropertiesEdit(
                self._object.target,
                self._name.text().strip(),
                int(self._x.value()),
                int(self._y.value()),
                int(self._width.value()),
                int(self._height.value()),
                float(self._threshold.value()),
                self._roles.currentData(),
                self._required.isChecked(),
                self._invariant.isChecked(),
                self._supports.currentData(),
                float(self._rotation.value()) if self._limit_rotation.isChecked() else None,
            )
        )

    def _on_remove(self) -> None:
        if self._object is not None:
            self.remove_requested.emit(self._object.target)

    def retranslateUi(self) -> None:
        self._heading.setText(translate("Object properties"))
        for label, source in self._labels:
            label.setText(translate(source))
        for index, source in enumerate(
            ("Present landmark", "Missing landmark", "Empty-mount landmark")
        ):
            self._roles.setItemText(index, translate(source))
        for index, source in enumerate(("Rectangle", "Circle")):
            self._supports.setItemText(index, translate(source))
        self._apply.setText(translate("Apply changes"))
        self._remove.setText(translate("Remove object"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
