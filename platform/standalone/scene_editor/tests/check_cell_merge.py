"""Offline selection-to-merge and saved-pending UI regression checks."""
from copy import deepcopy
from pathlib import Path
import sys,tempfile,time
from unittest.mock import Mock,patch
import numpy as np
from PyQt6.QtCore import QSettings
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication,QMenu
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.geometry import make_box,combine_meshes
from scene_editor.model import Scene,SceneObject,Pose
from scene_editor.window import EditorWindow


def main():
    app=QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory() as directory:
        QSettings.setPath(QSettings.Format.NativeFormat,QSettings.Scope.UserScope,directory)
        window=EditorWindow()
        first=SceneObject('One',make_box((10,20,30)),Pose((100,200,300),(0,0,30)),id='world/cell_fixture_one/0')
        second=SceneObject('Two',make_box((20,30,40)),Pose((400,200,300),(0,0,90)),id='world/cell_fixture_two/0')
        third=SceneObject('Other',make_box((1,2,3)),id='world/cell_fixture_other/0')
        errors=[];window._error=errors.append
        def wait():
            deadline=time.monotonic()+5
            while window._jobs and time.monotonic()<deadline:QTest.qWait(10)
            assert not window._jobs
        merged={'success':True,'profile':'tray','revision':'merged','merged_object_id':'cell_fixture_dispenser',
            'pending_application':False,'saved':{'CELL_COLLISION_OBJECTS':{
                'cell_fixture_one':{'enabled':False,'merged_into':'cell_fixture_dispenser'},
                'cell_fixture_two':{'enabled':False,'merged_into':'cell_fixture_dispenser'},
                'cell_fixture_dispenser':{'enabled':True,'parts':[{},{}]}}}}
        merged['applied']=deepcopy(merged['saved'])
        window._replace_scene(Scene([first,second,third]))
        window._select_many({first.id,second.id},first.id)
        menu=QMenu();window.add_cell_collision_actions(menu)
        action=next(a for a in menu.actions() if a.text().startswith('Merge selected'))
        assert action.isEnabled()
        with patch('scene_editor.window.BackendConfigurationClient') as Client, patch(
                'scene_editor.window.QInputDialog.getText',return_value=('dispenser',True)):
            client=Client.return_value;client.merge_fixtures.return_value=merged
            action.trigger();wait()
            client.merge_fixtures.assert_called_once_with(['cell_fixture_one','cell_fixture_two'],'dispenser')
            assert not errors,errors
            assert len(window.scene.objects)==2
            compound=window.selected()
            assert compound.id=='world/cell_fixture_dispenser/0'
            expected=combine_meshes([(obj.mesh,obj.matrix()) for obj in (first,second)])
            np.testing.assert_array_equal(compound.mesh.vertices,expected.vertices)
            assert len(compound.mesh.vertices)==24
            assert third.id in {obj.id for obj in window.scene.objects}
            assert not any('collision disabled' in obj.name for obj in window.scene.objects)
            # A durable-but-pending merge must retain the currently active originals.
            window._replace_scene(Scene([first,second,third]))
            window._select_many({first.id,second.id},first.id)
            pending=deepcopy(merged);pending['pending_application']=True
            pending['application_error']='Saved; robot is moving'
            pending['applied']={'CELL_COLLISION_OBJECTS':{'cell_fixture_one':{'enabled':True},'cell_fixture_two':{'enabled':True}}}
            client.merge_fixtures.return_value=pending
            window.merge_selected_cell_collisions();wait()
            assert {obj.id for obj in window.scene.objects}=={first.id,second.id,third.id}
            assert 'pending' in window.collision_status.text()
            window.cell_scene_configuration_received(merged)
            assert window.selected().id=='world/cell_fixture_dispenser/0'
            assert len(window.scene.objects)==2
            # Invalid selection and cancellation never submit a merge.
            window._select(third.id);client.merge_fixtures.reset_mock()
            window.merge_selected_cell_collisions()
            client.merge_fixtures.assert_not_called()
        window.history.setClean();window.close();app.processEvents()
    print('Cell merge UI checks passed: selection, exact geometry, one object, pending apply and source removal.')


if __name__=='__main__':main()
