"""Real GUI checks for multi-selection and local group translation; no ROS."""
from pathlib import Path
import sys

import numpy as np
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.window import EditorWindow
from scene_editor.model import Pose,Scene,SceneObject
from scene_editor.geometry import Mesh,make_box
from scene_editor.collision import make_draft,primitive_spec


def main():
    fmt = QSurfaceFormat()
    fmt.setVersion(3,3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)
    app = QApplication([])
    window = EditorWindow()
    window.show()
    viewport = window.viewport
    first = make_draft('first','fixture_a','base_link',primitive_spec('box',(90,100,120)),
                       Pose(rotation=(10,20,30),pivot=(5,6,7)), Pose((-180,-80,60),(0,0,90)).matrix().tolist())
    second = make_draft('second','fixture_b','base_link',primitive_spec('cylinder',(45,120)),
                        Pose(),Pose((180,-80,60),(0,30,0)).matrix().tolist())
    third = SceneObject('STL-like mesh',Mesh(make_box((90,100,120)).vertices.copy()),Pose((0,180,60)))
    window._replace_scene(Scene([first,second,third],'base_link'))

    def point(obj):
        vp,*_ = viewport.camera()
        projected = vp @ np.r_[obj.world_bounds().mean(axis=0),1]
        ndc = projected[:3]/projected[3]
        return QPoint(round((ndc[0]+1)*viewport.width()/2),round((1-ndc[1])*viewport.height()/2))

    def list_click(row,modifiers=Qt.KeyboardModifier.NoModifier):
        rectangle = window.objects.visualItemRect(window.objects.item(row))
        QTest.mouseClick(window.objects.viewport(),Qt.MouseButton.LeftButton,modifiers,pos=QPoint(80,rectangle.center().y()))

    def drag(obj,delta=QPoint(40,20)):
        position = point(obj)
        QTest.mousePress(viewport,Qt.MouseButton.LeftButton,pos=position)
        QTest.mouseMove(viewport,position+delta/2,20)
        QTest.mouseMove(viewport,position+delta,20)
        QTest.mouseRelease(viewport,Qt.MouseButton.LeftButton,pos=position+delta)

    try:
        QTest.qWait(200)
        list_click(0)
        list_click(1,Qt.KeyboardModifier.ControlModifier)
        assert viewport.selection_ids() == {first.id,second.id}
        assert len(window.objects.selectedItems()) == 2
        list_click(2,Qt.KeyboardModifier.ShiftModifier)
        assert viewport.selection_ids() == {first.id,second.id,third.id}
        list_click(2,Qt.KeyboardModifier.ControlModifier)
        assert viewport.selection_ids() == {first.id,second.id}
        before = {obj.id:obj.matrix().copy() for obj in window.scene.objects}
        index = window.history.index()
        window.mode.setCurrentIndex(0)
        drag(window.scene.objects[1])  # Drag non-primary member without collapsing selection.
        assert viewport.selection_ids() == {first.id,second.id}
        assert window.history.index() == index+1
        a,b,c = window.scene.objects
        delta = a.world_origin()-before[a.id][:3,3]
        assert np.linalg.norm(delta) > 1
        np.testing.assert_allclose(b.world_origin()-before[b.id][:3,3],delta,atol=1e-10)
        np.testing.assert_allclose(a.world_origin()-b.world_origin(),before[a.id][:3,3]-before[b.id][:3,3],atol=1e-10)
        for obj in (a,b):
            np.testing.assert_array_equal(obj.matrix()[:3,:3],before[obj.id][:3,:3])
        np.testing.assert_array_equal(c.matrix(),before[c.id])
        moved = {obj.id:obj.matrix().copy() for obj in (a,b)}
        window.undo_button.click()
        for obj in window.scene.objects:
            np.testing.assert_allclose(obj.matrix(),before[obj.id],atol=1e-10)
        assert viewport.selection_ids() == {first.id,second.id}
        window.redo_button.click()
        for obj in window.selected_objects():
            np.testing.assert_allclose(obj.matrix(),moved[obj.id],atol=1e-10)
        for control,value in zip(window.group_fields,(25,-40,10)):
            control.setValue(value)
        window.group_move_button.click()
        for obj in window.selected_objects():
            np.testing.assert_allclose(obj.world_origin()-moved[obj.id][:3,3],(25,-40,10),atol=1e-10)
        assert all(field.value() == 0 for field in window.group_fields)
        window.history.undo()
        # A world-axis constraint must apply equally in both reference frames.
        window.mode.setCurrentIndex(1)
        window.axis.setCurrentText('X')
        drag(window.scene.objects[0],QPoint(40,-20))
        delta = window.scene.objects[0].world_origin()-moved[first.id][:3,3]
        assert abs(delta[0]) > 1
        np.testing.assert_allclose(delta[1:],(0,0),atol=1e-10)
        np.testing.assert_allclose(window.scene.objects[1].world_origin()-moved[second.id][:3,3],delta,atol=1e-10)
        window.history.undo()
        # Any locked member blocks the whole move, never a partial group update.
        lock_rect = window.objects._object_delegate.lock_rect(window.objects.visualItemRect(window.objects.item(1)))
        QTest.mouseClick(window.objects.viewport(),Qt.MouseButton.LeftButton,pos=lock_rect.center())
        assert viewport.selection_ids() == {first.id,second.id}
        assert not window.group_move_button.isEnabled()
        matrices = [obj.matrix().copy() for obj in window.scene.objects]
        drag(window.scene.objects[0])
        for obj,matrix in zip(window.scene.objects,matrices):
            np.testing.assert_array_equal(obj.matrix(),matrix)
        QTest.mouseClick(window.objects.viewport(),Qt.MouseButton.LeftButton,pos=lock_rect.center())
        # Ctrl-click viewport adds/removes and never transforms the selection.
        window.frame_scene()
        QTest.qWait(100)
        QTest.mouseClick(viewport,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.ControlModifier,pos=point(window.scene.objects[2]))
        assert viewport.selection_ids() == {first.id,second.id,third.id}
        QTest.mouseClick(viewport,Qt.MouseButton.LeftButton,Qt.KeyboardModifier.ControlModifier,pos=point(window.scene.objects[1]))
        assert viewport.selection_ids() == {first.id,third.id}
        before = {obj.id:obj.matrix().copy() for obj in window.scene.objects}
        window.mode.setCurrentIndex(0)
        drag(window.scene.objects[2])  # Meshes participate in direct group drag.
        delta = window.scene.objects[2].world_origin()-before[third.id][:3,3]
        assert np.linalg.norm(delta) > 1
        np.testing.assert_allclose(window.scene.objects[0].world_origin()-before[first.id][:3,3],delta,atol=1e-10)
        np.testing.assert_array_equal(window.scene.objects[1].matrix(),before[second.id])
        assert not window.snap_button.isEnabled() and not window.reset_button.isEnabled()
        assert not window.update_collision_action.isEnabled()
        assert not window.mode.model().item(2).isEnabled()
        # Live-view group selection is inspect-only.
        window._live = True
        window._busy_actions()
        window._refresh()
        matrices = [obj.matrix().copy() for obj in window.scene.objects]
        drag(window.scene.objects[0])
        for obj,matrix in zip(window.scene.objects,matrices):
            np.testing.assert_array_equal(obj.matrix(),matrix)
        window._live = False
        window._busy_actions()
        window._refresh()
        QTest.qWait(100)
        assert not viewport._error,viewport._error
        assert window.grab().save('/tmp/scene-editor-group-move.png')
        print('Group checks passed: Ctrl/Shift list selection, Ctrl viewport selection, drag and numeric world offsets across frames, relative positions, mixed meshes, one-step undo/redo, lock/live guards and selection preservation')
    finally:
        window.history.setClean()
        window.close()
        app.processEvents()


if __name__ == '__main__':
    main()
