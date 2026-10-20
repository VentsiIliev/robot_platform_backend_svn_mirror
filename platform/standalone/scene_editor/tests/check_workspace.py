"""Real OpenGL workspace checks; no ROS connection or scene writes."""
from pathlib import Path
import sys
import tempfile
import numpy as np
from PyQt6.QtCore import QPoint, Qt
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QToolBar

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.window import EditorWindow, demo_scene
from scene_editor.geometry import make_box, export_stl, read_stl
from scene_editor.model import Pose, Scene, SceneObject, save_scene, load_scene


def main():
    fmt = QSurfaceFormat()
    fmt.setVersion(3,3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)
    app = QApplication([])
    w = EditorWindow()
    w.set_theme('light',persist=False)
    w.show()
    w._replace_scene(demo_scene())
    QTest.qWait(250)
    ui,v = w._workspace,w.viewport
    try:
        assert sum(bar.isVisible() for bar in w.findChildren(QToolBar)) == 1
        assert w.axis.isVisible()
        before = [obj.visible for obj in w.scene.objects]
        ui.search.setText('fixture')
        assert sum(not w.objects.item(i).isHidden() for i in range(w.objects.count())) == 1
        assert [obj.visible for obj in w.scene.objects] == before
        ui.search.clear()
        ui.filters['Robot'].click()
        assert all(w.objects.item(i).isHidden() for i in range(w.objects.count()))
        ui.filters['All'].click()
        assert ui.properties.count() == 4
        w._select(w.scene.objects[2].id)
        obj = w.selected()
        original_id = obj.id
        for identifier,expected in (
            ('robot/link_2/visual/0','Robot link visual geometry'),
            ('world/fixture/part/0','Planning-scene world collision object'),
            ('attached/tool/0','Attached collision object'),
        ):
            obj.id = identifier
            description = ui._collision_description(obj)
            assert description.startswith(expected)
            if identifier.startswith('world/'):
                assert 'Collision ID: fixture/part' in description
        obj.id = original_id
        assert ui._collision_description(None).startswith('Select an object')
        ui.origin_section.header.click()
        assert ui.origin_section.body.isVisible()
        ui.origin_section.header.click()
        w._select(w.scene.objects[2].id)
        ui.properties.setCurrentIndex(1)
        ui.opacity.setValue(65)
        assert abs(w.selected().color[3]-.65) < 1e-6
        ui.properties.setCurrentIndex(0)
        ui.grid_button.click()
        assert not v.show_grid
        ui.grid_button.click()
        ui.camera.setCurrentText('Front')
        assert v.projection_mode == 'orthographic' and v.yaw == -90
        QTest.qWait(50)
        polygon,view = v._view_cube._faces[0]
        QTest.mouseClick(v._view_cube,Qt.MouseButton.LeftButton,pos=polygon.boundingRect().center().toPoint())
        assert v.projection_mode == 'orthographic'
        ui.camera.setCurrentText('Perspective')
        ui.tool_buttons[1].click()
        assert v.mode == 'move'
        # A projected X handle constrains movement in world coordinates and
        # produces one undo command for the entire gesture.
        obj = w.selected()
        start_pose = obj.pose
        start_origin = obj.world_origin().copy()
        pivot = obj.world_pivot()
        length = max(np.linalg.norm(v.camera()[1]-pivot)*.075,.1)
        start = v.project(pivot)
        line = v.project(pivot+np.array([length,0,0]))-start
        point = QPoint(*np.rint(start+.8*line).astype(int))
        assert v._hit_translation_axis(point)[0] == 'X'
        delta = QPoint(*np.rint(.6*line).astype(int))
        index = w.history.index()
        QTest.mousePress(v,Qt.MouseButton.LeftButton,pos=point)
        QTest.mouseMove(v,point+delta,30)
        QTest.mouseRelease(v,Qt.MouseButton.LeftButton,pos=point+delta)
        assert w.history.index() == index+1
        moved = w.selected().world_origin()-start_origin
        assert abs(moved[0]) > 1
        np.testing.assert_allclose(moved[1:],0,atol=1e-8)
        w.history.undo()
        assert w.selected().pose == start_pose
        ui.gizmo_button.click()
        assert v._hit_translation_axis(point) is None
        QTest.qWait(50)
        assert v._origin_label.isVisible(), 'Origin must remain visible without transform handles'
        index = w.history.index()
        ui.origin_action.setChecked(False)
        QTest.qWait(50)
        assert not v._origin_label.isVisible() and not v.show_origin
        ui.origin_action.setChecked(True)
        QTest.qWait(50)
        assert v._origin_label.isVisible() and w.history.index() == index
        ui.gizmo_button.click()
        QTest.qWait(100)
        w.grab().save('/tmp/scene-editor-workspace-light.png')
        w.set_theme('dark',persist=False)
        QTest.qWait(100)
        w.grab().save('/tmp/scene-editor-workspace-dark.png')
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'fixture.stl'
            export_stl(make_box((2,3,4)),np.eye(4),source)
            source_bytes = source.read_bytes()
            mesh = read_stl(source)
            pose = Pose((10,20,30),(15,25,35),(1,2,3))
            imported = SceneObject('Imported STL',mesh,pose,unit_scale=(1000.,)*3)
            w._replace_scene(Scene([imported]))
            w._select(imported.id)
            assert ui.units_box.isVisible() and ui.units.currentText() == 'Meters'
            index = w.history.index()
            ui.units.setCurrentText('Millimeters')
            assert w.selected().unit_scale == (1.,)*3 and w.selected().pose == pose
            assert w.selected().mesh is mesh and source.read_bytes() == source_bytes
            assert w.history.index() == index+1
            np.testing.assert_allclose(np.ptp(w.selected().world_bounds(),axis=0),
                                       np.ptp(imported.world_bounds(),axis=0)/1000,rtol=1e-6)
            w.history.undo()
            assert w.selected().unit_scale == (1000.,)*3 and ui.units.currentText() == 'Meters'
            w.history.redo()
            assert ui.units.currentText() == 'Millimeters'
            QTest.qWait(50)
            assert v._origin_label.isVisible()
            origin = v.project(w.selected().world_origin())
            assert abs(v._origin_label.x()-(round(origin[0])+12)) <= 1
            assert not np.allclose(w.selected().world_origin(),w.selected().world_pivot())
            ui.units.setCurrentText('Centimeters')
            assert w.selected().unit_scale == (10.,)*3
            saved = Path(directory)/'scene.json'
            save_scene(w.scene,saved)
            restored = load_scene(saved).objects[0]
            assert restored.unit_scale == (10.,)*3 and restored.pose == pose
            # Picking previews a surface point without moving the object or
            # adding undo history. Escape discards it, confirmation commits once.
            before_matrix = w.selected().matrix().copy()
            index = w.history.index()
            ui.pick_mounting_button.click()
            assert v.origin_pick_id == w.selected().id
            QTest.qWait(100)
            QTest.mouseClick(v,Qt.MouseButton.LeftButton,pos=QPoint(2,v.height()-2))
            assert w._origin_edit and not w._origin_edit['picked']
            assert w.history.index() == index
            projected = v.project(w.selected().world_bounds().mean(axis=0))
            surface_point = QPoint(*np.rint(projected).astype(int))
            QTest.mouseClick(v,Qt.MouseButton.LeftButton,pos=surface_point)
            assert w._origin_edit and w._origin_edit['picked']
            assert v.origin_preview is not None and ui.set_origin_button.isEnabled()
            QTest.qWait(50)
            w.grab().save('/tmp/scene-editor-mounting-workflow.png')
            assert w.history.index() == index
            np.testing.assert_allclose(w.selected().matrix(),before_matrix)
            local = np.asarray(w._origin_edit['point'])/w.selected().unit_scale
            low,high = mesh.bounds
            assert np.min(np.abs(np.r_[local-low,local-high])) < .01
            QTest.keyClick(v,Qt.Key.Key_Escape)
            assert w._origin_edit is None and v.origin_preview is None and v.origin_pick_id is None
            assert w.history.index() == index
            ui.pick_mounting_button.click()
            QTest.mouseClick(v,Qt.MouseButton.LeftButton,pos=surface_point)
            picked_point = w._origin_edit['point']
            ui.set_origin_button.click()
            assert w._origin_edit is None and w.history.index() == index+1
            np.testing.assert_allclose(w.selected().origin_source,np.asarray(picked_point)/w.selected().unit_scale)
            np.testing.assert_allclose(w.selected().matrix(),before_matrix,atol=1e-10)
            w.history.undo()
            assert w.selected().origin_source == (0.,0.,0.)
            ui.mounting_section.header.setChecked(True)
            before_matrix = w.selected().matrix().copy()
            index = w.history.index()
            for field,value in zip(ui.mounting_fields,(4,5,6)):
                field.setValue(value)
            ui.set_origin_button.click()
            assert w.history.index() == index+1
            np.testing.assert_allclose(w.selected().origin_source,(.4,.5,.6))
            np.testing.assert_allclose(w.selected().matrix(),before_matrix,atol=1e-10)
            assert w.selected().pose.pivot == (4.,5.,6.)
            w.history.undo()
            assert w.selected().origin_source == (0.,0.,0.)
            w.history.redo()
            assert tuple(field.value() for field in ui.mounting_fields) == (4.,5.,6.)
            target = SceneObject('Flange',make_box((10,10,10)),Pose((200,300,400)))
            source_id = w.selected().id
            w.scene.objects.append(target)
            w._refresh()
            w.begin_mounting_origin_pick()
            w._select(target.id)
            assert w._origin_edit is None and v.origin_pick_id is None
            w._select(source_id)
            index = w.history.index()
            w.preview_mounting_origin((7,8,9))
            ui.origin_snap_button.click()
            assert w._snap_source == source_id and w._origin_edit is None
            w._select(target.id)
            assert w.history.index() == index+2
            assert w.selected().id == source_id
            np.testing.assert_allclose(w.selected().world_origin(),target.world_origin(),atol=1e-10)
            w.history.undo()
            assert w.selected().pose.pivot == (7.,8.,9.)
            w.history.undo()
            np.testing.assert_allclose(w.selected().origin_source,(.4,.5,.6))
            w.history.redo()
            w.history.redo()
            save_scene(w.scene,saved)
            restored = load_scene(saved).objects[0]
            np.testing.assert_allclose(restored.world_origin(),target.world_origin(),atol=1e-10)
            w.change_stl_units('Millimeters')
            np.testing.assert_allclose(w.selected().pose.pivot,(.7,.8,.9))
            w.change_stl_units('Centimeters')
            w.selected().locked = True
            w._refresh()
            assert not ui.units.isEnabled()
            w.change_stl_units('Meters')
            assert w.selected().unit_scale == (10.,)*3
            origin_before = w.selected().origin_source
            w.set_mounting_origin((100,200,300))
            assert w.selected().origin_source == origin_before
            w.selected().locked = False
            w._live = True
            w.change_stl_units('Meters')
            assert w.selected().unit_scale == (10.,)*3
            w._live = False
            w._refresh()
            assert not w.has_editable_stl_units(SceneObject('Primitive',make_box((1,2,3))))
            w.selected().id = 'robot/link/visual/0'
            assert not w.has_editable_stl_units(w.scene.objects[0])
            print('STL units checks passed: scale correction, pose/source preservation, undo/redo, persistence and edit guards')
        print('Workspace checks passed: filters, properties, opacity, cameras, cube, handles and undo')
    finally:
        w.history.setClean()
        w.close()
        app.processEvents()


if __name__ == '__main__':
    main()
