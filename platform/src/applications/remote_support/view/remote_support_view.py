import time
from PyQt6.QtCore import QEvent, Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QComboBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QTabWidget, QVBoxLayout

from pl_gui.settings.settings_view.styles import (
    APP_PAGE_TITLE_STYLE, APP_PHASE_TAB_STYLE, BG_COLOR, BORDER, TERTIARY_TEXT, TEXT_COLOR,
    ACTION_BTN_STYLE, GHOST_BTN_STYLE,
    TOUCH_SCROLL_AREA_STYLE,
)
from pl_gui.utils.utils_widgets.SwitchButton import QToggle
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.app_dialog import DIALOG_INPUT_STYLE, DIALOG_COMBO_STYLE
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit


class RemoteSupportView(IApplicationView):
    language_changed = pyqtSignal()
    remote_support_requested = pyqtSignal(bool)
    remote_support_refresh_requested = pyqtSignal()
    password_change_requested = pyqtSignal(str, str, str, str)
    password_remove_requested = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__("RemoteSupport", parent)

    def setup_ui(self) -> None:
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        self._busy = {"remote": False, "password": False}
        self._password_operation_busy = False
        self._timed_access_supported = False
        self._remaining_deadline = None
        self._password_status = None
        self._password_error = None
        self._remote_enabled = None
        self._remote_active = None
        self._remote_error = None
        root = QVBoxLayout(self)
        root.setContentsMargins(30, 16, 30, 20)
        root.setSpacing(14)
        self._title = QLabel()
        self._title.setStyleSheet(APP_PAGE_TITLE_STYLE)
        root.addWidget(self._title)
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet(APP_PHASE_TAB_STYLE)
        root.addWidget(self._tabs, 1)
        self._build_remote_support_page()
        self._build_password_page()
        self._tabs.currentChanged.connect(self._on_tab_changed)
        self._status = QLabel()
        self._status.setWordWrap(True)
        self._status.setStyleSheet(f"color: {TERTIARY_TEXT};")
        root.addWidget(self._status)
        self._countdown_timer = QTimer(self)
        self._countdown_timer.setInterval(1000)
        self._countdown_timer.timeout.connect(self._update_countdown)
        self._countdown_timer.start()
        self.retranslateUi()

    def _build_remote_support_page(self) -> None:
        page = QFrame()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(12)
        self._remote_heading = QLabel()
        self._remote_heading.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 18pt; font-weight: bold; background: transparent;"
        )
        self._remote_hint = QLabel()
        self._remote_hint.setStyleSheet(f"color: {TERTIARY_TEXT}; background: transparent;")
        layout.addWidget(self._remote_heading)
        layout.addWidget(self._remote_hint)
        card = QFrame()
        card.setObjectName("remoteSupportCard")
        card.setStyleSheet(
            f"QFrame#remoteSupportCard {{ background: white; border: 1px solid {BORDER};"
            " border-radius: 16px; }"
        )
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(20)
        labels = QVBoxLayout()
        labels.setSpacing(8)
        self._remote_state = QLabel()
        self._remote_state.setStyleSheet(
            f"color: {TEXT_COLOR}; font-size: 13pt; font-weight: bold; background: transparent;"
        )
        self._remote_service = QLabel()
        self._remote_service.setWordWrap(True)
        self._remote_service.setStyleSheet(f"color: {TERTIARY_TEXT}; background: transparent;")
        labels.addWidget(self._remote_state)
        labels.addWidget(self._remote_service)
        card_layout.addLayout(labels, 1)
        self._remote_switch = QToggle()
        self._remote_switch.setFixedHeight(36)
        self._remote_switch.setMinimumWidth(76)
        self._remote_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        self._remote_switch.setEnabled(False)
        self._remote_switch.clicked.connect(self._on_remote_switch_clicked)
        card_layout.addWidget(self._remote_switch)
        layout.addWidget(card)
        form = QFormLayout()
        self._duration_label = QLabel()
        self._duration = QComboBox()
        self._duration.setStyleSheet(DIALOG_COMBO_STYLE)
        for seconds in (900, 7200, 18000):
            self._duration.addItem("", seconds)
        form.addRow(self._duration_label, self._duration)
        layout.addLayout(form)
        self._duration_hint = QLabel()
        self._duration_hint.setWordWrap(True)
        layout.addWidget(self._duration_hint)
        self._countdown = QLabel()
        layout.addWidget(self._countdown)
        layout.addStretch(1)
        self._tabs.addTab(page, "")

    def _build_password_page(self) -> None:
        page = QFrame()
        layout = QVBoxLayout(page)
        self._password_hint = QLabel()
        self._password_hint.setWordWrap(True)
        layout.addWidget(self._password_hint)
        self._password_state = QLabel()
        self._password_state.setWordWrap(True)
        layout.addWidget(self._password_state)
        form = QFormLayout()
        self._password_fields = {}
        self._password_labels = {}
        for key in ("admin_id", "admin_password", "password", "confirmation"):
            field = KeyboardLineEdit()
            field.setStyleSheet(DIALOG_INPUT_STYLE)
            if key != "admin_id":
                field.setEchoMode(QLineEdit.EchoMode.Password)
            field.setMaxLength(64 if key in ("password", "confirmation") else 256)
            label = QLabel()
            form.addRow(label, field)
            self._password_fields[key] = field
            self._password_labels[key] = label
        layout.addLayout(form)
        self._password_buttons = {}
        for key, handler in (("set", self._emit_password_change),
                             ("reset", self._emit_password_change),
                             ("remove", self._emit_password_remove)):
            button = QPushButton()
            button.setStyleSheet(ACTION_BTN_STYLE if key == "set" else GHOST_BTN_STYLE)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(handler)
            self._password_buttons[key] = button
            layout.addWidget(button)
        layout.addStretch(1)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(TOUCH_SCROLL_AREA_STYLE)
        scroll.setWidget(page)
        self._tabs.addTab(scroll, "")

    def _emit_password_change(self) -> None:
        fields = self._password_fields
        values = tuple(fields[key].text() for key in ("admin_id", "admin_password", "password", "confirmation"))
        self.clear_password_fields()
        self.password_change_requested.emit(*values)

    def _emit_password_remove(self) -> None:
        admin_id = self._password_fields["admin_id"].text()
        admin_password = self._password_fields["admin_password"].text()
        self.clear_password_fields()
        self.password_remove_requested.emit(admin_id, admin_password)

    def clear_password_fields(self) -> None:
        for key, field in self._password_fields.items():
            if key != "admin_id":
                field.clear()

    def get_access_duration(self) -> int:
        return int(self._duration.currentData())

    def set_password_status(self, status: dict) -> None:
        self._password_status = status
        self._password_error = None
        self._update_password_labels()
        self._sync_actions()

    def set_password_error(self, message: str) -> None:
        self._password_error = message
        self._password_status = None
        self._update_password_labels()
        self._sync_actions()

    def _update_password_labels(self) -> None:
        if self._password_error:
            self._password_state.setText(self._password_error)
        elif self._password_status is None:
            self._password_state.setText(self.tr("Checking unattended access…"))
        elif self._password_status.get("available") is False:
            self._password_state.setText(self.tr("Enable timed support before managing unattended access"))
        elif self._password_status.get("unattended_enabled"):
            self._password_state.setText(self.tr("Unattended access enabled; password configured."))
        else:
            self._password_state.setText(self.tr("Unattended access disabled."))

    def _update_countdown(self) -> None:
        if self._remaining_deadline is None or not self._remote_enabled:
            self._countdown.setText("")
            return
        remaining = max(0, int(self._remaining_deadline - time.monotonic()))
        display = f"{remaining // 3600:02d}:{remaining // 60 % 60:02d}:{remaining % 60:02d}"
        self._countdown.setText(self.tr("Access expires in {remaining}").format(remaining=display))

    def _on_remote_switch_clicked(self, enabled: bool) -> None:
        self._remote_switch.sync_visual_state(bool(self._remote_enabled))
        self.remote_support_requested.emit(enabled)

    def _on_tab_changed(self, index: int) -> None:
        self.remote_support_refresh_requested.emit()

    def is_remote_support_visible(self) -> bool:
        return self.isVisible()

    def set_remote_support_status(self, status: dict) -> None:
        self._remote_error = None
        self._remote_enabled = bool(status["enabled"])
        self._remote_active = bool(status["active"])
        self._timed_access_supported = status.get("timed_access_supported") is True
        remaining = status.get("remaining_seconds")
        self._remaining_deadline = time.monotonic() + remaining if type(remaining) in (int, float) else None
        if self._remote_enabled and status.get("duration_seconds") in (900, 7200, 18000):
            self._duration.setCurrentIndex(self._duration.findData(status["duration_seconds"]))
        self._remote_switch.sync_visual_state(self._remote_enabled)
        self._update_remote_labels()
        self._sync_actions()
        self._update_countdown()

    def set_remote_support_error(self, message: str) -> None:
        self._remote_error = message
        self._remote_enabled = None
        self._remote_active = None
        self._remote_switch.sync_visual_state(False)
        self._update_remote_labels()
        self._sync_actions()
        self._update_countdown()

    def _update_remote_labels(self) -> None:
        if self._remote_error:
            self._remote_state.setText(self.tr("Remote Support unavailable"))
            self._remote_service.setText(self._remote_error)
        elif self._remote_enabled is None:
            self._remote_state.setText(self.tr("Remote Support: checking…"))
            self._remote_service.setText(self.tr("Checking remote support status…"))
        elif self._remote_enabled != self._remote_active:
            self._remote_state.setText(self.tr("Remote Support: action needed"))
            self._remote_service.setText(
                self.tr("Remote access is still active.") if self._remote_active
                else self.tr("Remote access is not running.")
            )
        elif self._remote_enabled:
            self._remote_state.setText(self.tr("Remote Support: ON"))
            self._remote_service.setText(self.tr("PL PROJECT support can connect to this robot."))
        else:
            self._remote_state.setText(self.tr("Remote Support: OFF"))
            self._remote_service.setText(self.tr("PL PROJECT support cannot connect to this robot."))

    def _sync_actions(self) -> None:
        busy = any(self._busy.values())
        self._remote_switch.setEnabled(self._remote_enabled is not None and not busy)
        self._duration.setEnabled(not busy and not self._remote_enabled)
        for button in self._password_buttons.values():
            button.setEnabled(not busy and self._password_status is not None
                              and self._password_status.get("available") is not False)
        for field in self._password_fields.values():
            field.setEnabled(not self._password_operation_busy)

    def set_password_operation_busy(self, busy: bool) -> None:
        self._password_operation_busy = busy
        self._sync_actions()

    def set_busy(self, kind: str, busy: bool) -> None:
        self._busy[kind] = busy
        self._sync_actions()

    def set_status(self, message: str) -> None:
        self._status.setText(message)

    def set_error(self, message: str) -> None:
        self._status.setText(message)

    def retranslateUi(self) -> None:
        self._title.setText(self.tr("Remote Support"))
        self._tabs.setTabText(0, self.tr("Access"))
        self._tabs.setTabText(1, self.tr("Unattended Access"))
        self._remote_heading.setText(self.tr("Remote Support"))
        self._remote_hint.setText(self.tr("Allow PL PROJECT support engineers to connect to this robot."))
        self._remote_hint.setWordWrap(True)
        self._update_remote_labels()
        self._duration_label.setText(self.tr("Access duration"))
        for index, source in enumerate(("15 minutes", "2 hours", "5 hours")):
            self._duration.setItemText(index, self.tr(source))
        self._duration_hint.setText(self.tr("The timer starts when support is enabled. Access ends on expiry or reboot."))
        self._password_hint.setText(self.tr("Use platform Admin credentials to set, reset, or remove the remote password. Reset does not require the old remote password and does not extend access."))
        for key, source in (("admin_id", "Admin user ID"), ("admin_password", "Platform Admin password"),
                            ("password", "New remote password"), ("confirmation", "Confirm remote password")):
            self._password_labels[key].setText(self.tr(source))
        for key, source in (("set", "Set / change password"), ("reset", "Reset forgotten password"),
                            ("remove", "Remove unattended access")):
            self._password_buttons[key].setText(self.tr(source))
        self._update_password_labels()
        self._update_countdown()

    def changeEvent(self, event) -> None:
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
            self.language_changed.emit()
        super().changeEvent(event)

    def clean_up(self) -> None:
        self._countdown_timer.stop()
        self.clear_password_fields()
