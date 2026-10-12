from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QEvent, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QImage, QPainter, QFont
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFileDialog, QFrame, QHBoxLayout,
                            QLabel, QPushButton, QScrollArea, QLayout, QSizePolicy, QVBoxLayout, QWidget)
from pl_gui.settings.settings_view.styles import (
    BG_COLOR, BORDER, PRIMARY, TEXT_COLOR, TEXT_PRIMARY, TEXT_ON_PRIMARY,
    SECONDARY_BG, TERTIARY_TEXT, DISABLED_PREVIEW_BG, ERROR_COLOR, STATUS_OK,
    ACTION_BTN_STYLE, GHOST_BTN_STYLE, APP_PAGE_TITLE_STYLE, LABEL_STYLE,
)
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit
from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField

class _ImageCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = QImage()
        self._placeholder = ''
        self.setMinimumSize(200, 240)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def set_frame(self, width, height, rgb):
        self._image = QImage(rgb, width, height, width * 3, QImage.Format.Format_RGB888).copy()
        self.update()

    def set_placeholder(self, text):
        self._placeholder = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(DISABLED_PREVIEW_BG))
        if self._image.isNull():
            painter.setPen(QColor(TERTIARY_TEXT))
            painter.drawText(self.rect().adjusted(24, 24, -24, -24),
                             Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap, self._placeholder)
        else:
            size = self._image.size()
            size.scale(self.size(), Qt.AspectRatioMode.KeepAspectRatio)
            rect = QRectF((self.width() - size.width()) / 2, (self.height() - size.height()) / 2,
                          size.width(), size.height())
            painter.drawImage(rect, self._image)
        painter.end()

class ContourDXFView(IApplicationView):
    camera_requested = pyqtSignal()
    capture_requested = pyqtSignal(bool)
    calibrate_requested = pyqtSignal(float, float, float)
    export_requested = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    language_requested = pyqtSignal(str)

    _STATUS = {
        'connecting': 'Connecting to camera…',
        'disconnecting': 'Disconnecting camera…',
        'ready': 'Ready to capture',
        'disconnected': 'Camera disconnected',
        'capturing': 'Detecting and processing contour…',
        'captured': 'Contour captured. Review the preview before export.',
        'calibrating': 'Measuring reference rectangle…',
        'calibrated': 'Calibration saved. Remove the reference and capture a part.',
        'exporting': 'Writing DXF…',
        'exported': 'DXF exported successfully',
        'error': 'Operation failed',
        'waiting': 'Waiting for camera',
        'closing': 'Please wait for the current operation to finish.',
    }

    def __init__(self, parent=None):
        self._connected = False
        self._busy = False
        self._exportable = False
        self._status = 'waiting'
        self._detail = ''
        self._output_dir = ''
        self._last_export = ''
        self._residual = None
        super().__init__('ContourDXF', parent)

    @staticmethod
    def _button(style):
        button = QPushButton()
        button.setStyleSheet(style)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        return button

    @staticmethod
    def _card():
        card = QFrame()
        card.setObjectName('studioCard')
        return card

    @staticmethod
    def _number(value, low, high, step, suffix, decimals=2):
        field = KeyboardNumberField(decimal=True)
        field.setRange(low, high)
        field.setDecimals(decimals)
        field.setSingleStep(step)
        field.setSuffix(suffix)
        field.setValue(value)
        return field

    def setup_ui(self):
        self.setStyleSheet(f"""
            QWidget {{ background: {BG_COLOR}; color: {TEXT_PRIMARY}; }}
            QFrame#studioCard {{ background: {TEXT_ON_PRIMARY}; border: 1px solid {BORDER}; border-radius: 14px; }}
            QLabel {{ background: transparent; border: none; }}
            QCheckBox {{ background: transparent; spacing: 9px; }}
            QComboBox {{ background: {TEXT_ON_PRIMARY}; border: 1px solid {BORDER}; border-radius: 8px; padding: 8px 12px; }}
        """)
        self.setFont(QFont('DejaVu Sans', 10))
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(20)
        header = QHBoxLayout()
        titles = QVBoxLayout()
        self._title = QLabel()
        self._title.setStyleSheet(APP_PAGE_TITLE_STYLE + 'font-size: 24pt; font-weight: bold;')
        self._subtitle = QLabel()
        self._subtitle.setStyleSheet(f'color: {TERTIARY_TEXT}; font-size: 10pt;')
        titles.addWidget(self._title)
        titles.addWidget(self._subtitle)
        header.addLayout(titles)
        header.addStretch()
        self._source = QLabel()
        self._source.setStyleSheet(f'background: {SECONDARY_BG}; color: {PRIMARY}; padding: 10px 14px; border-radius: 8px;')
        header.addWidget(self._source)
        self._language = QComboBox()
        self._language.addItem('English', 'en')
        self._language.addItem('Български', 'bg')
        self._language.setCursor(Qt.CursorShape.PointingHandCursor)
        self._language.currentIndexChanged.connect(self._on_language)
        header.addWidget(self._language)
        self._camera = self._button(GHOST_BTN_STYLE)
        self._camera.clicked.connect(self._on_camera)
        header.addWidget(self._camera)
        layout.addLayout(header)

        body = QHBoxLayout()
        body.setSpacing(20)
        content = QVBoxLayout()
        content.setSpacing(18)
        previews = QHBoxLayout()
        previews.setSpacing(16)
        self._live_card, self._live_title, self._live_caption, self._live = self._preview_card()
        self._capture_card, self._capture_title, self._capture_caption, self._captured = self._preview_card()
        previews.addWidget(self._live_card, 1)
        previews.addWidget(self._capture_card, 1)
        content.addLayout(previews, 1)
        metrics = QHBoxLayout()
        metrics.setSpacing(16)
        self._metric_titles = []
        self._metric_values = []
        for _index in range(3):
            card = self._card()
            column = QVBoxLayout(card)
            column.setContentsMargins(18, 14, 18, 14)
            title, value = QLabel(), QLabel('—')
            title.setStyleSheet(f'color: {TERTIARY_TEXT}; font-size: 9pt;')
            value.setStyleSheet(f'color: {TEXT_PRIMARY}; font-size: 22pt; font-weight: bold;')
            column.addWidget(title)
            column.addWidget(value)
            self._metric_titles.append(title)
            self._metric_values.append(value)
            metrics.addWidget(card, 1)
        content.addLayout(metrics)
        capture_bar = QHBoxLayout()
        self._smooth = QCheckBox()
        self._smooth.setChecked(True)
        self._smooth.setCursor(Qt.CursorShape.PointingHandCursor)
        capture_bar.addWidget(self._smooth)
        capture_bar.addStretch()
        self._capture_button = self._button(ACTION_BTN_STYLE)
        self._capture_button.setMinimumWidth(200)
        self._capture_button.clicked.connect(self._on_capture)
        capture_bar.addWidget(self._capture_button)
        content.addLayout(capture_bar)
        body.addLayout(content, 1)

        sidebar_widget = QWidget()
        sidebar = QVBoxLayout(sidebar_widget)
        sidebar.setContentsMargins(0, 0, 0, 0)
        sidebar.setSizeConstraint(QLayout.SizeConstraint.SetMinimumSize)
        sidebar.setSpacing(18)
        calibration = self._card()
        calibration.setFixedWidth(330)
        form = QVBoxLayout(calibration)
        form.setContentsMargins(20, 18, 20, 18)
        form.setSpacing(8)
        self._calibration_title = QLabel()
        self._calibration_title.setStyleSheet(LABEL_STYLE)
        self._calibration_help = QLabel()
        self._calibration_help.setWordWrap(True)
        self._calibration_help.setStyleSheet(f'color: {TERTIARY_TEXT}; font-size: 9pt;')
        form.addWidget(self._calibration_title)
        form.addWidget(self._calibration_help)
        self._field_labels = []
        self._reference_width = self._number(120, 0.01, 20000, 1, ' mm')
        self._reference_height = self._number(100, 0.01, 20000, 1, ' mm')
        self._tolerance = self._number(2, 0.01, 100, 0.1, ' %')
        for field in (self._reference_width, self._reference_height, self._tolerance):
            label = QLabel()
            form.addWidget(label)
            form.addWidget(field)
            self._field_labels.append(label)
        self._calibrate_button = self._button(GHOST_BTN_STYLE)
        self._calibrate_button.clicked.connect(self._on_calibrate)
        form.addWidget(self._calibrate_button)
        self._scale_heading = QLabel()
        self._scale_heading.setStyleSheet(LABEL_STYLE)
        self._scale_value = QLabel('—')
        self._correction_value = QLabel('×1.000000')
        self._residual_value = QLabel()
        self._residual_value.setWordWrap(True)
        self._residual_value.setStyleSheet(f'color: {TERTIARY_TEXT}; font-size: 9pt;')
        form.addWidget(self._scale_heading)
        form.addWidget(self._scale_value)
        form.addWidget(self._correction_value)
        form.addWidget(self._residual_value)
        sidebar.addWidget(calibration)

        export_card = self._card()
        export_card.setFixedWidth(330)
        export_layout = QVBoxLayout(export_card)
        export_layout.setContentsMargins(20, 18, 20, 18)
        export_layout.setSpacing(12)
        self._export_title = QLabel()
        self._export_title.setStyleSheet(LABEL_STYLE)
        self._output = KeyboardLineEdit()
        self._output.setReadOnly(True)
        self._output.setStyleSheet(f'background: {BG_COLOR}; border: 1px solid {BORDER}; border-radius: 8px; padding: 10px; color: {TEXT_COLOR};')
        self._export_help = QLabel()
        self._export_help.setWordWrap(True)
        self._export_help.setStyleSheet(f'color: {TERTIARY_TEXT}; font-size: 9pt;')
        self._export_button = self._button(ACTION_BTN_STYLE)
        self._export_button.clicked.connect(self._on_export)
        export_layout.addWidget(self._export_title)
        export_layout.addWidget(self._output)
        export_layout.addWidget(self._export_help)
        export_layout.addWidget(self._export_button)
        sidebar.addWidget(export_card)
        sidebar.addStretch()
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFrameShape(QFrame.Shape.NoFrame)
        sidebar_scroll.setFixedWidth(350)
        sidebar_scroll.setWidget(sidebar_widget)
        body.addWidget(sidebar_scroll)
        layout.addLayout(body, 1)

        footer = self._card()
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(16, 12, 16, 12)
        self._status_label = QLabel()
        self._status_label.setWordWrap(True)
        self._last_file = QLabel()
        self._last_file.setStyleSheet(f'color: {TERTIARY_TEXT}; font-size: 9pt;')
        self._last_file.hide()
        footer_layout.addWidget(self._status_label)
        footer_layout.addWidget(self._last_file)
        layout.addWidget(footer)
        self._timer = QTimer(self)
        self._timer.setInterval(120)
        self._timer.timeout.connect(self._on_refresh)
        self.retranslateUi()
        self._update_buttons()

    def _preview_card(self):
        card = self._card()
        column = QVBoxLayout(card)
        column.setContentsMargins(16, 16, 16, 16)
        column.setSpacing(12)
        title, caption = QLabel(), QLabel()
        title.setStyleSheet(LABEL_STYLE)
        caption.setStyleSheet(f'color: {TERTIARY_TEXT}; font-size: 9pt;')
        canvas = _ImageCanvas()
        column.addWidget(title)
        column.addWidget(canvas, 1)
        column.addWidget(caption)
        return card, title, caption, canvas

    def _t(self, source):
        return self.tr(source) or source

    def retranslateUi(self):
        self._title.setText(self._t('Photo to DXF'))
        self._subtitle.setText(self._t('Capture a contour. Verify its scale. Export a precise DXF.'))
        self._live_title.setText(self._t('Live camera'))
        self._capture_title.setText(self._t('Contour preview'))
        self._live_caption.setText(self._t('Position the workpiece inside the configured capture area.'))
        self._capture_caption.setText(self._t('Green: exported contour  ·  Yellow: measurement rectangle'))
        self._live.set_placeholder(self._t('Camera preview will appear here'))
        self._captured.set_placeholder(self._t('Capture a workpiece to inspect its contour'))
        for label, source in zip(self._metric_titles, ('Width', 'Height', 'Contour points')):
            label.setText(self._t(source))
        self._smooth.setText(self._t('Apply paint contour smoothing'))
        self._capture_button.setText(self._t('Capture contour'))
        self._calibration_title.setText(self._t('Reference calibration'))
        self._calibration_help.setText(self._t('Place a known rectangle at the same height as your parts, then measure it.'))
        for label, source in zip(self._field_labels, ('Reference width', 'Reference height', 'Maximum error')):
            label.setText(self._t(source))
        self._calibrate_button.setText(self._t('Measure reference and calibrate'))
        self._scale_heading.setText(self._t('Effective scale'))
        self._export_title.setText(self._t('DXF export'))
        self._export_help.setText(self._t('Closed contour · millimetres · Y upwards. Existing files are preserved.'))
        self._export_button.setText(self._t('Export DXF…'))
        self._language.setToolTip(self._t('Language'))
        self._camera.setText(self._t('Disconnect camera' if self._connected else 'Connect camera'))
        self._render_status()
        self._render_residual()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def _on_language(self, _index):
        self.language_requested.emit(self._language.currentData())

    def _on_camera(self):
        self.camera_requested.emit()

    def _on_capture(self):
        self.capture_requested.emit(self._smooth.isChecked())

    def _on_calibrate(self):
        self.calibrate_requested.emit(float(self._reference_width.value()),
                                      float(self._reference_height.value()), float(self._tolerance.value()))

    def _on_export(self):
        name = datetime.now().strftime('capture_%Y%m%d_%H%M%S_%f.dxf')
        dialog = QFileDialog(self, self._t('Export DXF'), str(Path(self._output_dir) / name))
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setNameFilter(self._t('DXF files (*.dxf)'))
        dialog.setDefaultSuffix('dxf')
        dialog.setOption(QFileDialog.Option.DontConfirmOverwrite)
        if dialog.exec() and dialog.selectedFiles():
            self.export_requested.emit(dialog.selectedFiles()[0])

    def _on_refresh(self):
        self.refresh_requested.emit()

    def start_refresh(self):
        self._timer.start()

    def stop_refresh(self):
        self._timer.stop()

    def set_live_frame(self, width, height, rgb):
        self._live.set_frame(width, height, rgb)

    def set_capture(self, width, height, rgb, width_mm, height_mm, count, exportable):
        self._captured.set_frame(width, height, rgb)
        self._metric_values[0].setText(f'{width_mm:.2f} mm')
        self._metric_values[1].setText(f'{height_mm:.2f} mm')
        self._metric_values[2].setText(str(count))
        self._exportable = exportable
        self._update_buttons()

    def set_connected(self, connected):
        self._connected = connected
        self._camera.setText(self._t('Disconnect camera' if connected else 'Connect camera'))
        self._update_buttons()

    def set_busy(self, busy):
        self._busy = busy
        self._update_buttons()

    def _update_buttons(self):
        self._camera.setEnabled(not self._busy)
        self._capture_button.setEnabled(self._connected and not self._busy)
        self._calibrate_button.setEnabled(self._connected and not self._busy)
        self._export_button.setEnabled(self._exportable and not self._busy)
        for field in (self._reference_width, self._reference_height, self._tolerance, self._smooth):
            field.setEnabled(not self._busy)

    def set_reference(self, width, height, tolerance):
        self._reference_width.setValue(width)
        self._reference_height.setValue(height)
        self._tolerance.setValue(tolerance)

    def set_smoothing(self, enabled):
        self._smooth.setChecked(enabled)

    def set_info(self, source, scale, correction, output_dir, calibration_path, residual, last_export):
        self._source.setText(source)
        self._scale_value.setText(f'{scale:.6f} mm / px')
        self._correction_value.setText(f'×{correction:.6f}')
        self._correction_value.setToolTip(calibration_path)
        self._output_dir = output_dir
        self._output.setText(output_dir)
        self._output.setToolTip(output_dir)
        self._residual = residual
        self._render_residual()
        self._last_export = last_export
        self._last_file.setText(last_export)
        self._last_file.setVisible(bool(last_export))

    def _render_residual(self):
        if self._residual is None:
            self._residual_value.setText(self._t('Calibration stays separate from production settings.'))
        else:
            self._residual_value.setText(self._t('Reference error: {first:+.2f} / {second:+.2f} mm').format(
                first=self._residual[0], second=self._residual[1]))

    def set_status(self, status, detail=''):
        self._status, self._detail = status, detail
        self._render_status()

    def _render_status(self):
        source = self._STATUS.get(self._status, self._status)
        color = ERROR_COLOR if self._status == 'error' else STATUS_OK if self._status in ('ready', 'calibrated', 'exported') else TEXT_PRIMARY
        self._status_label.setStyleSheet(f'color: {color}; font-weight: bold;')
        self._status_label.setText(self._t(source) + (f' · {self._detail}' if self._detail else ''))

    def clean_up(self):
        self.stop_refresh()
