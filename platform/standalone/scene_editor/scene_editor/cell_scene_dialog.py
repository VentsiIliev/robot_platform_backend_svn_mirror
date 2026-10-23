"""Persistent cell collision configuration, separate from local visibility."""
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (
    QAbstractItemView, QDialog, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout,
)

from .backend_configuration import BackendConfigurationClient, default_backend_url


class CellSceneDialog(QDialog):
    def __init__(self, parent, selected_id=None):
        super().__init__(parent)
        self.setWindowTitle('Cell collision configuration')
        self.resize(820, 600)
        self._view = None
        self._busy = False
        self._client = None
        self._loading = False
        self._selected_id = selected_id
        layout = QVBoxLayout(self)
        note = QLabel('Enabled objects participate in MoveIt collision checking. Save and apply persists '
                      'the selected states in the active backend profile. Visibility checkboxes in the scene remain separate.')
        note.setWordWrap(True)
        layout.addWidget(note)
        connection = QHBoxLayout()
        connection.addWidget(QLabel('Backend URL'))
        settings = QSettings('Standalone Scene Editor', 'Scene Editor')
        try:
            initial = settings.value('cell_scene/backend_url', '') or default_backend_url()
        except (ValueError, KeyError, OSError):
            initial = ''
        self.url = QLineEdit(initial)
        connection.addWidget(self.url, 1)
        self.reload_button = QPushButton('Reload')
        self.reload_button.clicked.connect(self.reload)
        connection.addWidget(self.reload_button)
        layout.addLayout(connection)
        self.profile = QLabel('No backend profile loaded')
        layout.addWidget(self.profile)
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(['Collision object', 'Enable collision checking', 'Applied', 'Geometry'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.itemChanged.connect(self._edited)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        self.status = QLabel('Reload to read saved and applied configuration.')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        actions = QHBoxLayout()
        self.save_button = QPushButton('Save and apply')
        self.save_button.clicked.connect(self.save)
        self.apply_button = QPushButton('Apply saved configuration')
        self.apply_button.clicked.connect(self.apply_saved)
        self.close_button = QPushButton('Close')
        self.close_button.clicked.connect(self.reject)
        for button in (self.save_button, self.apply_button, self.close_button):
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            actions.addWidget(button)
        self.reload_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addLayout(actions)
        self.url.textEdited.connect(self._url_edited)
        self._sync()
        self.reload()

    def _states(self):
        return {self.table.item(row,0).text(): self.table.item(row,1).checkState() == Qt.CheckState.Checked
                for row in range(self.table.rowCount())}

    def _dirty(self):
        return self._view is not None and self._states() != {
            key:item['enabled'] for key,item in self._view['saved']['CELL_COLLISION_OBJECTS'].items()
            if 'merged_into' not in item}

    def _sync(self):
        ready = self._view is not None and not self._busy
        self.save_button.setEnabled(ready and self._dirty())
        self.apply_button.setEnabled(ready and not self._dirty() and self._view.get('pending_application',False))
        self.reload_button.setEnabled(not self._busy)
        self.close_button.setEnabled(not self._busy)
        self.url.setEnabled(not self._busy)
        self.table.setEnabled(ready)

    def _url_edited(self):
        self._view = None
        self.table.setRowCount(0)
        self.profile.setText('Reload to connect to this backend')
        self._sync()

    def _edited(self, _item):
        if not self._loading:
            if self._dirty():
                self.status.setText('Unsaved changes — collision checking has not changed.')
            self._sync()

    def _run(self, function):
        if self._busy:
            return
        self._busy = True
        self.status.setText('Waiting for backend confirmation…')
        self._sync()
        def work():
            try:
                return function(), None
            except Exception as error:
                return None, str(error)
        self.parent()._submit('Cell collision configuration…', work, self._done)

    def reload(self):
        if self._busy:
            return
        try:
            client = BackendConfigurationClient(self.url.text().strip())
        except ValueError as error:
            self.status.setText(str(error))
            return
        self._client = client
        self._run(client.get)

    def save(self):
        if self._view is None or self._busy:
            return
        revision, states = self._view['revision'], self._states()
        self._run(lambda: self._client.save(revision, states))

    def apply_saved(self):
        if self._view is None or self._dirty() or self._busy:
            return
        revision = self._view['revision']
        self._run(lambda: self._client.apply(revision))

    def _done(self, result):
        view, error = result
        self._busy = False
        if error:
            self.status.setText(error+' Reload before retrying if the save result is uncertain.')
            self._sync()
            return
        self._view = view
        if hasattr(self.parent(), 'cell_scene_configuration_received'):
            self.parent().cell_scene_configuration_received(view)
        QSettings('Standalone Scene Editor', 'Scene Editor').setValue('cell_scene/backend_url', self._client.url)
        self.profile.setText('Backend profile: '+view['profile'])
        self._loading = True
        saved = {key:item for key,item in view['saved']['CELL_COLLISION_OBJECTS'].items() if 'merged_into' not in item}
        applied = (view.get('applied') or {}).get('CELL_COLLISION_OBJECTS',{})
        self.table.setRowCount(len(saved))
        for row, (key, item) in enumerate(saved.items()):
            applied_item = applied.get(key)
            state = 'Unknown' if applied_item is None else ('Enabled' if applied_item['enabled'] else 'Disabled')
            geometry = f'{len(item["parts"])} boxes' if 'parts' in item else ' × '.join(f'{value:.2f}' for value in item['size_mm'])+' mm'
            for column, text in ((0,key),(2,state),(3,geometry)):
                cell = QTableWidgetItem(text)
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row,column,cell)
            checkbox = QTableWidgetItem()
            checkbox.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsSelectable)
            checkbox.setCheckState(Qt.CheckState.Checked if item['enabled'] else Qt.CheckState.Unchecked)
            self.table.setItem(row,1,checkbox)
            if key == self._selected_id:
                self.table.selectRow(row)
        self._loading = False
        self.table.resizeColumnsToContents()
        self.status.setText(('Saved; application pending. '+(view.get('application_error') or 'Use Apply saved configuration.'))
                            if view.get('pending_application') else 'Saved and applied to MoveIt. These states survive backend restart.')
        self._sync()

    def reject(self):
        if not self._busy:
            super().reject()
