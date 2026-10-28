"""Read-only account events with selectable field-by-field change details."""
from PyQt6.QtCore import QCoreApplication, QEvent, Qt
from PyQt6.QtWidgets import (
    QAbstractItemView, QDialog, QHeaderView, QLabel, QPushButton,
    QTableWidgetItem, QVBoxLayout,
)

from pl_gui.settings.settings_view.styles import ACTION_BTN_STYLE, BG_COLOR
from pl_gui.utils.utils_widgets.table_helpers import make_table


_ACTIONS = {
    "users.create": "Account created", "users.edit_profile": "Profile edited",
    "users.delete": "Account deleted", "users.change_role": "Role changed",
    "users.change_password": "Password changed", "users.reveal_password": "Operator password viewed",
    "users.issue_login_token": "Login card issued", "users.login": "Login",
    "permissions.manage": "Application permissions changed", "audit.view": "History viewed",
    "recovery.issue": "Recovery codes issued", "recovery.complete": "Password recovered",
    "commissioning.admin_created": "First Admin created",
    "maintenance.manufacturer_created": "Manufacturer created",
    "maintenance.manufacturer_password_reset": "Manufacturer password reset",
}
_FIELDS = {
    "login_id": "Login ID", "first_name": "First Name", "last_name": "Last Name",
    "email": "Email", "role": "Role", "enabled": "Enabled", "allowed_roles": "Allowed roles",
}
_OUTCOMES = {"succeeded": "Succeeded", "failed": "Failed", "denied": "Denied"}


class AccountHistoryDialog(QDialog):
    def __init__(self, entries, parent=None):
        super().__init__(parent)
        self._entries = tuple(entries)
        self.resize(960, 640)
        self.setStyleSheet(f"background-color: {BG_COLOR};")
        layout = QVBoxLayout(self)
        self._notice = QLabel()
        self._notice.setWordWrap(True)
        layout.addWidget(self._notice)
        self._events = self._table(4)
        self._events.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._events.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._events.setRowCount(len(self._entries))
        self._events.itemSelectionChanged.connect(self._show_changes)
        layout.addWidget(self._events, 2)
        self._details = QLabel()
        layout.addWidget(self._details)
        self._changes = self._table(3)
        layout.addWidget(self._changes, 1)
        self._password_notice = QLabel()
        self._password_notice.setWordWrap(True)
        layout.addWidget(self._password_notice)
        self._close = QPushButton()
        self._close.setStyleSheet(ACTION_BTN_STYLE)
        self._close.setCursor(Qt.CursorShape.PointingHandCursor)
        self._close.clicked.connect(self.accept)
        layout.addWidget(self._close)
        self.retranslateUi()
        if self._entries:
            self._events.selectRow(0)

    @staticmethod
    def _table(columns):
        table = make_table([""] * columns)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.verticalHeader().hide()
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setWordWrap(True)
        return table

    @staticmethod
    def _t(text):
        return QCoreApplication.translate("UserManagement", text) or text

    def retranslateUi(self):
        self.setWindowTitle(self._t("Account history"))
        self._notice.setText(self._t("Latest 100 events, newest first. Select an event to inspect its changes.")
                             if self._entries else self._t("No history is available for this account."))
        self._events.setHorizontalHeaderLabels([self._t(text) for text in ("Time (UTC)", "Changed by", "Action", "Outcome")])
        for row, entry in enumerate(self._entries):
            values = (entry.occurred_at, entry.actor, self._t(_ACTIONS.get(entry.action, entry.action)),
                      self._t(_OUTCOMES.get(entry.outcome, entry.outcome)))
            for column, text in enumerate(values):
                self._events.setItem(row, column, QTableWidgetItem(text))
        self._events.resizeRowsToContents()
        self._changes.setHorizontalHeaderLabels([self._t(text) for text in ("Field", "Before", "After")])
        self._close.setText(self._t("Close"))
        self._show_changes()

    def _show_changes(self):
        row = self._events.currentRow()
        entry = self._entries[row] if 0 <= row < len(self._entries) else None
        changes = entry.changes if entry else ()
        self._details.setText(self._t("Changed fields") if changes else self._t("No profile fields changed in this event."))
        self._changes.setRowCount(len(changes))
        for index, change in enumerate(changes):
            values = (self._t(_FIELDS.get(change.field, change.field)),
                      "—" if change.before is None else change.before,
                      "—" if change.after is None else change.after)
            for column, text in enumerate(values):
                self._changes.setItem(index, column, QTableWidgetItem(text))
        self._changes.resizeRowsToContents()
        self._password_notice.setText(self._t("Password changed. Password values are never stored in history.")
                                     if entry and entry.password_changed else "")

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)

    def done(self, result):
        self._entries = ()
        self._events.clearContents()
        self._changes.clearContents()
        self._password_notice.clear()
        super().done(result)
