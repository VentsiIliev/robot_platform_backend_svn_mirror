from __future__ import annotations

from PyQt6.QtCore import QEvent, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from pl_gui.settings.settings_view.styles import (
    ACTION_BTN_STYLE,
    GHOST_BTN_STYLE,
    GROUP_STYLE,
    LABEL_STYLE,
    STATUS_OK,
    ERROR_COLOR,
)
from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField


class SensorlessCollisionTab(QWidget):
    """Runtime configuration for the ZeroErr sensorless collision monitor."""

    refresh_requested = pyqtSignal()
    save_requested = pyqtSignal(dict)
    open_diagnostics_requested = pyqtSignal()
    active_response_edited = pyqtSignal(bool, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._joint_fields: dict[str, list[KeyboardNumberField]] = {}
        self._build_ui()
        self._active_stop.toggled.connect(self._on_active_response_edited)
        self._last_active_response = self._active_stop.isChecked()
        self._loading_config = False

    def _on_active_response_edited(self, enabled: bool) -> None:
        previous = self._last_active_response
        self._last_active_response = enabled
        if not self._loading_config:
            self.active_response_edited.emit(previous, enabled)

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        self._intro = QLabel()
        self._intro.setWordWrap(True)
        layout.addWidget(self._intro)

        self._mode_group = QGroupBox()
        self._mode_group.setStyleSheet(GROUP_STYLE)
        mode_layout = QGridLayout(self._mode_group)
        self._enabled = QCheckBox()
        self._active_stop = QCheckBox()
        self._dynamic_enabled = QCheckBox()
        self._diagnostics_enabled = QCheckBox()
        mode_layout.addWidget(self._enabled, 0, 0, 1, 2)
        mode_layout.addWidget(self._active_stop, 1, 0, 1, 2)
        mode_layout.addWidget(self._dynamic_enabled, 2, 0, 1, 2)
        mode_layout.addWidget(self._diagnostics_enabled, 3, 0, 1, 2)
        layout.addWidget(self._mode_group)

        self._tuning_group = QGroupBox()
        self._tuning_group.setStyleSheet(GROUP_STYLE)
        tuning_layout = QGridLayout(self._tuning_group)
        self._sensitivity = self._number(50, 200, 1, "%", decimals=0)
        self._confirm_duration_ms = self._number(0, 1000, 1, " ms", decimals=0)
        self._max_ratio = self._number(1, 20, 0.5, " × static", decimals=1)
        self._decay = self._number(0.01, 5, 0.05, " s", decimals=2)
        fields = [
            self._sensitivity,
            self._confirm_duration_ms,
            self._max_ratio,
            self._decay,
        ]
        self._tuning_labels = []
        for row, field in enumerate(fields):
            label = QLabel()
            label.setStyleSheet(LABEL_STYLE)
            self._tuning_labels.append(label)
            tuning_layout.addWidget(label, row, 0)
            tuning_layout.addWidget(field, row, 1)
        self._hint = QLabel()
        self._hint.setWordWrap(True)
        tuning_layout.addWidget(self._hint, len(fields), 0, 1, 2)
        layout.addWidget(self._tuning_group)

        self._primary_group = QGroupBox()
        self._primary_group.setStyleSheet(GROUP_STYLE)
        primary_grid = QGridLayout(self._primary_group)
        self._primary_hint = QLabel()
        self._primary_hint.setWordWrap(True)
        primary_grid.addWidget(self._primary_hint, 0, 0, 1, 2)
        self._primary_headers = [QLabel(), QLabel()]
        for column, label in enumerate(self._primary_headers):
            label.setStyleSheet(LABEL_STYLE)
            primary_grid.addWidget(label, 1, column)

        self._secondary_group = QGroupBox()
        self._secondary_group.setStyleSheet(GROUP_STYLE)
        secondary_grid = QGridLayout(self._secondary_group)
        self._secondary_enabled = QCheckBox()
        self._secondary_enabled.toggled.connect(self._set_secondary_fields_enabled)
        secondary_grid.addWidget(self._secondary_enabled, 0, 0, 1, 3)
        self._secondary_hint = QLabel()
        self._secondary_hint.setWordWrap(True)
        secondary_grid.addWidget(self._secondary_hint, 1, 0, 1, 3)
        self._secondary_headers = [QLabel(), QLabel(), QLabel()]
        for column, label in enumerate(self._secondary_headers):
            label.setStyleSheet(LABEL_STYLE)
            secondary_grid.addWidget(label, 2, column)

        for index in range(6):
            fields = [
                self._number(0.01, 200, 0.1, " Nm", decimals=2),
                self._number(0.01, 500, 0.5, " Nm", decimals=1),
                self._number(1, 100000, 50, " counts", decimals=0),
            ]
            self._joint_fields[f"Joint_{index + 1}"] = fields
            primary_grid.addWidget(QLabel(f"J{index + 1}"), index + 2, 0)
            primary_grid.addWidget(fields[0], index + 2, 1)
            secondary_grid.addWidget(QLabel(f"J{index + 1}"), index + 3, 0)
            secondary_grid.addWidget(fields[1], index + 3, 1)
            secondary_grid.addWidget(fields[2], index + 3, 2)
        layout.addWidget(self._primary_group)
        layout.addWidget(self._secondary_group)

        actions = QHBoxLayout()
        self._status = QLabel()
        self._status.setWordWrap(True)
        actions.addWidget(self._status, 1)
        self._refresh = QPushButton()
        self._refresh.setStyleSheet(GHOST_BTN_STYLE)
        self._refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh.clicked.connect(self.refresh_requested)
        self._open_diagnostics = QPushButton()
        self._open_diagnostics.setStyleSheet(GHOST_BTN_STYLE)
        self._open_diagnostics.setCursor(Qt.CursorShape.PointingHandCursor)
        self._open_diagnostics.clicked.connect(self.open_diagnostics_requested)
        self._save = QPushButton()
        self._save.setStyleSheet(ACTION_BTN_STYLE)
        self._save.setCursor(Qt.CursorShape.PointingHandCursor)
        self._save.clicked.connect(self._emit_save)
        actions.addWidget(self._refresh)
        actions.addWidget(self._open_diagnostics)
        actions.addWidget(self._save)
        layout.addLayout(actions)
        layout.addStretch()
        self.retranslateUi()

    def retranslateUi(self) -> None:
        self._intro.setText(self.tr(
            "Configure the ZeroErr torque-based collision monitor. Changes are "
            "applied to the running ROS2 backend and persisted there."))
        self._mode_group.setTitle(self.tr("Protection mode"))
        self._enabled.setText(self.tr("Sensorless collision detection enabled"))
        self._active_stop.setText(self.tr("Active response — stop robot motion"))
        self._dynamic_enabled.setText(self.tr("Direction-aware dynamic thresholds"))
        self._diagnostics_enabled.setText(self.tr(
            "Live observer diagnostics — publish PlotJuggler topics"))
        self._tuning_group.setTitle(self.tr("Detection tuning"))
        tuning_texts = [
            "Sensitivity", "Confirmation duration",
            "Maximum dynamic threshold", "Dynamic envelope decay",
        ]
        for label, text in zip(self._tuning_labels, tuning_texts):
            label.setText(self.tr(text))
        self._hint.setText(self.tr(
            "100% sensitivity uses calibrated thresholds. Higher values are more sensitive. "
            "A longer confirmation duration rejects short spikes but delays stopping. "
            "Duration is measured from robot-state timestamps, not callback count."))
        self._primary_group.setTitle(self.tr("Primary detector — torque observer"))
        self._primary_hint.setText(self.tr(
            "This is the main sensorless detector. It compares estimated external torque "
            "with the calibrated direction-aware threshold."))
        for label, text in zip(self._primary_headers, ["Joint", "External torque threshold (Nm)"]):
            label.setText(self.tr(text))
        self._secondary_group.setTitle(self.tr(
            "Secondary detector — effort and position following error"))
        self._secondary_enabled.setText(self.tr("Enable secondary detector"))
        self._secondary_hint.setText(self.tr(
            "Optional backup detector. It triggers only when measured effort AND position "
            "following error exceed their thresholds. Following error is in raw drive counts."))
        secondary_texts = ["Joint", "Effort threshold (Nm)",
                           "Following-error threshold (drive counts)"]
        for label, text in zip(self._secondary_headers, secondary_texts):
            label.setText(self.tr(text))
        if not self._status.text():
            self._status.setText(self.tr("Not loaded"))
        self._refresh.setText(self.tr("Refresh"))
        self._open_diagnostics.setText(self.tr("Open PlotJuggler"))
        self._save.setText(self.tr("Apply settings"))

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    @staticmethod
    def _number(minimum, maximum, step, suffix, decimals):
        field = KeyboardNumberField(decimal=bool(decimals))
        field.setRange(minimum, maximum)
        field.setSingleStep(step)
        if decimals:
            field.setDecimals(decimals)
        field.setSuffix(suffix)
        return field

    def _emit_save(self) -> None:
        self.save_requested.emit(self.values())

    def _set_secondary_fields_enabled(self, enabled: bool) -> None:
        for fields in self._joint_fields.values():
            fields[1].setEnabled(enabled)
            fields[2].setEnabled(enabled)

    def values(self) -> dict:
        external, effort, following = [], [], []
        for fields in self._joint_fields.values():
            external.append(float(fields[0].value()))
            effort.append(float(fields[1].value()))
            following.append(float(fields[2].value()))
        return {
            "detection_enabled": self._enabled.isChecked(),
            "active_stop_enabled": self._active_stop.isChecked(),
            "effort_following_error_detection_enabled": self._secondary_enabled.isChecked(),
            "dynamic_threshold_enabled": self._dynamic_enabled.isChecked(),
            "diagnostics_enabled": self._diagnostics_enabled.isChecked(),
            "collision_sensitivity_percent": float(self._sensitivity.value()),
            "confirm_duration_ms": float(self._confirm_duration_ms.value()),
            "dynamic_threshold_max_ratio": float(self._max_ratio.value()),
            "dynamic_threshold_decay_sec": float(self._decay.value()),
            "external_torque_thresholds": external,
            "effort_thresholds": effort,
            "following_error_thresholds": following,
        }

    def load_config(self, config: dict) -> None:
        self._loading_config = True
        try:
            self._load_config(config)
        finally:
            self._last_active_response = self._active_stop.isChecked()
            self._loading_config = False

    def _load_config(self, config: dict) -> None:
        self._enabled.setChecked(bool(config.get("detection_enabled", True)))
        self._active_stop.setChecked(bool(config.get("active_stop_enabled", False)))
        self._secondary_enabled.setChecked(bool(
            config.get("effort_following_error_detection_enabled", False)))
        self._dynamic_enabled.setChecked(bool(config.get("dynamic_threshold_enabled", False)))
        self._diagnostics_enabled.setChecked(bool(config.get("diagnostics_enabled", False)))
        self._sensitivity.setValue(int(round(float(
            config.get("collision_sensitivity_percent", 100)))))
        self._confirm_duration_ms.setValue(int(round(float(
            config.get("confirm_duration_ms", 25.0)))))
        self._max_ratio.setValue(float(config.get("dynamic_threshold_max_ratio", 5)))
        self._decay.setValue(float(config.get("dynamic_threshold_decay_sec", 0.35)))
        arrays = [
            config.get("external_torque_thresholds", []),
            config.get("effort_thresholds", []),
            config.get("following_error_thresholds", []),
        ]
        for index, fields in enumerate(self._joint_fields.values()):
            for column, field in enumerate(fields):
                if index < len(arrays[column]):
                    value = float(arrays[column][index])
                    field.setValue(int(round(value)) if column == 2 else value)
        self.set_status(self.tr("Configuration loaded"), success=True)

    def set_status(self, message: str, success: bool) -> None:
        color = STATUS_OK if success else ERROR_COLOR
        self._status.setText(message)
        self._status.setStyleSheet(f"color: {color}; font-weight: bold;")

    def set_busy(self, busy: bool) -> None:
        self.setEnabled(not busy)
