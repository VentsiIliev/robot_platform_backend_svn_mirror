from typing import List, Optional
from PyQt6.QtCore import pyqtSignal, Qt, QCoreApplication
from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QSizePolicy, QWidget, QLineEdit, QPushButton, QTabWidget, QDialog,
)
from PyQt6.QtGui import QFont

from pl_gui.utils.utils_widgets.table_helpers import make_table
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit
from src.applications.user_management.domain.user_schema import UserRecord, UserSchema
from src.applications.user_management.view.account_form_dialog import AccountFormDialog
from src.applications.user_management.view.permissions_view import PermissionsView
from src.applications.user_management.view.login_card_dialog import LoginCardDialog
from src.applications.user_management.view.account_history_dialog import AccountHistoryDialog
from src.applications.base.widgets.private_text_dialog import PrivateTextDialog
from src.applications.base.access.adapters import WidgetAdapter, TabAdapter


class UserManagementView(IApplicationView):

    add_requested     = pyqtSignal()
    edit_requested    = pyqtSignal(object)    # UserRecord
    delete_requested  = pyqtSignal(object)    # UserRecord
    qr_requested      = pyqtSignal(object)    # UserRecord
    refresh_requested = pyqtSignal()
    filter_changed    = pyqtSignal(str, str)  # column label, value
    selection_changed = pyqtSignal(object)
    password_requested = pyqtSignal(object)
    reveal_requested = pyqtSignal(object)
    role_requested = pyqtSignal(object)
    history_requested = pyqtSignal(object)
    codes_requested = pyqtSignal()

    def __init__(self, schema: UserSchema, parent=None):
        self._schema = schema
        self._private_dialog = None
        super().__init__("User Management", parent)

    # ── IApplicationView ─────────────────────────────────────────────

    def setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_users_tab(), "")
        self._permissions_page = QWidget()
        QVBoxLayout(self._permissions_page)
        self._perm_tab_idx = self._tabs.addTab(self._permissions_page, "")
        self._tabs.setTabVisible(self._perm_tab_idx, False)
        root.addWidget(self._tabs)
        self.setStyleSheet(self._stylesheet())
        self.retranslateUi()

    def ensure_permissions_view(self):
        if not hasattr(self, "_permissions_view"):
            self._permissions_view = PermissionsView(self._permissions_page)
            self._permissions_page.layout().addWidget(self._permissions_view)
        return self._permissions_view

    def access_adapters(self):
        controls = {key: WidgetAdapter(getattr(self, "_btn_" + key))
                    for key in ("add", "edit", "delete", "qr", "password", "reveal", "role", "history", "codes")}
        controls["permissions"] = TabAdapter(self._tabs, self._permissions_page)
        return controls

    def set_busy(self, busy):
        self._table.setEnabled(not busy)
        self._btn_refresh.setEnabled(not busy)

    def ask_form(self, title, fields, values=None, choices=None):
        dialog = AccountFormDialog(title, fields, values, choices, self)
        self._private_dialog = dialog
        result = dialog.values() if dialog.exec() == QDialog.DialogCode.Accepted else None
        self._private_dialog = None
        dialog.clear()
        dialog.deleteLater()
        return result

    def display_secret(self, title, notice, text):
        dialog = PrivateTextDialog(title, notice, text, self)
        self._private_dialog = dialog
        dialog.exec()
        self._private_dialog = None
        dialog.deleteLater()

    def display_qr(self, png):
        dialog = LoginCardDialog(png, self)
        self._private_dialog = dialog
        dialog.exec()
        self._private_dialog = None
        dialog.deleteLater()

    def display_history(self, entries):
        dialog = AccountHistoryDialog(entries, self)
        self._private_dialog = dialog
        dialog.exec()
        self._private_dialog = None
        dialog.deleteLater()

    def clear_private_displays(self):
        if self._private_dialog is not None:
            self._private_dialog.reject()

    def _build_users_tab(self) -> QWidget:
        container = QWidget()
        layout    = QVBoxLayout(container)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(8)

        self._title_label = QLabel()
        self._title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        f = QFont(); f.setPointSize(16); f.setBold(True)
        self._title_label.setFont(f)
        layout.addWidget(self._title_label)

        layout.addWidget(self._build_filter_bar())
        layout.addWidget(self._build_table())
        layout.addWidget(self._build_buttons())

        self._status = QLabel()
        layout.addWidget(self._status)
        return container

    def clean_up(self) -> None:
        self.clear_private_displays()

    # ── Public setters ────────────────────────────────────────────────

    def set_users(self, records: List[UserRecord]) -> None:
        table_fields = self._schema.get_table_fields()
        self._table.clearContents()
        self._table.setRowCount(len(records))
        for row, record in enumerate(records):
            for col, fd in enumerate(table_fields):
                val  = record.get(fd.key, "")
                text = "****" if fd.mask_in_table and val else str(val)
                item = QTableWidgetItem(text)
                item.setData(Qt.ItemDataRole.UserRole, record)
                item.setFlags(Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled)
                self._table.setItem(row, col, item)
        self._table.viewport().update()
        self._on_selection_changed()

    def set_status(self, msg: str) -> None:
        self._status.setText(msg)

    def selected_record(self) -> Optional[UserRecord]:
        row = self._table.currentRow()
        if row < 0:
            return None
        item = self._table.item(row, 0)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    # ── Localization ─────────────────────────────────────────────────

    @staticmethod
    def _t(text: str) -> str:
        translated = QCoreApplication.translate("UserManagement", text)
        return translated or text

    def retranslateUi(self) -> None:
        self._tabs.setTabText(0, self._t("Users"))
        if hasattr(self, "_perm_tab_idx"):
            self._tabs.setTabText(self._perm_tab_idx, self._t("App Permissions"))
        self._title_label.setText(self._t("User Management"))
        self._filter_group.setTitle(self._t("Filter"))
        self._filter_label.setText(self._t("Filter by:"))
        self._filter_input.setPlaceholderText(self._t("Enter filter value…"))
        self._btn_filter.setText(self._t("Filter"))
        self._btn_clear.setText(self._t("Clear"))
        self._btn_add.setText(self._t("Add User"))
        self._btn_edit.setText(self._t("Edit User"))
        self._btn_delete.setText(self._t("Delete User"))
        self._btn_refresh.setText(self._t("Refresh"))
        self._btn_qr.setText(self._t("Generate QR"))
        for key, source in (("password", "Change password"), ("reveal", "Show Operator password"),
                            ("role", "Change role"), ("history", "Account history"),
                            ("codes", "Generate recovery codes")):
            getattr(self, "_btn_" + key).setText(self._t(source))
        current = self._filter_col.currentData()
        self._filter_col.clear()
        self._filter_col.addItem(self._t("All"), "")
        for fd in self._schema.get_table_fields():
            self._filter_col.addItem(self._t(fd.label), fd.key)
        self._filter_col.setCurrentIndex(max(0, self._filter_col.findData(current)))
        self._table.setHorizontalHeaderLabels(
            [self._t(h) for h in self._schema.get_table_headers()]
        )

    # ── Builders ─────────────────────────────────────────────────────

    def _build_filter_bar(self) -> QWidget:
        self._filter_group  = QGroupBox()
        layout = QHBoxLayout(self._filter_group)

        self._filter_label = QLabel()
        layout.addWidget(self._filter_label)

        self._filter_col = QComboBox()
        layout.addWidget(self._filter_col)

        self._filter_input = KeyboardLineEdit()
        layout.addWidget(self._filter_input)

        self._btn_filter = QPushButton()
        self._btn_clear  = QPushButton()
        self._btn_filter.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn_filter.clicked.connect(self._emit_filter)
        self._btn_clear.clicked.connect(self._clear_filter)
        self._filter_input.returnPressed.connect(self._emit_filter)
        layout.addWidget(self._btn_filter)
        layout.addWidget(self._btn_clear)
        return self._filter_group

    def _build_table(self) -> QTableWidget:
        self._table = make_table(self._schema.get_table_headers(), min_height=200)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        return self._table

    def _build_buttons(self) -> QWidget:
        group  = QGroupBox()
        layout = QHBoxLayout(group)

        self._btn_add     = QPushButton()
        self._btn_edit    = QPushButton()
        self._btn_delete  = QPushButton()
        self._btn_refresh = QPushButton()
        self._btn_qr      = QPushButton()

        for btn in (self._btn_add, self._btn_edit, self._btn_delete, self._btn_refresh, self._btn_qr):
            btn.setMinimumHeight(48)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn)

        self._btn_edit.setEnabled(False)
        self._btn_delete.setEnabled(False)
        self._btn_qr.setEnabled(False)

        self._btn_add.clicked.connect(self._on_add)
        self._btn_edit.clicked.connect(self._on_edit)
        self._btn_delete.clicked.connect(self._on_delete)
        self._btn_refresh.clicked.connect(self.refresh_requested)
        self._btn_qr.clicked.connect(self._on_qr)
        container = QWidget()
        outer = QVBoxLayout(container)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(group)
        extra = QGroupBox()
        row = QHBoxLayout(extra)
        for key, callback in (("password", self._on_password), ("reveal", self._on_reveal),
                              ("role", self._on_role), ("history", self._on_history),
                              ("codes", self._on_codes)):
            button = QPushButton()
            button.setMinimumHeight(48)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(callback)
            setattr(self, "_btn_" + key, button)
            row.addWidget(button)
        outer.addWidget(extra)
        return container

    # ── Internal slots ────────────────────────────────────────────────

    def _on_selection_changed(self) -> None:
        self.selection_changed.emit(self.selected_record())

    def _on_password(self):
        if self.selected_record(): self.password_requested.emit(self.selected_record())

    def _on_reveal(self):
        if self.selected_record(): self.reveal_requested.emit(self.selected_record())

    def _on_role(self):
        if self.selected_record(): self.role_requested.emit(self.selected_record())

    def _on_history(self):
        if self.selected_record(): self.history_requested.emit(self.selected_record())

    def _on_codes(self):
        self.codes_requested.emit()

    def _on_add(self)    -> None: self.add_requested.emit()
    def _on_edit(self)   -> None:
        r = self.selected_record()
        if r: self.edit_requested.emit(r)
    def _on_delete(self) -> None:
        r = self.selected_record()
        if r: self.delete_requested.emit(r)
    def _on_qr(self)     -> None:
        r = self.selected_record()
        if r: self.qr_requested.emit(r)

    def _emit_filter(self) -> None:
        self.filter_changed.emit(self._filter_col.currentData() or "", self._filter_input.text().strip())

    def _clear_filter(self) -> None:
        self._filter_input.clear()
        self._filter_col.setCurrentIndex(0)
        self.filter_changed.emit("", "")

    @staticmethod
    def _stylesheet() -> str:
        return """
            QWidget { background-color: white; color: black; }
            QHeaderView::section { background-color: #f0f0f0; color: black; padding: 4px; border: 1px solid #d0d0d0; }
            QGroupBox { font-weight: bold; border: 2px solid #cccccc; border-radius: 5px; margin-top: 1ex; padding-top: 10px; }
            QTableWidget { gridline-color: #d0d0d0; background-color: white; alternate-background-color: #f5f5f5; color: black; }
            QTableWidget::item:selected { background-color: #905BA9; color: white; }
            QPushButton { background-color: #905BA9; border: none; color: white; padding: 8px 16px; font-size: 14px; border-radius: 4px; }
            QPushButton:hover { background-color: #7A4D92; }
            QPushButton:disabled { background-color: #cccccc; color: #666666; }
        """
