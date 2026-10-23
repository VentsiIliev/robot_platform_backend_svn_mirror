"""Offline Qt check of saved/applied states; does not contact a backend."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import QApplication, QWidget
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.cell_scene_dialog import CellSceneDialog


class Parent(QWidget):
    def __init__(self):
        super().__init__()
        self.pending=[]
    def _submit(self,label,function,callback):
        self.pending.append((function,callback))
    def finish(self):
        function,callback=self.pending.pop(0)
        callback(function())


def run():
    app=QApplication.instance() or QApplication([])
    initial={'success':True,'profile':'paint_tray_dry','revision':'old',
        'saved':{'CELL_COLLISION_OBJECTS':{'cell_fixture_tray_01':{
            'enabled':True,'size_mm':[10,20,30]}}},'pending_application':False}
    initial['applied']=deepcopy(initial['saved'])
    with tempfile.TemporaryDirectory() as directory:
        QSettings.setPath(QSettings.Format.NativeFormat,QSettings.Scope.UserScope,directory)
        parent=Parent()
        with patch('scene_editor.cell_scene_dialog.BackendConfigurationClient') as Client:
            client=Client.return_value
            client.url='http://localhost:5000'
            client.get.return_value=initial
            dialog=CellSceneDialog(parent,'cell_fixture_tray_01')
            assert not dialog.save_button.isEnabled()
            parent.finish()
            assert dialog.table.item(0,1).checkState()==Qt.CheckState.Checked
            assert dialog.table.item(0,2).text()=='Enabled'
            assert not dialog.save_button.isEnabled()
            dialog.table.item(0,1).setCheckState(Qt.CheckState.Unchecked)
            assert dialog.save_button.isEnabled()
            client.save.assert_not_called()
            saved=deepcopy(initial)
            saved['revision']='saved'
            saved['saved']['CELL_COLLISION_OBJECTS']['cell_fixture_tray_01']['enabled']=False
            saved['pending_application']=True
            saved['application_error']='Saved; robot is moving'
            client.save.return_value=saved
            dialog.save()
            assert not dialog.close_button.isEnabled()
            parent.finish()
            client.save.assert_called_once_with('old',{'cell_fixture_tray_01':False})
            assert 'pending' in dialog.status.text()
            assert dialog.table.item(0,2).text()=='Enabled'
            assert dialog.apply_button.isEnabled()
            applied=deepcopy(saved)
            applied['applied']=deepcopy(saved['saved'])
            applied['pending_application']=False
            client.apply.return_value=applied
            dialog.apply_saved()
            parent.finish()
            client.apply.assert_called_once_with('saved')
            assert dialog.table.item(0,2).text()=='Disabled'
            assert 'survive' in dialog.status.text()
            dialog.table.item(0,1).setCheckState(Qt.CheckState.Checked)
            client.save.side_effect=RuntimeError('Configuration changed; reload')
            dialog.save()
            parent.finish()
            assert 'reload' in dialog.status.text()
            assert dialog.table.item(0,1).checkState()==Qt.CheckState.Checked
            compound=deepcopy(initial)
            source=compound['saved']['CELL_COLLISION_OBJECTS']['cell_fixture_tray_01']
            source['enabled']=False
            source['merged_into']='cell_fixture_dispenser'
            compound['saved']['CELL_COLLISION_OBJECTS']['cell_fixture_dispenser']={'enabled':True,'parts':[{},{}]}
            compound['applied']=deepcopy(compound['saved'])
            client.get.return_value=compound
            dialog.reload()
            parent.finish()
            assert dialog.table.rowCount()==1,'Merged source definitions leaked into the editable object list'
            assert dialog.table.item(0,0).text()=='cell_fixture_dispenser'
            assert dialog.table.item(0,3).text()=='2 boxes'
            assert not dialog._dirty()
            dialog.reject()
            dialog.deleteLater()
            parent.deleteLater()
            app.processEvents()
    print('Cell configuration dialog: save, pending application, retry and conflict checks passed.')


if __name__=='__main__':run()
