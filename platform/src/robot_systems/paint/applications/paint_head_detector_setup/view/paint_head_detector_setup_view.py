"""Paint-owned developer screen; widgets and presentation, without service/model access."""

from collections.abc import Mapping

import qtawesome as qta
from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QHideEvent, QShowEvent
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSplitter,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from pl_gui.settings.settings_view.styles import (
    APP_PAGE_TITLE_STYLE,
    ERROR_COLOR,
    PRIMARY,
    TEXT_COLOR,
    TOUCH_SCROLL_AREA_STYLE,
)
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.styled_message_box import ask_yes_no, show_critical
from src.robot_systems.paint.contracts.paint_head_calibration.errors import (
    CalibrationFailure,
    CalibrationFailureCode,
)
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationEvaluation,
    ImageFrame,
    ImagePixels,
    Landmark,
    LandmarkRole,
    ProfileId,
    ReferenceAsset,
    ReferenceRole,
    RevisionRef,
)

from ..editor_contracts import EditorObject, EditorTarget, EditorTool, SetupPage, UnsavedDecision
from ..presentation import SetupSnapshot
from ..tuning_fields import TUNING_PARAMETERS, TuningParameterId, TuningSection
from .styles import CAPTION_STYLE, CARD_STYLE, PAGE_STYLE, SECTION_TITLE_STYLE
from .widgets.calibration_canvas import CalibrationCanvas
from .widgets.forms import (
    EditorToolButton,
    IconActionButton,
    ProfileDialog,
    ReferenceDialog,
    RuntimePicker,
    SaveRevisionDialog,
    SettingsSection,
    SetupDialog,
    TuningField,
    UnsavedDialog,
    action_button,
    translate,
)
from .widgets.object_properties import ObjectPropertiesPanel
from .widgets.result_panel import CalibrationResultPanel, result_color, state_text

_PAGES = (
    (SetupPage.PROFILES, "Profiles"),
    (SetupPage.CAMERA, "Camera & capture"),
    (SetupPage.REGIONS, "Regions & landmarks"),
    (SetupPage.TEST, "Test & results"),
    (SetupPage.SETTINGS, "Settings"),
)
_PAGE_ICONS = {
    SetupPage.PROFILES: "mdi.folder-outline",
    SetupPage.CAMERA: "mdi.camera-outline",
    SetupPage.REGIONS: "mdi.vector-square",
    SetupPage.TEST: "mdi.flask-outline",
    SetupPage.SETTINGS: "mdi.tune",
}
_TOOLS = (
    (EditorTool.SELECT, "Select / move"),
    (EditorTool.PAN, "Pan"),
    (EditorTool.INSPECTION, "Inspection region"),
    (EditorTool.EMPTY_MOUNT, "Empty-mount region"),
    (EditorTool.EXCLUDED, "Excluded region"),
    (EditorTool.RECTANGLE_LANDMARK, "Rectangle landmark"),
    (EditorTool.CIRCLE_LANDMARK, "Circle landmark"),
)


class PaintHeadDetectorSetupView(IApplicationView):
    profile_selected = pyqtSignal(object)
    create_requested = pyqtSignal(str, str)
    import_requested = pyqtSignal(str)
    save_draft_requested = pyqtSignal()
    save_revision_requested = pyqtSignal(str)
    edit_revision_requested = pyqtSignal(object)
    select_revision_requested = pyqtSignal(object)
    delete_revision_requested = pyqtSignal(object)
    delete_profile_requested = pyqtSignal(object)
    discard_local_requested = pyqtSignal()
    discard_saved_draft_requested = pyqtSignal()
    capture_requested = pyqtSignal(object)
    reference_preview_requested = pyqtSignal(object)
    freeze_requested = pyqtSignal(bool)
    live_requested = pyqtSignal(bool)
    page_selected = pyqtSignal(object)
    test_requested = pyqtSignal()
    geometry_edited = pyqtSignal(object)
    object_selected = pyqtSignal(object)
    properties_edited = pyqtSignal(object)
    object_removed = pyqtSignal(object)
    tuning_edited = pyqtSignal(object, object)
    screen_shown = pyqtSignal()
    screen_hidden = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        self._snapshot: SetupSnapshot | None = None
        self._objects: tuple[EditorObject, ...] = ()
        self._selection: EditorTarget | None = None
        self._image: ImagePixels | None = None
        self._evaluation: CalibrationEvaluation | None = None
        self._busy = False
        self._page = SetupPage.CAMERA
        self._static_labels: list[tuple[QLabel, str]] = []
        self._static_buttons: list[tuple[QPushButton, str]] = []
        self._canvases: dict[SetupPage, CalibrationCanvas] = {}
        self._camera_labels: dict[SetupPage, QLabel] = {}
        self._tuning_fields: dict[TuningParameterId, TuningField] = {}
        self._result_panels: list[CalibrationResultPanel] = []
        self._fullscreen: SetupDialog | None = None
        self._fullscreen_canvas: CalibrationCanvas | None = None
        self._last_frame: ImageFrame | None = None
        self._preview_failed = False
        self._preview_failure: CalibrationFailure | None = None
        self._last_fps = "—"
        super().__init__("PaintHeadDetectorSetup", parent)
        self.retranslateUi()

    def _label(self, source: str, *, wrap: bool = False) -> QLabel:
        label = QLabel()
        label.setWordWrap(wrap)
        self._static_labels.append((label, source))
        return label

    @property
    def current_page(self) -> SetupPage:
        return self._page

    def _button(self, source: str, *, primary: bool = False) -> QPushButton:
        button = action_button(source, primary=primary)
        self._static_buttons.append((button, source))
        return button

    def setup_ui(self) -> None:
        self.setObjectName("paintHeadSetup")
        self.setStyleSheet(PAGE_STYLE)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(10)
        self._title = self._label("Paint-head detector setup")
        self._title.setStyleSheet(APP_PAGE_TITLE_STYLE)
        outer.addWidget(self._title)
        subtitle = self._label("Primary vision · Vertical Shaft Alignment")
        subtitle.setStyleSheet(CAPTION_STYLE)
        outer.addWidget(subtitle)
        profile_card, profile_layout = self._card()
        header = QHBoxLayout()
        editing = QVBoxLayout()
        editing.setSpacing(4)
        caption = self._label("Editing profile")
        caption.setStyleSheet(CAPTION_STYLE)
        editing.addWidget(caption)
        self._profile_picker = QComboBox()
        self._profile_picker.setMinimumWidth(260)
        self._profile_picker.setMaximumWidth(340)
        self._profile_picker.setObjectName("calibrationProfilePicker")
        self._profile_picker.currentIndexChanged.connect(self._on_profile_picker)
        self._runtime_label = QLabel()
        self._runtime_label.setObjectName("calibrationRuntimeSelection")
        self._runtime_label.setWordWrap(True)
        self._runtime_button = self._button("Select for runtime")
        self._runtime_button.clicked.connect(self._pick_runtime)
        editing.addWidget(self._profile_picker)
        header.addLayout(editing, 1)
        header.addWidget(self._runtime_label, 2)
        header.addWidget(self._runtime_button)
        profile_layout.addLayout(header)
        outer.addWidget(profile_card)
        body = QHBoxLayout()
        body.setSpacing(14)
        self._navigation = QListWidget()
        self._navigation.setObjectName("calibrationNavigation")
        self._navigation.setFixedWidth(224)
        self._navigation.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._navigation.setWordWrap(True)
        self._navigation.setIconSize(QSize(20, 20))
        self._navigation.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        for page, _ in _PAGES:
            item = QListWidgetItem()
            item.setIcon(qta.icon(_PAGE_ICONS[page], color=PRIMARY))
            self._navigation.addItem(item)
        self._navigation.currentRowChanged.connect(self._on_page_changed)
        body.addWidget(self._navigation)
        self._pages = QStackedWidget()
        self._pages.addWidget(self._build_profiles())
        self._pages.addWidget(self._build_camera())
        self._pages.addWidget(self._build_regions())
        self._pages.addWidget(self._build_test())
        self._pages.addWidget(self._build_settings())
        body.addWidget(self._pages, 1)
        outer.addLayout(body, 1)
        self._notice = QLabel()
        self._notice.setWordWrap(True)
        self._notice.setObjectName("calibrationNotice")
        self._notice.hide()
        outer.addWidget(self._notice)
        footer_card, footer_layout = self._card()
        footer_layout.setContentsMargins(14, 10, 14, 10)
        footer = QHBoxLayout()
        self._draft_label = QLabel()
        self._draft_label.setObjectName("calibrationDraftStatus")
        self._draft_label.setWordWrap(True)
        self._draft_label.setStyleSheet(CAPTION_STYLE)
        footer.addWidget(self._draft_label, 1)
        self._save_draft = self._button("Save draft")
        self._save_draft.setObjectName("saveCalibrationDraft")
        self._save_revision = self._button("Save calibration", primary=True)
        self._save_revision.setObjectName("saveCalibrationRevision")
        self._save_draft.clicked.connect(self._on_save_draft)
        self._save_revision.clicked.connect(self._on_save_revision)
        footer.addWidget(self._save_draft)
        footer.addWidget(self._save_revision)
        footer_layout.addLayout(footer)
        outer.addWidget(footer_card)
        self._navigation.setCurrentRow(1)

    def _card(self, source: str | None = None) -> tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("settingsCard")
        card.setStyleSheet(CARD_STYLE)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(10)
        if source is not None:
            heading = self._label(source)
            heading.setStyleSheet(SECTION_TITLE_STYLE)
            layout.addWidget(heading)
        return card, layout

    def _table(self, columns: int) -> QTableWidget:
        table = QTableWidget(0, columns)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        header = table.horizontalHeader()
        header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setDefaultSectionSize(44)
        table.setShowGrid(False)
        table.setAlternatingRowColors(True)
        table.verticalHeader().hide()
        return table

    def _build_profiles(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        profiles, profile_layout = self._card()
        actions = QHBoxLayout()
        heading = self._label("Profiles")
        heading.setStyleSheet(SECTION_TITLE_STYLE)
        actions.addWidget(heading, 1)
        new = self._button("New profile", primary=True)
        new.clicked.connect(self._new_profile)
        importing = self._button("Import factory calibration")
        importing.clicked.connect(self._import_profile)
        actions.addWidget(new)
        actions.addWidget(importing)
        profile_layout.addLayout(actions)
        self._profile_table = self._table(4)
        self._profile_table.setObjectName("calibrationProfilesTable")
        self._profile_table.itemSelectionChanged.connect(self._on_profile_table)
        profile_layout.addWidget(self._profile_table, 1)
        layout.addWidget(profiles, 2)
        revisions, revision_layout = self._card("Saved revisions")
        self._revision_table = self._table(3)
        self._revision_table.setObjectName("calibrationRevisionsTable")
        self._revision_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        self._revision_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self._revision_table.itemSelectionChanged.connect(self._on_revision_selection)
        revision_layout.addWidget(self._revision_table, 1)
        row = QHBoxLayout()
        self._edit_revision = self._button("Edit as draft")
        self._use_revision = self._button("Use selected revision", primary=True)
        self._delete_revision = self._button("Delete revision")
        self._delete_profile = self._button("Delete profile")
        self._edit_revision.clicked.connect(self._on_edit_revision)
        self._use_revision.clicked.connect(self._on_use_revision)
        self._delete_revision.clicked.connect(self._on_delete_revision)
        self._delete_profile.clicked.connect(self._on_delete_profile)
        row.addWidget(self._edit_revision)
        row.addWidget(self._use_revision)
        row.addStretch()
        row.addWidget(self._delete_revision)
        row.addWidget(self._delete_profile)
        revision_layout.addLayout(row)
        layout.addWidget(revisions, 3)
        return page

    def _camera(self, page: SetupPage) -> tuple[QWidget, CalibrationCanvas]:
        panel, layout = self._card()
        header = QHBoxLayout()
        heading = self._label("Live camera")
        heading.setStyleSheet(SECTION_TITLE_STYLE)
        header.addWidget(heading)
        status = QLabel()
        status.setWordWrap(True)
        status.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        status.setStyleSheet(CAPTION_STYLE)
        self._camera_labels[page] = status
        header.addWidget(status, 1)
        layout.addLayout(header)
        canvas = CalibrationCanvas()
        canvas.geometry_edited.connect(self._on_geometry_edit)
        canvas.object_selected.connect(self._on_object_selected)
        self._canvases[page] = canvas
        layout.addWidget(canvas, 1)
        row = QHBoxLayout()
        fit = self._button("Fit image")
        plus = IconActionButton("mdi.magnify-plus-outline", "Zoom in")
        minus = IconActionButton("mdi.magnify-minus-outline", "Zoom out")
        fit.clicked.connect(canvas.fit_image)
        plus.clicked.connect(canvas.zoom_in)
        minus.clicked.connect(canvas.zoom_out)
        row.addWidget(fit)
        row.addStretch()
        row.addWidget(minus)
        row.addWidget(plus)
        if page is SetupPage.SETTINGS:
            fullscreen = IconActionButton("mdi.fullscreen", "Open fullscreen")
            fullscreen.clicked.connect(self._open_fullscreen)
            row.addWidget(fullscreen)
        layout.addLayout(row)
        return panel, canvas

    def _build_camera(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        camera, canvas = self._camera(SetupPage.CAMERA)
        canvas.setInteractive(False)
        layout.addWidget(camera, 1)
        inspector = QWidget()
        inspector.setFixedWidth(300)
        side = QVBoxLayout(inspector)
        side.setContentsMargins(0, 0, 0, 0)
        side.setSpacing(12)
        present, present_layout = self._card("Head present")
        self._present_reference = QLabel()
        self._present_reference.setStyleSheet(CAPTION_STYLE)
        present_layout.addWidget(self._present_reference)
        capture_present = self._button("Capture", primary=True)
        preview_present = self._button("Preview")
        capture_present.clicked.connect(self._capture_present)
        preview_present.clicked.connect(self._preview_present)
        present_layout.addWidget(capture_present)
        present_layout.addWidget(preview_present)
        side.addWidget(present)
        missing, missing_layout = self._card("Head missing")
        self._missing_reference = QLabel()
        self._missing_reference.setStyleSheet(CAPTION_STYLE)
        missing_layout.addWidget(self._missing_reference)
        capture_missing = self._button("Capture")
        preview_missing = self._button("Preview")
        capture_missing.clicked.connect(self._capture_missing)
        preview_missing.clicked.connect(self._preview_missing)
        missing_layout.addWidget(capture_missing)
        missing_layout.addWidget(preview_missing)
        side.addWidget(missing)
        controls, controls_layout = self._card("Preview controls")
        self._freeze = self._button("Freeze frame")
        self._freeze.clicked.connect(self._on_freeze)
        controls_layout.addWidget(self._freeze)
        fullscreen = self._button("Open fullscreen")
        fullscreen.clicked.connect(self._open_fullscreen)
        controls_layout.addWidget(fullscreen)
        side.addWidget(controls)
        hint = self._label(
            "Confirm captured references before adding them to the draft.", wrap=True
        )
        hint.setStyleSheet(CAPTION_STYLE)
        side.addWidget(hint)
        side.addStretch()
        layout.addWidget(inspector)
        return page

    def _build_regions(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        toolbar, toolbar_layout = self._card()
        toolbar_layout.setContentsMargins(12, 8, 12, 8)
        tools = QHBoxLayout()
        tools.setSpacing(6)
        self._tool_group = QButtonGroup(self)
        self._tool_group.setExclusive(True)
        self._tool_buttons: list[EditorToolButton] = []
        for tool, source in _TOOLS:
            if tool in (EditorTool.INSPECTION, EditorTool.RECTANGLE_LANDMARK):
                tools.addSpacing(8)
            button = EditorToolButton(tool, source, self)
            button.chosen.connect(self._on_tool_selected)
            self._tool_group.addButton(button)
            self._tool_buttons.append(button)
            tools.addWidget(button)
        self._tool_buttons[0].setChecked(True)
        tools.addStretch()
        self._new_landmark_role = QComboBox()
        for role in LandmarkRole:
            self._new_landmark_role.addItem("", role)
        self._new_landmark_role.setMinimumWidth(200)
        self._new_landmark_role.currentIndexChanged.connect(self._on_new_role)
        tools.addWidget(self._label("New landmark role"))
        tools.addWidget(self._new_landmark_role)
        toolbar_layout.addLayout(tools)
        layout.addWidget(toolbar)
        splitter = QSplitter()
        splitter.setChildrenCollapsible(False)
        camera, _ = self._camera(SetupPage.REGIONS)
        splitter.addWidget(camera)
        inspector = QWidget()
        inspector.setMinimumWidth(350)
        side = QVBoxLayout(inspector)
        side.setContentsMargins(0, 0, 0, 0)
        side.setSpacing(12)
        objects, objects_layout = self._card("Objects")
        self._object_list = QListWidget()
        self._object_list.setObjectName("calibrationObjects")
        self._object_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._object_list.setMinimumHeight(100)
        self._object_list.setMaximumHeight(170)
        self._object_list.currentRowChanged.connect(self._on_object_list)
        objects_layout.addWidget(self._object_list)
        side.addWidget(objects)
        properties, property_layout = self._card()
        property_layout.setContentsMargins(4, 4, 4, 4)
        self._properties = ObjectPropertiesPanel()
        self._properties.apply_requested.connect(self._on_properties_edit)
        self._properties.remove_requested.connect(self._on_object_removed)
        scrolling = QScrollArea()
        scrolling.setObjectName("calibrationPropertiesScroll")
        scrolling.setWidgetResizable(True)
        scrolling.setStyleSheet(TOUCH_SCROLL_AREA_STYLE)
        scrolling.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrolling.setWidget(self._properties)
        property_layout.addWidget(scrolling)
        side.addWidget(properties, 1)
        splitter.addWidget(inspector)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)
        splitter.setSizes([700, 350])
        layout.addWidget(splitter, 1)
        return page

    def _build_test(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        actions, action_layout = self._card()
        action_layout.setContentsMargins(12, 8, 12, 8)
        row = QHBoxLayout()
        self._run = self._button("Test current draft", primary=True)
        self._live = self._button("Continuous evaluation")
        self._live.setCheckable(True)
        self._run.clicked.connect(self._on_test)
        self._live.clicked.connect(self._on_live)
        row.addWidget(self._run)
        row.addWidget(self._live)
        hint = self._label("Evaluation uses the current draft, including unsaved edits.", wrap=True)
        hint.setStyleSheet(CAPTION_STYLE)
        row.addWidget(hint, 1)
        action_layout.addLayout(row)
        layout.addWidget(actions)
        body = QHBoxLayout()
        body.setSpacing(12)
        camera, canvas = self._camera(SetupPage.TEST)
        canvas.setInteractive(False)
        body.addWidget(camera, 1)
        result_card = CalibrationResultPanel()
        result_card.setMinimumWidth(390)
        result_card.setMaximumWidth(430)
        self._result_panels.append(result_card)
        body.addWidget(result_card)
        layout.addLayout(body, 1)
        return page

    def _build_settings(self) -> QWidget:
        container = QWidget()
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(12)
        row = QHBoxLayout()
        hint = self._label("Detector settings belong to the editing draft.", wrap=True)
        hint.setStyleSheet(CAPTION_STYLE)
        row.addWidget(hint, 1)
        self._settings_live = self._button("Live preview")
        self._settings_live.setObjectName("calibrationSettingsLivePreview")
        self._settings_live.setCheckable(True)
        self._settings_live.clicked.connect(self._on_live)
        row.addWidget(self._settings_live)
        self._discard_draft = self._button("Discard saved draft")
        self._discard_draft.clicked.connect(self._on_discard_saved_draft)
        row.addWidget(self._discard_draft)
        outer.addLayout(row)
        split = QSplitter()
        split.setChildrenCollapsible(False)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(TOUCH_SCROLL_AREA_STYLE)
        content = QWidget()
        content.setObjectName("calibrationSettingsContent")
        layout = QVBoxLayout(content)
        layout.setContentsMargins(0, 0, 8, 0)
        layout.setSpacing(12)
        for section, source in (
            (TuningSection.ALIGNMENT, "Alignment and confirmation"),
            (TuningSection.MATCHING, "Advanced matching"),
            (TuningSection.PREPROCESSING, "Advanced preprocessing"),
        ):
            group = SettingsSection(source, expanded=section is TuningSection.ALIGNMENT)
            group.fields.setColumnStretch(1, 0)
            index = 0
            for parameter in TUNING_PARAMETERS:
                if parameter.section is section:
                    field = TuningField(parameter)
                    field.edited.connect(self._on_tuning_edited)
                    self._tuning_fields[parameter.identity] = field
                    group.fields.addWidget(field, index, 0)
                    index += 1
            layout.addWidget(group)
        layout.addStretch()
        scroll.setWidget(content)
        scroll.setMinimumWidth(380)
        split.addWidget(scroll)
        preview = QWidget()
        preview_layout = QVBoxLayout(preview)
        preview_layout.setContentsMargins(0, 0, 0, 0)
        preview_layout.setSpacing(10)
        camera, canvas = self._camera(SetupPage.SETTINGS)
        canvas.setInteractive(False)
        canvas.setMinimumHeight(140)
        preview_layout.addWidget(camera, 1)
        result = CalibrationResultPanel(compact=True)
        self._result_panels.append(result)
        preview_layout.addWidget(result)
        preview.setMinimumWidth(390)
        split.addWidget(preview)
        split.setStretchFactor(0, 0)
        split.setStretchFactor(1, 1)
        split.setSizes([440, 550])
        outer.addWidget(split, 1)
        return container

    def set_snapshot(
        self,
        snapshot: SetupSnapshot,
        objects: tuple[EditorObject, ...],
        selected: EditorTarget | None = None,
        landmark: Landmark | None = None,
    ) -> None:
        self._snapshot, self._objects, self._selection = snapshot, objects, selected
        picker = self._profile_picker
        blocked = picker.blockSignals(True)
        picker.clear()
        catalog = snapshot.catalog
        if catalog is not None:
            selected_index = -1
            for index, profile in enumerate(catalog.profiles):
                picker.addItem(profile.name, profile.profile_id)
                if profile.profile_id == snapshot.profile_id:
                    selected_index = index
            picker.setCurrentIndex(selected_index)
        picker.blockSignals(blocked)
        runtime = translate("Runtime: no calibration selected")
        if catalog is not None and catalog.selected is not None:
            profile = catalog.profile(catalog.selected.profile_id)
            runtime = translate("Runtime: {profile} · r{revision}").format(
                profile=profile.name, revision=catalog.selected.number
            )
        self._runtime_label.setText(runtime)
        profile_name = (
            catalog.profile(snapshot.profile_id).name
            if catalog and snapshot.profile_id
            else translate("No profile")
        )
        draft = translate("Unsaved draft") if snapshot.dirty else translate("Draft saved")
        base = (
            translate("New draft")
            if snapshot.base_revision is None
            else translate("Based on r{revision}").format(revision=snapshot.base_revision)
        )
        self._draft_label.setText(
            f"{profile_name} · {draft} · {base}\n"
            + translate("Saving does not change runtime selection.")
        )
        self._render_tables()
        self._object_list.blockSignals(True)
        self._object_list.clear()
        selected_object = None
        for index, item in enumerate(objects):
            self._object_list.addItem(item.name)
            if item.target == selected:
                self._object_list.setCurrentRow(index)
                selected_object = item
        self._object_list.blockSignals(False)
        self._properties.set_object(selected_object, landmark)
        for page, canvas in self._canvases.items():
            if canvas.image_size is not None:
                canvas.set_objects(objects, selected, editable=page is SetupPage.REGIONS)
        definition = snapshot.definition
        self._present_reference.setText(
            self._reference_text(None if definition is None else definition.references.present)
        )
        self._missing_reference.setText(
            self._reference_text(None if definition is None else definition.references.missing)
        )
        self._freeze.setText(translate("Resume preview" if snapshot.frozen else "Freeze frame"))
        self._live.setChecked(snapshot.live)
        self._settings_live.setChecked(snapshot.live)
        self._render_frame_labels()
        self.set_busy(self._busy)

    def _reference_text(self, reference: ReferenceAsset | None) -> str:
        return (
            translate("Not captured")
            if reference is None
            else f"{reference.size.width} × {reference.size.height} px"
        )

    def set_tuning_values(self, values: Mapping[TuningParameterId, int | float]) -> None:
        for identity, value in values.items():
            self._tuning_fields[identity].set_value(value)

    def _render_tables(self) -> None:
        snapshot = self._snapshot
        if snapshot is None or snapshot.catalog is None:
            return
        catalog = snapshot.catalog
        self._profile_table.blockSignals(True)
        self._profile_table.setRowCount(len(catalog.profiles))
        for row, profile in enumerate(catalog.profiles):
            selected = (
                catalog.selected is not None and catalog.selected.profile_id == profile.profile_id
            )
            values = (
                profile.name,
                str(len(profile.revisions)),
                translate("Primary vision"),
                self._revision_status(
                    selected,
                    any(ref.profile_id == profile.profile_id for ref in snapshot.in_use_revisions),
                ),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                item.setData(Qt.ItemDataRole.UserRole, profile.profile_id)
                self._profile_table.setItem(row, column, item)
            if profile.profile_id == snapshot.profile_id:
                self._profile_table.selectRow(row)
        self._profile_table.blockSignals(False)
        self._revision_table.blockSignals(True)
        revisions = (
            () if snapshot.profile_id is None else catalog.profile(snapshot.profile_id).revisions
        )
        self._revision_table.setRowCount(len(revisions))
        for row, revision in enumerate(
            sorted(revisions, key=lambda item: item.number, reverse=True)
        ):
            ref = RevisionRef(snapshot.profile_id, revision.number)
            values = (
                f"r{revision.number}",
                revision.created_at.strftime("%Y-%m-%d %H:%M"),
                self._revision_status(ref == catalog.selected, ref in snapshot.in_use_revisions),
            )
            for column, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setToolTip(value)
                item.setData(Qt.ItemDataRole.UserRole, ref)
                self._revision_table.setItem(row, column, item)
        if revisions:
            self._revision_table.selectRow(0)
        self._revision_table.blockSignals(False)
        self._on_revision_selection()

    @staticmethod
    def _revision_status(selected: bool, in_use: bool) -> str:
        if selected and in_use:
            return translate("Selected for runtime · In use")
        if in_use:
            return translate("In use")
        return translate("Selected for runtime") if selected else translate("Saved")

    def set_frame(self, frame: ImageFrame) -> None:
        fps = "—"
        previous = self._last_frame
        if self._preview_failed or previous is None or previous.sequence != frame.sequence:
            self.clear_evaluation()
        if self._preview_failed:
            self._preview_failed = False
            self._preview_failure = None
            self.set_notice("")
        if previous is not None:
            elapsed = frame.captured_at_monotonic - previous.captured_at_monotonic
            if elapsed > 0:
                fps = f"{(frame.sequence - previous.sequence) / elapsed:.1f}"
        self._last_frame, self._image = frame, frame.image
        self._last_fps = fps
        canvas = self._canvases.get(self._page)
        if canvas is not None:
            changed = canvas.image_size != frame.image.size
            canvas.set_image(frame.image)
            if changed:
                canvas.set_objects(
                    self._objects, self._selection, editable=self._page is SetupPage.REGIONS
                )
        self._render_frame_labels()
        if self._fullscreen_canvas is not None:
            self._fullscreen_canvas.set_image(frame.image)

    def _render_frame_labels(self) -> None:
        frame = self._last_frame
        if frame is None or self._preview_failed:
            return
        for label in self._camera_labels.values():
            mode = translate(
                "Frozen frame" if self._snapshot and self._snapshot.frozen else "Camera live"
            )
            label.setText(
                f"{mode} · {frame.image.size.width} × {frame.image.size.height} · "
                + translate("Frame {sequence} · {fps} FPS").format(
                    sequence=frame.sequence, fps=self._last_fps
                )
            )
            label.setStyleSheet(f"color: {TEXT_COLOR};")

    def set_preview_failure(self, failure: CalibrationFailure) -> None:
        self._preview_failed = True
        self._preview_failure = failure
        frame_failure = failure.code in (
            CalibrationFailureCode.CAMERA_UNAVAILABLE,
            CalibrationFailureCode.FRAME_INVALID,
            CalibrationFailureCode.FRAME_STALE,
            CalibrationFailureCode.CANCELLED,
        )
        title = translate("Camera frame unavailable" if frame_failure else "Evaluation unavailable")
        for label in self._camera_labels.values():
            label.setText(title + " · " + failure.detail)
            label.setStyleSheet(f"color: {ERROR_COLOR};")
        self.clear_evaluation()
        for panel in self._result_panels:
            panel.show_unavailable(title, failure.detail)
        for canvas in self._canvases.values():
            canvas.set_result_overlay(title, ERROR_COLOR)
        if self._fullscreen_canvas is not None:
            self._fullscreen_canvas.set_result_overlay(title, ERROR_COLOR)
        self.set_notice(translate("Live result unavailable") + ": " + failure.detail, error=True)

    def set_evaluation(self, report: CalibrationEvaluation) -> None:
        self._evaluation = report
        for panel in self._result_panels:
            panel.set_evaluation(report)
        color = result_color(report)
        overlay_text = state_text(report.state)
        if not report.image_usable:
            overlay_text += " · " + translate("Image unusable")
        for page in (SetupPage.TEST, SetupPage.SETTINGS):
            self._canvases[page].set_result_overlay(
                overlay_text, color, report.evidence if report.image_usable else ()
            )
        if self._fullscreen_canvas is not None and self._page in (
            SetupPage.TEST,
            SetupPage.SETTINGS,
        ):
            self._fullscreen_canvas.set_result_overlay(
                overlay_text, color, report.evidence if report.image_usable else ()
            )

    def clear_evaluation(self) -> None:
        self._evaluation = None
        for panel in self._result_panels:
            panel.clear_evaluation()
        for canvas in self._canvases.values():
            canvas.clear_result_overlay()
        if self._fullscreen_canvas is not None:
            self._fullscreen_canvas.clear_result_overlay()

    def set_notice(self, text: str, *, error: bool = False) -> None:
        self._notice.setText(text)
        self._notice.setVisible(bool(text))
        self._notice.setStyleSheet(f"color: {ERROR_COLOR if error else TEXT_COLOR};")

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._pages.setEnabled(not busy)
        self._navigation.setEnabled(not busy)
        self._profile_picker.setEnabled(not busy)
        has_draft = self._snapshot is not None and self._snapshot.definition is not None
        self._save_draft.setEnabled(not busy and has_draft)
        self._save_revision.setEnabled(not busy and has_draft)
        self._runtime_button.setEnabled(
            not busy and self._snapshot is not None and self._snapshot.catalog is not None
        )
        self._on_revision_selection()

    def show_failure(self, failure: CalibrationFailure) -> None:
        self.set_notice(failure.detail, error=True)
        show_critical(self, translate("Calibration operation failed"), failure.detail)

    def ask_unsaved(self) -> UnsavedDecision:
        dialog = UnsavedDialog(self)
        dialog.exec()
        return dialog.decision

    def confirm_capture(self, frame: ImageFrame, role: ReferenceRole) -> ReferenceRole | None:
        dialog = ReferenceDialog(self, frame.image, role=role)
        return dialog.role if dialog.exec() == QDialog.DialogCode.Accepted else None

    def show_reference(self, image: ImagePixels) -> None:
        ReferenceDialog(self, image, role=None).exec()

    def _new_profile(self) -> None:
        dialog = ProfileDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.create_requested.emit(dialog.profile_name, dialog.description)

    def _import_profile(self) -> None:
        dialog = ProfileDialog(self, importing=True)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.import_requested.emit(dialog.profile_name)

    def _on_save_revision(self) -> None:
        if (
            self._snapshot is None
            or self._snapshot.catalog is None
            or self._snapshot.profile_id is None
        ):
            return
        name = self._snapshot.catalog.profile(self._snapshot.profile_id).name
        dialog = SaveRevisionDialog(self, name)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.save_revision_requested.emit(dialog.description)

    def _pick_runtime(self) -> None:
        if self._snapshot is None or self._snapshot.catalog is None:
            return
        dialog = RuntimePicker(self, self._snapshot.catalog)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.select_revision_requested.emit(dialog.selected_revision)

    def _revision(self) -> RevisionRef | None:
        row = self._revision_table.currentRow()
        item = self._revision_table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item is not None else None

    def _on_revision_selection(self) -> None:
        ref = self._revision()
        selected = (
            self._snapshot.catalog.selected if self._snapshot and self._snapshot.catalog else None
        )
        for button in (self._edit_revision, self._use_revision, self._delete_revision):
            button.setEnabled(not self._busy and ref is not None)
        in_use = self._snapshot.in_use_revisions if self._snapshot else ()
        self._delete_revision.setEnabled(
            not self._busy and ref is not None and ref != selected and ref not in in_use
        )
        profile_id = self._snapshot.profile_id if self._snapshot else None
        protected_profiles = {item.profile_id for item in in_use}
        if selected is not None:
            protected_profiles.add(selected.profile_id)
        self._delete_profile.setEnabled(
            not self._busy and profile_id is not None and profile_id not in protected_profiles
        )

    def confirm_replace_draft(self) -> bool:
        return ask_yes_no(
            self,
            translate("Replace saved draft"),
            translate("Editing this revision will replace the profile's saved draft. Continue?"),
        )

    def _on_edit_revision(self) -> None:
        ref = self._revision()
        if ref is not None:
            self.edit_revision_requested.emit(ref)

    def _on_use_revision(self) -> None:
        ref = self._revision()
        if ref is not None:
            self.select_revision_requested.emit(ref)

    def _on_delete_revision(self) -> None:
        ref = self._revision()
        if ref is not None and ask_yes_no(
            self,
            translate("Delete revision"),
            translate("Delete revision r{revision}? Runtime selection will not change.").format(
                revision=ref.number
            ),
        ):
            self.delete_revision_requested.emit(ref)

    def _on_delete_profile(self) -> None:
        if (
            self._snapshot
            and self._snapshot.profile_id is not None
            and ask_yes_no(
                self,
                translate("Delete profile"),
                translate("Delete this profile, its draft and all inactive revisions?"),
            )
        ):
            self.delete_profile_requested.emit(self._snapshot.profile_id)

    def _on_discard_saved_draft(self) -> None:
        if ask_yes_no(
            self,
            translate("Discard saved draft"),
            translate("Discard the persisted draft for this profile?"),
        ):
            self.discard_saved_draft_requested.emit()

    def _on_profile_picker(self, index: int) -> None:
        value = self._profile_picker.itemData(index)
        if isinstance(value, ProfileId):
            self.profile_selected.emit(value)

    def _on_profile_table(self) -> None:
        item = self._profile_table.item(self._profile_table.currentRow(), 0)
        if item is not None:
            self.profile_selected.emit(item.data(Qt.ItemDataRole.UserRole))

    def _on_page_changed(self, index: int) -> None:
        if not 0 <= index < len(_PAGES):
            return
        self._page = _PAGES[index][0]
        self._pages.setCurrentIndex(index)
        canvas = self._canvases.get(self._page)
        if canvas is not None and self._image is not None:
            canvas.set_image(self._image)
            canvas.set_objects(
                self._objects, self._selection, editable=self._page is SetupPage.REGIONS
            )
            canvas.fit_image()
        self.page_selected.emit(self._page)

    def _on_tool_selected(self, tool: EditorTool) -> None:
        self._canvases[SetupPage.REGIONS].set_tool(tool)

    def _on_new_role(self, index: int) -> None:
        self._canvases[SetupPage.REGIONS].set_landmark_role(self._new_landmark_role.itemData(index))

    def _on_object_list(self, index: int) -> None:
        if 0 <= index < len(self._objects):
            self.object_selected.emit(self._objects[index].target)

    def _on_geometry_edit(self, value: object) -> None:
        self.geometry_edited.emit(value)

    def _on_object_selected(self, value: object) -> None:
        self.object_selected.emit(value)

    def _on_properties_edit(self, value: object) -> None:
        self.properties_edited.emit(value)

    def _on_object_removed(self, value: object) -> None:
        self.object_removed.emit(value)

    def _on_tuning_edited(self, identity: object, value: object) -> None:
        self.tuning_edited.emit(identity, value)

    def _capture_present(self) -> None:
        self.capture_requested.emit(ReferenceRole.PRESENT)

    def _capture_missing(self) -> None:
        self.capture_requested.emit(ReferenceRole.MISSING)

    def _preview_present(self) -> None:
        self.reference_preview_requested.emit(ReferenceRole.PRESENT)

    def _preview_missing(self) -> None:
        self.reference_preview_requested.emit(ReferenceRole.MISSING)

    def _on_freeze(self) -> None:
        self.freeze_requested.emit(not (self._snapshot and self._snapshot.frozen))

    def _on_live(self, checked: bool) -> None:
        self.live_requested.emit(checked)

    def _on_test(self) -> None:
        self.test_requested.emit()

    def _on_save_draft(self) -> None:
        self.save_draft_requested.emit()

    def _open_fullscreen(self) -> None:
        if self._image is None:
            return
        if self._fullscreen is not None:
            self._fullscreen.raise_()
            return
        dialog = SetupDialog("Live camera", self)
        canvas = CalibrationCanvas()
        canvas.setInteractive(False)
        canvas.set_image(self._image)
        dialog.content.addWidget(canvas, 1)
        dialog.finish_layout("Close")
        dialog.buttons.button(dialog.buttons.StandardButton.Cancel).hide()
        dialog.finished.connect(self._on_fullscreen_closed)
        self._fullscreen, self._fullscreen_canvas = dialog, canvas
        if self._evaluation is not None:
            self.set_evaluation(self._evaluation)
        dialog.showMaximized()

    def _on_fullscreen_closed(self) -> None:
        if self._fullscreen is not None:
            self._fullscreen.deleteLater()
        self._fullscreen, self._fullscreen_canvas = None, None

    def can_close(self) -> bool:
        if not super().can_close():
            return False
        if self._snapshot and self._snapshot.dirty:
            decision = self.ask_unsaved()
            if decision is UnsavedDecision.SAVE:
                self.save_draft_requested.emit()
                return False
            if decision is UnsavedDecision.CANCEL:
                return False
            self.discard_local_requested.emit()
        return True

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self.screen_shown.emit()

    def hideEvent(self, event: QHideEvent) -> None:
        self.screen_hidden.emit()
        if self._fullscreen is not None:
            self._fullscreen.reject()
        super().hideEvent(event)

    def clean_up(self) -> None:
        if self._fullscreen is not None:
            self._fullscreen.reject()

    def retranslateUi(self) -> None:
        for label, source in self._static_labels:
            label.setText(translate(source))
        for button, source in self._static_buttons:
            button.setText(translate(source))
        for index, (_, source) in enumerate(_PAGES):
            self._navigation.item(index).setText(translate(source))
            self._navigation.item(index).setToolTip(translate(source))
        for index, source in enumerate(
            ("Present landmark", "Missing landmark", "Empty-mount landmark")
        ):
            self._new_landmark_role.setItemText(index, translate(source))
        for button in self._tool_buttons:
            button.retranslateUi()
        self._profile_table.setHorizontalHeaderLabels(
            [translate(source) for source in ("Profile", "Revisions", "Camera", "State")]
        )
        self._revision_table.setHorizontalHeaderLabels(
            [translate(source) for source in ("Revision", "Created", "State")]
        )
        if self._evaluation is not None:
            self.set_evaluation(self._evaluation)
        else:
            self.clear_evaluation()
        self._render_frame_labels()
        if self._preview_failure is not None:
            self.set_preview_failure(self._preview_failure)
