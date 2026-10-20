"""Primitive dimensions and ROS identity, separate from local visual objects."""
import uuid

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QDoubleSpinBox,
    QLabel, QDialogButtonBox, QMessageBox,
)

from .collision import primitive_spec, frame_name, object_id
from .model import Pose


class CollisionDialog(QDialog):
    def __init__(self, editor_frame, obj=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit collision primitive' if obj else 'New collision primitive')
        self.resize(460, 560)
        self.obj, self.editor_frame = obj, editor_frame
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.identifier = QLineEdit(obj.collision['object_id'] if obj else 'scene_editor_'+uuid.uuid4().hex[:10])
        self.frame = QLineEdit(obj.collision['frame'] if obj else editor_frame)
        # Identity is stable. A new object is required to target a different ROS ID.
        self.identifier.setReadOnly(obj is not None)
        self.frame.setReadOnly(obj is not None)
        form.addRow('Collision object ID', self.identifier)
        form.addRow('Reference frame', self.frame)
        self.kind = QComboBox()
        self.kind.addItems(['box', 'cylinder', 'sphere'])
        form.addRow('Shape', self.kind)
        self.dimensions, self.labels = [], []
        for _ in range(3):
            field = QDoubleSpinBox()
            field.setRange(.001, 1e8)
            field.setDecimals(3)
            field.setValue(100)
            field.setSuffix(' mm')
            label = QLabel()
            self.dimensions.append(field)
            self.labels.append(label)
            form.addRow(label, field)
        self.pose_fields = {}
        for field_name, caption, suffix in [('translation', 'Position', ' mm'), ('rotation', 'Rotation', '°')]:
            controls = []
            for index, axis in enumerate('XYZ'):
                field = QDoubleSpinBox()
                field.setRange(-1e9, 1e9)
                field.setDecimals(3)
                field.setSuffix(suffix)
                field.setValue(getattr(obj.pose, field_name)[index] if obj else 0)
                controls.append(field)
                form.addRow(caption+' '+axis, field)
            self.pose_fields[field_name] = controls
        layout.addLayout(form)
        note = QLabel('Dimensions are full extents; cylinder uses radius and height along local Z. Position and rotation are relative to the reference frame. Preview is local until you choose Add or Update in ROS.')
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.kind.currentTextChanged.connect(self._shape_changed)
        self._shape_changed(self.kind.currentText())
        if obj:
            spec = obj.mesh.primitive
            self.kind.setCurrentText(spec['kind'])
            values = spec['size_mm'] if spec['kind'] == 'box' else ([spec['radius_mm'], spec['length_mm']] if spec['kind'] == 'cylinder' else [spec['radius_mm']])
            for control, value in zip(self.dimensions, values):
                control.setValue(value)

    def _shape_changed(self, kind):
        labels = {'box': ['Size X', 'Size Y', 'Size Z'], 'cylinder': ['Radius', 'Height'], 'sphere': ['Radius']}[kind]
        for index, (label, field) in enumerate(zip(self.labels, self.dimensions)):
            label.setVisible(index < len(labels))
            field.setVisible(index < len(labels))
            label.setText(labels[index] if index < len(labels) else '')

    def values(self):
        kind = self.kind.currentText()
        count = {'box':3, 'cylinder':2, 'sphere':1}[kind]
        spec = primitive_spec(kind, [field.value() for field in self.dimensions[:count]])
        pose = Pose(**{name:tuple(control.value() for control in controls) for name, controls in self.pose_fields.items()},
                    pivot=self.obj.pose.pivot if self.obj else (0,0,0))
        return object_id(self.identifier.text()), frame_name(self.frame.text()), spec, pose

    def accept(self):
        try:
            self.values()
        except ValueError as exc:
            QMessageBox.warning(self, 'Collision primitive', str(exc))
            return
        super().accept()
