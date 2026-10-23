"""Offline GUI import regression for cached URDFs and ROS package folders."""
from pathlib import Path
import sys
import tempfile
import time
from unittest.mock import patch

import numpy as np
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QFileDialog

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.geometry import make_box, export_stl
from scene_editor.window import EditorWindow
from scene_editor.model import Scene,SceneObject
from scene_editor.ros_connection import RobotDescriptionUnavailable,RosConnection,RosOptions


def main():
    fmt = QSurfaceFormat()
    fmt.setVersion(3,3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)
    app = QApplication([])
    window = EditorWindow()
    errors = []
    window._error = errors.append
    window.show()
    settings = QSettings('Standalone Scene Editor','Scene Editor')
    previous = settings.value('urdf/mesh_root')

    def wait():
        deadline = time.monotonic()+5
        while window._jobs and time.monotonic() < deadline:
            QTest.qWait(20)
        assert not window._jobs,'URDF worker did not finish'

    try:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workspace = root/'workspace'
            mesh = workspace/'install'/'description'/'share'/'description'/'meshes'/'part.stl'
            mesh.parent.mkdir(parents=True)
            export_stl(make_box((.1,.2,.3)),np.eye(4),mesh)
            cached = root/'resolved.urdf'
            cached.write_text('<robot name="test"><link name="base"><visual><geometry>'
                              '<mesh filename="package://description/meshes/part.stl"/>'
                              '</geometry></visual></link></robot>')
            with patch.object(QFileDialog,'getOpenFileName',return_value=(str(cached),'')), \
                 patch.object(QFileDialog,'getExistingDirectory',return_value=str(workspace)):
                window.import_urdf()
            wait()
            assert not errors,errors
            assert len(window.scene.objects) == 1
            assert window.scene.objects[0].mesh.source == mesh
            # Cancel the folder picker: remembered roots still resolve packages.
            with patch.object(QFileDialog,'getOpenFileName',return_value=(str(cached),'')), \
                 patch.object(QFileDialog,'getExistingDirectory',return_value=''):
                window.import_urdf()
            wait()
            assert not errors and len(window.scene.objects) == 2
            before = [obj.id for obj in window.scene.objects]
            cached.write_text('<robot name="test"><link name="base"><visual><geometry>'
                              '<mesh filename="package://unavailable/meshes/missing.stl"/>'
                              '</geometry></visual></link></robot>')
            with patch.object(QFileDialog,'getOpenFileName',return_value=(str(cached),'')), \
                 patch.object(QFileDialog,'getExistingDirectory',return_value=''):
                window.import_urdf()
            wait()
            assert len(errors) == 1 and 'Cannot resolve package://unavailable/' in errors[0],errors
            assert [obj.id for obj in window.scene.objects] == before
            assert window.urdf_action.isEnabled()
            local_ids = [obj.id for obj in window.scene.objects]
            def robot():
                return Scene([SceneObject('Robot visual',make_box((20,30,40)),id='robot/resolved/0')])
            # The resolved action loads directly; neither picker may open.
            with patch('scene_editor.window.resolved_robot_snapshot',side_effect=lambda options, **kwargs:robot()) as snapshot, \
                 patch.object(QFileDialog,'getOpenFileName',side_effect=AssertionError('Unexpected file picker')):
                window.resolved_urdf_action.trigger()
                wait()
                assert len(window.scene.objects) == 3
                window.resolved_urdf_action.trigger()
                wait()
                assert len(window.scene.objects) == 3,'Automatic reload duplicated the robot'
                assert snapshot.call_args.kwargs['package_root'] == str(workspace)
            assert [obj.id for obj in window.scene.objects if not obj.id.startswith('robot/resolved/')] == local_ids
            window.history.undo()
            assert len(window.scene.objects) == 3
            window.history.undo()
            assert [obj.id for obj in window.scene.objects] == local_ids
            # Missing meshes offer a package picker and retry the automatic load.
            with patch('scene_editor.window.resolved_robot_snapshot',
                       side_effect=[FileNotFoundError('Cannot resolve package://description/meshes/part.stl'),robot()]) as snapshot, \
                 patch.object(QFileDialog,'getExistingDirectory',return_value=str(workspace)) as folder, \
                 patch.object(QFileDialog,'getOpenFileName',side_effect=AssertionError('Unexpected URDF picker')):
                window.resolved_urdf_action.trigger()
                wait()
                assert len(window.scene.objects) == 3
                folder.assert_called_once()
                assert snapshot.call_count == 2
                assert snapshot.call_args.kwargs['package_root'] == str(workspace)
            window.history.undo()
            assert [obj.id for obj in window.scene.objects] == local_ids
            with patch('scene_editor.window.resolved_robot_snapshot',side_effect=FileNotFoundError('Missing mesh')), \
                 patch.object(QFileDialog,'getExistingDirectory',return_value=''):
                window.resolved_urdf_action.trigger()
                wait()
            assert [obj.id for obj in window.scene.objects] == local_ids
            # Missing ROS opens the manual picker with the reason in its title.
            with patch('scene_editor.window.resolved_robot_snapshot',side_effect=RobotDescriptionUnavailable('No publisher')), \
                 patch.object(QFileDialog,'getOpenFileName',return_value=('','')) as picker:
                window.resolved_urdf_action.trigger()
                wait()
                picker.assert_called_once()
                assert 'ROS 2 unavailable' in picker.call_args.args[1]
                assert 'manually' in picker.call_args.args[1]
            assert [obj.id for obj in window.scene.objects] == local_ids
            assert window.resolved_urdf_action.isEnabled()
            # Live URDF collision display remains separate from ROS authoring.
            visual = SceneObject('base / visual 1',make_box((20,30,40)),id='robot/base/visual/0')
            collision = SceneObject('base / collision 1',make_box((10,20,30)),id='robot/base/collision/0')
            with patch.object(RosConnection,'start'),patch.object(RosConnection,'stop'):
                window.begin_ros(RosOptions())
                with patch.object(window._ros,'take_latest',return_value=Scene([visual,collision])):
                    window._poll_ros()
                    assert visual.visible and not collision.visible
                    window.robot_collisions_action.setChecked(True)
                    window.robot_visuals_action.setChecked(False)
                    assert collision.visible and not visual.visible
                    window._poll_ros()
                    assert collision.visible and not visual.visible,'Next live frame reset display choice'
                window._select(collision.id)
                assert 'URDF <collision>' in window._workspace.collision_info.text()
                assert not window.add_collision_action.isEnabled()
                assert not window.update_collision_action.isEnabled()
                assert not window.remove_collision_action.isEnabled()
                window._workspace.filters['Collision'].click()
                assert window.objects.item(0).isHidden()
                assert not window.objects.item(1).isHidden()
                window._workspace.filters['Robot'].click()
                assert not window.objects.item(0).isHidden() and not window.objects.item(1).isHidden()
                preview = SceneObject('Plan segment 2: approach [failed]',make_box((10,10,100)),id='preview/test/1')
                summary = 'Plan test · planning_failed\nFailure at segment 2: IK failed\nExact failure location unavailable.'
                window._ros_status_changed(dict(type='status',robot=True,planning=True,objects=3,preview=summary))
                assert 'IK failed' in window.preview_status.text()
                assert 'segment 2' in window._ros_details
                with patch.object(window._ros,'take_latest',return_value=Scene([visual,collision,preview])):
                    window._poll_ros()
                    assert preview.visible
                    window.planned_path_action.setChecked(False)
                    assert not preview.visible
                    window._poll_ros()
                    assert not preview.visible
                    window.planned_path_action.setChecked(True)
                window._select(preview.id)
                assert 'Planned-motion visualization only' in window._workspace.collision_info.text()
                assert not window.add_collision_action.isEnabled()
                window._ros_stopped('')
                assert window.scene.objects[1].visible
            print('URDF GUI checks passed: workspace lookup, remembered folder, async import and failed-import recovery')
    finally:
        if previous is None:
            settings.remove('urdf/mesh_root')
        else:
            settings.setValue('urdf/mesh_root',previous)
        window.history.setClean()
        window.close()
        app.processEvents()


if __name__ == '__main__':
    main()
