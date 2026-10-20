"""Reference-inspired editor workspace, composed around existing actions/widgets.

Presentation only: scene edits and ROS requests continue through EditorWindow.
"""
from PyQt6.QtCore import QObject, QSize, Qt, QSignalBlocker
from PyQt6.QtWidgets import (
    QWidget, QFrame, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QSplitter, QTabWidget, QScrollArea, QToolBar, QToolButton, QMenu,
    QLineEdit, QComboBox, QButtonGroup, QFormLayout, QSlider, QGroupBox, QDoubleSpinBox, QCheckBox,
)

from .icons import editor_icon, object_category
from .geometry import STL_UNITS


class CollapsibleSection(QFrame):
    def __init__(self, title):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        self.header = QToolButton()
        self.header.setObjectName('sectionToggle')
        self.header.setText(title)
        self.header.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.header.setCheckable(True)
        self.header.setArrowType(Qt.ArrowType.RightArrow)
        self.header.setCursor(Qt.CursorShape.PointingHandCursor)
        self.body = QWidget()
        self.body.hide()
        self.header.toggled.connect(self._toggle)
        layout.addWidget(self.header)
        layout.addWidget(self.body)

    def _toggle(self, checked):
        self.body.setVisible(checked)
        self.header.setArrowType(Qt.ArrowType.DownArrow if checked else Qt.ArrowType.RightArrow)


class Workspace(QObject):
    def __init__(self, window):
        super().__init__(window)
        self.window = w = window
        self._icons = []
        self._category = 'All'
        self._known_categories = {}
        self._build()

    def _icon_button(self, text, icon, handler=None, *, action=None):
        button = QToolButton()
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setToolTip(text)
        button.setAccessibleName(text)
        button.setIconSize(QSize(20,20))
        if action is not None:
            button.setDefaultAction(action)
        else:
            button.setText(text)
            if handler:
                button.clicked.connect(handler)
        self._icons.append((button,icon))
        button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        return button

    @staticmethod
    def _page():
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12,12,12,12)
        layout.setSpacing(12)
        scroll.setWidget(page)
        return scroll,layout

    def _build(self):
        w = self.window
        # Keep the original toolbar owners alive; their actions/widgets are reused.
        old_content = w.centralWidget()
        old_content.hide()
        old_bars = w.findChildren(QToolBar,options=Qt.FindChildOption.FindDirectChildrenOnly)
        frame_actions = [action for action in w.scene_toolbar.actions() if action.text() in ('Frame scene','Frame selected')]
        for bar in old_bars:
            w.removeToolBar(bar)
            bar.hide()
        toolbar = QToolBar('Main toolbar',w)
        toolbar.setMovable(False)
        w.scene_toolbar = toolbar
        w.addToolBar(toolbar)
        shape = self._icon_button('Add shape','plus')
        shape.setText('Add Shape')
        shape.setObjectName('primaryTool')
        shape.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        shape.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        shape_menu = QMenu(shape)
        shape_menu.addAction('Collision box…',self._new_box)
        shape_menu.addAction('Collision cylinder…',self._new_cylinder)
        shape_menu.addAction('Collision sphere…',self._new_sphere)
        shape_menu.addSeparator()
        shape_menu.addActions([w.box_action,w.cylinder_action])
        shape.setMenu(shape_menu)
        self.add_shape_button = shape
        toolbar.addWidget(shape)
        file = self._icon_button('Add or load objects','file')
        file.setText('Add / Load…')
        file.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        file.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        files = QMenu(file)
        files.addAction(w.resolved_urdf_action)
        files.addSeparator()
        files.addActions([w.import_action,w.urdf_action])
        file.setMenu(files)
        toolbar.addWidget(file)
        toolbar.addSeparator()
        toolbar.addWidget(QLabel('View:'))
        self.camera = QComboBox()
        self.camera.addItems(['Perspective','Top','Front','Back','Right','Left','Bottom'])
        self.camera.setMinimumWidth(125)
        self.camera.currentTextChanged.connect(self._camera_changed)
        w.viewport.camera_view_changed.connect(self._camera_from_view)
        toolbar.addWidget(self.camera)
        toolbar.addWidget(QLabel('Axis:'))
        previous_axis = w.axis
        w.axis = QComboBox()
        w.axis.addItems(['X','Y','Z','Screen'])
        w.axis.setCurrentText(previous_axis.currentText())
        w.axis.currentTextChanged.connect(w._axis_changed)
        toolbar.addWidget(w.axis)
        w.axis.show()
        for action in frame_actions:
            toolbar.addAction(action)
        spacer = QWidget()
        from PyQt6.QtWidgets import QSizePolicy
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        self.connection = self._icon_button('ROS connection','ros')
        self.connection.setText('ROS 2 · Offline')
        self.connection.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.connection.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        connection_menu = QMenu(self.connection)
        connection_menu.addActions([w.connect_ros_action,w.snapshot_action,w.disconnect_ros_action])
        connection_menu.addSeparator()
        connection_menu.addAction('Connection settings…',w.ros_settings)
        connection_menu.addAction('Connection details…',w.connection_details)
        self.connection.setMenu(connection_menu)
        toolbar.addWidget(self.connection)
        self.splitter = QSplitter()
        self.splitter.setChildrenCollapsible(False)
        left = QFrame()
        left.setObjectName('workspaceCard')
        left.setMinimumWidth(245)
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0,0,0,0)
        self.explorer_tabs = QTabWidget()
        left_layout.addWidget(self.explorer_tabs)
        scene = QWidget()
        scene_layout = QVBoxLayout(scene)
        scene_layout.setContentsMargins(10,10,10,10)
        title = QLabel('Scene Explorer')
        title.setObjectName('sectionTitle')
        scene_layout.addWidget(title)
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search objects…  (Ctrl+F)')
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(self._filter_changed)
        scene_layout.addWidget(self.search)
        filters = QGridLayout()
        filters.setSpacing(4)
        self.filter_group = QButtonGroup(self)
        self.filters = {}
        for index,name in enumerate(('All','Robot','Collision','Visual','Marker','Imported')):
            button = QToolButton()
            button.setObjectName('filterChip')
            button.setText(name)
            button.setCheckable(True)
            button.setChecked(index == 0)
            self.filter_group.addButton(button,index)
            self.filters[name] = button
            filters.addWidget(button,index//3,index%3)
        self.filter_group.idClicked.connect(self._category_changed)
        scene_layout.addLayout(filters)
        scene_layout.addWidget(w.objects,1)
        self.selection_hint = QLabel('Ctrl-click: multi-select · Shift: range')
        self.selection_hint.setObjectName('mutedText')
        scene_layout.addWidget(self.selection_hint)
        object_actions = QHBoxLayout()
        object_actions.addWidget(self._icon_button('New collision','plus',action=w.new_collision_action))
        for button,label,icon in ((w.duplicate_button,'Duplicate selected','copy'),(w.delete_button,'Delete selected','trash')):
            button.setParent(scene)
            button.setText('')
            button.setToolTip(label)
            button.setAccessibleName(label)
            button.setObjectName('compactButton')
            self._icons.append((button,icon))
            object_actions.addWidget(button)
        object_actions.addStretch()
        object_actions.addWidget(self._icon_button('Frame selected','frame',w.frame_selected))
        scene_layout.addLayout(object_actions)
        self.explorer_tabs.addTab(scene,'Scene')
        ros_page,ros_layout = self._page()
        heading = QLabel('ROS 2 connection')
        heading.setObjectName('sectionTitle')
        ros_layout.addWidget(heading)
        w.ros_status.setWordWrap(True)
        ros_layout.addWidget(w.ros_status)
        for action in (w.connect_ros_action,w.snapshot_action,w.disconnect_ros_action):
            button = QToolButton()
            button.setDefaultAction(action)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            ros_layout.addWidget(button)
        ros_layout.addWidget(w._button('Connection settings…',w.ros_settings))
        ros_layout.addWidget(w._button('Connection details…',w.connection_details))
        ros_note = QLabel('Live view follows ROS. Editable snapshot keeps a local copy. Scene writes require an explicit collision action.')
        ros_note.setWordWrap(True)
        ros_layout.addWidget(ros_note)
        ros_layout.addStretch()
        self.explorer_tabs.addTab(ros_page,'ROS 2')
        w.objects.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        w.objects.customContextMenuRequested.connect(self._context_menu)
        self.splitter.addWidget(left)
        center = QFrame()
        center.setObjectName('viewportCard')
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(1,1,1,1)
        center_layout.addWidget(w.viewport)
        self.splitter.addWidget(center)
        self._viewport_tools()
        self._properties()
        self.splitter.addWidget(w.inspector)
        self.splitter.setStretchFactor(1,1)
        self.splitter.setSizes([290,850,390])
        content = QWidget()
        content.setObjectName('editorWorkspace')
        root = QVBoxLayout(content)
        root.setContentsMargins(8,8,8,8)
        root.setSpacing(6)
        root.addWidget(self.splitter,1)
        footer = QFrame()
        footer.setObjectName('workspaceFooter')
        row = QHBoxLayout(footer)
        row.setContentsMargins(10,8,10,8)
        row.addWidget(QLabel('Mode:'))
        self.edit_mode = self._icon_button('Edit (local)','select',self._local_mode)
        self.edit_mode.setCheckable(True)
        self.edit_mode.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        row.addWidget(self.edit_mode)
        self.live_mode = self._icon_button('Live view','ros',w.connect_ros)
        self.live_mode.setCheckable(True)
        self.live_mode.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        row.addWidget(self.live_mode)
        snapshot = self._icon_button('Snapshot (editable)','snapshot',action=w.snapshot_action)
        snapshot.setText('Snapshot')
        snapshot.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        row.addWidget(snapshot)
        self.scene_stats = QLabel()
        self.scene_stats.setObjectName('mutedText')
        row.addWidget(self.scene_stats,1)
        for button,icon,label in ((w.undo_button,'undo','Undo'),(w.redo_button,'redo','Redo')):
            button.setText('')
            button.setAccessibleName(label)
            button.setObjectName('compactButton')
            self._icons.append((button,icon))
            row.addWidget(button)
        self.apply_button = self._icon_button('Apply to ROS 2','upload')
        self.apply_button.setObjectName('primaryTool')
        self.apply_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.apply_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        menu = QMenu(self.apply_button)
        menu.addActions([w.add_collision_action,w.update_collision_action,w.remove_collision_action])
        self.apply_button.setMenu(menu)
        row.addWidget(self.apply_button)
        root.addWidget(footer)
        w.setCentralWidget(content)
        old_content.setParent(w)
        old_content.hide()
        w.viewport._stats.hide()
        search_action = w._action('Search objects',self._focus_search,'Ctrl+F')
        w.addAction(search_action)

    def _viewport_tools(self):
        w = self.window
        tools = QFrame(w.viewport)
        tools.setObjectName('viewportTools')
        row = QHBoxLayout(tools)
        row.setContentsMargins(5,5,5,5)
        row.setSpacing(2)
        self.tool_group = QButtonGroup(self)
        self.tool_buttons = []
        for index,(name,icon,key) in enumerate((('Select','select','Q'),('Move','move','G'),('Rotate','rotate','R'))):
            button = self._icon_button(name+' ('+key+')',icon)
            button.setCheckable(True)
            button.setText(name)
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            self.tool_group.addButton(button,index)
            self.tool_buttons.append(button)
            row.addWidget(button)
            action = w._action(name+' tool',self._shortcut_tool,key)
            action.setData(index)
            action.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            w.viewport.addAction(action)
        self.tool_group.idClicked.connect(w.activate_edit_tool)
        w.mode.currentIndexChanged.connect(self._sync_tools)
        w.mode.setParent(w.viewport)
        w.mode.hide()
        row.addWidget(self._icon_button('Snap origin to another object','origin',action=w.snap_action))
        row.addWidget(self._icon_button('Mate surfaces','mate',action=w.surface_mate_action))
        self.grid_button = self._icon_button('Show grid','grid',self._toggle_grid)
        self.grid_button.setCheckable(True)
        self.grid_button.setChecked(True)
        row.addWidget(self.grid_button)
        self.gizmo_button = self._icon_button('Show transform handles','origin',self._toggle_gizmo)
        self.gizmo_button.setCheckable(True)
        self.gizmo_button.setChecked(True)
        row.addWidget(self.gizmo_button)
        tools.adjustSize()
        w.viewport._tool_overlay = tools
        tools.move(12,12)
        tools.show()
        w.viewport._help.hide()
        from .view_cube import ViewCube
        w.viewport._view_cube = ViewCube(w.viewport)
        w.viewport._view_cube.move(max(w.viewport.width()-104,0),82)
        w.viewport._view_cube.show()
        view_menu = w.menuBar().addMenu('View')
        self.origin_action = view_menu.addAction('Show selected object origin')
        self.origin_action.setCheckable(True)
        self.origin_action.setChecked(True)
        self.origin_action.toggled.connect(self._toggle_origin)
        view_menu.addAction('Frame scene',w.frame_scene)
        view_menu.addAction('Frame selection',w.frame_selected)
        for name in ('Perspective','Top','Front','Back','Right','Left','Bottom'):
            action = view_menu.addAction(name)
            action.setData(name)
            action.triggered.connect(self._view_requested)

    def _compact_pose(self, box, controls, names):
        old = box.layout()
        holder = QWidget()
        holder.setLayout(old)
        grid = QGridLayout(box)
        grid.setContentsMargins(10,8,10,10)
        grid.setSpacing(5)
        for index,(control,name) in enumerate(zip(controls,names)):
            from PyQt6.QtWidgets import QSizePolicy
            control.setMinimumWidth(0)
            from PyQt6.QtWidgets import QAbstractSpinBox
            control.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
            control.setObjectName('poseValue')
            control.setSuffix('')
            control.setToolTip(name + (' (degrees)' if name in ('Roll','Pitch','Yaw') else ' (mm)'))
            control.setSizePolicy(QSizePolicy.Policy.Ignored,QSizePolicy.Policy.Fixed)
            grid.addWidget(QLabel(name),0,index)
            grid.addWidget(control,1,index)
            grid.setColumnStretch(index,1)
        holder.deleteLater()

    def _properties(self):
        w = self.window
        old_children = set(w.inspector.findChildren(QWidget,options=Qt.FindChildOption.FindDirectChildrenOnly))
        old_layout = w.inspector.layout()
        while old_layout.count():
            old_layout.takeAt(0)
        w.inspector.setMinimumWidth(365)
        w.inspector.setObjectName('workspaceCard')
        old_layout.setContentsMargins(10,10,10,10)
        title = QLabel('Object Properties')
        title.setObjectName('sectionTitle')
        old_layout.addWidget(title)
        name = QFormLayout()
        name.addRow('Name',w.name)
        old_layout.addLayout(name)
        old_layout.addWidget(w.selection_summary)
        self.properties = QTabWidget()
        old_layout.addWidget(self.properties,1)
        general,layout = self._page()
        self.general_page = general
        self.mate_panel = QGroupBox('Mate surfaces')
        mate_layout = QVBoxLayout(self.mate_panel)
        self.mate_hint = QLabel()
        self.mate_hint.setWordWrap(True)
        mate_layout.addWidget(self.mate_hint)
        parameters = QFormLayout()
        parameters.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapAllRows)
        self.mate_offset = QDoubleSpinBox()
        self.mate_offset.setRange(-1e9,1e9)
        self.mate_offset.setDecimals(3)
        self.mate_offset.setSuffix(' mm')
        self.mate_offset.setKeyboardTracking(False)
        self.mate_twist = QDoubleSpinBox()
        self.mate_twist.setRange(-360,360)
        self.mate_twist.setDecimals(2)
        self.mate_twist.setSuffix('°')
        self.mate_twist.setKeyboardTracking(False)
        self.mate_flip = QCheckBox('Flip (same-facing normals)')
        parameters.addRow('Gap / offset',self.mate_offset)
        parameters.addRow('Rotate on face',self.mate_twist)
        parameters.addRow(self.mate_flip)
        mate_layout.addLayout(parameters)
        self.mate_offset.valueChanged.connect(self._mate_parameters)
        self.mate_twist.valueChanged.connect(self._mate_parameters)
        self.mate_flip.toggled.connect(self._mate_parameters)
        self.mate_apply = w._button('Apply surface mate',w.apply_surface_mate)
        self.mate_apply.setProperty('secondary',False)
        self.mate_apply.setObjectName('compactButton')
        mate_layout.addWidget(self.mate_apply)
        controls = QVBoxLayout()
        for text,handler in (('Pick faces again',w.begin_surface_mate),('Cancel',w.cancel_surface_mate)):
            button = w._button(text,handler)
            button.setObjectName('compactButton')
            controls.addWidget(button)
        mate_layout.addLayout(controls)
        self.mate_panel.hide()
        layout.addWidget(self.mate_panel)
        layout.addWidget(w.group_box)
        self.type_label = QLabel()
        self.type_label.setObjectName('mutedText')
        layout.addWidget(self.type_label)
        self.units_box = QGroupBox('STL source units')
        units_layout = QVBoxLayout(self.units_box)
        self.units = QComboBox()
        self.units.addItems(list(STL_UNITS))
        self.units.setPlaceholderText('Custom scale')
        self.units.setToolTip('Interpret the source mesh coordinates in these units. Scene positions stay in millimeters.')
        self.units.currentTextChanged.connect(w.change_stl_units)
        units_layout.addWidget(self.units)
        units_note = QLabel('Correct the source units without reimporting. Changes apply immediately and support Undo.')
        units_note.setWordWrap(True)
        units_layout.addWidget(units_note)
        self.mounting_section = CollapsibleSection('Mounting origin')
        self.mounting_section.header.setChecked(True)
        mounting = QVBoxLayout(self.mounting_section.body)
        mounting.setContentsMargins(4,4,4,4)
        mounting.setSpacing(6)
        note = QLabel('Pick where this object mounts. Setting the point keeps the geometry in place.')
        note.setWordWrap(True)
        mounting.addWidget(note)
        self.pick_mounting_button = w._button('Pick mounting point on object',w.begin_mounting_origin_pick)
        self.pick_mounting_button.setObjectName('compactButton')
        mounting.addWidget(self.pick_mounting_button)
        self.mounting_hint = QLabel()
        self.mounting_hint.setWordWrap(True)
        mounting.addWidget(self.mounting_hint)
        self.mounting_fine = CollapsibleSection('Fine adjustment (local mm)')
        coordinates = QFormLayout(self.mounting_fine.body)
        self.mounting_fields = []
        for axis in 'XYZ':
            field = QDoubleSpinBox()
            field.setRange(-1e9,1e9)
            field.setDecimals(4)
            field.setSuffix(' mm')
            field.setKeyboardTracking(False)
            field.valueChanged.connect(self._preview_mounting_fields)
            coordinates.addRow(axis,field)
            self.mounting_fields.append(field)
        mounting.addWidget(self.mounting_fine)
        presets = QHBoxLayout()
        self.mounting_preset = QComboBox()
        self.mounting_preset.addItems(['Mesh center','Bottom center','Top center','Current pivot','STL origin'])
        self.mounting_preset.setToolTip('Mesh/bottom/top centers use the bounding box, not mounting-hole detection.')
        presets.addWidget(self.mounting_preset,1)
        preset_button = w._button('Use preset',self._mounting_preset)
        preset_button.setObjectName('compactButton')
        presets.addWidget(preset_button)
        mounting.addLayout(presets)
        self.set_origin_button = w._button('Confirm mounting point',self._set_mounting_origin)
        self.set_origin_button.setProperty('secondary',False)
        self.set_origin_button.setObjectName('compactButton')
        mounting.addWidget(self.set_origin_button)
        self.origin_snap_button = w._button('Confirm and align to another object…',self._mounting_origin_and_snap)
        self.origin_snap_button.setObjectName('compactButton')
        mounting.addWidget(self.origin_snap_button)
        self.cancel_origin_button = w._button('Cancel',w.cancel_mounting_origin)
        self.cancel_origin_button.setObjectName('compactButton')
        mounting.addWidget(self.cancel_origin_button)
        layout.addWidget(self.mounting_section)
        layout.addWidget(self.units_box)
        layout.addWidget(w.size_box)
        w.size_box.setTitle('Dimensions (mm)')
        for field,names in (('translation',('X','Y','Z')),('rotation',('Roll','Pitch','Yaw'))):
            self._compact_pose(w._pose_boxes[field],w.pose_fields[field],names)
            layout.addWidget(w._pose_boxes[field])
        w.reset_button.setObjectName('compactButton')
        layout.addWidget(w.reset_button)
        origin = CollapsibleSection('Editing pivot')
        self.origin_section = origin
        origin_layout = QVBoxLayout(origin.body)
        self._compact_pose(w._pose_boxes['pivot'],w.pose_fields['pivot'],('X','Y','Z'))
        origin_layout.addWidget(w._pose_boxes['pivot'])
        for button in w._inspector_buttons[:2]:
            button.setObjectName('compactButton')
            origin_layout.addWidget(button)
        w.snap_button.setObjectName('compactButton')
        origin_layout.addWidget(w.snap_button)
        origin_layout.addWidget(w.pose_note)
        layout.addWidget(origin)
        layout.addStretch()
        self.properties.addTab(general,'General')
        visual,layout = self._page()
        layout.addWidget(QLabel('Appearance'))
        layout.addWidget(w.color_button)
        alpha = QFormLayout()
        alpha.addRow('Opacity',w.opacity)
        layout.addLayout(alpha)
        self.opacity = QSlider(Qt.Orientation.Horizontal)
        self.opacity.setRange(5,100)
        self.opacity.valueChanged.connect(self._opacity_changed)
        layout.addWidget(self.opacity)
        layout.addWidget(QLabel('Object colors are saved with the scene.'))
        layout.addStretch()
        self.properties.addTab(visual,'Visual')
        collision,layout = self._page()
        self.collision_info = QLabel()
        self.collision_info.setWordWrap(True)
        layout.addWidget(self.collision_info)
        for action in (w.new_collision_action,w.edit_collision_action):
            button = QToolButton()
            button.setDefaultAction(action)
            layout.addWidget(button)
        layout.addStretch()
        self.properties.addTab(collision,'Collision')
        ros,layout = self._page()
        layout.addWidget(w.details)
        for action in (w.add_collision_action,w.update_collision_action,w.remove_collision_action):
            button = QToolButton()
            button.setDefaultAction(action)
            layout.addWidget(button)
        w.collision_status.setWordWrap(True)
        layout.addWidget(w.collision_status)
        layout.addStretch()
        self.properties.addTab(ros,'ROS 2')
        # Retire the old repeated reset control and stale headings.
        for child in old_children:
            if child.parent() is w.inspector and child not in (w.name,w.selection_summary,self.properties):
                child.hide()

    def set_theme(self, colors):
        for widget,name in self._icons:
            icon = editor_icon(name,'#FFFFFF' if widget.objectName() == 'primaryTool' else colors['primary'])
            if isinstance(widget,QToolButton) and widget.defaultAction() is not None:
                widget.defaultAction().setIcon(icon)
            widget.setIcon(icon)
        self._icon_color = colors['primary']
        self._known_categories.clear()
        self.sync()

    def sync(self):
        w = self.window
        w.cancel_snap_action.setEnabled(w._snap_source is not None or w._surface_mate is not None or w._origin_edit is not None)
        self._sync_tools()
        self.edit_mode.setChecked(not w._live)
        self.live_mode.setChecked(w._live)
        self.edit_mode.setEnabled(not w._jobs)
        self.live_mode.setEnabled(w._live or w.connect_ros_action.isEnabled())
        self.connection.setText('ROS 2 · Live' if w._live and w._live_received else ('ROS 2 · Connecting' if w._ros else 'ROS 2 · Offline'))
        self.connection.setToolTip(w._ros_details)
        self.add_shape_button.setEnabled(w.new_collision_action.isEnabled())
        self.apply_button.setEnabled(any(action.isEnabled() for action in (w.add_collision_action,w.update_collision_action,w.remove_collision_action)))
        self.scene_stats.setText(f'{len(w.scene.objects)} objects · {len(w.selected_objects())} selected · mm')
        self.scene_stats.setToolTip(f'{sum(len(obj.mesh.vertices) for obj in w.scene.objects):,} triangles. Group moves remain local.')
        selected = w.selected()
        state = w._surface_mate
        self.mate_panel.setVisible(state is not None)
        if state is not None:
            ready = state['pose'] is not None
            self.mate_apply.setEnabled(ready)
            self.mate_hint.setText('Preview only. Surface centers align. Source is purple; target is green. Adjust, then Apply.' if ready else
                                   ('2. Drag to orbit; click the target face. Middle-drag pans. The first face stays selected.' if state['source'] else
                                    '1. Click a highlighted face on the unlocked object to move. Drag to orbit; middle-drag to pan.'))
            for widget,value in ((self.mate_offset,state['offset']),(self.mate_twist,state['twist'])):
                with QSignalBlocker(widget):
                    widget.setValue(value)
            with QSignalBlocker(self.mate_flip):
                self.mate_flip.setChecked(state['flip'])
        self.units_box.setVisible(w.has_editable_stl_units(selected) and len(w.selected_objects()) == 1)
        self.mounting_section.setVisible(w.has_editable_stl_units(selected) and len(w.selected_objects()) == 1)
        self.mounting_section.body.setEnabled(selected is not None and not selected.locked and not w._live and not w._jobs)
        pending = w._origin_edit if selected and w._origin_edit and w._origin_edit['id'] == selected.id else None
        candidate = pending['point'] if pending else None
        for index,field in enumerate(self.mounting_fields):
            with QSignalBlocker(field):
                field.setValue(candidate[index] if candidate else (selected.origin_source[index]*selected.unit_scale[index] if selected else 0))
        ready = bool(pending and pending['picked'])
        self.set_origin_button.setEnabled(ready)
        self.origin_snap_button.setEnabled(ready and len(w.scene.objects) > 1)
        self.cancel_origin_button.setVisible(pending is not None)
        self.pick_mounting_button.setEnabled(selected is not None and selected.visible)
        self.pick_mounting_button.setText('Pick a different point' if ready else 'Pick mounting point on object')
        self.mounting_hint.setText('Preview only. Confirm below or pick again. Use Fine adjustment for exact coordinates.' if ready else
                                  ('Click a visible surface of this object. Right-drag to orbit. Escape cancels.' if pending else
                                   'Pick on the mesh, or choose a bounding-box preset below.'))
        self.units.setEnabled(selected is not None and not selected.locked and not w._live and not w._jobs)
        with QSignalBlocker(self.units):
            self.units.setCurrentIndex(next((i for i,scale in enumerate(STL_UNITS.values())
                                            if selected and selected.unit_scale == (scale,)*3),-1))
        category = object_category(selected) if selected else None
        self.type_label.setText((category+' · '+(selected.mesh.primitive['kind'].title() if selected.mesh.primitive else 'Mesh')) if selected else 'Select an object to inspect it.')
        self.collision_info.setText(self._collision_description(selected))
        self.opacity.setEnabled(selected is not None and not selected.locked and not w._live and len(w.selected_objects()) == 1)
        with QSignalBlocker(self.opacity):
            self.opacity.setValue(round(selected.color[3]*100) if selected else 100)
        if selected:
            from PyQt6.QtGui import QColor,QIcon,QPixmap
            color = QColor.fromRgbF(*selected.color)
            pixmap = QPixmap(20,20)
            pixmap.fill(color)
            w.color_button.setIcon(QIcon(pixmap))
            w.color_button.setText('Color  '+color.name().upper())
        counts = {name:0 for name in self.filters}
        for index,obj in enumerate(w.scene.objects):
            category = object_category(obj)
            counts[category] += 1
            item = w.objects.item(index)
            if item is not None and (item.icon().isNull() or self._known_categories.get(obj.id) != category):
                with QSignalBlocker(w.objects):
                    item.setIcon(editor_icon({'Robot':'robot','Collision':'cube','Marker':'marker','Imported':'file','Visual':'cube'}[category],getattr(self,'_icon_color','#905BA9'),18))
                    self._known_categories[obj.id] = category
        for name,button in self.filters.items():
            button.setToolTip(f'{len(w.scene.objects) if name == "All" else counts[name]} objects')
        self._filter_changed()
        w.viewport._tool_overlay.adjustSize()

    @staticmethod
    def _collision_description(obj):
        if obj is None:
            return 'Select an object to inspect its collision role.'
        if obj.id.startswith('robot/'):
            return ('Robot link visual geometry, loaded from the URDF <visual> definition. '
                    'The link may also have separate URDF <collision> geometry used by MoveIt. '
                    'This editor does not currently load or inspect those collision definitions. '
                    'Robot links are not world collision objects; these ROS apply actions do not modify the robot model.')
        if obj.id.startswith(('world/','attached/')):
            attached = obj.id.startswith('attached/')
            identifier = obj.id.split('/',1)[1].rsplit('/',1)[0]
            return (('Attached collision object' if attached else 'Planning-scene world collision object')+
                    '\nCollision ID: '+identifier+
                    '\n\nImported collision geometry from ROS. This object is not currently editable through '
                    'the authored collision-object ROS actions. Local snapshot edits do not update ROS.')
        if obj.collision:
            return ('Authored collision object\nCollision ID: '+obj.collision['object_id']+
                    '\nReference frame: '+obj.collision['frame']+
                    '\n\nLocal collision geometry. Creating or editing it here does not confirm it exists in ROS. '
                    'Changes reach the planning scene only through an explicit ROS action.')
        return ('Visual geometry with no collision-object metadata in this editor. '
                'This does not establish whether equivalent collision geometry exists in ROS. '
                'Use New collision to author a box, cylinder or sphere for MoveIt.')

    def _sync_tools(self,*args):
        with QSignalBlocker(self.window.surface_mate_action):
            self.window.surface_mate_action.setChecked(self.window._surface_mate is not None)
        self.tool_group.setExclusive(False)
        for index,button in enumerate(self.tool_buttons):
            with QSignalBlocker(button):
                button.setChecked(self.window._surface_mate is None and self.window.mode.currentIndex() == index)
            button.setEnabled(self.window.mode.isEnabled() and self.window.mode.model().item(index).isEnabled())
        self.tool_group.setExclusive(True)

    def _filter_changed(self,*args):
        query = self.search.text().strip().casefold()
        w = self.window
        with QSignalBlocker(w.objects):
            for index,obj in enumerate(w.scene.objects):
                item = w.objects.item(index)
                if item:
                    item.setHidden((self._category != 'All' and object_category(obj) != self._category) or bool(query and query not in (obj.name+' '+obj.id).casefold()))

    def _category_changed(self,index):
        self._category = tuple(self.filters)[index]
        self._filter_changed()

    def _new_box(self): self.window.new_collision(shape='box')
    def _new_cylinder(self): self.window.new_collision(shape='cylinder')
    def _new_sphere(self): self.window.new_collision(shape='sphere')
    def _focus_search(self):
        self.explorer_tabs.setCurrentIndex(0)
        self.search.setFocus()
        self.search.selectAll()
    def _camera_changed(self,name): self.window.viewport.set_camera_view(name)

    def _camera_from_view(self,name):
        with QSignalBlocker(self.camera):
            self.camera.setCurrentText(name)
    def _view_requested(self): self.camera.setCurrentText(self.sender().data())
    def _shortcut_tool(self):
        index = self.sender().data()
        if self.tool_buttons[index].isEnabled():
            self.window.activate_edit_tool(index)
    def _toggle_grid(self):
        self.window.viewport.show_grid = self.grid_button.isChecked()
        self.window.viewport.update()
    def _toggle_gizmo(self):
        self.window.viewport.show_gizmo = self.gizmo_button.isChecked()
        self.window.viewport.update()
    def _toggle_origin(self,checked):
        self.window.viewport.show_origin = checked
        self.window.viewport.update()
    def show_surface_mate(self):
        self.properties.setCurrentIndex(0)
        self.general_page.verticalScrollBar().setValue(0)
    def _mate_parameters(self,*args):
        self.window.update_surface_mate(self.mate_offset.value(),self.mate_flip.isChecked(),self.mate_twist.value())
    def _mounting_preset(self):
        for field,value in zip(self.mounting_fields,self.window.mounting_origin_preset(self.mounting_preset.currentText())):
            with QSignalBlocker(field):
                field.setValue(value)
        self._preview_mounting_fields()
    def _set_mounting_origin(self):
        pending = self.window._origin_edit
        if pending and pending['picked']:
            self.window.set_mounting_origin(pending['point'])
    def _preview_mounting_fields(self,*args):
        self.window.preview_mounting_origin(tuple(field.value() for field in self.mounting_fields))
    def _mounting_origin_and_snap(self):
        self._set_mounting_origin()
        self.window.begin_snap()
    def _local_mode(self):
        if self.window._live:
            self.window.editable_snapshot()
        self.sync()
    def _opacity_changed(self,value): self.window.opacity.setValue(value/100)

    def _context_menu(self,point):
        w = self.window
        item = w.objects.itemAt(point)
        if item is None:
            return
        identifier = item.data(Qt.ItemDataRole.UserRole)
        if identifier not in w.viewport.selection_ids():
            w._select(identifier)
        menu = QMenu(w.objects)
        menu.addAction('Frame selection',w.frame_selected)
        menu.addAction(w.lock_action)
        menu.addAction(w.snap_action)
        menu.addSeparator()
        duplicate = menu.addAction('Duplicate',w.duplicate)
        duplicate.setEnabled(w.duplicate_button.isEnabled())
        delete = menu.addAction('Delete',w.delete)
        delete.setEnabled(w.delete_button.isEnabled())
        menu.exec(w.objects.mapToGlobal(point))
