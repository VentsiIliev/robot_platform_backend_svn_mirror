"""Offline checks: object context actions persist state and preserve orbit gestures."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import Mock, patch

from PyQt6.QtCore import QPoint, QPointF, QSettings, Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QMenu

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.geometry import make_box
from scene_editor.model import Scene,SceneObject
from scene_editor.window import EditorWindow


def main():
    app=QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory() as directory:
        QSettings.setPath(QSettings.Format.NativeFormat,QSettings.Scope.UserScope,directory)
        window=EditorWindow()
        first=SceneObject('World: cell_fixture_tray_01 / 1',make_box((10,20,30)),id='world/cell_fixture_tray_01/0')
        second=SceneObject('World: cell_fixture_tray_02 / 1',make_box((20,30,40)),id='world/cell_fixture_tray_02/0')
        surface=SceneObject('Table',make_box((100,200,1)),id='world/cell_surface_tray/0')
        window._replace_scene(Scene([first,second,surface]))
        errors=[]
        window._error=errors.append
        window._select(first.id)
        def wait():
            deadline=time.monotonic()+5
            while window._jobs and time.monotonic()<deadline:QTest.qWait(10)
            assert not window._jobs
        initial={'success':True,'profile':'paint_tray_dry','revision':'new',
            'saved':{'CELL_COLLISION_OBJECTS':{'cell_fixture_tray_01':{'enabled':True},
                                             'cell_fixture_tray_02':{'enabled':True}}},
            'pending_application':False}
        initial['applied']=deepcopy(initial['saved'])
        disabled=deepcopy(initial)
        disabled['saved']['CELL_COLLISION_OBJECTS']['cell_fixture_tray_01']['enabled']=False
        disabled['applied']=deepcopy(disabled['saved'])
        with patch('scene_editor.window.BackendConfigurationClient') as Client:
            client=Client.return_value
            client.set_enabled.return_value=disabled
            menu=QMenu()
            window.add_cell_collision_actions(menu)
            actions={action.text():action for action in menu.actions()}
            assert actions['Disable collision checking (save)'].isEnabled()
            actions['Disable collision checking (save)'].trigger()
            window._select(second.id)  # The queued action must retain the original object.
            wait()
            client.set_enabled.assert_called_once_with('cell_fixture_tray_01',False)
            assert not errors,errors
            ghost=next(obj for obj in window.scene.objects if obj.id==first.id)
            assert ghost.locked and 'collision disabled' in ghost.name
            assert len(window.scene.objects)==3
            window._ros=Mock()
            window._live=window._live_received=True
            window._ros.take_latest.return_value=Scene([second,surface])
            window._poll_ros()
            assert any(obj.id==first.id for obj in window.scene.objects),'Live removal discarded the restore preview'
            window._ros.take_latest.return_value=Scene([first,second,surface])
            window._poll_ros()
            observed=next(obj for obj in window.scene.objects if obj.id==first.id)
            assert observed.name==first.name,'Cached config hid an object restored by another editor'
            window._ros.take_latest.return_value=Scene([second,surface])
            window._poll_ros()
            window._select(first.id)
            client.set_enabled.return_value=initial
            window.enable_selected_cell_collision()
            wait()
            restored=next(obj for obj in window.scene.objects if obj.id==first.id)
            assert restored.name==first.name and not restored.locked
            assert client.set_enabled.call_args.args==('cell_fixture_tray_01',True)
            # A save can succeed before the backend can verify its applied state.
            # ROS may already have removed the geometry when that reply arrives.
            unverified=deepcopy(disabled)
            unverified['applied']=None
            unverified['pending_application']=True
            client.set_enabled.return_value=unverified
            window._select(first.id)
            window.disable_selected_cell_collision()
            window._ros.take_latest.return_value=Scene([second,surface])
            window._poll_ros()
            wait()
            window._poll_ros()
            ghost=next((obj for obj in window.scene.objects if obj.id==first.id),None)
            assert ghost is not None,'Unverified application discarded disabled restore geometry'
            assert ghost.visible and ghost.locked
            assert 'unverified' in ghost.name
            window._select(first.id)
            client.set_enabled.return_value=initial
            window.enable_selected_cell_collision()
            wait()
            assert window.selected().name==first.name
            client.set_enabled.side_effect=RuntimeError('Configuration changed; reload')
            window.disable_selected_cell_collision()
            wait()
            assert errors and 'reload' in errors[-1]
            assert not window._collision_busy
            assert window._cell_scene_view==initial,'A failed write changed the displayed applied state'
            window._live=False
            window._ros=None
        window._select(surface.id)
        menu=QMenu()
        window.add_cell_collision_actions(menu)
        assert not menu.actions(),'Table surfaces must not get equipment enable/disable actions'
        window._select(first.id)
        viewport=window.viewport
        point=QPoint(40,40)
        def event(kind,position,button,buttons):
            return QMouseEvent(kind,QPointF(position),QPointF(position),button,buttons,Qt.KeyboardModifier.NoModifier)
        with patch.object(viewport,'_pick',return_value=first.id), patch('scene_editor.window.QMenu') as Menu:
            viewport.mousePressEvent(event(QMouseEvent.Type.MouseButtonPress,point,Qt.MouseButton.RightButton,Qt.MouseButton.RightButton))
            viewport.mouseReleaseEvent(event(QMouseEvent.Type.MouseButtonRelease,point,Qt.MouseButton.RightButton,Qt.MouseButton.NoButton))
            Menu.assert_called_once()
            Menu.reset_mock()
            yaw=viewport.yaw
            viewport.mousePressEvent(event(QMouseEvent.Type.MouseButtonPress,point,Qt.MouseButton.RightButton,Qt.MouseButton.RightButton))
            viewport.mouseMoveEvent(event(QMouseEvent.Type.MouseMove,point+QPoint(40,20),Qt.MouseButton.NoButton,Qt.MouseButton.RightButton))
            viewport.mouseReleaseEvent(event(QMouseEvent.Type.MouseButtonRelease,point+QPoint(40,20),Qt.MouseButton.RightButton,Qt.MouseButton.NoButton))
            Menu.assert_not_called()
            assert viewport.yaw!=yaw,'Right drag stopped orbiting'
        window._replace_scene(Scene())
        assert not window._cell_fixture_previews and window._cell_scene_view is None
        window.history.setClean()
        window.close()
        app.processEvents()
    print('Cell context menu: selection, save, restore preview, live updates, errors and right-drag orbit checks passed.')


if __name__=='__main__':main()
