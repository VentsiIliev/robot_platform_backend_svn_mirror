import json
from datetime import datetime

from PyQt6.QtCore import QDateTime, QEvent, QSignalBlocker, Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QDateTimeEdit, QFileDialog, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QPlainTextEdit, QPushButton, QSplitter, QTableWidget,
    QTableWidgetItem, QVBoxLayout, QWidget, QAbstractItemView,
)

from pl_gui.settings.settings_view.styles import (
    ACTION_BTN_STYLE, APP_PAGE_TITLE_STYLE, BG_COLOR, GHOST_BTN_STYLE, LABEL_STYLE,
)
from src.applications.base.i_application_view import IApplicationView
from src.applications.base.widgets.custom_virtual_keyboard import KeyboardLineEdit


class DiagnosticsView(IApplicationView):
    """Read-only history presentation and semantic filter signals."""
    SHOW_JOG_WIDGET = False
    refresh_requested = pyqtSignal()
    export_requested = pyqtSignal(dict, str)
    language_requested = pyqtSignal(str)
    _WINDOWS = (900, 3600, 28800, 86400, None, None)

    def __init__(self, parent=None):
        self._events = []
        self._result = None
        self._error = None
        self._busy = False
        super().__init__('Diagnostics', parent)

    def _t(self, text):
        return self.tr(text) or text

    def setup_ui(self):
        self.setStyleSheet(f'background-color: {BG_COLOR};')
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        heading = QHBoxLayout()
        self._title = QLabel()
        self._title.setStyleSheet(APP_PAGE_TITLE_STYLE)
        heading.addWidget(self._title, 1)
        self._language = QComboBox()
        self._language.addItem('English', 'en')
        self._language.addItem('Български', 'bg')
        heading.addWidget(self._language)
        layout.addLayout(heading)
        self._notice = QLabel()
        self._notice.setWordWrap(True)
        layout.addWidget(self._notice)
        source = QHBoxLayout()
        self._directory = KeyboardLineEdit()
        self._directory.setReadOnly(True)
        self._browse = QPushButton()
        self._browse.setStyleSheet(GHOST_BTN_STYLE)
        self._refresh = QPushButton()
        self._export = QPushButton()
        self._export.setStyleSheet(GHOST_BTN_STYLE)
        self._refresh.setStyleSheet(ACTION_BTN_STYLE)
        for button in (self._browse, self._refresh, self._export):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
        source.addWidget(self._directory, 1)
        source.addWidget(self._browse)
        source.addWidget(self._export)
        source.addWidget(self._refresh)
        layout.addLayout(source)
        filters = QGridLayout()
        self._range_label, self._level_label, self._search_label = QLabel(), QLabel(), QLabel()
        for label in (self._range_label, self._level_label, self._search_label):
            label.setStyleSheet(LABEL_STYLE)
        self._range = QComboBox()
        self._range.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)
        for seconds in self._WINDOWS:
            self._range.addItem('', seconds)
        self._range.setCurrentIndex(1)
        self._level = QComboBox()
        for value in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
            self._level.addItem(value, value)
        self._level.setCurrentIndex(0)
        self._search = KeyboardLineEdit()
        filters.addWidget(self._range_label, 0, 0)
        filters.addWidget(self._level_label, 0, 1)
        filters.addWidget(self._search_label, 0, 2)
        filters.addWidget(self._range, 1, 0)
        filters.addWidget(self._level, 1, 1)
        filters.addWidget(self._search, 1, 2)
        filters.setColumnStretch(2, 1)
        self._live = QCheckBox()
        filters.addWidget(self._live, 1, 3)
        layout.addLayout(filters)
        self._custom = QWidget()
        custom_layout = QHBoxLayout(self._custom)
        custom_layout.setContentsMargins(0, 0, 0, 0)
        self._from_label, self._until_label = QLabel(), QLabel()
        self._since, self._until = QDateTimeEdit(), QDateTimeEdit()
        self._since.setDateTime(QDateTime.currentDateTime().addSecs(-3600))
        self._until.setDateTime(QDateTime.currentDateTime())
        for field in (self._since, self._until):
            field.setCalendarPopup(True)
            field.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        custom_layout.addWidget(self._from_label)
        custom_layout.addWidget(self._since, 1)
        custom_layout.addWidget(self._until_label)
        custom_layout.addWidget(self._until, 1)
        layout.addWidget(self._custom)
        self._custom.hide()
        self._status = QLabel()
        self._status.setTextFormat(Qt.TextFormat.PlainText)
        self._status.setWordWrap(True)
        self._warnings = QLabel()
        self._warnings.setWordWrap(True)
        self._warnings.setTextFormat(Qt.TextFormat.PlainText)
        self._warnings.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self._status)
        layout.addWidget(self._warnings)
        self._export_status = QLabel()
        self._export_status.setWordWrap(True)
        self._export_status.setTextFormat(Qt.TextFormat.PlainText)
        self._export_status.hide()
        self._last_export = self._last_export_error = None
        layout.addWidget(self._export_status)
        splitter = QSplitter(Qt.Orientation.Vertical)
        self._table = QTableWidget(0, 7)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.setAlternatingRowColors(True)
        self._table.setWordWrap(False)
        self._table.verticalHeader().hide()
        for index, width in enumerate((215, 80, 240, 100, 340, 70, 140)):
            self._table.setColumnWidth(index, width)
        self._table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self._details = QPlainTextEdit()
        self._details.setReadOnly(True)
        self._details.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        splitter.addWidget(self._table)
        splitter.addWidget(self._details)
        splitter.setSizes([450, 230])
        layout.addWidget(splitter, 1)
        self._debounce = QTimer(self)
        self._debounce.setSingleShot(True)
        self._debounce.setInterval(250)
        self._debounce.timeout.connect(self._request_refresh)
        self._timer = QTimer(self)
        self._timer.setInterval(3000)
        self._timer.timeout.connect(self._on_tick)
        self._refresh.clicked.connect(self._request_refresh)
        self._browse.clicked.connect(self._choose_directory)
        self._export.clicked.connect(self._choose_export)
        self._range.currentIndexChanged.connect(self._on_filters_changed)
        self._level.currentIndexChanged.connect(self._on_filters_changed)
        self._search.textChanged.connect(self._on_filters_changed)
        self._since.dateTimeChanged.connect(self._on_filters_changed)
        self._until.dateTimeChanged.connect(self._on_filters_changed)
        self._live.toggled.connect(self._on_live_changed)
        self._language.currentIndexChanged.connect(self._on_language_changed)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        self.retranslateUi()

    def set_directory(self, directory):
        self._directory.setText(directory)

    def filters(self):
        custom = self._range.currentIndex() == 5
        return {'directory': self._directory.text(), 'window_seconds': self._range.currentData(),
                'since': self._since.dateTime().toPyDateTime().astimezone().isoformat() if custom else None,
                'until': self._until.dateTime().toPyDateTime().astimezone().isoformat() if custom else None,
                'level': self._level.currentData(), 'search': self._search.text()}

    def set_busy(self, busy):
        self._busy = busy
        self._refresh.setEnabled(not busy)
        self._export.setEnabled(not busy)
        self._update_status()

    @staticmethod
    def _identity(record):
        return (record.get('timestamp'), record.get('event'), record.get('message'),
                record.get('context'), record.get('fields'))

    def set_result(self, result):
        row = self._table.currentRow()
        previous = self._identity(self._events[row]) if 0 <= row < len(self._events) else None
        self._result, self._error, self._events = result, None, result.get('events', [])
        selected = len(self._events) - 1
        with QSignalBlocker(self._table):
            self._table.setRowCount(len(self._events))
            for row, record in enumerate(self._events):
                context = record.get('context')
                context = context if isinstance(context, dict) else {}
                actor = context.get('actor')
                actor = actor if isinstance(actor, dict) else {}
                fields = record.get('fields')
                fields = fields if isinstance(fields, dict) else {}
                operation = next((context[key] for key in ('cycle_id', 'operation_id', 'run_id', 'action_id')
                                  if context.get(key)), '')
                values = (record.get('_display_time', ''), record.get('level', ''),
                          record.get('event') or record.get('logger', ''), fields.get('outcome', ''),
                          record.get('_summary', ''), actor.get('user_id') or '', operation)
                for column, value in enumerate(values):
                    item = QTableWidgetItem(str(value)[:2048])
                    self._table.setItem(row, column, item)
                if self._identity(record) == previous:
                    selected = row
            if selected >= 0:
                self._table.selectRow(selected)
        self._on_selection_changed()
        self._warnings.setText('\n'.join(result.get('warnings', [])))
        self._warnings.setVisible(bool(result.get('warnings')))
        self._update_status()
        if previous is None:
            self._table.scrollToBottom()

    def set_error(self, error):
        self.set_result({'events': [], 'warnings': [], 'matched': 0})
        self._error = str(error)[:2048]
        self._update_status()

    def _update_status(self):
        if self._busy:
            text = self._t('Reading retained history…')
        elif self._error:
            text = self._t('Read failed: {error}').format(error=self._error)
        elif self._result is None:
            text = self._t('Choose a diagnostics directory to begin.')
        else:
            text = self._t('{shown} of {matched} matching retained events · local time · newest 500 maximum').format(
                shown=len(self._events), matched=self._result.get('matched', 0))
            if not self._events:
                text += ' · ' + self._t('No matching retained events; check filters and capture coverage.')
            if self._result.get('limited'):
                text += ' · ' + self._t('Scan incomplete; see warnings.')
        self._status.setText(text)

    def _on_selection_changed(self):
        row = self._table.currentRow()
        record = self._events[row] if 0 <= row < len(self._events) else None
        self._details.setPlainText(json.dumps({key: value for key, value in record.items()
            if not key.startswith('_')}, ensure_ascii=False, indent=2)[:262144] if record else '')

    def _request_refresh(self):
        self._debounce.stop()
        self.refresh_requested.emit()

    def _on_filters_changed(self, *_):
        self._custom.setVisible(self._range.currentIndex() == 5)
        self._debounce.start()

    def _choose_directory(self):
        path = QFileDialog.getExistingDirectory(self, self._t('Open diagnostics directory'), self._directory.text())
        if path:
            self.set_directory(path)
            self._request_refresh()

    def _on_tick(self):
        if self.isVisible():
            self._request_refresh()

    def _choose_export(self):
        path, _ = QFileDialog.getSaveFileName(self, self._t('Export incident'),
            datetime.now().strftime('incident-%Y%m%d-%H%M%S.zip'), self._t('ZIP archive (*.zip)'))
        if path:
            filters = self.filters()
            row = self._table.currentRow()
            context = self._events[row].get('context') if 0 <= row < len(self._events) else None
            if isinstance(context, dict):
                filters['selected_operation_id'] = context.get('operation_id')
            self.export_requested.emit(filters, path)

    def set_export_result(self, result):
        self._last_export, self._last_export_error = result, None
        self._update_export_status()

    def set_export_error(self, error):
        self._last_export_error, self._last_export = str(error), None
        self._update_export_status()

    def _update_export_status(self):
        if self._last_export_error:
            text = self._t('Export failed: {error}').format(error=self._last_export_error)
        elif self._last_export:
            text = self._t('Exported {count} retained events to {path}. Check manifest.json for gaps.').format(
                count=self._last_export['event_count'], path=self._last_export['path'])
        else:
            text = ''
        self._export_status.setText(text)
        self._export_status.setVisible(bool(text))

    def _on_live_changed(self, checked):
        if checked:
            self._timer.start()
            self._request_refresh()
        else:
            self._timer.stop()

    def _on_language_changed(self):
        self.language_requested.emit(self._language.currentData())

    def set_language(self, code):
        with QSignalBlocker(self._language):
            self._language.setCurrentIndex(max(0, self._language.findData(code)))

    def retranslateUi(self):
        self._title.setText(self._t('Machine diagnostics'))
        self._notice.setText(self._t('Read-only retained history. Gaps and uncaptured actions may exist.'))
        self._browse.setText(self._t('Open folder'))
        self._refresh.setText(self._t('Refresh'))
        self._export.setText(self._t('Export incident'))
        self._export.setToolTip(self._t('Exports the selected event’s retained operation when available; otherwise the current filters.'))
        for button in (self._browse, self._refresh, self._export):
            button.setMinimumWidth(button.fontMetrics().horizontalAdvance(button.text()) + 40)
        self._range_label.setText(self._t('Time window'))
        self._level_label.setText(self._t('Minimum severity'))
        self._search_label.setText(self._t('Search'))
        self._search.setPlaceholderText(self._t('Message, event, user, source, cycle or action ID'))
        self._live.setText(self._t('Live refresh'))
        self._live.setMinimumWidth(self._live.fontMetrics().horizontalAdvance(self._live.text()) + 32)
        self._from_label.setText(self._t('From (local time)'))
        self._until_label.setText(self._t('Until (local time)'))
        self._details.setPlaceholderText(self._t('Select an event to inspect its captured fields and traceback.'))
        with QSignalBlocker(self._range):
            for index, text in enumerate(('Last 15 minutes', 'Last hour', 'Last 8 hours', 'Last 24 hours',
                                           'All retained history', 'Custom interval')):
                self._range.setItemText(index, self._t(text))
        self._table.setHorizontalHeaderLabels([self._t(text) for text in (
            'Time', 'Level', 'Event / source', 'Outcome', 'Summary', 'User', 'Operation / action')])
        for index in (5, 6):
            text = self._table.horizontalHeaderItem(index).text()
            width = self._table.horizontalHeader().fontMetrics().horizontalAdvance(text) + 24
            self._table.setColumnWidth(index, max(self._table.columnWidth(index), width))
        self._update_status()
        self._update_export_status()

    def changeEvent(self, event):
        if event.type() == QEvent.Type.LanguageChange and hasattr(self, '_title'):
            self.retranslateUi()
        super().changeEvent(event)

    def clean_up(self):
        self._timer.stop()
        self._debounce.stop()
