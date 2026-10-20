"""Standalone desktop editor with an optional read-only ROS scene connection."""
from dataclasses import replace
from math import isclose
from pathlib import Path
import uuid

from PyQt6.QtCore import QObject, QRunnable, QThreadPool, QTimer, QSettings, QItemSelectionModel, Qt, QSignalBlocker, pyqtSignal
from PyQt6.QtGui import QAction, QActionGroup, QColor, QKeySequence, QUndoCommand, QUndoStack
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QListWidgetItem, QFormLayout, QDoubleSpinBox, QLineEdit, QPushButton,
    QLabel, QComboBox, QFileDialog, QMessageBox, QInputDialog, QColorDialog,
    QGroupBox, QScrollArea,
    QApplication,
    QSizePolicy,
)

from .geometry import STL_UNITS, read_stl, make_box, make_cylinder, mesh_from_primitive, export_stl
from .model import Scene, SceneObject, Pose, load_scene, save_scene, translated_poses
from .urdf import load_urdf
from .viewport import Viewport
from .ros_connection import RosConnection, collision_operation, resolved_robot_snapshot, RobotDescriptionUnavailable
from .ros_dialog import RosDialog, load_ros_options
from .collision import make_draft, request_for
from .collision_dialog import CollisionDialog
from .object_list import ObjectList, LOCKED_ROLE, LOCK_ENABLED_ROLE
from .styles import PALETTES, qt_palette, stylesheet, viewport_colors
from .surface_mating import mate_pose



class _Result(QObject):
    done = pyqtSignal(int, object, object)


class _Job(QRunnable):
    def __init__(self, job_id, function):
        super().__init__()
        self.job_id, self.function, self.signals = job_id, function, _Result()

    def run(self):
        try:
            result, error = self.function(), None
        except Exception as exc:
            result, error = None, str(exc) or type(exc).__name__
        self.signals.done.emit(self.job_id, result, error)


def _snapshot(scene):
    # Mesh buffers are immutable and shared, including through undo history.
    return [replace(obj) for obj in scene.objects]


class _Edit(QUndoCommand):
    def __init__(self, window, label, before, after, selection, merge_key=None):
        super().__init__(label)
        self.window, self.before, self.after = window, before, after
        self.selection, self.merge_key = selection, merge_key

    def id(self):
        return 1 if self.merge_key is not None else -1

    def mergeWith(self, other):
        if self.merge_key != other.merge_key:
            return False
        self.after = other.after
        return True

    def undo(self):
        self.window._restore(self.before, self.selection)

    def redo(self):
        self.window._restore(self.after, self.selection)


class EditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        QApplication.instance().setStyle('Fusion')
        self.resize(1400, 900)
        self.scene, self.project_path = Scene(), None
        self._refreshing, self._edit_session = False, 0
        self._origin_edit = None
        self._surface_mate = None
        self._jobs, self._job_counter, self._generation = {}, 0, 0
        self._closing = False
        self._ros = None
        self._live = self._live_received = False
        self._ros_options = load_ros_options()
        self._ros_details = 'No ROS connection.'
        self._collision_busy = False
        self._snap_source = None
        self._ros_timer = QTimer(self)
        self._ros_timer.setInterval(100)
        self._ros_timer.timeout.connect(self._poll_ros)
        self._pool = QThreadPool(self)
        # Serialize file operations to bound peak mesh memory and keep writes
        # to the same destination ordered, while the UI remains responsive.
        self._pool.setMaxThreadCount(1)
        self.history = QUndoStack(self)
        self.history.setUndoLimit(200)
        self.history.cleanChanged.connect(self._title)
        self.viewport = Viewport()
        self.viewport.scene = self.scene
        self.viewport.selected.connect(self._select)
        self.viewport.selection_changed.connect(self._select_many)
        self.viewport.pose_dragged.connect(self._drag_pose)
        self.viewport.group_dragged.connect(self._drag_group)
        self.viewport.error.connect(self._render_error)
        self.viewport.cancel_requested.connect(self.cancel_snap)
        self.viewport.mounting_point_picked.connect(self._mounting_point_picked)
        self.viewport.surface_picked.connect(self._surface_mate_picked)
        self._build_ui()
        from .workspace import Workspace
        self._workspace = Workspace(self)
        theme = QSettings('Standalone Scene Editor','Scene Editor').value('appearance/theme','light')
        self.set_theme(theme if theme in PALETTES else 'light', persist=False)
        self._busy_actions()
        self._title()
        self.statusBar().showMessage('Ready. Add an STL or open the example scene. All coordinates are in mm.')

    def _action(self, text, handler, shortcut=None):
        action = QAction(text, self)
        action.triggered.connect(handler)
        if shortcut:
            action.setShortcut(shortcut)
        return action

    def _build_ui(self):
        file_menu = self.menuBar().addMenu('File')
        self.new_action = self._action('New scene', self.new_scene, QKeySequence.StandardKey.New)
        self.open_action = self._action('Open scene…', self.open_scene, QKeySequence.StandardKey.Open)
        self.save_action = self._action('Save scene', self.save, QKeySequence.StandardKey.Save)
        self.save_as_action = self._action('Save scene as…', self.save_as, QKeySequence.StandardKey.SaveAs)
        file_menu.addActions([self.new_action, self.open_action, self.save_action, self.save_as_action])
        file_menu.addSeparator()
        self.import_action = self._action('Add STL…', self.import_stl)
        self.resolved_urdf_action = self._action('Load resolved URDF',self.load_resolved_urdf)
        self.resolved_urdf_action.setToolTip('Read the current robot_description from ROS once. Load static visuals at zero joint positions.')
        self.urdf_action = self._action('Import URDF file…', self.import_urdf)
        file_menu.addActions([self.import_action,self.resolved_urdf_action,self.urdf_action,
            self._action('Export selected STL…', self.export_selected)])
        file_menu.addSeparator()
        self.example_action = self._action('Example scene', self.example_scene)
        file_menu.addAction(self.example_action)
        edit = self.menuBar().addMenu('Edit')
        self.edit_menu = edit
        undo = self.history.createUndoAction(self, 'Undo')
        redo = self.history.createRedoAction(self, 'Redo')
        undo.setShortcuts(QKeySequence.StandardKey.Undo)
        redo.setShortcuts(QKeySequence.StandardKey.Redo)
        edit.addActions([undo, redo, self._action('Duplicate selected', self.duplicate),
                         self._action('Delete selected', self.delete)])
        self.lock_action = self._action('Lock selected', self.toggle_lock)
        self.snap_action = self._action('Snap origin to another object', self.begin_snap)
        self.surface_mate_action = self._action('Mate surfaces…',self.begin_surface_mate)
        self.surface_mate_action.setCheckable(True)
        self.cancel_snap_action = self._action('Cancel snap', self.cancel_snap, 'Escape')
        edit.addActions([self.lock_action,self.snap_action,self.surface_mate_action,self.cancel_snap_action])
        appearance = self.menuBar().addMenu('Appearance')
        self._theme_group = QActionGroup(self)
        self._theme_actions = {}
        for name in PALETTES:
            action = QAction(name.title(), self)
            action.setCheckable(True)
            action.setData(name)
            self._theme_group.addAction(action)
            appearance.addAction(action)
            self._theme_actions[name] = action
        self._theme_group.triggered.connect(self._theme_requested)
        toolbar = self.addToolBar('Scene')
        self.scene_toolbar = toolbar
        toolbar.setMovable(False)
        self.box_action = self._action('Add box', self.add_box)
        self.cylinder_action = self._action('Add cylinder', self.add_cylinder)
        toolbar.addActions([self.import_action, self.box_action, self.cylinder_action])
        toolbar.addSeparator()
        self.mode = QComboBox()
        self.mode.addItems(['View / orbit', 'Move object', 'Rotate object'])
        self.mode.currentIndexChanged.connect(self._mode_changed)
        toolbar.addWidget(self.mode)
        toolbar.addWidget(QLabel('  Axis: '))
        self.axis = QComboBox()
        self.axis.addItems(['X', 'Y', 'Z', 'Screen'])
        self.axis.setCurrentText('Z')
        self.axis.currentTextChanged.connect(self._axis_changed)
        toolbar.addWidget(self.axis)
        toolbar.addSeparator()
        toolbar.addActions([self._action('Frame scene', self.frame_scene),
                            self._action('Frame selected', self.frame_selected, 'F')])
        ros_menu = self.menuBar().addMenu('ROS 2')
        ros_toolbar = self.addToolBar('ROS 2')
        ros_toolbar.setMovable(False)
        self.insertToolBarBreak(ros_toolbar)
        self.connect_ros_action = self._action('Connect to ROS 2…', self.connect_ros)
        self.snapshot_action = self._action('Editable snapshot', self.editable_snapshot)
        self.disconnect_ros_action = self._action('Disconnect', self.disconnect_ros)
        self.snapshot_action.setEnabled(False)
        self.disconnect_ros_action.setEnabled(False)
        for action in (self.connect_ros_action, self.snapshot_action, self.disconnect_ros_action):
            ros_menu.addAction(action)
            ros_toolbar.addAction(action)
        ros_menu.addAction(self._action('Connection details', self.connection_details))
        ros_menu.addAction(self._action('ROS connection settings…', self.ros_settings))
        self.ros_status = QLabel('Offline — local scene')
        self.ros_status.setMargin(6)
        ros_toolbar.addWidget(self.ros_status)
        collision_menu = self.menuBar().addMenu('Collision objects')
        collision_toolbar = self.addToolBar('Collision objects')
        self.insertToolBarBreak(collision_toolbar)
        collision_toolbar.setMovable(False)
        self.new_collision_action = self._action('New collision…', self.new_collision)
        self.edit_collision_action = self._action('Edit dimensions…', self.edit_collision)
        self.add_collision_action = self._action('Add to ROS', self.add_collision_ros)
        self.update_collision_action = self._action('Update in ROS', self.update_collision_ros)
        self.remove_collision_action = self._action('Remove from ROS', self.remove_collision_ros)
        for action in (self.new_collision_action, self.edit_collision_action, self.add_collision_action,
                       self.update_collision_action, self.remove_collision_action):
            collision_menu.addAction(action)
            collision_toolbar.addAction(action)
        self.collision_status = QLabel('Local preview — apply explicitly')
        self.collision_status.setMargin(6)
        collision_toolbar.addWidget(self.collision_status)
        splitter = QSplitter()
        left = QWidget()
        left_layout = QVBoxLayout(left)
        object_title = QLabel('Scene objects')
        object_title.setObjectName('sectionTitle')
        left_layout.addWidget(object_title)
        self.objects = ObjectList()
        self.objects.lock_requested.connect(self._toggle_object_lock)
        self.objects.itemSelectionChanged.connect(self._list_selection)
        self.objects.itemChanged.connect(self._visibility_changed)
        left_layout.addWidget(self.objects)
        history_buttons = QHBoxLayout()
        self.undo_button = self._button('Undo', self.history.undo)
        self.redo_button = self._button('Redo', self.history.redo)
        self.undo_button.setToolTip('Undo the last local edit (Ctrl+Z)')
        self.redo_button.setToolTip('Redo the last undone local edit (Ctrl+Shift+Z)')
        history_buttons.addWidget(self.undo_button)
        history_buttons.addWidget(self.redo_button)
        left_layout.addLayout(history_buttons)
        self.reset_button = self._button('Reset transform', self._reset_pose)
        self.reset_button.setToolTip('Set selected object position, rotation and pivot to zero in its reference frame. Supports undo.')
        left_layout.addWidget(self.reset_button)
        self.history.canUndoChanged.connect(self._history_buttons_changed)
        self.history.canRedoChanged.connect(self._history_buttons_changed)
        self.snap_button = self._button('Snap origin to…', self.begin_snap)
        left_layout.addWidget(self.snap_button)
        self.duplicate_button = self._button('Duplicate', self.duplicate)
        self.delete_button = self._button('Delete', self.delete)
        left_layout.addWidget(self.duplicate_button)
        left_layout.addWidget(self.delete_button)
        splitter.addWidget(left)
        splitter.addWidget(self.viewport)
        scroll = QScrollArea()
        scroll.setMinimumWidth(360)
        scroll.setWidgetResizable(True)
        self.inspector = QWidget()
        self._inspector_buttons = []
        form = QVBoxLayout(self.inspector)
        inspector_title = QLabel('Selected object')
        inspector_title.setObjectName('sectionTitle')
        form.addWidget(inspector_title)
        self.selection_summary = QLabel()
        self.selection_summary.setWordWrap(True)
        form.addWidget(self.selection_summary)
        self.group_box = QGroupBox('Move selection — editor frame')
        group_form = QFormLayout(self.group_box)
        self.group_fields = []
        for axis in 'XYZ':
            control = QDoubleSpinBox()
            control.setRange(-1e8,1e8)
            control.setDecimals(3)
            control.setSuffix(' mm')
            control.setKeyboardTracking(False)
            control.setMinimumWidth(100)
            control.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Fixed)
            group_form.addRow('Δ '+axis,control)
            self.group_fields.append(control)
        self.group_move_button = self._button('Move selection',self._move_group_numeric)
        group_form.addRow(self.group_move_button)
        form.addWidget(self.group_box)
        self.group_box.hide()
        identity = QFormLayout()
        self.name = QLineEdit()
        self.name.editingFinished.connect(self._rename)
        identity.addRow('Name', self.name)
        form.addLayout(identity)
        self.size_box = QGroupBox('Size')
        size_form = QFormLayout(self.size_box)
        self.size_fields, self.size_labels = [], []
        for _ in range(3):
            label = QLabel()
            control = QDoubleSpinBox()
            control.setRange(.001, 1e8)
            control.setDecimals(3)
            control.setSingleStep(1)
            control.setSuffix(' mm')
            control.setKeyboardTracking(False)
            control.valueChanged.connect(self._resize_primitive)
            control.editingFinished.connect(self._finish_edit)
            size_form.addRow(label, control)
            self.size_fields.append(control)
            self.size_labels.append(label)
        form.addWidget(self.size_box)
        self.size_box.hide()
        self.pose_fields = {}
        self._pose_boxes = {}
        for group_name, field, suffix in [('Position offset', 'translation', ' mm'), ('Rotation', 'rotation', '°'), ('Pivot (local)', 'pivot', ' mm')]:
            box = QGroupBox(group_name)
            self._pose_boxes[field] = box
            rows = QFormLayout(box)
            controls = []
            for axis in 'XYZ':
                spin = QDoubleSpinBox()
                spin.setRange(-1e9, 1e9)
                spin.setDecimals(3)
                spin.setSingleStep(1)
                spin.setSuffix(suffix)
                spin.setKeyboardTracking(False)
                spin.setMinimumWidth(100)
                spin.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
                spin.valueChanged.connect(self._numeric_pose)
                spin.editingFinished.connect(self._finish_edit)
                controls.append(spin)
                rows.addRow(axis if field != 'rotation' else {'X':'X / roll', 'Y':'Y / pitch', 'Z':'Z / yaw'}[axis], spin)
            self.pose_fields[field] = controls
            form.addWidget(box)
        form.addWidget(self._inspector_button('Pivot at mesh center', self._pivot_center))
        form.addWidget(self._inspector_button('Pivot at source origin', self._pivot_origin))
        self.pose_note = QLabel('Pivot changes preserve the current pose.\nRotations use Rz × Ry × Rx.\nPosition is an offset from the source coordinates.')
        self.pose_note.setWordWrap(True)
        form.addWidget(self.pose_note)
        form.addWidget(self._inspector_button('Reset transform', self._reset_pose))
        self.color_button = self._inspector_button('Object color…', self._choose_color)
        form.addWidget(self.color_button)
        alpha = QFormLayout()
        self.opacity = QDoubleSpinBox()
        self.opacity.setRange(0.05, 1)
        self.opacity.setDecimals(2)
        self.opacity.setSingleStep(.05)
        self.opacity.setKeyboardTracking(False)
        self.opacity.valueChanged.connect(self._opacity_changed)
        self.opacity.editingFinished.connect(self._finish_edit)
        alpha.addRow('Opacity', self.opacity)
        form.addLayout(alpha)
        self.details = QLabel()
        self.details.setWordWrap(True)
        self.details.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        form.addWidget(self.details)
        form.addStretch()
        scroll.setWidget(self.inspector)
        splitter.addWidget(scroll)
        splitter.setSizes([250, 770, 380])
        splitter.setStretchFactor(1, 1)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(16, 10, 16, 16)
        page_title = QLabel('Scene Editor')
        page_title.setObjectName('pageTitle')
        content_layout.addWidget(page_title)
        content_layout.addWidget(splitter, 1)
        self.setCentralWidget(content)
        self.inspector.setEnabled(False)

    def _theme_requested(self, action):
        self.set_theme(action.data())

    def set_theme(self, name, *, persist=True):
        colors = PALETTES[name]
        self._theme_name = name
        QApplication.instance().setPalette(qt_palette(colors))
        self.setStyleSheet(stylesheet(colors))
        self.viewport.set_theme(viewport_colors(colors))
        self._theme_actions[name].setChecked(True)
        self.objects.viewport().update()
        if hasattr(self,'_workspace'):
            self._workspace.set_theme(colors)
        if persist:
            QSettings('Standalone Scene Editor','Scene Editor').setValue('appearance/theme',name)

    @staticmethod
    def _button(text, handler):
        button = QPushButton(text)
        button.setProperty('secondary', True)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.clicked.connect(handler)
        return button

    def _inspector_button(self, text, handler):
        button = self._button(text, handler)
        self._inspector_buttons.append(button)
        return button

    def _title(self, *args):
        if self._live:
            self.setWindowTitle('ROS 2 live view — Scene Editor')
            return
        name = self.project_path.name if self.project_path else 'Untitled'
        self.setWindowTitle(f'{name}{" *" if not self.history.isClean() else ""} — Scene Editor')

    def selected(self):
        return next((obj for obj in self.scene.objects if obj.id == self.viewport.selected_id), None)

    def selected_objects(self):
        ids = self.viewport.selection_ids()
        return [obj for obj in self.scene.objects if obj.id in ids]

    def _select(self, object_id):
        self._select_many({object_id} if object_id else set(),object_id)

    def _select_many(self, object_ids, primary=None):
        if self._surface_mate is not None:
            self.cancel_surface_mate()
        if self._origin_edit is not None and (set(object_ids) != {self._origin_edit['id']}):
            self.cancel_mounting_origin()
        if self._snap_source is not None:
            self._snap_target(primary)
            return
        valid = {obj.id for obj in self.scene.objects} & set(object_ids)
        primary = primary if primary in valid else next((obj.id for obj in self.scene.objects if obj.id in valid),None)
        changed = valid != self.viewport.selection_ids()
        self.viewport.set_selected(primary,valid)
        if changed:
            for field in self.group_fields:
                field.setValue(0)
        self._edit_session += 1
        self._refresh()

    def _list_selection(self):
        if not self._refreshing:
            ids = {item.data(Qt.ItemDataRole.UserRole) for item in self.objects.selectedItems()}
            current = self.objects.currentItem()
            self._select_many(ids,current.data(Qt.ItemDataRole.UserRole) if current else None)

    def _refresh(self):
        self._refreshing = True
        try:
            selected = self.selected()
            members = self.selected_objects()
            multi = len(members) > 1
            self.mode.model().item(2).setEnabled(not multi)
            if multi and self.mode.currentIndex() == 2:
                self.mode.setCurrentIndex(0)
            group_locked = any(obj.locked for obj in members)
            read_only = self._live or multi or bool(selected and selected.locked)
            with QSignalBlocker(self.objects):
                existing = [(self.objects.item(i).data(Qt.ItemDataRole.UserRole), self.objects.item(i).text()) for i in range(self.objects.count())]
                expected = [(obj.id, obj.name) for obj in self.scene.objects]
                if existing != expected:
                    self.objects.clear()
                    for obj in self.scene.objects:
                        item = QListWidgetItem(obj.name)
                        item.setData(Qt.ItemDataRole.UserRole, obj.id)
                        self.objects.addItem(item)
                for index, obj in enumerate(self.scene.objects):
                    item = self.objects.item(index)
                    item.setData(LOCKED_ROLE, obj.locked)
                    item.setData(LOCK_ENABLED_ROLE, not self._live and not self._jobs and not self._closing)
                    item.setToolTip('Locked — unlock to edit' if obj.locked else 'Unlocked')
                    font = item.font()
                    font.setItalic(obj.locked)
                    item.setFont(font)
                    flags = item.flags()
                    item.setFlags(flags & ~Qt.ItemFlag.ItemIsUserCheckable if self._live else flags | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Checked if obj.visible else Qt.CheckState.Unchecked)
                    item.setSelected(obj.id in self.viewport.selection_ids())
                    if selected and obj.id == selected.id:
                        self.objects.setCurrentItem(item,QItemSelectionModel.SelectionFlag.NoUpdate)
                if selected is None:
                    self.objects.setCurrentItem(None,QItemSelectionModel.SelectionFlag.NoUpdate)
            self.selection_summary.setVisible(multi)
            self.selection_summary.setText(f'{len(members)} selected. '+('Unlock or deselect locked objects to move the whole group.' if group_locked else 'Drag any highlighted object to move the group. Ctrl-click adds/removes; Shift selects ranges in the list.'))
            self.group_box.setVisible(multi)
            self.group_box.setEnabled(not self._live and not group_locked and not self._jobs)
            self.inspector.setEnabled(selected is not None)
            spec = selected.mesh.primitive if selected else None
            kind = spec.get('kind') if spec else None
            editable_size = kind in ('box', 'cylinder', 'sphere') and selected.unit_scale == (1.,1.,1.)
            self.size_box.setVisible(editable_size and not multi)
            if editable_size:
                labels = {'box':['Size X', 'Size Y', 'Size Z'], 'cylinder':['Radius', 'Height'], 'sphere':['Radius']}[kind]
                values = spec['size_mm'] if kind == 'box' else ([spec['radius_mm'],spec['length_mm']] if kind == 'cylinder' else [spec['radius_mm']])
                for index, (label, control) in enumerate(zip(self.size_labels, self.size_fields)):
                    label.setVisible(index < len(labels))
                    control.setVisible(index < len(labels))
                    control.setReadOnly(read_only)
                    if index < len(labels):
                        label.setText(labels[index])
                        with QSignalBlocker(control):
                            control.setValue(values[index])
            self.name.setReadOnly(read_only)
            self.opacity.setReadOnly(read_only)
            for controls in self.pose_fields.values():
                for control in controls:
                    control.setReadOnly(read_only)
            for button in self._inspector_buttons:
                button.setEnabled(not read_only)
            if selected:
                self._pose_boxes['translation'].setTitle('Position (mm) · '+selected.collision['frame'] if selected.collision else 'Position (mm)')
                self._pose_boxes['rotation'].setTitle('Rotation (°)')
                self._pose_boxes['pivot'].setTitle('Origin offset (mm)')
                self.pose_note.setText('Pose values use the collision reference frame; preview uses the captured frame transform. Rotations use Rz × Ry × Rx. Pivot changes preserve the pose.' if selected.collision else 'Pivot changes preserve the current pose.\nRotations use Rz × Ry × Rx.\nPosition is an offset from the source coordinates.')
                if self.name.text() != selected.name:
                    self.name.setText(selected.name)
                for field, controls in self.pose_fields.items():
                    for control, value in zip(controls, getattr(selected.pose, field)):
                        with QSignalBlocker(control):
                            control.setValue(value)
                with QSignalBlocker(self.opacity):
                    self.opacity.setValue(selected.color[3])
                source = str(selected.mesh.source) if selected.mesh.source else 'Built-in primitive'
                bounds = selected.world_bounds()
                dimensions = ' × '.join(f'{v:,.1f}' for v in bounds[1] - bounds[0])
                self.details.setText(f'{len(selected.mesh.vertices):,} triangles\nWorld bounds: {dimensions} mm\n{source}')
                if selected.collision:
                    metadata = selected.collision
                    self.details.setText(self.details.text()+f'\nCollision ID: {metadata["object_id"]}\nPose frame: {metadata["frame"]}\nPreview frame: {metadata["editor_frame"]}\nFrame transform captured when created; use a new snapshot if the scene moves.')
            else:
                self.name.clear()
                self.details.clear()
            self.viewport.update()
            self._collision_actions()
        finally:
            self._refreshing = False
        if hasattr(self,'_workspace'):
            self._workspace.sync()

    def _restore(self, objects, selection):
        self.cancel_snap()
        self.scene.objects = [replace(obj) for obj in objects]
        primary, ids = selection
        valid = {obj.id for obj in objects} & set(ids)
        self.viewport.set_selected(primary if primary in valid else next(iter(valid),None), valid)
        self._refresh()

    def _edit(self, label, after, selection=None, merge_key=None):
        if self._live:
            return
        if self._surface_mate is not None:
            self.cancel_surface_mate()
        state = (selection,(selection,)) if selection else (self.viewport.selected_id,tuple(self.viewport.selection_ids()))
        self.history.push(_Edit(self, label, _snapshot(self.scene), after,
                               state, merge_key))

    def _change(self, label, merge_key=None, **changes):
        obj = self.selected()
        if obj is None or self._refreshing or len(self.selected_objects()) > 1 or (obj.locked and set(changes) != {'locked'}):
            return
        updated = replace(obj, **changes)
        after = [updated if item.id == obj.id else replace(item) for item in self.scene.objects]
        self._edit(label, after, merge_key=merge_key)
        if obj.collision and not self._live:
            self.collision_status.setText('Local edits — choose Add or Update to apply')

    def _numeric_pose(self, value):
        obj = self.selected()
        if obj is None or self._refreshing:
            return
        # Editing pivot fields also preserves geometry, like the pivot presets.
        values = {field: tuple(control.value() for control in controls) for field, controls in self.pose_fields.items()}
        if self.sender() in self.pose_fields['pivot']:
            pose = obj.pose.with_pivot(values['pivot'])
        else:
            pose = Pose(**values)
        self._change('Change transform', ('numeric', obj.id, self._edit_session), pose=pose)

    def _resize_primitive(self, value):
        obj = self.selected()
        if self._refreshing or self._live or obj is None or obj.mesh.primitive is None:
            return
        from .collision import primitive_spec
        kind = obj.mesh.primitive['kind']
        if kind not in ('box', 'cylinder', 'sphere') or obj.unit_scale != (1.,1.,1.):
            return
        count = {'box':3, 'cylinder':2, 'sphere':1}[kind]
        spec = primitive_spec(kind, [control.value() for control in self.size_fields[:count]])
        if spec != obj.mesh.primitive:
            self._change('Resize primitive', ('size', obj.id, self._edit_session), mesh=mesh_from_primitive(spec))

    @staticmethod
    def has_editable_stl_units(obj):
        """Source-unit correction applies to local STL meshes, not ROS geometry."""
        return bool(obj and obj.mesh.source and obj.mesh.source.suffix.lower() == '.stl'
                    and obj.mesh.primitive is None and obj.collision is None
                    and not obj.id.startswith(('robot/','world/','attached/','marker/')))

    def change_stl_units(self, unit):
        obj = self.selected()
        if (self._refreshing or self._live or self._jobs or self._closing
                or not self.has_editable_stl_units(obj) or obj.locked
                or len(self.selected_objects()) != 1 or unit not in STL_UNITS):
            return
        scale = (STL_UNITS[unit],)*3
        if obj.unit_scale != scale:
            origin_mm = tuple(a*b for a,b in zip(obj.origin_source,obj.unit_scale))
            pose = obj.pose
            if all(isclose(a,b,rel_tol=1e-12,abs_tol=1e-9) for a,b in zip(pose.pivot,origin_mm)):
                pose = pose.with_pivot(tuple(a*b for a,b in zip(obj.origin_source,scale)))
            self._change('Change STL source units',unit_scale=scale,pose=pose)
            self.viewport.fit(selected=True)

    def set_mounting_origin(self, point):
        obj = self.selected()
        if (self._refreshing or self._live or self._jobs or self._closing
                or not self.has_editable_stl_units(obj) or obj.locked
                or len(self.selected_objects()) != 1):
            return
        updated = obj.with_origin_mm(point)
        if updated.origin_source == obj.origin_source and updated.pose == obj.pose:
            self.cancel_mounting_origin()
            return
        after = [updated if item.id == obj.id else replace(item) for item in self.scene.objects]
        self._edit('Set mounting origin',after)
        self.statusBar().showMessage('Mounting origin changed. Geometry kept in place. Snap origin to… aligns this mounting point.',7000)

    def begin_mounting_origin_pick(self):
        obj = self.selected()
        if (self._live or self._jobs or self._closing or not self.has_editable_stl_units(obj)
                or obj.locked or not obj.visible or len(self.selected_objects()) != 1):
            return
        self.cancel_snap()
        self._origin_edit = dict(id=obj.id,point=tuple(a*b for a,b in zip(obj.origin_source,obj.unit_scale)),picked=False)
        self.viewport.origin_pick_id = obj.id
        self.viewport._drag = None
        self.viewport.setFocus()
        self.statusBar().showMessage('Click the mounting point on the selected mesh. Right-drag to orbit; Escape cancels.')
        self._workspace.sync()

    def _mounting_point_picked(self, world):
        obj = self.selected()
        if self.viewport.origin_pick_id is None or obj is None:
            return
        import numpy as np
        local = np.linalg.solve(obj.matrix(),np.r_[world,1.])[:3]*obj.unit_scale
        self.preview_mounting_origin(tuple(local))

    def preview_mounting_origin(self, point):
        obj = self.selected()
        if (self._refreshing or self._live or self._jobs or self._closing or not self.has_editable_stl_units(obj)
                or obj.locked or len(self.selected_objects()) != 1):
            return
        # Validate through the same model operation used at confirmation.
        candidate = obj.with_origin_mm(point)
        self.cancel_surface_mate()
        self._origin_edit = dict(id=obj.id,point=tuple(point),picked=True)
        self.viewport.origin_preview = candidate.world_origin()
        self.viewport.update()
        self._workspace.sync()

    def cancel_mounting_origin(self):
        self._origin_edit = None
        self.viewport.origin_preview = None
        self.viewport.origin_pick_id = None
        self.viewport.update()
        if hasattr(self,'_workspace'):
            self._workspace.sync()

    def mounting_origin_preset(self, name):
        obj = self.selected()
        if obj is None:
            return (0.,0.,0.)
        if name == 'STL origin':
            return (0.,0.,0.)
        if name == 'Current pivot':
            return obj.pose.pivot
        low,high = obj.mesh.bounds*obj.unit_scale
        center = (low+high)/2
        if name == 'Bottom center':
            center[2] = low[2]
        elif name == 'Top center':
            center[2] = high[2]
        return tuple(center)

    def _finish_edit(self):
        self._edit_session += 1

    def _drag_pose(self, object_id, pose, gesture):
        if self.viewport.selected_id == object_id:
            self._change('Drag transform', ('drag', object_id, gesture), pose=pose)

    def _drag_group(self, poses, gesture):
        members = self.selected_objects()
        if self._live or self._jobs or len(members) < 2 or any(obj.locked for obj in members) or set(poses) != {obj.id for obj in members}:
            return
        self._apply_group_poses(poses,('group-drag',tuple(sorted(poses)),gesture))

    def _apply_group_poses(self, poses, merge_key=None):
        after = [replace(obj,pose=poses[obj.id]) if obj.id in poses else replace(obj) for obj in self.scene.objects]
        self._edit('Move selection',after,merge_key=merge_key)
        self.collision_status.setText('Local group move — apply collision updates individually')

    def _move_group_numeric(self):
        members = self.selected_objects()
        if self._live or self._jobs or len(members) < 2 or any(obj.locked for obj in members):
            return
        delta = tuple(field.value() for field in self.group_fields)
        if not any(delta):
            return
        self._apply_group_poses(translated_poses(members,delta))
        for field in self.group_fields:
            field.setValue(0)

    def _rename(self):
        obj = self.selected()
        if obj and self.name.text().strip() and self.name.text().strip() != obj.name:
            self._change('Rename object', name=self.name.text().strip())

    def _visibility_changed(self, item):
        if self._refreshing:
            return
        object_id = item.data(Qt.ItemDataRole.UserRole)
        after = [replace(obj, visible=item.checkState() == Qt.CheckState.Checked) if obj.id == object_id else replace(obj) for obj in self.scene.objects]
        self._edit('Change visibility', after)

    def _pivot_center(self):
        obj = self.selected()
        if obj:
            self._change('Center pivot', pose=obj.pose.with_pivot(obj.local_center()))

    def _pivot_origin(self):
        obj = self.selected()
        if obj:
            self._change('Reset pivot', pose=obj.pose.with_pivot((0, 0, 0)))

    def _reset_pose(self):
        obj = self.selected()
        if obj is not None and obj.pose != Pose():
            self._change('Reset transform', pose=Pose())

    def _choose_color(self):
        obj = self.selected()
        if obj:
            color = QColorDialog.getColor(QColor.fromRgbF(*obj.color), self, 'Object color')
            if color.isValid():
                self._change('Change color', color=(*color.getRgbF()[:3], obj.color[3]))

    def _opacity_changed(self, value):
        obj = self.selected()
        if obj and not self._refreshing:
            self._change('Change opacity', ('opacity', obj.id, self._edit_session), color=(*obj.color[:3], value))

    def _mode_changed(self, index):
        self.cancel_snap()
        self.viewport.mode = 'view' if self._live else ('view', 'move', 'rotate')[index]

    def activate_edit_tool(self,index):
        """Exit pending picks even when activating the already-selected tool."""
        self.cancel_snap()
        self.mode.setCurrentIndex(index)
        self.viewport.setFocus()

    def _axis_changed(self, axis):
        self.viewport.axis = axis

    def frame_scene(self):
        self.viewport.fit()

    def frame_selected(self):
        self.viewport.fit(selected=True)

    def _add(self, objects, label='Add objects'):
        if not objects:
            return
        was_empty = not self.scene.objects
        self._edit(label, _snapshot(self.scene) + objects, selection=objects[0].id)
        if was_empty:
            self.viewport.fit()

    def duplicate(self):
        obj = self.selected()
        if obj and len(self.selected_objects()) == 1:
            metadata = dict(obj.collision, object_id='scene_editor_'+uuid.uuid4().hex[:10]) if obj.collision else None
            self._add([replace(obj, id=uuid.uuid4().hex, name=obj.name + ' copy', collision=metadata, locked=False)], 'Duplicate object')

    def delete(self):
        obj = self.selected()
        if obj and not obj.locked and len(self.selected_objects()) == 1:
            self._edit('Delete object', [replace(item) for item in self.scene.objects if item.id != obj.id])

    def add_box(self):
        text, ok = QInputDialog.getText(self, 'Add box', 'Size X Y Z in mm:', text='500 300 20')
        if ok:
            try:
                size = tuple(float(v) for v in text.split())
                self._add([SceneObject('Box', make_box(size))])
            except Exception as exc:
                self._error(str(exc))

    def add_cylinder(self):
        text, ok = QInputDialog.getText(self, 'Add cylinder', 'Radius and length in mm:', text='20 150')
        if ok:
            try:
                radius, length = (float(v) for v in text.split())
                self._add([SceneObject('Cylinder', make_cylinder(radius, length))])
            except Exception as exc:
                self._error(str(exc))

    def _submit(self, label, function, callback, changes_scene=False):
        if self._surface_mate is not None:
            self.cancel_surface_mate()
        self._job_counter += 1
        job = _Job(self._job_counter, function)
        self._jobs[self._job_counter] = (job, callback, self._generation, changes_scene)
        job.signals.done.connect(self._job_done)
        self._pool.start(job)
        self.statusBar().showMessage(label)
        self._busy_actions()

    def _busy_actions(self):
        self.viewport.editable = not self._live
        loading = any(row[3] for row in self._jobs.values())
        for action in (self.import_action,self.urdf_action,self.resolved_urdf_action,self.open_action,self.new_action,self.example_action):
            action.setEnabled(not loading and not self._live)
        self.centralWidget().setEnabled(not loading)
        self.scene_toolbar.setEnabled(not loading)
        self.edit_menu.setEnabled(not loading and not self._live)
        for control in (self.box_action, self.cylinder_action, self.mode, self.axis,
                        self.duplicate_button, self.delete_button, self.save_action, self.save_as_action):
            control.setEnabled(not loading and not self._live)
        self.connect_ros_action.setEnabled(not loading and self._ros is None and not self._closing)
        self.snapshot_action.setEnabled(self._live and self._live_received)
        self.disconnect_ros_action.setEnabled(self._ros is not None)
        self._collision_actions()
        if hasattr(self,'_workspace'):
            self._workspace.sync()

    def _collision_actions(self):
        if not hasattr(self, 'new_collision_action'):
            return
        available = not self._jobs and not self._collision_busy and not self._closing
        self.surface_mate_action.setEnabled(available and not self._live and sum(obj.visible for obj in self.scene.objects) >= 2)
        selected = self.selected()
        single = len(self.selected_objects()) == 1
        editable = available and not self._live and selected is not None and not selected.locked and single
        self.duplicate_button.setEnabled(available and not self._live and single)
        self.lock_action.setEnabled(available and not self._live and selected is not None and single)
        self.lock_action.setText('Unlock selected' if selected and selected.locked else 'Lock selected')
        self.snap_action.setEnabled(editable and len(self.scene.objects) > 1)
        self.snap_button.setEnabled(self.snap_action.isEnabled())
        self.snap_button.setText('Cancel snap (Esc)' if self._snap_source else 'Snap origin to…')
        self.cancel_snap_action.setEnabled(self._snap_source is not None)
        self.delete_button.setEnabled(editable)
        self.reset_button.setEnabled(editable and selected.pose != Pose())
        self._history_buttons_changed()
        authored = editable and selected.collision is not None
        self.new_collision_action.setEnabled(available and not self._live)
        for action in (self.edit_collision_action, self.add_collision_action, self.update_collision_action, self.remove_collision_action):
            action.setEnabled(authored)

    def _history_buttons_changed(self, *args):
        if not hasattr(self, 'undo_button'):
            return
        available = not self._live and not self._jobs and not self._closing
        self.undo_button.setEnabled(available and self.history.canUndo())
        self.redo_button.setEnabled(available and self.history.canRedo())

    def toggle_lock(self):
        obj = self.selected()
        if obj is not None:
            self._toggle_object_lock(obj.id)

    def _toggle_object_lock(self, object_id):
        obj = next((item for item in self.scene.objects if item.id == object_id), None)
        if self._live or self._jobs or self._closing or obj is None:
            return
        self.cancel_snap()
        after = [replace(item, locked=not item.locked) if item.id == obj.id else replace(item) for item in self.scene.objects]
        self._edit('Unlock object' if obj.locked else 'Lock object', after)

    def begin_snap(self):
        self.cancel_surface_mate()
        self.cancel_mounting_origin()
        if self._snap_source is not None:
            self.cancel_snap()
            return
        obj = self.selected()
        if self._live or self._jobs or obj is None or obj.locked or len(self.selected_objects()) != 1 or len(self.scene.objects) < 2:
            return
        self._snap_source = obj.id
        self.viewport.selection_only = True
        self.statusBar().showMessage(f'Snap {obj.name}: click the target object in the view or list. Escape cancels.')
        self._collision_actions()

    def cancel_snap(self):
        self.cancel_surface_mate()
        self.cancel_mounting_origin()
        active = self._snap_source is not None
        self._snap_source = None
        self.viewport.selection_only = False
        if active:
            self.statusBar().showMessage('Origin snap cancelled.', 4000)
        self._collision_actions()

    def begin_surface_mate(self):
        if self._live or self._jobs or self._closing or sum(obj.visible for obj in self.scene.objects) < 2:
            return
        self.cancel_snap()
        self._surface_mate = dict(source=None,target=None,pose=None,offset=0.,flip=False,twist=0.)
        self.viewport.surface_pick_enabled = True
        self.viewport._drag = None
        self.viewport.setFocus()
        self.statusBar().showMessage('Mate surfaces: click a face on the object to move. Escape cancels.')
        self._workspace.show_surface_mate()
        self._workspace.sync()

    def cancel_surface_mate(self):
        active = self._surface_mate is not None or self.viewport.surface_pick_enabled or self.viewport._surface_press is not None
        self._surface_mate = None
        self.viewport.surface_pick_enabled = False
        self.viewport._surface_press = None
        if active:
            self.viewport._drag = None
        self.viewport.surface_hits = []
        self.viewport.surface_hover = None
        self.viewport._surface_hover_timer.stop()
        self.viewport.pose_preview = {}
        self.viewport.update()
        if hasattr(self,'_workspace'):
            self._workspace.sync()

    def _surface_mate_picked(self,hit):
        state = self._surface_mate
        if state is None or self._live or self._jobs or state['pose'] is not None:
            return
        obj = next((obj for obj in self.scene.objects if obj.id == hit.object_id),None)
        if obj is None or not obj.visible:
            return
        if state['source'] is None or state['source'].object_id == hit.object_id:
            if obj.locked:
                self.statusBar().showMessage('Unlock the moving object first. The target object may stay locked.')
                return
            state['source'] = hit
            self.viewport.set_selected(obj.id)
            self.viewport.surface_hits = [hit]
            self.statusBar().showMessage('Source face selected. Drag to orbit, then click the target face. Middle-drag pans; Escape cancels.')
            self._refresh()
            self._workspace.show_surface_mate()
        else:
            state['target'] = hit
            self.update_surface_mate(state['offset'],state['flip'],state['twist'])
        self.viewport.update()
        self._workspace.sync()

    def update_surface_mate(self,offset,flip,twist):
        state = self._surface_mate
        if state is None:
            return
        state.update(offset=offset,flip=flip,twist=twist)
        if state['source'] is None or state['target'] is None:
            return
        source = next((obj for obj in self.scene.objects if obj.id == state['source'].object_id),None)
        target = next((obj for obj in self.scene.objects if obj.id == state['target'].object_id),None)
        if source is None or target is None or source.locked or self._live or self._jobs:
            self.cancel_surface_mate()
            return
        try:
            state['pose'] = mate_pose(source,state['source'],target,state['target'],offset,flip,twist)
        except ValueError as exc:
            self.cancel_surface_mate()
            self.statusBar().showMessage(str(exc),7000)
            return
        self.viewport.pose_preview = {source.id:state['pose']}
        self.viewport.surface_hits = [state['source'],state['target']]
        self.statusBar().showMessage('Surface mate preview. Adjust offset / flip / rotation, then Apply. Escape cancels.')
        self.viewport.update()
        self._workspace.sync()

    def apply_surface_mate(self):
        state = self._surface_mate
        if state is None or state['pose'] is None or self._live or self._jobs:
            return
        source = next((obj for obj in self.scene.objects if obj.id == state['source'].object_id),None)
        if source is None or source.locked:
            self.cancel_surface_mate()
            return
        pose = state['pose']
        self.viewport.set_selected(source.id)
        self.cancel_surface_mate()
        self._change('Mate surfaces',pose=pose)
        self.statusBar().showMessage('Surfaces mated locally. Undo restores the original placement.',7000)

    def _snap_target(self, object_id):
        source = next((obj for obj in self.scene.objects if obj.id == self._snap_source), None)
        target = next((obj for obj in self.scene.objects if obj.id == object_id), None)
        if source is None or source.locked or self._live:
            self.cancel_snap()
            return
        self.viewport.set_selected(source.id)
        if target is None or target.id == source.id:
            self._refresh()
            return
        pose = source.pose_snapped_to(target)
        self.cancel_snap()
        self._change('Snap origin to '+target.name, pose=pose)
        self.statusBar().showMessage(f'{source.name} origin snapped to {target.name}. Rotation preserved.', 7000)

    def ros_settings(self):
        if self._ros is not None or self._jobs:
            self.statusBar().showMessage('Disconnect and finish file operations before changing ROS settings.', 6000)
            return
        dialog = RosDialog(self._ros_options, self)
        if dialog.exec():
            self._ros_options = dialog.selected_options()

    def new_collision(self, *, shape=None):
        if self._live or self._jobs:
            return
        editor_frame = self.scene.reference_frame or self._ros_options.fixed_frame
        dialog = CollisionDialog(editor_frame, parent=self)
        if shape in ('box','cylinder','sphere'):
            dialog.kind.setCurrentText(shape)
        if not dialog.exec():
            return
        identifier, frame, spec, pose = dialog.values()
        if any(obj.collision and obj.collision['object_id'] == identifier for obj in self.scene.objects):
            self._error('That collision ID already exists in this local scene. Choose a unique ID.')
            return
        def finish(matrix):
            self.scene.reference_frame = editor_frame
            self._add([make_draft(identifier, frame, editor_frame, spec, pose, matrix)], 'Add collision draft')
            self.collision_status.setText('Local draft — not applied to ROS')
        if frame == editor_frame:
            import numpy as np
            finish(np.eye(4).tolist())
        else:
            options = self._ros_options
            request = dict(operation='resolve', frame=frame, editor_frame=editor_frame)
            self._submit('Resolving collision preview frame…', lambda: collision_operation(options, request),
                         lambda result: finish(result['frame_to_editor']), True)

    def edit_collision(self):
        obj = self.selected()
        if self._live or obj is None or obj.locked or obj.collision is None or len(self.selected_objects()) != 1:
            return
        dialog = CollisionDialog(obj.collision['editor_frame'], obj, self)
        if dialog.exec():
            _, _, spec, pose = dialog.values()
            self._change('Edit collision primitive', mesh=mesh_from_primitive(spec), pose=pose)
            self.collision_status.setText('Local edits — choose Add or Update to apply')

    def add_collision_ros(self):
        self._apply_collision('add')

    def update_collision_ros(self):
        self._apply_collision('update')

    def remove_collision_ros(self):
        self._apply_collision('remove')

    def _apply_collision(self, operation):
        obj = self.selected()
        if self._live or self._jobs or self._collision_busy or obj is None or obj.locked or len(self.selected_objects()) != 1:
            return
        try:
            request = request_for(obj, operation)
        except ValueError as exc:
            self._error(str(exc))
            return
        options = self._ros_options
        self._collision_busy = True
        self.collision_status.setText(f'{operation.title()} pending: {request["object_id"]}')
        self._submit('Applying explicit collision operation…', lambda: collision_operation(options, request),
                     self._collision_applied, True)

    def _collision_applied(self, result):
        self.collision_status.setText(result['message'])
        self.collision_status.setToolTip(result['message'])

    def _job_done(self, job_id, result, error):
        row = self._jobs.pop(job_id, None)
        collision_request = self._collision_busy
        self._collision_busy = False
        if collision_request and error:
            self.collision_status.setText('Collision operation failed — local draft retained')
            self.statusBar().showMessage('Collision operation failed. '+str(error)[:150])
        self._busy_actions()
        if row and not self._closing:
            _, callback, generation, _ = row
            if generation == self._generation:
                if error:
                    self._error(error)
                else:
                    callback(result)
                    self.statusBar().showMessage('Done.', 6000)
        if self._closing and not self._jobs and self._ros is None:
            self.close()

    def connect_ros(self):
        if self._ros is not None or self._jobs or not self._confirm_discard():
            return
        dialog = RosDialog(self._ros_options, self)
        if dialog.exec():
            try:
                self.begin_ros(dialog.selected_options())
            except Exception as exc:
                self._error(str(exc))

    def begin_ros(self, options):
        """Begin an independent reader; callers must resolve local unsaved edits first."""
        if self._ros is not None or self._jobs:
            raise RuntimeError('Finish the current connection or file operation first.')
        self._ros_options = options
        self.cancel_snap()
        self._live, self._live_received = True, False
        self._ros = RosConnection(options, self)
        self._ros.status.connect(self._ros_status_changed)
        self._ros.stopped.connect(self._ros_stopped)
        self.mode.setCurrentIndex(0)
        self.ros_status.setText('Connecting to ROS 2…')
        self._ros_details = 'Waiting for the ROS helper to start.'
        self._busy_actions()
        self._refresh()
        self._title()
        self._ros.start()
        self._ros_timer.start()

    def _poll_ros(self):
        if self._ros is None or not self._live:
            return
        scene = self._ros.take_latest()
        if scene is None or (not scene.objects and not self._live_received):
            return
        selection = self.viewport.selected_id
        selection_ids = self.viewport.selection_ids()
        previous_ids = {obj.id for obj in self.scene.objects}
        if not self._live_received:
            self.project_path = None
            self.history.clear()
        self._live_received = True
        self.scene = scene
        self.viewport.scene = scene
        valid = {obj.id for obj in scene.objects} & selection_ids
        self.viewport.set_selected(selection if selection in valid else next(iter(valid),None), valid)
        if previous_ids != {obj.id for obj in scene.objects}:
            self.viewport.fit()
        self._refresh()
        self._busy_actions()

    def _ros_status_changed(self, packet):
        if not self._live or self._closing:
            return
        kind = packet.get('type')
        if kind == 'ready':
            self.ros_status.setText(f'ROS domain {packet.get("domain")} — waiting for scene data…')
        elif kind == 'status':
            warnings = packet.get('warnings', [])
            state = 'Live' if self._live_received else 'Waiting for scene'
            if packet.get('tf_age') is not None and packet['tf_age'] > 5:
                warnings = [*warnings, f'No TF updates for {packet["tf_age"]} s']
            pending = []
            if not packet.get('robot'):
                pending.append('robot description')
            if not packet.get('planning'):
                pending.append('initial planning scene')
            suffix = f' — {len(warnings)} warning(s)' if warnings else ''
            if pending:
                suffix += ' — waiting for '+', '.join(pending)
            self.ros_status.setText(f'{state} · {packet.get("objects", 0)} objects · {self._ros_options.fixed_frame}{suffix}')
            self._ros_details = (f'Domain: {packet.get("domain")}\nFixed frame: {self._ros_options.fixed_frame}\n'
                                 f'Robot description received: {packet.get("robot")}\n'
                                 f'Initial planning scene received: {packet.get("planning")}\n\n'+
                                 ('\n'.join(warnings) or 'No warnings.'))
        elif kind in ('warning', 'error'):
            self._ros_details = packet.get('message', 'ROS connection error')
            self.ros_status.setText('ROS: '+self._ros_details[:110])
        self.ros_status.setToolTip(self._ros_details)
        if hasattr(self,'_workspace'):
            self._workspace.sync()

    def editable_snapshot(self):
        if not self._live or not self._live_received:
            return
        self._poll_ros()
        self.disconnect_ros()

    def disconnect_ros(self):
        if self._ros is None:
            return
        self._ros_timer.stop()
        self._live = False
        if self._live_received:
            self.scene = Scene(_snapshot(self.scene), self.scene.reference_frame)
            self.viewport.scene = self.scene
            self.project_path = None
            self.history.clear()
            self.history.resetClean()
        self._ros.stop()
        self.ros_status.setText('Editable snapshot — disconnected' if self._live_received else 'Offline — local scene')
        self._refresh()
        self._busy_actions()
        self._title()

    def _ros_stopped(self, error):
        connection = self._ros
        if self._live:
            self.disconnect_ros()
        self._ros = None
        if connection is not None:
            connection.deleteLater()
        if error and not self._closing:
            self._ros_details = error
            self.ros_status.setText('ROS disconnected — see Connection details')
            self.ros_status.setToolTip(error)
            self.statusBar().showMessage('ROS connection ended: '+error[:150])
        self._busy_actions()
        if self._closing and not self._jobs:
            self.close()

    def connection_details(self):
        QMessageBox.information(self, 'ROS 2 connection details', self._ros_details)

    def import_stl(self):
        paths, _ = QFileDialog.getOpenFileNames(self, 'Add STL meshes', '', 'STL meshes (*.stl *.STL)')
        if not paths:
            return
        unit, ok = QInputDialog.getItem(self, 'STL units', 'Source units (STL files do not store units):', list(STL_UNITS), 0, False)
        if not ok:
            return
        scale = STL_UNITS[unit]
        def read():
            return [SceneObject(Path(path).stem, read_stl(path), unit_scale=(scale,)*3) for path in paths]
        self._submit('Loading meshes…', read, self._add, True)

    def load_resolved_urdf(self):
        if self._live or self._jobs or self._closing:
            return
        self.cancel_snap()
        options = self._ros_options
        def resolve():
            try:
                return resolved_robot_snapshot(options),None
            except RobotDescriptionUnavailable as exc:
                return None,str(exc)
        self._submit('Resolving the current robot URDF from ROS 2…',resolve,self._resolved_urdf_loaded,True)

    def _resolved_urdf_loaded(self,result):
        scene,unavailable = result
        if scene is None:
            self.statusBar().setToolTip(unavailable)
            self.statusBar().showMessage('ROS 2 is not running or robot_description is unavailable. Cannot resolve URDF; select it manually.')
            self.import_urdf(fallback=True)
            return
        after = [obj for obj in _snapshot(self.scene) if not obj.id.startswith('robot/resolved/')]+scene.objects
        self._edit('Load resolved robot URDF',after,selection=scene.objects[0].id)
        self.viewport.fit()

    def import_urdf(self, *, fallback=False):
        title = ('ROS 2 unavailable: cannot resolve URDF. Select a URDF file manually.' if fallback else 'Import URDF file')
        path, _ = QFileDialog.getOpenFileName(self,title,'','URDF files (*.urdf);;All files (*)')
        if not path:
            return
        settings = QSettings('Standalone Scene Editor','Scene Editor')
        package = QFileDialog.getExistingDirectory(self,
                    'Mesh package / ROS workspace folder (Cancel: automatic lookup)',
                    str(settings.value('urdf/mesh_root','')))
        if package:
            settings.setValue('urdf/mesh_root',package)
        remembered = str(settings.value('urdf/mesh_root',''))
        roots = [remembered] if remembered else []
        if self._ros_options.workspace_setup:
            roots.append(str(Path(self._ros_options.workspace_setup).expanduser().parent))
        self._submit('Loading static URDF visuals…',
                     lambda: load_urdf(path, package or None,search_roots=roots).objects,self._add,True)

    def _confirm_discard(self):
        if self.history.isClean():
            return True
        choice = QMessageBox.warning(self, 'Unsaved scene', 'Save the current scene before continuing?',
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save)
        if choice == QMessageBox.StandardButton.Save:
            return self.save()
        return choice == QMessageBox.StandardButton.Discard

    def _replace_scene(self, scene, path=None, dirty=False):
        self.cancel_snap()
        self._generation += 1
        self.scene = scene
        self.project_path = Path(path).resolve() if path else None
        self.viewport.set_scene(scene)
        self.history.clear()
        if dirty:
            self.history.resetClean()
        self._refresh()
        self._title()

    def new_scene(self):
        if self._confirm_discard():
            self._replace_scene(Scene())

    def example_scene(self):
        if self._confirm_discard():
            self._replace_scene(demo_scene(), dirty=True)

    def open_scene(self):
        if not self._confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, 'Open scene', '', 'Scene files (*.scene.json);;JSON files (*.json)')
        if path:
            self.open_path(path)

    def open_path(self, path):
        self._submit('Loading scene…', lambda: load_scene(path), lambda scene: self._replace_scene(scene, path), True)

    def save(self):
        if self.project_path is None:
            return self.save_as()
        try:
            save_scene(self.scene, self.project_path)
            self.history.setClean()
            self._title()
            self.statusBar().showMessage(f'Saved {self.project_path}', 6000)
            return True
        except Exception as exc:
            self._error(str(exc))
            return False

    def save_as(self):
        path = self._save_path('Save scene', str(self.project_path or 'workcell.scene.json'), 'Scene files (*.scene.json)', 'scene.json')
        if not path:
            return False
        old_path = self.project_path
        self.project_path = Path(path).resolve()
        if self.save():
            return True
        self.project_path = old_path
        self._title()
        return False

    def export_selected(self):
        obj = self.selected()
        if obj is None:
            self.statusBar().showMessage('Select an object to export.', 6000)
            return
        path = self._save_path('Export transformed STL in mm', 'transformed.stl', 'STL meshes (*.stl)', 'stl')
        if path:
            # Protect every original mesh in the scene, including shared sources.
            destination = Path(path).resolve()
            if any(item.mesh.source == destination for item in self.scene.objects):
                self._error('Export to a new file. Original mesh files cannot be overwritten.')
                return
            mesh, matrix = obj.mesh, obj.matrix().copy()
            self._submit('Exporting full-resolution STL…', lambda: export_stl(mesh, matrix, destination), self._export_done)

    def _save_path(self, title, suggested, name_filter, suffix):
        dialog = QFileDialog(self, title)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setNameFilter(name_filter)
        dialog.setDefaultSuffix(suffix)
        dialog.selectFile(suggested)
        return dialog.selectedFiles()[0] if dialog.exec() else None

    def _export_done(self, result):
        pass

    def _render_error(self, message):
        self.statusBar().showMessage('3D renderer: ' + message)

    def _error(self, message):
        QMessageBox.critical(self, 'Scene Editor', message)

    def closeEvent(self, event):
        if not self._closing and not self._confirm_discard():
            event.ignore()
            return
        if self._jobs or self._ros is not None:
            self._closing = True
            self._ros_timer.stop()
            if self._ros is not None:
                self._live = False
                self._ros.stop()
            self.setEnabled(False)
            self.statusBar().showMessage('Finishing file operations and disconnecting ROS before closing…')
            event.ignore()
            return
        event.accept()


def demo_scene():
    return Scene([
        SceneObject('Work surface', make_box((600, 400, 25)), Pose((0, 0, -12.5)), color=(.35, .48, .62, 1)),
        SceneObject('Tool', make_cylinder(22, 160), Pose((0, 0, 170)), color=(.8, .58, .28, 1)),
        SceneObject('Fixture', make_box((160, 100, 65)), Pose((120, 60, 32.5), (0, 0, 20)), color=(.6, .45, .73, 1)),
    ])
