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
from scene_editor.ros_connection import RobotDescriptionUnavailable


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
            with patch('scene_editor.window.resolved_robot_snapshot',side_effect=lambda options:robot()), \
                 patch.object(QFileDialog,'getOpenFileName',side_effect=AssertionError('Unexpected file picker')):
                window.resolved_urdf_action.trigger()
                wait()
                assert len(window.scene.objects) == 3
                window.resolved_urdf_action.trigger()
                wait()
                assert len(window.scene.objects) == 3,'Automatic reload duplicated the robot'
            assert [obj.id for obj in window.scene.objects if not obj.id.startswith('robot/resolved/')] == local_ids
            window.history.undo()
            assert len(window.scene.objects) == 3
            window.history.undo()
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
