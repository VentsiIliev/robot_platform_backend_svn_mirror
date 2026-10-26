from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSizePolicy, QTabWidget

from pl_gui.settings.settings_view.styles import BG_COLOR, APP_PAGE_TITLE_STYLE, ACTION_BTN_STYLE, GHOST_BTN_STYLE
from src.applications.base.i_application_view import IApplicationView


class ImageCaptureView(IApplicationView):
    capture_requested = pyqtSignal()
    save_requested = pyqtSignal()

    def __init__(self, parent=None):
        self._pixmap = None
        self._decomposition_pixmap = None
        self._robot_pixmap = None
        self._robot_counts = None
        self._sampled_pixmap = None
        self._decomposition_counts = None
        self._busy = False
        self._status_source = "Capture an image to preview it."
        self._status_detail = ""
        self._directory = ""
        super().__init__("ImageCapture", parent)

    def setup_ui(self) -> None:
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        layout = QVBoxLayout(self)
        self._title = QLabel()
        self._title.setStyleSheet(APP_PAGE_TITLE_STYLE)
        layout.addWidget(self._title)
        self._description = QLabel()
        self._description.setWordWrap(True)
        layout.addWidget(self._description)
        self._preview = QLabel()
        self._preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview.setMinimumSize(320, 240)
        self._preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self._tabs = QTabWidget()
        self._tabs.addTab(self._preview, "")
        self._decomposition_preview = QLabel()
        self._decomposition_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._decomposition_preview.setMinimumSize(320, 240)
        self._decomposition_preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self._tabs.addTab(self._decomposition_preview, "")
        self._robot_preview = QLabel()
        self._robot_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._robot_preview.setMinimumSize(320, 240)
        self._robot_preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self._tabs.addTab(self._robot_preview, "")
        self._tabs.setTabEnabled(2, False)
        self._sampled_preview = QLabel()
        self._sampled_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sampled_preview.setMinimumSize(320, 240)
        self._sampled_preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self._tabs.addTab(self._sampled_preview, "")
        self._tabs.setTabEnabled(3, False)
        layout.addWidget(self._tabs, 1)
        self._decomposition_summary = QLabel()
        self._decomposition_summary.setWordWrap(True)
        layout.addWidget(self._decomposition_summary)
        buttons = QHBoxLayout()
        self._capture = QPushButton()
        self._capture.setStyleSheet(ACTION_BTN_STYLE)
        self._save = QPushButton()
        self._save.setStyleSheet(GHOST_BTN_STYLE)
        for button in (self._capture, self._save):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            buttons.addWidget(button)
        self._capture.clicked.connect(self._request_capture)
        self._save.clicked.connect(self._request_save)
        layout.addLayout(buttons)
        self._destination = QLabel()
        self._destination.setWordWrap(True)
        self._status = QLabel()
        self._status.setWordWrap(True)
        self._status.setTextFormat(Qt.TextFormat.PlainText)
        self._destination.setTextFormat(Qt.TextFormat.PlainText)
        self._status.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._destination)
        layout.addWidget(self._status)
        self._tabs.currentChanged.connect(self._on_tab_changed)
        self.set_busy(False)
        self.retranslateUi()

    def _request_capture(self) -> None:
        self.capture_requested.emit()

    def _request_save(self) -> None:
        self.save_requested.emit()

    def set_directory(self, directory: str) -> None:
        self._directory = directory
        self.retranslateUi()

    def set_status(self, source: str, detail: str = "") -> None:
        self._status_source, self._status_detail = source, detail
        self.retranslateUi()

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._capture.setEnabled(not busy)
        self._save.setEnabled(not busy and self._pixmap is not None)

    def set_image(self, image: bytes | None) -> None:
        self._pixmap = None
        if image is not None:
            pixmap = QPixmap()
            if pixmap.loadFromData(image, "PNG"):
                self._pixmap = pixmap
        self._render_preview()
        self.set_busy(self._busy)

    def set_decomposition(self, image, lines=0, arcs=0, exceeds=0, failed=0) -> None:
        self._decomposition_pixmap = None
        self._decomposition_counts = None
        if image is not None:
            pixmap = QPixmap()
            if pixmap.loadFromData(image, "PNG"):
                self._decomposition_pixmap = pixmap
                self._decomposition_counts = (lines, arcs, exceeds, failed)
                self._tabs.setCurrentIndex(1)
        self.retranslateUi()

    def _on_tab_changed(self, _index) -> None:
        self.retranslateUi()

    def set_robot_image(self, image: bytes | None, counts=None) -> None:
        self._robot_counts = counts
        self._robot_pixmap = None
        if image is not None:
            pixmap = QPixmap()
            if pixmap.loadFromData(image, "PNG"):
                self._robot_pixmap = pixmap
        self._tabs.setTabEnabled(2, self._robot_pixmap is not None)
        if self._robot_pixmap is not None:
            self._tabs.setCurrentIndex(2)
        self.retranslateUi()

    def set_sampled_image(self, image: bytes | None) -> None:
        self._sampled_pixmap = None
        if image is not None:
            pixmap = QPixmap()
            if pixmap.loadFromData(image, "PNG"):
                self._sampled_pixmap = pixmap
        self._tabs.setTabEnabled(3, self._sampled_pixmap is not None)
        if self._sampled_pixmap is not None:
            self._tabs.setCurrentIndex(3)
        self.retranslateUi()

    def _render_preview(self) -> None:
        if self._sampled_pixmap is None:
            self._sampled_preview.clear()
        else:
            self._sampled_preview.setPixmap(self._sampled_pixmap.scaled(
                self._sampled_preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        if self._robot_pixmap is None:
            self._robot_preview.clear()
        else:
            self._robot_preview.setPixmap(self._robot_pixmap.scaled(
                self._robot_preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        if self._decomposition_pixmap is None:
            self._decomposition_preview.clear()
        else:
            self._decomposition_preview.setPixmap(self._decomposition_pixmap.scaled(
                self._decomposition_preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
        if self._pixmap is None:
            self._preview.clear()
            self._preview.setText(self.tr("No captured image") or "No captured image")
        else:
            self._preview.setPixmap(self._pixmap.scaled(
                self._preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._render_preview()

    def retranslateUi(self) -> None:
        def t(source):
            return self.tr(source) or source
        self._title.setText(t("Image Capture"))
        self._description.setText(t("Capture contours, fit lines and arcs, then save the images and results."))
        self._tabs.setTabText(0, t("Detected contours"))
        self._tabs.setTabText(1, t("Lines and arcs"))
        self._tabs.setTabText(2, t("Robot XY (mm)"))
        self._tabs.setTabText(3, t("Sampled path (mm)"))
        summary = t("Lines: red · Arcs: blue/green · Endpoints: yellow")
        counts = self._decomposition_counts
        if self._tabs.currentIndex() == 3:
            summary = t("1 mm samples on a periodic smooth curve. Diagnostic only; check exported deviations.")
            counts = None
        elif self._tabs.currentIndex() == 2:
            summary = t("Robot mm: detected = gray · Lines = red · Arcs = blue")
            counts = self._robot_counts
        elif self._tabs.currentIndex() == 0:
            summary = t("Detected contour in image pixels")
            counts = None
        else:
            summary = t("Pixel fit") + " · " + summary
        if counts is not None:
            lines, arcs, exceeds, failed = counts
            summary += "\n" + t("{lines} lines, {arcs} arcs · Outside tolerance: {exceeds} · Failed contours: {failed}").format(
                lines=lines, arcs=arcs, exceeds=exceeds, failed=failed,
            )
        self._decomposition_summary.setText(summary)
        self._capture.setText(t("Capture"))
        self._save.setText(t("Save capture"))
        self._destination.setText(t("Save folder: {detail}").format(detail=self._directory))
        detail = t(self._status_detail) if self._status_source == "Operation failed: {detail}" else self._status_detail
        self._status.setText(t(self._status_source).format(detail=detail))
        self._render_preview()

    def clean_up(self) -> None:
        pass
