import qtawesome as qta
from PyQt6.QtCore import QEvent, QTimer, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPalette, QPixmap
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QWidget,
    QFrame,
    QScrollArea,
    QSplitter,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QListView,
    QStackedWidget,
    QAbstractItemView,
    QButtonGroup,
)
from pl_gui.settings.settings_view.styles import (
    APP_PAGE_TITLE_STYLE,
    BG_COLOR,
    BORDER,
    PRIMARY,
    SECONDARY_BG,
    TERTIARY_TEXT,
    TEXT_COLOR,
    ACTION_BTN_STYLE,
    GHOST_BTN_STYLE,
    TOUCH_SCROLL_AREA_STYLE,
)
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit
from src.applications.base.widgets.keyboard_number_field import KeyboardNumberField
from src.applications.workpiece_library.domain.workpiece_schema import WorkpieceSchema, WorkpieceRecord
from src.applications.workpiece_library.view.library_card_delegate import LibraryCardDelegate


class WorkpieceLibraryView(IApplicationView):
    """Schema-driven library cards, selection controls, and an editable inspector."""
    delete_requested = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    search_changed = pyqtSignal(str)
    selection_changed = pyqtSignal(object)
    edit_requested = pyqtSignal(object, dict)
    open_in_editor_requested = pyqtSignal(object)
    duplicate_requested = pyqtSignal(object)
    selection_requested = pyqtSignal(object)
    show_selected_changed = pyqtSignal(bool)
    visible_thumbnails_requested = pyqtSignal(object)

    def __init__(self, schema: WorkpieceSchema, parent=None, *, selection_enabled=False, show_thumbnails=False):
        self._schema = schema
        self._selection_enabled = selection_enabled
        self._show_thumbnails = show_thumbnails
        self._selection_mode = False
        self._checked_ids = set()
        self._all_record_ids = set()
        self._records = []
        self._detail_record = None
        self._edit_widgets = {}
        self._thumbnail_items = {}
        self._loading_records = False
        self._sort_mode = 'recent'
        self._grid_mode = False
        super().__init__('Workpiece Library', parent)

    def _button(self, icon=None, *, primary=False):
        button = QPushButton()
        button.setMinimumHeight(44)
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(ACTION_BTN_STYLE if primary else GHOST_BTN_STYLE)
        if not primary:
            button.setStyleSheet(button.styleSheet() + f' QPushButton:checked {{ background: {SECONDARY_BG}; border: 2px solid {PRIMARY}; }}')
        if icon:
            button.setIcon(qta.icon(icon, color='white' if primary else PRIMARY))
        return button

    def setup_ui(self):
        self.setObjectName('workpieceLibrary')
        self.setStyleSheet(f"""
            QWidget#workpieceLibrary {{ background: {BG_COLOR}; color: {TEXT_COLOR}; }}
            QFrame#detailCard {{ background: white; border: 1px solid {BORDER}; border-radius: 16px; }}
            QLabel {{ color: {TEXT_COLOR}; background: transparent; }}
            QLineEdit, QComboBox {{ background: white; color: {TEXT_COLOR}; border: 1px solid {BORDER};
                border-radius: 10px; padding: 10px; min-height: 24px; }}
            QLineEdit:focus {{ border-color: {PRIMARY}; }}
            QTableWidget, QListWidget {{ background: transparent; border: none; outline: none; }}
            QTableWidget::item, QListWidget::item {{ border: none; padding: 0; }}
            QTableWidget::item:selected, QListWidget::item:selected {{ background: transparent; }}
            QScrollArea {{ background: transparent; border: none; }}
        """)
        root = QVBoxLayout(self)
        self.setStyleSheet(self.styleSheet() + TOUCH_SCROLL_AREA_STYLE)
        root.setContentsMargins(18, 12, 18, 12)
        root.setSpacing(12)
        header = QHBoxLayout()
        self._title_label = QLabel()
        self._title_label.setStyleSheet(APP_PAGE_TITLE_STYLE)
        self._count = QLabel()
        self._count.setStyleSheet(f'background: {SECONDARY_BG}; color: {PRIMARY}; border-radius: 9px; padding: 5px 10px;')
        header.addWidget(self._title_label)
        header.addWidget(self._count)
        header.addStretch()
        root.addLayout(header)
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        self._search = KeyboardLineEdit()
        self._search.textChanged.connect(self.search_changed)
        toolbar.addWidget(self._search, 1)
        self._sort_buttons = {}
        sort_group = QButtonGroup(self)
        for mode in ('recent', 'name', 'height'):
            button = self._button()
            button.setCheckable(True)
            button.setProperty('sort_mode', mode)
            button.clicked.connect(self._on_sort_clicked)
            sort_group.addButton(button)
            self._sort_buttons[mode] = button
            toolbar.addWidget(button)
        self._sort_buttons['recent'].setChecked(True)
        self._grid_button = self._button('fa5s.th-large')
        self._list_button = self._button('fa5s.list')
        modes = QButtonGroup(self)
        for button in (self._grid_button, self._list_button):
            button.setCheckable(True)
            modes.addButton(button)
            toolbar.addWidget(button)
        self._list_button.setChecked(True)
        self._grid_button.clicked.connect(self._show_grid)
        self._list_button.clicked.connect(self._show_list)
        self._select_button = self._button('fa5s.check-square')
        self._select_button.setCheckable(True)
        self._select_button.setVisible(self._selection_enabled)
        self._select_button.toggled.connect(self._toggle_selection_mode)
        toolbar.addWidget(self._select_button)
        self._refresh_button = self._button('fa5s.sync-alt')
        self._refresh_button.clicked.connect(self.refresh_requested)
        toolbar.addWidget(self._refresh_button)
        root.addLayout(toolbar)
        self._selection_bar = QWidget()
        selection_layout = QHBoxLayout(self._selection_bar)
        selection_layout.setContentsMargins(0, 0, 0, 0)
        self._selection_count = QLabel()
        selection_layout.addWidget(self._selection_count)
        self._btn_match_all = self._button()
        self._btn_match_all.clicked.connect(self._on_match_all)
        self._btn_clear_selection = self._button()
        self._btn_clear_selection.clicked.connect(self._on_clear_selection)
        self._show_selected = self._button()
        self._show_selected.setCheckable(True)
        self._show_selected.toggled.connect(self.show_selected_changed)
        for button in (self._btn_match_all, self._btn_clear_selection, self._show_selected):
            selection_layout.addWidget(button)
        selection_layout.addStretch()
        self._selection_bar.hide()
        root.addWidget(self._selection_bar)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._stack = QStackedWidget()
        self._table = QTableWidget()
        self._table.setColumnCount(3)
        self._table.horizontalHeader().hide()
        self._table.verticalHeader().hide()
        self._table.setShowGrid(False)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        palette = self._table.palette()
        palette.setColor(QPalette.ColorRole.Highlight, QColor(BG_COLOR))
        self._table.setPalette(palette)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._table.setColumnHidden(0, True)
        self._table.setColumnHidden(1, True)
        self._table.setColumnWidth(0, 42)
        self._list_delegate = LibraryCardDelegate(self)
        self._table.setItemDelegateForColumn(2, self._list_delegate)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        self._table.itemChanged.connect(self._on_selection_item_changed)
        self._stack.addWidget(self._table)
        self._grid = QListWidget()
        self._grid.setViewMode(QListView.ViewMode.IconMode)
        self._grid.setPalette(palette)
        self._grid.setResizeMode(QListView.ResizeMode.Adjust)
        self._grid.setMovement(QListView.Movement.Static)
        self._grid.setGridSize(QSize(200, 216))
        self._grid.setSpacing(3)
        self._grid_delegate = LibraryCardDelegate(self)
        self._grid_delegate.grid = True
        self._grid.setItemDelegate(self._grid_delegate)
        self._grid.currentItemChanged.connect(self._on_grid_selection)
        self._grid.itemChanged.connect(self._on_grid_check)
        self._stack.addWidget(self._grid)
        splitter.addWidget(self._stack)
        detail = QFrame()
        detail.setObjectName('detailCard')
        detail.setMinimumWidth(300)
        outer = QVBoxLayout(detail)
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(12)
        self._thumbnail = QLabel()
        self._thumbnail.setFixedHeight(160)
        self._thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._thumbnail.setStyleSheet(f'background: {SECONDARY_BG}; border-radius: 12px; color: {TERTIARY_TEXT};')
        outer.addWidget(self._thumbnail)
        self._preview_info = QLabel()
        self._preview_info.setWordWrap(True)
        self._preview_info.setStyleSheet(f'color: {PRIMARY}; font-size: 9pt;')
        outer.addWidget(self._preview_info)
        stats_row = QHBoxLayout()
        self._stat_values = []
        for _ in range(3):
            label = QLabel()
            label.setWordWrap(True)
            label.setStyleSheet(f'background: {BG_COLOR}; color: {TERTIARY_TEXT}; border-radius: 8px; padding: 8px; font-size: 8pt;')
            stats_row.addWidget(label, 1)
            self._stat_values.append(label)
        outer.addLayout(stats_row)
        scroll = QScrollArea()
        self._detail_scroll = scroll
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        container = QWidget()
        container.setStyleSheet('background: white;')
        self._detail_layout = QVBoxLayout(container)
        self._detail_layout.setContentsMargins(0, 0, 0, 0)
        self._detail_layout.setSpacing(4)
        scroll.setWidget(container)
        outer.addWidget(scroll, 1)
        self._btn_open = self._button('fa5s.external-link-alt', primary=True)
        self._btn_open.clicked.connect(self._on_open_in_editor)
        outer.addWidget(self._btn_open)
        actions = QHBoxLayout()
        self._btn_save = self._button('fa5s.save')
        self._btn_save.clicked.connect(self._on_save)
        actions.addWidget(self._btn_save, 1)
        self._btn_duplicate = self._button('fa5s.copy')
        self._btn_duplicate.clicked.connect(self._on_duplicate)
        self._btn_duplicate.hide()
        actions.addWidget(self._btn_duplicate)
        self._btn_delete = self._button('fa5s.trash-alt')
        self._btn_delete.clicked.connect(self._on_delete)
        actions.addWidget(self._btn_delete)
        outer.addLayout(actions)
        splitter.addWidget(detail)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([640, 310])
        root.addWidget(splitter, 1)
        self._status = QLabel()
        self._status.setStyleSheet(f'color: {TERTIARY_TEXT}; font-size: 9pt;')
        root.addWidget(self._status)
        self._thumbnail_timer = QTimer(self)
        self._thumbnail_timer.setSingleShot(True)
        self._thumbnail_timer.timeout.connect(self._request_visible_thumbnails)
        self._table.verticalScrollBar().valueChanged.connect(self._schedule_visible_thumbnails)
        self._grid.verticalScrollBar().valueChanged.connect(self._schedule_visible_thumbnails)
        self.retranslateUi()
        self.set_detail(None)

    def clean_up(self):
        self._thumbnail_timer.stop()

    def showEvent(self, event):
        super().showEvent(event)
        self.refresh_requested.emit()

    def set_schema(self, schema):
        self._schema = schema

    def set_records(self, records):
        selected = self.selected_record()
        selected_id = str(selected.get_id(self._schema.id_key)) if selected else None
        self._records = list(records)
        self._loading_records = True
        self._table.blockSignals(True)
        self._grid.blockSignals(True)
        self._table.setRowCount(0)
        self._grid.clear()
        self._thumbnail_items.clear()
        records = sorted(self._records, key=self._sort_key, reverse=self._sort_mode == 'recent')
        self._table.setRowCount(len(records))
        current = -1
        for row, record in enumerate(records):
            sid = str(record.get_id(self._schema.id_key))
            self._table.setRowHeight(row, 76)
            items = []
            for col in range(3):
                item = QTableWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, record)
                item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                if col == 0:
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Checked if sid in self._checked_ids else Qt.CheckState.Unchecked)
                self._table.setItem(row, col, item)
                items.append(item)
            grid_item = QListWidgetItem(self._grid)
            grid_item.setData(Qt.ItemDataRole.UserRole, record)
            grid_item.setSizeHint(QSize(194, 210))
            grid_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | (Qt.ItemFlag.ItemIsUserCheckable if self._selection_mode else Qt.ItemFlag.NoItemFlags))
            grid_item.setCheckState(items[0].checkState())
            items[2].setData(Qt.ItemDataRole.CheckStateRole, items[0].checkState())
            self._thumbnail_items[sid] = (items[1], items[2], grid_item)
            if sid == selected_id:
                current = row
        self._table.setCurrentCell(current, 2)
        self._grid.setCurrentRow(current)
        self._table.blockSignals(False)
        self._grid.blockSignals(False)
        self._loading_records = False
        self._count.setText(self.tr('{count} workpieces').format(count=len(records)))
        if current < 0:
            self.set_detail(None)
            self.selection_changed.emit(None)
        else:
            if self._detail_record is None or self._detail_record.to_dict() != records[current].to_dict():
                self.set_detail(records[current])
            self.selection_changed.emit(records[current])
        self._schedule_visible_thumbnails()

    def _sort_key(self, record):
        if self._sort_mode == 'name':
            return str(record.get(self._schema.name_key)).casefold()
        if self._sort_mode == 'height':
            try:
                return float(record.get('height_mm', record.get('height', 0)))
            except (ValueError, TypeError):
                return 0
        return str(record.get('date', ''))

    def record_summary(self, record):
        values = [str(record.get('date', ''))]
        dimensions = record.get('dimensions', '')
        if dimensions:
            values.append(str(dimensions))
        height = record.get('height_mm', record.get('height', ''))
        if height != '':
            values.append(f'{height} mm')
        return '  ·  '.join((v for v in values if v))

    def set_table_thumbnail(self, storage_id, image_bytes):
        pixmap = QPixmap()
        if image_bytes and pixmap.loadFromData(image_bytes):
            for item in self._thumbnail_items.get(storage_id, ()):
                item.setIcon(QIcon(pixmap))

    def set_thumbnail(self, image_bytes):
        pixmap = QPixmap()
        if image_bytes and pixmap.loadFromData(image_bytes):
            self._thumbnail.setPixmap(pixmap.scaled(max(150, self._thumbnail.width() - 20), 144, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self._thumbnail.clear()
            self._thumbnail.setText(self.tr('No preview'))

    def set_preview_stats(self, stats):
        self._preview_stats = stats
        self._stat_values[0].setText(f'{stats['points']}\n' + self.tr('points') if stats else '—\n' + self.tr('points'))
        self._stat_values[1].setText(f'{stats['path_length']:.1f} mm\n' + self.tr('path length') if stats else '—\n' + self.tr('path length'))
        record = self._detail_record
        self._stat_values[2].setText(str(record.get('date', '—')) + '\n' + self.tr('saved date') if record else '—\n' + self.tr('saved date'))
        self._preview_info.setText((stats.get('dimensions', '') + '   ·   ' if stats else '') + self.tr('ID {id}').format(id=record.get('workpieceId', record.get_id(self._schema.id_key))) if record else '')

    def set_detail(self, record):
        self._detail_record = record
        while self._detail_layout.count():
            item = self._detail_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                item.widget().deleteLater()
        self._edit_widgets = {}
        self._original_values = {}
        for button in (self._btn_open, self._btn_save, self._btn_delete, self._btn_duplicate):
            button.setEnabled(record is not None)
        self.set_preview_stats(None)
        if record is None:
            self._detail_layout.addWidget(QLabel(self.tr('Select a workpiece to view details')))
            self.set_thumbnail(None)
            self._set_saved(True)
            return
        for fd in self._schema.get_detail_fields():
            if not fd.editable:
                continue
            label = QLabel(self.tr(fd.label))
            label.setStyleSheet(f'color: {TERTIARY_TEXT}; font-size: 9pt;')
            self._detail_layout.addWidget(label)
            value = record.get(fd.key, '')
            if fd.widget == 'combo' and fd.options:
                widget = QComboBox()
                widget.addItems([str(v) for v in fd.options])
                widget.setCurrentText(str(value))
                widget.currentTextChanged.connect(self._mark_dirty)
            elif fd.key in ('height', 'height_mm'):
                widget = KeyboardNumberField(decimal=True, button_width=36)
                widget.setRange(0, 100000)
                widget.setDecimals(2)
                widget.setSingleStep(0.1)
                widget.setSuffix(' mm')
                try:
                    widget.setValue(float(value))
                except (TypeError, ValueError):
                    widget.setValue(0)
                widget.valueChanged.connect(self._mark_dirty)
            else:
                widget = KeyboardLineEdit(str(value))
                widget.textChanged.connect(self._mark_dirty)
            self._edit_widgets[fd.key] = widget
            self._detail_layout.addWidget(widget)
            self._original_values[fd.key] = self._field_value(widget)
        self._detail_layout.addStretch()
        self._set_saved(True)

    @staticmethod
    def _field_value(widget):
        if isinstance(widget, KeyboardNumberField):
            return widget.value()
        if isinstance(widget, QComboBox):
            return widget.currentText()
        return widget.text()

    def _mark_dirty(self, *_):
        self._set_saved(all((self._field_value(w) == self._original_values.get(k) for k, w in self._edit_widgets.items())))

    def _set_saved(self, saved):
        self._btn_save.setText(self.tr('Saved') if saved else self.tr('Save changes'))
        self._btn_save.setEnabled(not saved and self._detail_record is not None)

    def set_duplicate_enabled(self, enabled):
        self._btn_duplicate.setVisible(enabled)

    def set_status(self, msg):
        self._status.setText(msg)

    def set_available_ids(self, ids):
        self._all_record_ids = set(ids)

    def checked_ids(self):
        return self._checked_ids.copy()

    def set_selection(self, ids):
        self._checked_ids = self._all_record_ids.copy() if ids is None else set(ids)
        self._loading_records = True
        for row in range(self._table.rowCount()):
            item = self._table.item(row, 0)
            sid = str(item.data(Qt.ItemDataRole.UserRole).get_id(self._schema.id_key))
            state = Qt.CheckState.Checked if sid in self._checked_ids else Qt.CheckState.Unchecked
            item.setCheckState(state)
            self._table.item(row, 2).setData(Qt.ItemDataRole.CheckStateRole, state)
            self._grid.item(row).setCheckState(state)
        self._loading_records = False
        self._update_selection_label()

    def selected_record(self):
        item = self._grid.currentItem() if self._grid_mode else self._table.item(self._table.currentRow(), 2)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def _on_selection_changed(self):
        if self._loading_records:
            return
        self._grid.blockSignals(True)
        self._grid.setCurrentRow(self._table.currentRow())
        self._grid.blockSignals(False)
        record = self.selected_record()
        self.set_detail(record)
        self.selection_changed.emit(record)

    def _on_grid_selection(self, current, previous):
        if self._loading_records:
            return
        self._table.blockSignals(True)
        self._table.setCurrentCell(self._grid.currentRow(), 2)
        self._table.blockSignals(False)
        record = self.selected_record()
        self.set_detail(record)
        self.selection_changed.emit(record)

    def _on_selection_item_changed(self, item):
        if self._loading_records or item.column() != 0:
            return
        sid = str(item.data(Qt.ItemDataRole.UserRole).get_id(self._schema.id_key))
        if item.checkState() == Qt.CheckState.Checked:
            self._checked_ids.add(sid)
        else:
            self._checked_ids.discard(sid)
        self.set_selection(tuple(self._checked_ids))
        self._emit_selection()

    def _on_grid_check(self, item):
        if self._loading_records:
            return
        row = self._grid.row(item)
        self._table.item(row, 0).setCheckState(item.checkState())

    def _emit_selection(self):
        self.selection_requested.emit(None if self._checked_ids == self._all_record_ids else tuple(sorted(self._checked_ids)))

    def _on_match_all(self):
        self.set_selection(None)
        self._emit_selection()

    def _on_clear_selection(self):
        self.set_selection(())
        self._emit_selection()

    def _update_selection_label(self):
        self._selection_count.setText(self.tr('{count} selected').format(count=len(self._checked_ids)))

    def _toggle_selection_mode(self, enabled):
        self._selection_mode = enabled
        self._selection_bar.setVisible(enabled)
        self._table.setColumnHidden(0, not enabled)
        self.set_records(self._records)

    def _on_sort_clicked(self):
        self._sort_mode = self.sender().property('sort_mode')
        self.set_records(self._records)

    def _show_grid(self):
        self._set_display_mode(True)

    def _show_list(self):
        self._set_display_mode(False)

    def _set_display_mode(self, grid):
        self._grid_mode = grid
        self._stack.setCurrentIndex(int(grid))
        self._schedule_visible_thumbnails()

    def _schedule_visible_thumbnails(self, *_):
        self._thumbnail_timer.start(80)

    def _request_visible_thumbnails(self):
        ids = []
        for row in range(self._table.rowCount()):
            if self._grid_mode:
                item = self._grid.item(row)
                visible = self._grid.visualItemRect(item).intersects(self._grid.viewport().rect())
            else:
                item = self._table.item(row, 2)
                visible = self._table.visualItemRect(item).intersects(self._table.viewport().rect())
            if visible:
                ids.append(str(item.data(Qt.ItemDataRole.UserRole).get_id(self._schema.id_key)))
        if ids:
            self.visible_thumbnails_requested.emit(ids)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, '_thumbnail_timer'):
            self._schedule_visible_thumbnails()

    def _on_save(self):
        record = self.selected_record()
        if record:
            self.edit_requested.emit(record, {k: self._field_value(w) for k, w in self._edit_widgets.items()})

    def _on_delete(self):
        record = self.selected_record()
        if record:
            self.delete_requested.emit(str(record.get_id(self._schema.id_key)))

    def _on_duplicate(self):
        record = self.selected_record()
        if record:
            self.duplicate_requested.emit(record)

    def _on_open_in_editor(self):
        record = self.selected_record()
        if record:
            self.open_in_editor_requested.emit(record)

    def retranslateUi(self):
        if not hasattr(self, '_btn_save'):
            return
        self._title_label.setText(self.tr('Workpiece Library'))
        self._search.setPlaceholderText(self.tr('Search by name or ID…'))
        for mode, text in (('recent', 'Recent'), ('name', 'Name'), ('height', 'Height')):
            self._sort_buttons[mode].setText(self.tr(text))
        self._select_button.setText(self.tr('Select'))
        self._refresh_button.setToolTip(self.tr('Refresh'))
        self._grid_button.setToolTip(self.tr('Grid view'))
        self._list_button.setToolTip(self.tr('List view'))
        self._btn_open.setText(self.tr('Open in Editor'))
        self._btn_duplicate.setToolTip(self.tr('Duplicate'))
        self._btn_delete.setToolTip(self.tr('Delete'))
        self._btn_match_all.setText(self.tr('Select All'))
        self._btn_clear_selection.setText(self.tr('Clear Selection'))
        self._show_selected.setText(self.tr('Show Selected'))
        self._count.setText(self.tr('{count} workpieces').format(count=len(self._records)))
        self._update_selection_label()
        if hasattr(self, '_original_values'):
            values = {k: self._field_value(w) for k, w in self._edit_widgets.items()}
            original = self._original_values.copy()
            record = self._detail_record
            stats = self._preview_stats
            self.set_detail(record.with_updates(values) if record else None)
            self._detail_record = record
            self._original_values = original
            self._mark_dirty()
            self.set_preview_stats(stats)

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange:
            self.retranslateUi()
        super().changeEvent(event)
