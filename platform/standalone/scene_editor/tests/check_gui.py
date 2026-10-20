"""Run explicitly under a desktop or xvfb-run; exercises real OpenGL rendering."""
from pathlib import Path
import sys
import tempfile
import threading
import time

import numpy as np
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scene_editor.window import EditorWindow, demo_scene
from scene_editor.model import load_scene
from scene_editor.model import Scene, SceneObject
from scene_editor.geometry import read_stl
from scene_editor.ros_connection import RosOptions
from scene_editor.collision import make_draft, primitive_spec
from scene_editor.model import Pose


def main():
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)
    app = QApplication([])
    window = EditorWindow()
    errors = []
    window._error = errors.append
    window.show()
    window._replace_scene(demo_scene())
    QTest.qWait(700)
    viewport = window.viewport
    assert viewport.isValid(), 'No OpenGL context'
    assert not viewport._error, viewport._error
    assert len(viewport._buffers) == 3, 'Mesh buffers were not uploaded'
    tool = window.scene.objects[1]
    window._select(tool.id)
    window.pose_fields['translation'][0].setValue(80)
    assert window.selected().pose.translation[0] == 80
    window.history.undo()
    assert window.selected().pose.translation[0] == 0
    window.history.redo()
    assert window.selected().pose.translation[0] == 80
    before = window.selected().matrix()
    window._pivot_center()
    np.testing.assert_allclose(window.selected().matrix(), before)
    window.pose_fields['rotation'][1].setValue(35)
    assert window.selected().pose.rotation[1] == 35
    QTest.qWait(100)
    # Verify object picking against projected geometry in the real framebuffer.
    matrix, *_ = viewport.camera()
    obj = window.selected()
    center = obj.world_bounds().mean(axis=0)
    projected = matrix @ np.r_[center, 1]
    ndc = projected[:3] / projected[3]
    point = QPoint(round((ndc[0]+1)*viewport.width()/2), round((1-ndc[1])*viewport.height()/2))
    assert viewport._pick(point) == tool.id, 'Framebuffer object picking failed'
    window.mode.setCurrentIndex(1)
    window.axis.setCurrentText('X')
    start = window.selected().pose
    undo_index = window.history.index()
    QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=point)
    QTest.mouseMove(viewport, point+QPoint(25, 0), 30)
    QTest.mouseMove(viewport, point+QPoint(50, 0), 30)
    QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=point+QPoint(50, 0))
    assert window.selected().pose.translation[0] != start.translation[0], 'Mouse translation did not change pose'
    assert window.history.index() == undo_index+1, 'A drag must be a single undo step'
    window.history.undo()
    assert window.selected().pose == start
    window.mode.setCurrentIndex(2)
    window.axis.setCurrentText('Y')
    QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=point)
    QTest.mouseMove(viewport, point+QPoint(40, 0), 30)
    QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=point+QPoint(40, 0))
    assert window.selected().pose.rotation[1] == start.rotation[1]+16
    window.history.undo()
    assert window.selected().pose == start
    # Duplicate shares immutable geometry; deletion/undo retains object identity.
    window.duplicate()
    duplicate = window.selected()
    assert duplicate.mesh is window.scene.objects[1].mesh
    window.delete()
    window.history.undo()
    assert window.selected().id == duplicate.id
    window.history.undo()
    window._select(tool.id)
    with tempfile.TemporaryDirectory() as directory:
        window.project_path = Path(directory) / 'gui.scene.json'
        assert window.save()
        loaded = load_scene(window.project_path)
        np.testing.assert_allclose(loaded.objects[1].matrix(), window.scene.objects[1].matrix())
        window.open_path(window.project_path)
        deadline = time.monotonic()+10
        while window._jobs and time.monotonic() < deadline:
            QTest.qWait(20)
        assert not window._jobs, 'Scene load worker did not finish'
        assert len(window.scene.objects) == 3
        assert not errors, errors
        retained = window.scene
        window.open_path(Path(directory) / 'missing.scene.json')
        deadline = time.monotonic()+10
        while window._jobs and time.monotonic() < deadline:
            QTest.qWait(20)
        assert errors and window.scene is retained, 'Failed loads must retain the current scene'
        assert window.centralWidget().isEnabled(), 'Failed loads must unlock the editor'
        errors.clear()
        window._select(window.scene.objects[1].id)
        QTest.qWait(200)
        output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('/tmp/scene-editor-preview.png')
        assert window.grab().save(str(output))
        assert not viewport._error, viewport._error
        print(f'GUI checks passed; OpenGL {viewport.context().format().majorVersion()}.{viewport.context().format().minorVersion()}; screenshot: {output}')
        if len(sys.argv) > 2:
            path = Path(sys.argv[2])
            start_time = time.monotonic()
            mesh = read_stl(path)
            window._replace_scene(Scene([SceneObject(path.stem, mesh)]))
            window._select(window.scene.objects[0].id)
            QTest.qWait(400)
            assert id(mesh) in viewport._buffers, 'Real mesh was not uploaded'
            buffer_before = viewport._buffers[id(mesh)][1:3]
            window.pose_fields['rotation'][2].setValue(45)
            window.pose_fields['translation'][0].setValue(100)
            QTest.qWait(150)
            assert viewport._buffers[id(mesh)][1:3] == buffer_before, 'Transform rebuilt geometry'
            assert not viewport._error, viewport._error
            assert window.grab().save('/tmp/scene-editor-real-mesh.png')
            print(f'Real STL check passed: {len(mesh.vertices):,} triangles, {time.monotonic()-start_time:.2f}s load/render/edit; GPU buffers reused')
        # Direct size editing and drag/drop must work without selecting Move mode,
        # including when the collision reference frame is rotated and translated.
        def screen_point(obj):
            vp, *_ = viewport.camera()
            projected = vp @ np.r_[obj.world_bounds().mean(axis=0), 1]
            ndc = projected[:3]/projected[3]
            return np.array([(ndc[0]+1)*viewport.width()/2, (1-ndc[1])*viewport.height()/2])
        for kind, dimensions in [('box',(100,150,200)), ('cylinder',(40,180)), ('sphere',(60,))]:
            parent = Pose((200,300,400),(0,0,90)).matrix()
            draft = make_draft('drag_'+kind, 'fixture', 'base_link', primitive_spec(kind,dimensions), frame_to_editor=parent.tolist())
            window._replace_scene(Scene([draft], 'base_link'))
            window._select(draft.id)
            window.mode.setCurrentIndex(0)
            window.axis.setCurrentText('Z')  # Direct drag uses screen plane regardless.
            QTest.qWait(100)
            assert window.size_box.isVisible()
            original_mesh = window.selected().mesh
            original_pose = window.selected().pose
            for index, value in enumerate(dimensions):
                window._finish_edit()
                window.size_fields[index].setValue(value+10)
                assert window.selected().mesh is not original_mesh
                assert window.selected().pose == original_pose
                window.history.undo()
                assert window.selected().mesh is original_mesh
            before = screen_point(window.selected())
            point = QPoint(*[round(value) for value in before])
            history_index = window.history.index()
            camera_yaw = viewport.yaw
            QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=point)
            QTest.mouseMove(viewport, point+QPoint(20,10), 20)
            QTest.mouseMove(viewport, point+QPoint(40,20), 20)
            QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=point+QPoint(40,20))
            assert window.selected().pose != original_pose, f'{kind} was not dragged'
            assert viewport.yaw == camera_yaw, 'Dragging a primitive orbited the camera'
            assert window.history.index() == history_index+1, 'Drag created multiple undo steps'
            np.testing.assert_allclose(screen_point(window.selected())-before, (40,20), atol=.05)
            window.history.undo()
            assert window.selected().pose == original_pose
            QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=point)
            QTest.mouseMove(viewport, point+QPoint(1,1), 20)
            QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=point+QPoint(1,1))
            assert window.selected().pose == original_pose, 'Click jitter moved the object'
            window._live = True
            window._busy_actions()
            window._refresh()
            assert window.size_fields[0].isReadOnly()
            QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=point)
            QTest.mouseMove(viewport, point+QPoint(40,20), 20)
            QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=point+QPoint(40,20))
            assert window.selected().pose == original_pose, 'Live view allowed dragging an object'
            window._live = False
            window._busy_actions()
            window._refresh()
        QTest.qWait(100)
        assert window.grab().save('/tmp/scene-editor-size-drag.png')
        print('Direct Box/Cylinder/Sphere size editing and screen-plane drag checks passed, including rotated frames, undo, click jitter and live-view locks')
        # Locks apply to all edit paths; selecting a locked snap target is allowed.
        source = make_draft('source', 'fixture', 'base_link', primitive_spec('box',(60,80,100)),
                            Pose((10,20,30),(10,20,30),(5,6,7)), Pose((100,0,0),(0,0,90)).matrix().tolist())
        target = make_draft('target', 'base_link', 'base_link', primitive_spec('box',(100,120,140)), Pose((-180,0,0)))
        target.locked = True
        window._replace_scene(Scene([source,target], 'base_link'))
        window._select(source.id)
        window.mode.setCurrentIndex(0)
        window.toggle_lock()
        assert window.selected().locked
        assert window.pose_fields['translation'][0].isReadOnly()
        assert window.size_fields[0].isReadOnly()
        assert not window.delete_button.isEnabled() and not window.snap_button.isEnabled()
        before = window.selected().matrix().copy()
        before_mesh = window.selected().mesh
        window._change('Blocked transform', pose=Pose((999,0,0)))
        window._resize_primitive(999)
        window.delete()
        assert len(window.scene.objects) == 2
        assert window.selected().mesh is before_mesh
        np.testing.assert_array_equal(window.selected().matrix(), before)
        for mode in (0,1,2):
            window.mode.setCurrentIndex(mode)
            point = QPoint(*[round(value) for value in screen_point(window.selected())])
            QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=point)
            QTest.mouseMove(viewport, point+QPoint(30,15), 20)
            QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=point+QPoint(30,15))
            np.testing.assert_array_equal(window.scene.objects[0].matrix(), before)
        window._select(source.id)
        window.history.undo()
        assert not window.selected().locked
        window.history.redo()
        assert window.selected().locked
        window.toggle_lock()
        assert not window.selected().locked
        window.mode.setCurrentIndex(0)
        source_pose = window.selected().pose
        target_before = window.scene.objects[1].matrix().copy()
        window.begin_snap()
        assert viewport.selection_only
        # Target selection from the object list must keep the source selected.
        window.objects.setCurrentRow(1)
        assert window.selected().id == source.id
        assert window._snap_source is None
        np.testing.assert_allclose(window.selected().world_origin(), window.scene.objects[1].world_origin(), atol=1e-10)
        assert window.selected().pose.rotation == source_pose.rotation
        np.testing.assert_array_equal(window.scene.objects[1].matrix(), target_before)
        window.history.undo()
        assert window.selected().pose == source_pose
        window.begin_snap()
        QTest.keyClick(viewport, Qt.Key.Key_Escape)
        assert window._snap_source is None and not viewport.selection_only
        # A target click in the viewport is selection only: no subsequent drag.
        window.frame_scene()
        QTest.qWait(100)
        window.begin_snap()
        point = QPoint(*[round(value) for value in screen_point(window.scene.objects[1])])
        QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=point)
        QTest.mouseMove(viewport, point+QPoint(40,20), 20)
        QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=point+QPoint(40,20))
        assert window.selected().id == source.id
        np.testing.assert_allclose(window.selected().world_origin(), window.scene.objects[1].world_origin(), atol=1e-10)
        np.testing.assert_array_equal(window.scene.objects[1].matrix(), target_before)
        with tempfile.TemporaryDirectory() as directory:
            from scene_editor.model import save_scene
            project = Path(directory)/'locked.scene.json'
            save_scene(window.scene, project)
            assert load_scene(project).objects[1].locked
        assert window.grab().save('/tmp/scene-editor-lock-snap.png')
        print('Lock/unlock and origin snap checks passed: blocked edits/drags/deletion, undo/redo, list and viewport targets, Escape, rotation preservation and lock persistence')
        # A first gesture over another object only selects it in every mode.
        first = SceneObject('First', draft.mesh, Pose((180,0,50)))
        second = SceneObject('Second', draft.mesh, Pose((-180,0,50)))
        window._replace_scene(Scene([first,second]))
        for mode in (0,1,2):
            window._select(first.id)
            window.mode.setCurrentIndex(mode)
            window.axis.setCurrentText('Screen')
            QTest.qWait(80)
            point = QPoint(*[round(value) for value in screen_point(window.scene.objects[1])])
            original = [obj.pose for obj in window.scene.objects]
            index = window.history.index()
            yaw = viewport.yaw
            QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=point)
            QTest.mouseMove(viewport, point+QPoint(30,15), 20)
            QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=point+QPoint(30,15))
            assert window.selected().id == second.id
            assert [obj.pose for obj in window.scene.objects] == original
            assert window.history.index() == index
            assert viewport.yaw == yaw, 'Selection gesture orbited the camera'
            # The next gesture transforms only the already-selected object.
            QTest.mousePress(viewport, Qt.MouseButton.LeftButton, pos=point)
            QTest.mouseMove(viewport, point+QPoint(20,10), 20)
            QTest.mouseMove(viewport, point+QPoint(40,20), 20)
            QTest.mouseRelease(viewport, Qt.MouseButton.LeftButton, pos=point+QPoint(40,20))
            changed = window.selected().pose
            assert changed != original[1]
            assert window.scene.objects[0].pose == original[0]
            assert window.history.index() == index+1
            assert window.undo_button.isEnabled()
            window.undo_button.click()
            assert window.selected().pose == original[1]
            assert window.redo_button.isEnabled()
            window.redo_button.click()
            assert window.selected().pose == changed
            window.undo_button.click()
        window._select(second.id)
        before_reset = window.selected().pose
        before_mesh = window.selected().mesh
        assert window.reset_button.isEnabled()
        window.reset_button.click()
        assert window.selected().pose == Pose()
        assert window.selected().mesh is before_mesh
        assert not window.reset_button.isEnabled()
        window.undo_button.click()
        assert window.selected().pose == before_reset
        window.redo_button.click()
        assert window.selected().pose == Pose()
        window.toggle_lock()
        assert not window.reset_button.isEnabled()
        assert window.grab().save('/tmp/scene-editor-selected-drag.png')
        print('Selected-only drag, visible Undo/Redo and undoable Reset checks passed in View, Move and Rotate modes')
        window._replace_scene(demo_scene())
        window._select(window.scene.objects[0].id)
        selected_id = window.selected().id
        from scene_editor.object_list import LOCKED_ROLE
        row = window.objects.model().index(1,0)
        point = window.objects._object_delegate.lock_rect(window.objects.visualRect(row)).center()
        QTest.mouseClick(window.objects.viewport(), Qt.MouseButton.LeftButton, pos=point)
        assert window.scene.objects[1].locked
        assert window.selected().id == selected_id, 'Padlock click changed the current selection'
        assert window.objects.item(1).data(LOCKED_ROLE)
        assert window.scene.objects[1].visible, 'Padlock changed visibility'
        window.history.undo()
        assert not window.scene.objects[1].locked
        window.history.redo()
        assert window.scene.objects[1].locked
        QTest.mouseClick(window.objects.viewport(), Qt.MouseButton.LeftButton, pos=point)
        assert not window.scene.objects[1].locked
        # Pressing a padlock and releasing elsewhere must not toggle it.
        QTest.mousePress(window.objects.viewport(), Qt.MouseButton.LeftButton, pos=point)
        QTest.mouseRelease(window.objects.viewport(), Qt.MouseButton.LeftButton, pos=QPoint(40,point.y()))
        assert not window.scene.objects[1].locked
        window._live = True
        window._busy_actions()
        window._refresh()
        QTest.mouseClick(window.objects.viewport(), Qt.MouseButton.LeftButton, pos=point)
        assert not window.scene.objects[1].locked, 'Live view allowed changing lock state'
        window._live = False
        window._busy_actions()
        window._refresh()
        QTest.mouseClick(window.objects.viewport(), Qt.MouseButton.LeftButton, pos=point)
        QTest.qWait(100)
        assert window.grab().save('/tmp/scene-editor-row-padlocks.png')
        print('Per-row padlock checks passed: lock/unlock nonselected objects, preserve selection/visibility, undo/redo, release outside and live-view lockout')
        from scene_editor.styles import PALETTES
        from scene_editor.collision_dialog import CollisionDialog
        from PyQt6.QtGui import QColor
        original_theme = window._theme_name
        index = window.history.index()
        for theme in ('light','dark'):
            window.set_theme(theme, persist=False)
            QTest.qWait(100)
            assert window.history.index() == index, 'Changing appearance edited the scene'
            assert window.viewport._view_colors['background'] == PALETTES[theme]['background']
            assert window.inspector.width() <= window.inspector.parentWidget().width(), 'Inspector clipped horizontally'
            assert not viewport._error, viewport._error
            pixel = viewport.grabFramebuffer().pixelColor(2,2)
            expected = QColor(PALETTES[theme]['background'])
            assert max(abs(a-b) for a,b in zip(pixel.getRgb()[:3], expected.getRgb()[:3])) <= 2
            assert window.grab().save(f'/tmp/scene-editor-platform-{theme}.png')
            dialog = CollisionDialog('base_link', parent=window)
            dialog.show()
            QTest.qWait(100)
            assert dialog.grab().save(f'/tmp/scene-editor-platform-dialog-{theme}.png')
            dialog.close()
        window.set_theme(original_theme, persist=False)
        print('Platform-style light/dark rendering and dialog checks passed; appearance leaves scene history unchanged')
        window.history.setClean()
        retained = window.scene
        window.begin_ros(RosOptions(python='/missing-scene-editor-test-python'))
        deadline = time.monotonic()+5
        while window._ros is not None and time.monotonic() < deadline:
            QTest.qWait(20)
        assert window._ros is None and not window._live, 'Failed ROS startup did not unlock the editor'
        assert window.scene is retained, 'Failed ROS startup replaced the local scene'
        assert 'missing-scene-editor-test-python' in window._ros_details
        assert 'rclpy' not in sys.modules
        print('Offline operation and failed ROS startup recovery passed')
        window.history.setClean()
        release = threading.Event()
        window._submit('Testing safe shutdown', lambda: release.wait(5), window._export_done)
        window.close()
        assert window._closing and window.isVisible(), 'Closing must wait for file operations'
        release.set()
        deadline = time.monotonic()+10
        while window.isVisible() and time.monotonic() < deadline:
            QTest.qWait(20)
        assert not window.isVisible(), 'Editor did not close after workers finished'
        assert not window._jobs
        print('Failed-load recovery and worker shutdown checks passed')


if __name__ == '__main__':
    main()
