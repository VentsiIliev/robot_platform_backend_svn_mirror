import logging

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QWidget
from PyQt6.QtCore import pyqtSignal
from contour_editor import BezierSegmentManager
from pl_gui.settings.settings_view.styles import BG_COLOR

from src.applications.workpiece_editor.editor_core.config import (
    WorkpieceFormSchema, WorkpieceFormFactory, SegmentEditorConfig,
)
from src.applications.base.widgets.virtual_keyboard_widget_factory import (
    VirtualKeyboardWidgetFactory,
)
from src.applications.workpiece_editor.editor_core.adapters.i_workpiece_data_adapter import IWorkpieceDataAdapter
from src.applications.workpiece_editor.editor_core import WorkpieceEditorBuilder
from src.applications.base.i_application_view import IApplicationView
from src.applications.workpiece_editor.onboarding import build_workpiece_editor_tour

_logger = logging.getLogger(__name__)


class WorkpieceEditorView(IApplicationView):

    save_requested    = pyqtSignal(dict)
    execute_requested = pyqtSignal(dict)
    custom_action_requested = pyqtSignal(str)

    def __init__(self, schema: WorkpieceFormSchema, segment_config: SegmentEditorConfig,
                 workpiece_data_adapter: IWorkpieceDataAdapter, ui_config=None, parent=None):
        self._schema          = schema
        self._segment_config  = segment_config
        self._workpiece_data_adapter = workpiece_data_adapter
        self._ui_config      = ui_config
        self._editor          = None
        self._capture_handler = None
        self._onboarding_tour = None
        super().__init__("WorkpieceEditor", parent)

    def setup_ui(self) -> None:
        # The plugin's alternating list rows otherwise inherit the OS dark palette.
        self.setStyleSheet(f"QListWidget {{ alternate-background-color: {BG_COLOR}; }}")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        try:
            self._editor = self._build_editor()
            layout.addWidget(self._editor)
        except Exception as exc:
            _logger.exception("WorkpieceEditorView: failed to build editor")
            layout.addWidget(QLabel(f"WorkpieceEditor failed:\n{exc}"))

    def clean_up(self) -> None:
        if self._onboarding_tour is not None:
            self._onboarding_tour.stop()
            self._onboarding_tour.deleteLater()
            self._onboarding_tour = None
        if self._editor is None:
            return
        try:
            inner = (
                self._editor
                .contourEditor
                .editor_with_rulers
                .editor
            )
            if hasattr(inner, '_event_bus') and inner._event_bus is not None:
                bus = inner._event_bus
                for sig_name in (
                        "segment_visibility_changed",
                        "segment_deleted",
                        "segment_added",
                        "segment_layer_changed",
                        "points_changed",
                        "undo_executed",
                        "redo_executed",
                ):
                    sig = getattr(bus, sig_name, None)
                    if sig is not None:
                        try:
                            sig.disconnect()
                        except (RuntimeError, TypeError):
                            pass
        except (RuntimeError, AttributeError):
            pass
        self._editor = None

    def start_onboarding_tour(self) -> None:
        """Start or restart the editor tour from the shell Help action."""
        if self._editor is None:
            return
        if self._onboarding_tour is None:
            self._onboarding_tour = build_workpiece_editor_tour(self)
        self._onboarding_tour.start()

    def onboarding_target(self, target_id: str):
        """Resolve plugin widgets; unavailable or hidden controls are skipped."""
        editor = self._editor
        if editor is None:
            return None
        contour = getattr(editor, "contourEditor", None)
        topbar = getattr(editor, "topbar", None)
        panel = getattr(editor, "pointManagerWidget", None)
        coordinator = getattr(panel, "coordinator", None)
        if target_id == "nudge":
            return getattr(getattr(coordinator, "nudge_widget", None), "title_label", None)
        if target_id.startswith(("layer_", "segment_")) or target_id == "point_select":
            return self._onboarding_list_target(coordinator, target_id)
        canvas_buttons = {
            "point_visibility": "hide_points_button", "zoom_out": "zoom_out_button",
            "reset_zoom": "reset_zoom_button", "zoom_in": "zoom_in_button",
            "pan": "pan_toggle_button",
        }
        if target_id in canvas_buttons:
            return getattr(getattr(contour, "bottom_toolbar", None), canvas_buttons[target_id], None)
        targets = {
            "editor": editor,
            "canvas": getattr(contour, "editor_with_rulers", None),
            "navigation": getattr(contour, "bottom_toolbar", None),
            "segments": getattr(editor, "pointManagerWidget", None),
        }
        buttons = {"capture": "capture_button", "tools": "tools_button",
                   "settings": "settings_button", "undo": "undo_button", "redo": "redo_button",
                   "preview": "preview_button", "save": "save_button",
                   "execute": "start_button"}
        if target_id in buttons:
            return getattr(topbar, buttons[target_id], None)
        return targets.get(target_id)

    @staticmethod
    def _onboarding_list_target(coordinator, target_id: str):
        """Resolve live list rows, which the plugin rebuilds after edits."""
        controls = {
            "layer_expand": ("ExpandableLayerWidget", "expand_btn"),
            "layer_visibility": ("LayerButtonsWidget", "visibility_btn"),
            "layer_add": ("LayerButtonsWidget", "add_segment_btn"),
            "layer_lock": ("LayerButtonsWidget", "lock_btn"),
            "segment_expand": ("ExpandableSegmentWidget", "expand_btn"),
            "segment_activate": ("SegmentButtonsAndComboWidget", "index_label"),
            "segment_visibility": ("SegmentButtonsAndComboWidget", "visibility_btn"),
            "segment_delete": ("SegmentButtonsAndComboWidget", "delete_btn"),
            "segment_settings": ("SegmentButtonsAndComboWidget", "settings_btn"),
            "point_select": ("PointWidget", None),
        }
        listing = getattr(coordinator, "list", None)
        if listing is None:
            return None
        class_name, attribute = controls[target_id]
        for index in range(listing.count()):
            item = listing.item(index)
            row = listing.itemWidget(item)
            if row is None or listing.isRowHidden(index):
                continue
            for widget in (row, *row.findChildren(QWidget)):
                if type(widget).__name__ == class_name:
                    target = getattr(widget, attribute, None) if attribute else widget
                    if target is not None and target.isVisible():
                        listing.scrollToItem(item)
                        return target
        return None

    def hideEvent(self, event) -> None:
        if self._onboarding_tour is not None:
            self._onboarding_tour.stop()
        super().hideEvent(event)

    def retranslateUi(self) -> None:
        # Restart lazily so an active tour cannot retain the previous language.
        if self._onboarding_tour is not None:
            self._onboarding_tour.stop()

    def _build_editor(self):
        return (
            WorkpieceEditorBuilder()
            .with_segment_manager(BezierSegmentManager)
            .with_settings(
                self._segment_config.settings_config,
                self._segment_config.settings_provider,
            )
            .with_layer_config(self._schema.editor_layer_config)
            .with_ui_config(self._ui_config)
            .with_form(WorkpieceFormFactory(schema=self._schema))
            .with_widgets(VirtualKeyboardWidgetFactory())
            .with_workpiece_data_adapter(self._workpiece_data_adapter)
            .on_save(self._on_save_cb)
            .on_capture(self._on_capture_cb)
            .on_execute(self._on_execute_cb)
            .on_custom_action(self._on_custom_action_cb)
            .on_update_camera_feed(self._on_camera_feed_cb)
            .build()
        )

    def set_capture_handler(self, handler) -> None:
        self._capture_handler = handler

    def set_save_callback(self, callback) -> None:
        if self._editor is not None:
            self._editor.set_form_submit_callback(callback)

    # ── Callbacks ────────────────────────────────────────────────────

    def _on_save_cb(self, data: dict) -> None:
        self.save_requested.emit(data)

    def _on_execute_cb(self, data: dict) -> None:
        self.execute_requested.emit(data)

    def _on_custom_action_cb(self, action_id: str) -> None:
        self.custom_action_requested.emit(action_id)

    def _on_capture_cb(self) -> list:
        if self._capture_handler is not None:
            try:
                return self._capture_handler() or []
            except Exception as exc:
                _logger.error("capture handler failed: %s", exc)
        return []

    def _on_camera_feed_cb(self) -> None:
        pass

    # ── Public API ────────────────────────────────────────────────────

    def update_camera_feed(self, image) -> None:
        if self._editor is not None and image is not None:
            if hasattr(self._editor, "set_image"):
                self._editor.set_image(image)

    def update_contours(self, contours: list) -> None:
        if self._editor is None:
            return
        try:
            editor = self._editor.contourEditor.editor_with_rulers.editor
            if hasattr(editor, "set_contours"):
                editor.set_contours(contours)
        except AttributeError:
            pass
