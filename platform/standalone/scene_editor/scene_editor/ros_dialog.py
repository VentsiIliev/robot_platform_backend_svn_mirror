"""Connection options for the optional ROS reader."""
from dataclasses import replace
import json
import os
import logging
from pathlib import Path

from PyQt6.QtCore import QSettings
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QSpinBox,
    QLabel, QDialogButtonBox, QPushButton, QFileDialog, QMessageBox, QWidget,
)

from .ros_connection import RosOptions

logger = logging.getLogger(__name__)


def load_ros_options():
    settings = QSettings('Standalone Scene Editor', 'Scene Editor')
    try:
        values = json.loads(settings.value('ros_connection', '{}'))
        if 'marker_topics' in values:
            values['marker_topics'] = tuple(values['marker_topics'])
        return RosOptions(**values)
    except (TypeError, ValueError):
        return RosOptions()


class RosDialog(QDialog):
    def __init__(self, options=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Connect to ROS 2')
        self.resize(620, 570)
        self.options = options or RosOptions()
        layout = QVBoxLayout(self)
        note = QLabel('Live view reads the robot, planning scene and marker topics.\nCollision edits are sent only through explicit Add / Update / Remove actions.')
        note.setWordWrap(True)
        layout.addWidget(note)
        form = QFormLayout()
        self.fields = {}
        for key, title in [('fixed_frame', 'Fixed frame'), ('scene_topic', 'Planning scene topic'),
                           ('scene_service', 'Initial scene service'), ('apply_service', 'Apply planning scene service'), ('description_topic', 'Robot description topic'),
                           ('tf_topic', 'TF topic'), ('tf_static_topic', 'Static TF topic'),
                           ('preview_topic','Ordered-motion preview topic'),
                           ('marker_topics', 'MarkerArray topics (comma separated)'), ('python', 'ROS Python executable'),
                           ('ros_setup', 'ROS setup.bash (optional)'), ('workspace_setup', 'Workspace setup.bash (optional)')]:
            value = getattr(self.options, key)
            if key == 'marker_topics':
                value = ', '.join(value)
            if key == 'ros_setup' and not value and not os.environ.get('ROS_DISTRO'):
                candidate = Path('/opt/ros/jazzy/setup.bash')
                value = str(candidate) if candidate.exists() else ''
            field = QLineEdit(value)
            self.fields[key] = field
            if key in ('ros_setup', 'workspace_setup', 'python'):
                row = QWidget()
                row_layout = QHBoxLayout(row)
                row_layout.setContentsMargins(0, 0, 0, 0)
                browse = QPushButton('Browse…')
                browse.setProperty('field', key)
                browse.clicked.connect(self._browse)
                row_layout.addWidget(field, 1)
                row_layout.addWidget(browse)
                form.addRow(title, row)
            else:
                form.addRow(title, field)
        settings = QSettings('Standalone Scene Editor','Scene Editor')
        self.mesh_root = QLineEdit(str(settings.value('urdf/mesh_root','')))
        mesh_row = QWidget()
        mesh_layout = QHBoxLayout(mesh_row)
        mesh_layout.setContentsMargins(0,0,0,0)
        mesh_browse = QPushButton('Browse…')
        mesh_browse.clicked.connect(self._browse_mesh_root)
        mesh_layout.addWidget(self.mesh_root,1)
        mesh_layout.addWidget(mesh_browse)
        form.addRow('Mesh package / workspace folder (optional)',mesh_row)
        self.domain = QSpinBox()
        self.domain.setRange(-1, 232)
        self.domain.setSpecialValueText('Inherit ('+os.environ.get('ROS_DOMAIN_ID', '0')+')')
        self.domain.setValue(-1 if self.options.domain is None else self.options.domain)
        form.addRow('ROS domain ID', self.domain)
        layout.addLayout(form)
        note = QLabel('Leave setup paths blank to use the environment the editor was launched from.\nROS Python must match the selected ROS distribution. Local mesh packages must be available in that environment.')
        note.setWordWrap(True)
        layout.addWidget(note)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse(self):
        key = self.sender().property('field')
        path, _ = QFileDialog.getOpenFileName(self, 'Choose '+key.replace('_', ' '), self.fields[key].text())
        if path:
            self.fields[key].setText(path)

    def _browse_mesh_root(self):
        path = QFileDialog.getExistingDirectory(self,'Choose mesh package / ROS workspace folder',self.mesh_root.text())
        if path:
            self.mesh_root.setText(path)

    def accept(self):
        try:
            options = self.selected_options()
            mesh_root = self.mesh_root.text().strip()
            if mesh_root and not Path(mesh_root).is_dir():
                raise ValueError(f'Mesh folder does not exist: {mesh_root}')
        except ValueError as exc:
            logger.warning('ROS connection settings rejected: %s',exc)
            QMessageBox.warning(self, 'ROS 2 connection', str(exc))
            return
        from dataclasses import asdict
        QSettings('Standalone Scene Editor', 'Scene Editor').setValue('ros_connection', json.dumps(asdict(options)))
        QSettings('Standalone Scene Editor', 'Scene Editor').setValue('urdf/mesh_root',mesh_root)
        super().accept()

    def selected_options(self):
        values = {key: field.text().strip() for key, field in self.fields.items()}
        values['marker_topics'] = tuple(dict.fromkeys(value.strip() for value in values['marker_topics'].split(',') if value.strip()))
        values['domain'] = None if self.domain.value() < 0 else self.domain.value()
        if not values['fixed_frame'] or not values['python']:
            raise ValueError('A fixed frame and ROS Python executable are required.')
        for key in ('python', 'ros_setup', 'workspace_setup'):
            if values[key] and not Path(values[key]).is_file():
                raise ValueError(f'File does not exist: {values[key]}')
        for key in ('scene_topic', 'scene_service', 'apply_service', 'description_topic', 'tf_topic', 'tf_static_topic','preview_topic'):
            if not values[key]:
                raise ValueError('ROS topic and service names cannot be empty.')
        return replace(self.options, **values)
