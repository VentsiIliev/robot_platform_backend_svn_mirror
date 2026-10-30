"""Paint-owned developer screen; widgets and presentation, without service/model access."""

from collections.abc import Mapping

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QHideEvent, QShowEvent
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QComboBox,
    QDialog,
    QHBoxLayout,
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
    BG_COLOR,
    BORDER,
    ERROR_COLOR,
    PRIMARY,
    SECONDARY_BG,
    STATUS_OK,
    TEXT_COLOR,
    TOUCH_SCROLL_AREA_STYLE,
)
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.styled_message_box import ask_yes_no, show_critical
from src.robot_systems.paint.contracts.paint_head_calibration.errors import CalibrationFailure
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
from src.robot_systems.paint.contracts.paint_head_check.models import (
    PaintHeadObservationReason,
    PaintHeadState,
)

from ..editor_contracts import EditorObject, EditorTarget, EditorTool, SetupPage, UnsavedDecision
from ..presentation import SetupSnapshot
from ..tuning_fields import TUNING_PARAMETERS, TuningParameterId, TuningSection
from .widgets.calibration_canvas import CalibrationCanvas
from .widgets.forms import (
    EditorToolButton,
    ProfileDialog,
    ReferenceDialog,
    RuntimePicker,
    SaveRevisionDialog,
    SetupDialog,
    TuningField,
    UnsavedDialog,
    action_button,
    translate,
)
from .widgets.object_properties import ObjectPropertiesPanel

_PAGES = (
    (SetupPage.PROFILES, "Profiles"),
    (SetupPage.CAMERA, "Camera & capture"),
    (SetupPage.REGIONS, "Regions & landmarks"),
    (SetupPage.TEST, "Test & results"),
    (SetupPage.SETTINGS, "Settings"),
)
_TOOLS = (
    (EditorTool.SELECT, "Select / move"),
    (EditorTool.PAN, "Pan"),
    (EditorTool.INSPECTION, "Inspection region"),
    (EditorTool.EMPTY_MOUNT, "Empty-mount region"),
    (EditorTool.EXCLUDED, "Excluded region"),
    (EditorTool.RECTANGLE_LANDMARK, "Rectangle landmark"),
    (EditorTool.CIRCLE_LANDMARK, "Circle landmark"),
)
_STATES = {
    PaintHeadState.PRESENT: "Head present",
    PaintHeadState.MISSING: "Head missing",
    PaintHeadState.MISALIGNED: "Head misaligned",
    PaintHeadState.UNKNOWN: "Unknown",
}
_REASONS = {
    PaintHeadObservationReason.ALIGNED: "Aligned",
    PaintHeadObservationReason.MISALIGNED: "Misaligned",
    PaintHeadObservationReason.EMPTY_MOUNT: "Empty mount",
    PaintHeadObservationReason.INSUFFICIENT_EVIDENCE: "Insufficient evidence",
    PaintHeadObservationReason.CONFLICTING_EVIDENCE: "Conflicting evidence",
    PaintHeadObservationReason.POSE_UNDETERMINED: "Pose undetermined",
    PaintHeadObservationReason.TOO_DARK: "Too dark",
    PaintHeadObservationReason.OVEREXPOSED: "Overexposed",
    PaintHeadObservationReason.LOW_CONTRAST: "Low contrast",
    PaintHeadObservationReason.CONFIRMING_STATUS: "Confirming status",
    PaintHeadObservationReason.RECHECKING_POSITION: "Rechecking position",
}
_CARD_STYLE = (
    f"QFrame#setupCard {{background: {BG_COLOR}; border: 1px solid {BORDER}; border-radius: 8px;}}"
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

    def _button(self, source: str, *, primary: bool = False) -> QPushButton:
        button = action_button(source, primary=primary)
        self._static_buttons.append((button, source))
        return button

    def setup_ui(self) -> None:
        self.setStyleSheet(f"background-color: {BG_COLOR}; color: {TEXT_COLOR};")
        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 14, 16, 14)
        outer.setSpacing(12)
        self._title = self._label("Paint-head detector setup")
        self._title.setStyleSheet(APP_PAGE_TITLE_STYLE)
        outer.addWidget(self._title)
        outer.addWidget(self._label("Primary vision · Vertical Shaft Alignment"))
        header = QHBoxLayout()
        self._profile_picker = QComboBox()
        self._profile_picker.setMinimumHeight(44)
        self._profile_picker.setObjectName("calibrationProfilePicker")
        self._profile_picker.currentIndexChanged.connect(self._on_profile_picker)
        self._runtime_label = QLabel()
        self._runtime_label.setObjectName("calibrationRuntimeSelection")
        self._runtime_label.setWordWrap(True)
        self._runtime_button = self._button("Select for runtime")
        self._runtime_button.clicked.connect(self._pick_runtime)
        header.addWidget(self._label("Editing profile"))
        header.addWidget(self._profile_picker, 1)
        header.addWidget(self._runtime_label, 2)
        header.addWidget(self._runtime_button)
        outer.addLayout(header)
        body = QHBoxLayout()
        self._navigation = QListWidget()
        self._navigation.setObjectName("calibrationNavigation")
        self._navigation.setFixedWidth(205)
        self._navigation.setStyleSheet(
            f"QListWidget {{border: none; background: {BG_COLOR};}}"
            f"QListWidget::item {{padding: 14px 10px; border-radius: 6px;}}"
            f"QListWidget::item:selected {{background: {SECONDARY_BG}; color: {PRIMARY};}}"
        )
        for _ in _PAGES:
            self._navigation.addItem(QListWidgetItem())
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
        outer.addWidget(self._notice)
        footer = QHBoxLayout()
        self._draft_label = QLabel()
        self._draft_label.setObjectName("calibrationDraftStatus")
        self._draft_label.setWordWrap(True)
        footer.addWidget(self._draft_label, 1)
        self._save_draft = self._button("Save draft")
        self._save_draft.setObjectName("saveCalibrationDraft")
        self._save_revision = self._button("Save calibration", primary=True)
        self._save_revision.setObjectName("saveCalibrationRevision")
        self._save_draft.clicked.connect(self._on_save_draft)
        self._save_revision.clicked.connect(self._on_save_revision)
        footer.addWidget(self._save_draft)
        footer.addWidget(self._save_revision)
        outer.addLayout(footer)
        self._navigation.setCurrentRow(1)

    def _table(self, columns: int) -> QTableWidget:
        table = QTableWidget(0, columns)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().hide()
        return table

    def _build_profiles(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        actions = QHBoxLayout()
        new = self._button("New profile", primary=True)
        new.clicked.connect(self._new_profile)
        importing = self._button("Import factory calibration")
        importing.clicked.connect(self._import_profile)
        actions.addWidget(new)
        actions.addWidget(importing)
        actions.addStretch()
        layout.addLayout(actions)
        self._profile_table = self._table(4)
        self._profile_table.itemSelectionChanged.connect(self._on_profile_table)
        layout.addWidget(self._profile_table, 1)
        layout.addWidget(self._label("Saved revisions"))
        self._revision_table = self._table(3)
        self._revision_table.itemSelectionChanged.connect(self._on_revision_selection)
        layout.addWidget(self._revision_table, 1)
        row = QHBoxLayout()
        self._edit_revision = self._button("Edit as draft")
        self._use_revision = self._button("Use selected revision")
        self._delete_revision = self._button("Delete revision")
        self._delete_profile = self._button("Delete profile")
        self._edit_revision.clicked.connect(self._on_edit_revision)
        self._use_revision.clicked.connect(self._on_use_revision)
        self._delete_revision.clicked.connect(self._on_delete_revision)
        self._delete_profile.clicked.connect(self._on_delete_profile)
        for button in (
            self._edit_revision,
            self._use_revision,
            self._delete_revision,
            self._delete_profile,
        ):
            row.addWidget(button)
        layout.addLayout(row)
        return page

    def _camera(self, page: SetupPage) -> tuple[QWidget, CalibrationCanvas]:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        status = QLabel()
        status.setWordWrap(True)
        self._camera_labels[page] = status
        layout.addWidget(status)
        canvas = CalibrationCanvas()
        canvas.geometry_edited.connect(self._on_geometry_edit)
        canvas.object_selected.connect(self._on_object_selected)
        self._canvases[page] = canvas
        layout.addWidget(canvas, 1)
        row = QHBoxLayout()
        fit, plus, minus = (
            self._button("Fit image"),
            self._button("Zoom in"),
            self._button("Zoom out"),
        )
        fit.clicked.connect(canvas.fit_image)
        plus.clicked.connect(canvas.zoom_in)
        minus.clicked.connect(canvas.zoom_out)
        row.addWidget(fit)
        row.addWidget(minus)
        row.addWidget(plus)
        row.addStretch()
        layout.addLayout(row)
        return panel, canvas

    def _build_camera(self) -> QWidget:
        page = QWidget()
        layout = QHBoxLayout(page)
        camera, canvas = self._camera(SetupPage.CAMERA)
        canvas.setInteractive(False)
        layout.addWidget(camera, 3)
        side = QVBoxLayout()
        side.addWidget(self._label("Reference images"))
        self._present_reference, self._missing_reference = QLabel(), QLabel()
        side.addWidget(self._label("Head present"))
        side.addWidget(self._present_reference)
        capture_present = self._button("Capture present reference", primary=True)
        preview_present = self._button("Preview present reference")
        capture_present.clicked.connect(self._capture_present)
        preview_present.clicked.connect(self._preview_present)
        side.addWidget(capture_present)
        side.addWidget(preview_present)
        side.addSpacing(12)
        side.addWidget(self._label("Head missing"))
        side.addWidget(self._missing_reference)
        capture_missing = self._button("Capture missing reference")
        preview_missing = self._button("Preview missing reference")
        capture_missing.clicked.connect(self._capture_missing)
        preview_missing.clicked.connect(self._preview_missing)
        side.addWidget(capture_missing)
        side.addWidget(preview_missing)
        self._freeze = self._button("Freeze frame")
        self._freeze.clicked.connect(self._on_freeze)
        side.addWidget(self._freeze)
        fullscreen = self._button("Open fullscreen")
        fullscreen.clicked.connect(self._open_fullscreen)
        side.addWidget(fullscreen)
        side.addStretch()
        side.addWidget(
            self._label("Confirm captured references before adding them to the draft.", wrap=True)
        )
        layout.addLayout(side, 1)
        return page

    def _build_regions(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        tools = QHBoxLayout()
        self._tool_group = QButtonGroup(self)
        self._tool_group.setExclusive(True)
        self._tool_buttons: list[EditorToolButton] = []
        for tool, source in _TOOLS:
            button = EditorToolButton(tool, source, self)
            button.chosen.connect(self._on_tool_selected)
            self._tool_group.addButton(button)
            self._tool_buttons.append(button)
            tools.addWidget(button)
        self._tool_buttons[0].setChecked(True)
        layout.addLayout(tools)
        row = QHBoxLayout()
        row.addWidget(self._label("New landmark role"))
        self._new_landmark_role = QComboBox()
        for role in LandmarkRole:
            self._new_landmark_role.addItem("", role)
        self._new_landmark_role.currentIndexChanged.connect(self._on_new_role)
        row.addWidget(self._new_landmark_role)
        row.addStretch()
        layout.addLayout(row)
        splitter = QSplitter()
        camera, _ = self._camera(SetupPage.REGIONS)
        splitter.addWidget(camera)
        inspector = QWidget()
        inspector.setMinimumWidth(340)
        side = QVBoxLayout(inspector)
        self._object_list = QListWidget()
        self._object_list.setMaximumHeight(190)
        self._object_list.currentRowChanged.connect(self._on_object_list)
        side.addWidget(self._object_list)
        self._properties = ObjectPropertiesPanel()
        self._properties.apply_requested.connect(self._on_properties_edit)
        self._properties.remove_requested.connect(self._on_object_removed)
        scrolling = QScrollArea()
        scrolling.setWidgetResizable(True)
        scrolling.setStyleSheet(TOUCH_SCROLL_AREA_STYLE)
        scrolling.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scrolling.setWidget(self._properties)
        side.addWidget(scrolling, 1)
        splitter.addWidget(inspector)
        splitter.setSizes([650, 360])
        layout.addWidget(splitter, 1)
        return page

    def _build_test(self) -> QWidget:
        page = QWidget()
        layout = QVBoxLayout(page)
        row = QHBoxLayout()
        self._run = self._button("Test current draft", primary=True)
        self._live = self._button("Continuous evaluation")
        self._live.setCheckable(True)
        self._run.clicked.connect(self._on_test)
        self._live.clicked.connect(self._on_live)
        row.addWidget(self._run)
        row.addWidget(self._live)
        row.addWidget(
            self._label("Evaluation uses the current draft, including unsaved edits.", wrap=True), 1
        )
        layout.addLayout(row)
        body = QHBoxLayout()
        camera, canvas = self._camera(SetupPage.TEST)
        canvas.setInteractive(False)
        body.addWidget(camera, 3)
        results = QVBoxLayout()
        self._result_status = QLabel()
        self._result_status.setObjectName("calibrationResultStatus")
        self._result_status.setWordWrap(True)
        results.addWidget(self._result_status)
        self._result_details = QLabel()
        self._result_details.setWordWrap(True)
        results.addWidget(self._result_details)
        results.addWidget(self._label("Matching evidence"))
        self._evidence = self._table(3)
        results.addWidget(self._evidence, 1)
        body.addLayout(results, 2)
        layout.addLayout(body, 1)
        return page

    def _build_settings(self) -> QWidget:
        container = QWidget()
        outer = QVBoxLayout(container)
        outer.addWidget(self._label("Detector settings belong to the editing draft.", wrap=True))
        self._discard_draft = self._button("Discard saved draft")
        self._discard_draft.clicked.connect(self._on_discard_saved_draft)
        outer.addWidget(self._discard_draft)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(TOUCH_SCROLL_AREA_STYLE)
        content = QWidget()
        layout = QVBoxLayout(content)
        for section, source in (
            (TuningSection.ALIGNMENT, "Alignment and confirmation"),
            (TuningSection.MATCHING, "Advanced matching"),
            (TuningSection.PREPROCESSING, "Advanced preprocessing"),
        ):
            label = self._label(source)
            label.setStyleSheet(f"color: {PRIMARY}; font-size: 13pt; font-weight: bold;")
            layout.addWidget(label)
            for parameter in TUNING_PARAMETERS:
                if parameter.section is section:
                    field = TuningField(parameter)
                    field.edited.connect(self._on_tuning_edited)
                    self._tuning_fields[parameter.identity] = field
                    layout.addWidget(field)
        layout.addStretch()
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)
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
            for profile in catalog.profiles:
                picker.addItem(profile.name, profile.profile_id)
            picker.setCurrentIndex(picker.findData(snapshot.profile_id))
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
        for label in self._camera_labels.values():
            label.setText(translate("Camera frame unavailable") + " · " + failure.detail)
            label.setStyleSheet(f"color: {ERROR_COLOR};")
        self.clear_evaluation()
        for canvas in self._canvases.values():
            canvas.set_result_overlay(translate("Camera frame unavailable"), ERROR_COLOR)
        self.set_notice(translate("Live result unavailable") + ": " + failure.detail, error=True)

    def set_evaluation(self, report: CalibrationEvaluation) -> None:
        self._evaluation = report
        self._result_status.setText(translate(_STATES[report.state]))
        color = (
            STATUS_OK
            if report.state is PaintHeadState.PRESENT and report.image_usable
            else ERROR_COLOR
        )
        self._result_status.setStyleSheet(f"color: {color}; font-size: 17pt; font-weight: bold;")
        overlay_text = translate(_STATES[report.state])
        if not report.image_usable:
            overlay_text += " · " + translate("Image unusable")
        self._canvases[SetupPage.TEST].set_result_overlay(
            overlay_text, color, report.evidence if report.image_usable else ()
        )
        if self._fullscreen_canvas is not None and self._page is SetupPage.TEST:
            self._fullscreen_canvas.set_result_overlay(
                overlay_text, color, report.evidence if report.image_usable else ()
            )

        def number(value: float | None, unit: str) -> str:
            return translate("Unavailable") if value is None else f"{value:.2f} {unit}"

        self._result_details.setText(
            "\n".join(
                (
                    translate("Observed state") + ": " + translate(_STATES[report.observed_state]),
                    translate("Reason") + ": " + translate(_REASONS[report.reason]),
                    translate("Translation") + ": " + number(report.translation_pixels, "px"),
                    translate("X / Y offset")
                    + ": "
                    + number(report.offset_x_pixels, "px")
                    + " / "
                    + number(report.offset_y_pixels, "px"),
                    translate("Rotation") + ": " + number(report.rotation_degrees, "°"),
                    translate("Held warning")
                    + ": "
                    + translate("Yes" if report.held_warning else "No"),
                    translate("Image usable")
                    + ": "
                    + translate("Yes" if report.image_usable else "No"),
                )
            )
        )
        self._evidence.setRowCount(len(report.evidence))
        for row, item in enumerate(report.evidence):
            values = (item.name, f"{item.score:.3f}", translate("Pass" if item.passed else "Fail"))
            for column, value in enumerate(values):
                self._evidence.setItem(row, column, QTableWidgetItem(value))

    def clear_evaluation(self) -> None:
        self._evaluation = None
        self._result_status.setText(translate("No current result"))
        self._result_status.setStyleSheet(f"color: {TEXT_COLOR};")
        self._result_details.clear()
        self._evidence.setRowCount(0)
        for canvas in self._canvases.values():
            canvas.clear_result_overlay()
        if self._fullscreen_canvas is not None:
            self._fullscreen_canvas.clear_result_overlay()

    def set_notice(self, text: str, *, error: bool = False) -> None:
        self._notice.setText(text)
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
        self._evidence.setHorizontalHeaderLabels(
            [translate(source) for source in ("Landmark", "Score", "Result")]
        )
        if self._evaluation is not None:
            self.set_evaluation(self._evaluation)
        else:
            self.clear_evaluation()
        self._render_frame_labels()
        if self._preview_failure is not None:
            self.set_preview_failure(self._preview_failure)
