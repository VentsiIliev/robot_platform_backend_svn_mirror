"""Translated choice labels with stable IDs in Qt item data."""

from collections.abc import Callable
from enum import StrEnum

from PyQt6.QtCore import QCoreApplication, Qt
from PyQt6.QtWidgets import QComboBox, QWidget

from pl_gui.settings.settings_view.schema import SettingField
from src.applications.base.app_dialog import DIALOG_INPUT_STYLE
from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField
from src.robot_systems.paint.contracts.paint_head_check.errors import PaintHeadConfigurationError
from src.robot_systems.paint.contracts.paint_head_check.models import PaintHeadAction
from src.robot_systems.paint.paint_head_check.policy_registry import (
    build_head_check_policy_registry,
)


class HeadCheckChoiceType(StrEnum):
    POLICY = "paint_head_check_policy"
    ACTION = "paint_head_check_action"
    TIMEOUT_ACTION = "paint_head_check_timeout_action"


HEAD_CHECK_INTERVAL_WIDGET_TYPE = "paint_head_check_interval"


def _t(source: str) -> str:
    return QCoreApplication.translate("PaintProcessSettings", source) or source


class HeadCheckChoiceCombo(QComboBox):
    def __init__(self, field: SettingField, emit: Callable[[str], None]) -> None:
        super().__init__()
        self.setObjectName(field.key)
        self._emit_value = emit
        self.setStyleSheet(DIALOG_INPUT_STYLE)
        self.setMinimumHeight(44)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        kind = HeadCheckChoiceType(field.widget_type)
        if kind is HeadCheckChoiceType.POLICY:
            for description in build_head_check_policy_registry(1).descriptions():
                self.addItem(_t(description.label), description.policy_id.value)
        else:
            labels = {
                PaintHeadAction.REPORT_ONLY: _t("Report only"),
                PaintHeadAction.CONTINUE: _t("Continue"),
                PaintHeadAction.RETRY: _t("Retry observation"),
                PaintHeadAction.PAUSE: _t("Pause for operator"),
                PaintHeadAction.STOP: _t("Stop process (Start to retry)"),
                PaintHeadAction.REJECT: _t("Fail the cycle"),
            }
            for action, label in labels.items():
                if kind is HeadCheckChoiceType.TIMEOUT_ACTION and action is PaintHeadAction.RETRY:
                    continue
                self.addItem(label, action.value)
        self.set_choice(field.default)
        self.currentIndexChanged.connect(self._on_changed)

    def choice(self) -> str:
        value = self.currentData()
        if not isinstance(value, str):
            raise PaintHeadConfigurationError("Paint-head setting has no selected choice")
        return value

    def set_choice(self, value: object) -> None:
        index = self.findData(value)
        if index < 0:
            raise PaintHeadConfigurationError(f"Unknown paint-head setting choice: {value}")
        self.setCurrentIndex(index)

    def _on_changed(self, _index: int) -> None:
        self._emit_value(self.choice())


def get_head_check_choice(widget: QWidget) -> str:
    if not isinstance(widget, HeadCheckChoiceCombo):
        raise PaintHeadConfigurationError("Paint-head setting requires a choice widget")
    return widget.choice()


def set_head_check_choice(widget: QWidget, value: object) -> None:
    if not isinstance(widget, HeadCheckChoiceCombo):
        raise PaintHeadConfigurationError("Paint-head setting requires a choice widget")
    widget.set_choice(value)


def get_head_check_interval(widget: QWidget) -> int:
    if not isinstance(widget, KeyboardNumberField):
        raise PaintHeadConfigurationError("Head-check interval requires the shared numeric field")
    reader: Callable[[], object] = widget.value
    value = reader()
    if type(value) is not int:
        raise PaintHeadConfigurationError("Head-check interval must contain an integer value")
    return value


def set_head_check_interval(widget: QWidget, value: object) -> None:
    if not isinstance(widget, KeyboardNumberField) or type(value) is not int:
        raise PaintHeadConfigurationError("Head-check interval requires an integer numeric field")
    widget.setValue(value)
