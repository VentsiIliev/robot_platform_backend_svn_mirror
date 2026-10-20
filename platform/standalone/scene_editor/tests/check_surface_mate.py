"""Real GPU triangle picking and surface-mate workflow; no ROS writes."""
from dataclasses import replace
from pathlib import Path
import sys
import numpy as np
from PyQt6.QtCore import QPoint,Qt
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.window import EditorWindow
from scene_editor.model import Scene,SceneObject,Pose
from scene_editor.geometry import make_box


def main():
    fmt = QSurfaceFormat()
    fmt.setVersion(3,3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)
    app = QApplication([])
    w = EditorWindow()
    w.show()
    source = SceneObject('Move this fixture',make_box((100,100,100)),Pose((-160,-20,90)))
    target = SceneObject('Locked mounting surface',make_box((150,150,80)),Pose((180,20,0)),locked=True)
    w._replace_scene(Scene([source,target]))
    w._select(source.id)
    v,ui = w.viewport,w._workspace
    v.set_camera_view('Top')
    QTest.qWait(200)

    def click(obj,local):
        world = (obj.matrix()@np.r_[local,1.])[:3]
        point = QPoint(*np.rint(v.project(world)).astype(int))
        QTest.mouseClick(v,Qt.MouseButton.LeftButton,pos=point)
        QTest.qWait(30)

    try:
        assert v.isValid() and not v._error,v._error
        before = source.matrix().copy()
        target_before = target.matrix().copy()
        index = w.history.index()
        w.surface_mate_action.trigger()
        assert v.surface_pick_enabled
        source_point = QPoint(*np.rint(v.project((source.matrix()@np.array([12,-8,50,1]))[:3])).astype(int))
        QTest.mouseMove(v,source_point)
        QTest.qWait(180)
        assert v.surface_hover is not None and len(v.surface_hover.region.triangles) == 2
        click(source,(12,-8,50))
        a = w._surface_mate['source']
        assert a is not None and a.object_id == source.id
        assert a.triangle in (2,3)
        assert abs(a.point[2]-50) < 1e-8
        assert len(a.region.triangles) == 2
        np.testing.assert_allclose(a.point,(0,0,50))
        # Any triangle of this face selects the same region and center.
        click(source,(-30,20,50))
        other = w._surface_mate['source']
        np.testing.assert_allclose(other.point,a.point)
        assert other.region is a.region
        a = other
        assert w.selected().id == source.id
        # After choosing the first face, both left/right drag navigate without
        # selecting a new face, changing geometry, or creating undo history.
        saved_camera = (v.yaw,v.elevation,v.target.copy())
        navigation_start = QPoint(*np.rint(v.project(a.world_point(source))).astype(int))
        for button in (Qt.MouseButton.LeftButton,Qt.MouseButton.RightButton):
            yaw,elevation = v.yaw,v.elevation
            QTest.mousePress(v,button,pos=navigation_start)
            QTest.mouseMove(v,navigation_start+QPoint(35,25),30)
            QTest.mouseRelease(v,button,pos=navigation_start+QPoint(35,25))
            assert (v.yaw,v.elevation) != (yaw,elevation)
            assert w._surface_mate['source'] is a and w._surface_mate['target'] is None
            assert w.history.index() == index
            np.testing.assert_array_equal(w.selected().matrix(),before)
        pan_before = v.target.copy()
        QTest.mousePress(v,Qt.MouseButton.MiddleButton,pos=navigation_start)
        QTest.mouseMove(v,navigation_start+QPoint(25,15),30)
        QTest.mouseRelease(v,Qt.MouseButton.MiddleButton,pos=navigation_start+QPoint(25,15))
        assert not np.allclose(v.target,pan_before)
        assert w._surface_mate['source'] is a and w._surface_mate['target'] is None
        v.yaw,v.elevation,v.target = saved_camera
        v.update()
        QTest.qWait(50)
        click(target,(10,-15,40))
        state = w._surface_mate
        assert state['pose'] is not None
        b = state['target']
        preview = replace(source,pose=state['pose'])
        np.testing.assert_allclose(a.world_point(preview),b.world_point(target),atol=1e-8)
        np.testing.assert_allclose(a.world_normal(preview),-b.world_normal(target),atol=1e-10)
        assert w.history.index() == index
        preview_pose = state['pose']
        QTest.mousePress(v,Qt.MouseButton.LeftButton,pos=navigation_start)
        QTest.mouseMove(v,navigation_start+QPoint(25,15),30)
        QTest.mouseRelease(v,Qt.MouseButton.LeftButton,pos=navigation_start+QPoint(25,15))
        assert w._surface_mate['pose'] == preview_pose
        assert w._surface_mate['source'] is a and w._surface_mate['target'] is b
        assert w.history.index() == index
        np.testing.assert_array_equal(w.selected().matrix(),before)
        ui.mate_offset.setValue(8)
        ui.mate_twist.setValue(45)
        ui.mate_flip.setChecked(True)
        preview = replace(source,pose=w._surface_mate['pose'])
        np.testing.assert_allclose(a.world_normal(preview),b.world_normal(target),atol=1e-10)
        ui.mate_flip.setChecked(False)
        preview = replace(source,pose=w._surface_mate['pose'])
        np.testing.assert_allclose(a.world_point(preview),b.world_point(target)+8*b.world_normal(target),atol=1e-8)
        assert w.history.index() == index
        QTest.qWait(100)
        w.grab().save('/tmp/scene-editor-surface-mate.png')
        ui.mate_apply.click()
        assert w._surface_mate is None and not v.pose_preview and not v.surface_pick_enabled
        assert w.history.index() == index+1
        np.testing.assert_allclose(w.selected().matrix(),preview.matrix(),atol=1e-9)
        np.testing.assert_array_equal(w.scene.objects[1].matrix(),target_before)
        w.history.undo()
        np.testing.assert_allclose(w.selected().matrix(),before,atol=1e-9)
        w.history.redo()
        np.testing.assert_allclose(w.selected().matrix(),preview.matrix(),atol=1e-9)
        w.history.undo()
        # Cancellation after a second real pick leaves history/model untouched.
        w.begin_surface_mate()
        click(w.scene.objects[0],(12,-8,50))
        click(w.scene.objects[1],(10,-15,40))
        assert v.pose_preview
        QTest.keyClick(v,Qt.Key.Key_Escape)
        assert w._surface_mate is None and not v.pose_preview
        assert v.surface_hover is None
        np.testing.assert_allclose(w.selected().matrix(),before,atol=1e-9)
        assert w.history.index() == index
        w.begin_surface_mate()
        click(w.scene.objects[1],(10,-15,40))
        assert w._surface_mate['source'] is None,'Locked object was accepted as moving source'
        w._select(target.id)
        assert w._surface_mate is None,'List selection did not cancel the active mate'
        # Choosing Move must exit mating even if Move was already checked.
        w._select(source.id)
        v.set_camera_view('Perspective')
        w.mode.setCurrentIndex(1)
        w.axis.setCurrentText('Screen')
        w.begin_surface_mate()
        click(w.scene.objects[0],(12,-8,50))
        assert w._surface_mate['source'] is not None
        assert w.surface_mate_action.isChecked() and not any(button.isChecked() for button in ui.tool_buttons)
        ui.tool_buttons[1].click()
        assert w._surface_mate is None and not v.surface_pick_enabled
        assert not w.surface_mate_action.isChecked() and ui.tool_buttons[1].isChecked()
        assert v._surface_press is None and not v.pose_preview
        obj = w.selected()
        movement_before = obj.matrix().copy()
        move_point = QPoint(*np.rint(v.project(obj.world_bounds().mean(axis=0))).astype(int))
        movement_index = w.history.index()
        QTest.mousePress(v,Qt.MouseButton.LeftButton,pos=move_point)
        previous_position = w.selected().world_origin().copy()
        for delta in (QPoint(20,10),QPoint(45,25),QPoint(70,40),QPoint(95,55)):
            QTest.mouseMove(v,move_point+delta,30)
            assert v._drag is not None,'Drag was cleared before mouse release'
            current_position = w.selected().world_origin().copy()
            assert not np.allclose(current_position,previous_position),'Object stopped following the held mouse'
            assert w.history.index() == movement_index+1,'One held drag must remain one undo command'
            previous_position = current_position
        QTest.mouseRelease(v,Qt.MouseButton.LeftButton,pos=move_point+QPoint(95,55))
        assert not np.allclose(w.selected().matrix(),movement_before),'Object did not move after exiting mate mode'
        assert w.history.index() == movement_index+1
        w.history.undo()
        np.testing.assert_allclose(w.selected().matrix(),movement_before,atol=1e-9)
        w.begin_surface_mate()
        w.activateWindow()
        v.setFocus()
        QTest.qWait(50)
        QTest.keyClick(v,Qt.Key.Key_G)
        QTest.qWait(20)
        assert w._surface_mate is None and v.mode == 'move'
        w._live = True
        w.begin_surface_mate()
        assert w._surface_mate is None
        w._live = False
        assert not v._error,v._error
        print('Surface mate GUI checks passed: GPU face picks, preview, offset/flip/twist, apply, one-step undo/redo, cancel and lock/live guards')
    finally:
        w._live = False
        w.history.setClean()
        w.close()
        app.processEvents()


if __name__ == '__main__':
    main()
