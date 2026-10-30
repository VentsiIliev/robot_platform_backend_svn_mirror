"""Reusable pieces within the setup view; all operations remain presentation-only."""

import qtawesome as qta
from PyQt6.QtCore import QCoreApplication, QEvent, QSize, Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from pl_gui.settings.settings_view.styles import (
    ACTION_BTN_STYLE,
    BG_COLOR,
    BORDER,
    GHOST_BTN_STYLE,
    LABEL_STYLE,
    PRIMARY,
    TEXT_COLOR,
)
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit
from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField
from src.robot_systems.paint.contracts.paint_head_calibration.models import (
    CalibrationCatalog,
    ImagePixels,
    ReferenceRole,
    RevisionRef,
)

from ...editor_contracts import EditorTool
from ...tuning_fields import TuningParameter
from ..styles import CARD_STYLE, ICON_BUTTON_STYLE, SECONDARY_BUTTON_STYLE
from .calibration_canvas import CalibrationCanvas


def translate(source: str) -> str:
    return QCoreApplication.translate("PaintHeadDetectorSetup", source) or source


def action_button(source: str, *, primary: bool = False) -> QPushButton:
    button = QPushButton(translate(source))
    button.setStyleSheet(ACTION_BTN_STYLE if primary else SECONDARY_BUTTON_STYLE)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    return button


class IconActionButton(QPushButton):
    def __init__(self, icon: str, source: str) -> None:
        super().__init__()
        self._source = source
        self.setIcon(qta.icon(icon, color=PRIMARY))
        self.setIconSize(QSize(22, 22))
        self.setFixedSize(46, 46)
        self.setStyleSheet(ICON_BUTTON_STYLE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.retranslateUi()

    def retranslateUi(self) -> None:
        self.setToolTip(translate(self._source))
        self.setAccessibleName(translate(self._source))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)


class SettingsSection(QFrame):
    """Collapsible presentation group; every field remains owned by the view."""

    def __init__(self, source: str, *, expanded: bool) -> None:
        super().__init__()
        self._source = source
        self.setObjectName("settingsCard")
        self.setStyleSheet(CARD_STYLE)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 16)
        self._toggle = QToolButton()
        self._toggle.setObjectName("calibrationSettingsSection")
        self._toggle.setCheckable(True)
        self._toggle.setChecked(expanded)
        self._toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle.setMinimumHeight(44)
        self._toggle.setCursor(Qt.CursorShape.PointingHandCursor)
        self._body = QWidget()
        self.fields = QGridLayout(self._body)
        self.fields.setContentsMargins(0, 8, 0, 0)
        self.fields.setHorizontalSpacing(20)
        self.fields.setVerticalSpacing(16)
        self.fields.setColumnStretch(0, 1)
        self.fields.setColumnStretch(1, 1)
        layout.addWidget(self._toggle)
        layout.addWidget(self._body)
        self._toggle.toggled.connect(self._on_toggled)
        self._on_toggled(expanded)
        self.retranslateUi()

    def _on_toggled(self, expanded: bool) -> None:
        self._body.setVisible(expanded)
        self._toggle.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)

    def retranslateUi(self) -> None:
        self._toggle.setText(translate(self._source))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)


class TuningField(QWidget):
    edited = pyqtSignal(object, object)

    def __init__(self, parameter: TuningParameter, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._parameter = parameter
        self.setObjectName("calibrationTuning_" + parameter.identity.value)
        self._label = QLabel()
        self._label.setWordWrap(True)
        self._label.setMinimumHeight(32)
        self._number = KeyboardNumberField(decimal=not parameter.integer, button_width=36)
        self._number.setRange(0, 1_000_000_000)
        self._number.setSingleStep(1 if parameter.integer else 0.1)
        if not parameter.integer:
            self._number.setDecimals(6)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._label)
        layout.addWidget(self._number)
        self._number.valueChanged.connect(self._on_changed)
        self.retranslateUi()

    def set_value(self, value: int | float) -> None:
        blocked = self._number.blockSignals(True)
        try:
            self._number.setMaximum(max(1_000_000_000, value))
            self._number.setValue(value)
        finally:
            self._number.blockSignals(blocked)

    def _on_changed(self, value: object) -> None:
        self.edited.emit(self._parameter.identity, value)

    def retranslateUi(self) -> None:
        self._label.setText(translate(self._parameter.label))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)


class SetupDialog(QDialog):
    def __init__(self, title: str, parent: QWidget) -> None:
        super().__init__(parent)
        self._title_source = title
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setModal(True)
        self.setMinimumWidth(420)
        self.setStyleSheet(
            f"QDialog {{ background: {BG_COLOR}; color: {TEXT_COLOR}; border: 1px solid {BORDER}; border-radius: 10px; }}"
        )
        self.content = QVBoxLayout(self)
        self.content.setContentsMargins(22, 22, 22, 22)
        header = QHBoxLayout()
        self._title = QLabel()
        self._title.setStyleSheet(LABEL_STYLE)
        header.addWidget(self._title, 1)
        self._close = action_button("Close")
        self._close.clicked.connect(self.reject)
        header.addWidget(self._close)
        self.content.addLayout(header)
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        for button in self.buttons.buttons():
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(GHOST_BTN_STYLE)
        self._ok_source = "Confirm"
        self._retranslate_base()

    def finish_layout(self, ok_source: str) -> None:
        self._ok_source = ok_source
        self.content.addWidget(self.buttons)
        self._retranslate_base()

    def _retranslate_base(self) -> None:
        self.setWindowTitle(translate(self._title_source))
        self._title.setText(translate(self._title_source))
        self._close.setText(translate("Close"))
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setText(translate(self._ok_source))
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setStyleSheet(ACTION_BTN_STYLE)
        self.buttons.button(QDialogButtonBox.StandardButton.Cancel).setText(translate("Cancel"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self._retranslate_base()
        super().changeEvent(event)


class ProfileDialog(SetupDialog):
    def __init__(self, parent: QWidget, *, importing: bool = False) -> None:
        super().__init__(
            "Import factory calibration" if importing else "New calibration profile", parent
        )
        self._name = KeyboardLineEdit()
        self._description = KeyboardLineEdit()
        self._name_label = QLabel()
        self._description_label = QLabel()
        self._name.setObjectName("calibrationProfileName")
        form = QFormLayout()
        form.addRow(self._name_label, self._name)
        form.addRow(self._description_label, self._description)
        self.content.addLayout(form)
        self._name.textChanged.connect(self._validate)
        self.finish_layout("Import as saved revision" if importing else "Create draft")
        self._validate()
        self._retranslate()

    @property
    def profile_name(self) -> str:
        return self._name.text().strip()

    @property
    def description(self) -> str:
        return self._description.text().strip()

    def _validate(self) -> None:
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(bool(self.profile_name))

    def _retranslate(self) -> None:
        self._name_label.setText(translate("Profile name"))
        self._description_label.setText(translate("Description (optional)"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self._retranslate()
        super().changeEvent(event)


class ReferenceDialog(SetupDialog):
    def __init__(
        self,
        parent: QWidget,
        image: ImagePixels,
        *,
        role: ReferenceRole | None,
    ) -> None:
        super().__init__("Review reference image", parent)
        self.resize(720, 650)
        self._canvas = CalibrationCanvas(self)
        self._canvas.set_image(image)
        self._canvas.setInteractive(False)
        self.content.addWidget(self._canvas, 1)
        self._role_label = QLabel()
        self._roles = QComboBox()
        self._roles.addItem("", ReferenceRole.PRESENT)
        self._roles.addItem("", ReferenceRole.MISSING)
        if role is not None:
            self._roles.setCurrentIndex(self._roles.findData(role))
        else:
            self._roles.hide()
        self.content.addWidget(self._role_label)
        self.content.addWidget(self._roles)
        self.finish_layout("Use in draft" if role is not None else "Close")
        if role is None:
            self.buttons.button(QDialogButtonBox.StandardButton.Cancel).hide()
        self._retranslate()

    @property
    def role(self) -> ReferenceRole:
        return self._roles.currentData()

    def _retranslate(self) -> None:
        self._role_label.setText(translate("Reference role"))
        self._roles.setItemText(0, translate("Head present"))
        self._roles.setItemText(1, translate("Head missing"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self._retranslate()
        super().changeEvent(event)


class RuntimePicker(SetupDialog):
    def __init__(self, parent: QWidget, catalog: CalibrationCatalog) -> None:
        super().__init__("Select for runtime", parent)
        self._label = QLabel()
        self._label.setWordWrap(True)
        self._choices = QComboBox()
        for profile in catalog.profiles:
            for revision in sorted(profile.revisions, key=lambda item: item.number, reverse=True):
                ref = RevisionRef(profile.profile_id, revision.number)
                self._choices.addItem(f"{profile.name} · r{revision.number}", ref)
                if ref == catalog.selected:
                    self._choices.setCurrentIndex(self._choices.count() - 1)
        self.content.addWidget(self._label)
        self.content.addWidget(self._choices)
        self.finish_layout("Use selected revision")
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(
            self._choices.count() > 0
        )
        self._retranslate()

    @property
    def selected_revision(self) -> RevisionRef:
        return self._choices.currentData()

    def _retranslate(self) -> None:
        self._label.setText(
            translate("Choose a saved revision. Drafts are never used by production.")
        )

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self._retranslate()
        super().changeEvent(event)


class SaveRevisionDialog(SetupDialog):
    def __init__(self, parent: QWidget, profile_name: str) -> None:
        super().__init__("Save calibration revision", parent)
        self._profile = QLabel(profile_name)
        self._description_label = QLabel()
        self._description = KeyboardLineEdit()
        self._notice = QLabel()
        self._notice.setWordWrap(True)
        self.content.addWidget(self._profile)
        self.content.addWidget(self._description_label)
        self.content.addWidget(self._description)
        self.content.addWidget(self._notice)
        self.finish_layout("Validate and save")
        self._retranslate()

    @property
    def description(self) -> str:
        return self._description.text().strip()

    def _retranslate(self) -> None:
        self._description_label.setText(translate("Description (optional)"))
        self._notice.setText(
            translate(
                "A new revision will be validated and saved. Runtime selection will not change."
            )
        )

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self._retranslate()
        super().changeEvent(event)


class UnsavedDialog(SetupDialog):
    def __init__(self, parent: QWidget) -> None:
        from ...editor_contracts import UnsavedDecision

        super().__init__("Unsaved draft changes", parent)
        self.decision = UnsavedDecision.CANCEL
        self._notice = QLabel()
        self._notice.setWordWrap(True)
        self.content.addWidget(self._notice)
        self._save = action_button("Save draft", primary=True)
        self._discard = action_button("Discard changes")
        self._cancel = action_button("Cancel")
        self._save.clicked.connect(self._on_save)
        self._discard.clicked.connect(self._on_discard)
        self._cancel.clicked.connect(self.reject)
        row = QHBoxLayout()
        row.addWidget(self._save)
        row.addWidget(self._discard)
        row.addWidget(self._cancel)
        self.content.addLayout(row)
        self._retranslate()

    def _on_save(self) -> None:
        from ...editor_contracts import UnsavedDecision

        self.decision = UnsavedDecision.SAVE
        self.accept()

    def _on_discard(self) -> None:
        from ...editor_contracts import UnsavedDecision

        self.decision = UnsavedDecision.DISCARD
        self.accept()

    def _retranslate(self) -> None:
        self._notice.setText(
            translate("Save or discard the current edits before leaving this draft.")
        )
        self._save.setText(translate("Save draft"))
        self._discard.setText(translate("Discard changes"))
        self._cancel.setText(translate("Cancel"))

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self._retranslate()
        super().changeEvent(event)


class EditorToolButton(QPushButton):
    chosen = pyqtSignal(object)

    def __init__(self, tool: EditorTool, source: str, parent: QWidget) -> None:
        super().__init__(parent)
        self._tool = tool
        self._source = source
        self.setCheckable(True)
        names = {
            EditorTool.SELECT: "mdi.cursor-default",
            EditorTool.PAN: "mdi.cursor-move",
            EditorTool.INSPECTION: "mdi.crop-free",
            EditorTool.EMPTY_MOUNT: "mdi.vector-square",
            EditorTool.EXCLUDED: "mdi.cancel",
            EditorTool.RECTANGLE_LANDMARK: "mdi.rectangle-outline",
            EditorTool.CIRCLE_LANDMARK: "mdi.circle-outline",
        }
        self.setIcon(qta.icon(names[tool], color=PRIMARY))
        self.setIconSize(QSize(22, 22))
        self.setFixedSize(46, 46)
        self.setStyleSheet(ICON_BUTTON_STYLE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._on_clicked)
        self.retranslateUi()

    def _on_clicked(self) -> None:
        self.chosen.emit(self._tool)

    def retranslateUi(self) -> None:
        self.setToolTip(translate(self._source))
        self.setAccessibleName(translate(self._source))
