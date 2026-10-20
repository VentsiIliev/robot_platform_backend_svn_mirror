"""GUI + real ROS messages/services on an isolated domain with a fake MoveIt.

Does not use the running robot's domain or scene services.
"""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import uuid

import numpy as np
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scene_editor.collision import make_draft, primitive_spec
from scene_editor.collision_dialog import CollisionDialog
from scene_editor.model import Pose, load_scene
from scene_editor.ros_connection import RosOptions, collision_operation
from scene_editor.window import EditorWindow


def wait_until(predicate, seconds=15):
    deadline = time.monotonic()+seconds
    while not predicate() and time.monotonic() < deadline:
        QTest.qWait(25)
    assert predicate(), 'Timed out waiting for a test operation'


def main():
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)
    app = QApplication([])
    with tempfile.TemporaryDirectory(prefix='collision-editor-test-') as directory:
        root = Path(directory)
        prefix = '/scene_editor_test_'+uuid.uuid4().hex[:10]
        environment = dict(os.environ, ROS_DOMAIN_ID='173')
        fixture = Path(__file__).with_name('ros_collision_fixture.py')
        journal = root/'requests.jsonl'
        server = subprocess.Popen(['/usr/bin/python3', '-u', '-B', str(fixture), prefix, str(journal)],
                                  env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        window = None
        try:
            # Readiness is handled by the ROS client's bounded service wait.
            options = RosOptions(domain=173, scene_service=prefix+'/get', apply_service=prefix+'/apply')
            result = collision_operation(options, dict(operation='resolve', frame='fixture', editor_frame='base_link'))
            np.testing.assert_allclose(np.asarray(result['frame_to_editor'])[:3,3], (1000,2000,0))
            window = EditorWindow()
            window._ros_options = options
            errors = []
            window._error = errors.append
            window.show()
            assert not window.add_collision_action.isEnabled()
            try:
                collision_operation(options, dict(operation='remove', object_id='attached_tool', frame='base_link'))
                raise AssertionError('Attached collision objects must not be modified')
            except RuntimeError as exc:
                assert 'attached to the robot' in str(exc)
            dialog = CollisionDialog('base_link', parent=window)
            dialog.kind.setCurrentText('cylinder')
            dialog.dimensions[0].setValue(12.5)
            dialog.dimensions[1].setValue(200)
            assert dialog.values()[2] == primitive_spec('cylinder',(12.5,200))
            dialog.close()
            def create_box():
                dialog = QApplication.activeModalWidget()
                assert isinstance(dialog, CollisionDialog)
                dialog.identifier.setText('test_box')
                dialog.frame.setText('fixture')
                for control, value in zip(dialog.dimensions, (100,200,300)):
                    control.setValue(value)
                for control, value in zip(dialog.pose_fields['translation'], (50,60,70)):
                    control.setValue(value)
                dialog.pose_fields['rotation'][2].setValue(90)
                dialog.accept()
            QTimer.singleShot(50, create_box)
            window.new_collision()
            wait_until(lambda: not window._jobs)
            assert not errors, errors
            draft = window.selected()
            assert draft is not None and draft.collision['object_id'] == 'test_box'
            np.testing.assert_allclose(draft.parent_matrix(), result['frame_to_editor'])
            QTest.qWait(300)
            assert window.add_collision_action.isEnabled()
            assert not journal.exists(), 'Creating/editing local drafts must not publish'
            window.add_collision_ros()
            assert not window.add_collision_action.isEnabled(), 'Apply must prevent overlapping operations'
            wait_until(lambda: not window._jobs)
            assert not errors, errors
            rows = [json.loads(line) for line in journal.read_text().splitlines()]
            self_row = rows[-1]
            assert self_row['id'] == 'test_box' and self_row['frame'] == 'fixture'
            assert self_row['scene_diff'] and self_row['robot_diff']
            np.testing.assert_allclose(self_row['dimensions'], (.1,.2,.3))
            np.testing.assert_allclose(self_row['position'], (.05,.06,.07))
            np.testing.assert_allclose(self_row['quaternion'], (0,0,np.sqrt(.5),np.sqrt(.5)))
            assert self_row['success']
            assert 'acknowledged' in window.collision_status.text()
            window.add_collision_ros()
            wait_until(lambda: not window._jobs)
            assert errors and 'already exists' in errors[-1]
            assert len(journal.read_text().splitlines()) == 1, 'Duplicate ADD must not reach Apply'
            errors.clear()
            def edit_box():
                dialog = QApplication.activeModalWidget()
                assert isinstance(dialog, CollisionDialog)
                assert dialog.identifier.isReadOnly() and dialog.frame.isReadOnly()
                dialog.dimensions[0].setValue(110)
                dialog.accept()
            QTimer.singleShot(50, edit_box)
            window.edit_collision()
            assert window.selected().mesh.primitive['size_mm'][0] == 110
            window.pose_fields['translation'][0].setValue(150)
            assert len(journal.read_text().splitlines()) == 1, 'Numeric edits must remain local'
            window.update_collision_ros()
            wait_until(lambda: not window._jobs)
            assert not errors, errors
            row = json.loads(journal.read_text().splitlines()[-1])
            np.testing.assert_allclose(row['position'], (.15,.06,.07))
            np.testing.assert_allclose(row['dimensions'], (.11,.2,.3))
            window.project_path = root/'draft.scene.json'
            assert window.save()
            restored = load_scene(window.project_path).objects[0]
            assert restored.collision == window.selected().collision
            np.testing.assert_allclose(restored.matrix(), window.selected().matrix())
            # Each shape exercises the real ROS dimensions/order on Add/Remove.
            for kind, dimensions in [('cylinder',(12.5,200)), ('sphere',(25,))]:
                obj = make_draft('test_'+kind, 'base_link', 'base_link', primitive_spec(kind, dimensions))
                window._add([obj])
                window.add_collision_ros()
                wait_until(lambda: not window._jobs)
                assert not errors, errors
                row = json.loads(journal.read_text().splitlines()[-1])
                np.testing.assert_allclose(row['dimensions'], (.2,.0125) if kind == 'cylinder' else (.025,))
                window.remove_collision_ros()
                wait_until(lambda: not window._jobs)
                assert not errors, errors
            window._select(draft.id)
            window.remove_collision_ros()
            wait_until(lambda: not window._jobs)
            assert not errors, errors
            row = json.loads(journal.read_text().splitlines()[-1])
            assert row['operation'] == 1 and not row['world_ids']
            assert window.selected() is not None, 'Removing from ROS must retain the local definition'
            window.update_collision_ros()
            wait_until(lambda: not window._jobs)
            assert errors and 'does not exist' in errors[-1]
            errors.clear()
            reject = make_draft('reject_me', 'base_link', 'base_link', primitive_spec('box',(1,2,3)))
            window._add([reject])
            window.add_collision_ros()
            wait_until(lambda: not window._jobs)
            assert errors and 'rejected' in errors[-1]
            assert window.selected().id == reject.id
            assert window.centralWidget().isEnabled()
            assert 'failed' in window.collision_status.text()
            window.delete()
            window._select(draft.id)
            window.collision_status.setText('Local preview — explicit Add / Update / Remove')
            window.frame_selected()
            window.duplicate()
            assert window.selected().collision['object_id'] != draft.collision['object_id']
            window.history.undo()
            window._select(draft.id)
            QTest.qWait(200)
            assert not window.viewport._error, window.viewport._error
            assert window.grab().save('/tmp/scene-editor-collision.png')
            assert 'rclpy' not in sys.modules
            print('Isolated collision checks passed: Box/Cylinder/Sphere Add, Update, Remove, frame resolution, mm→m/quaternion, duplicate/missing/attached ID guards, rejection recovery, persistence and local-only edits')
        finally:
            if window is not None:
                window.history.setClean()
                window.close()
                wait_until(lambda: not window.isVisible())
            server.terminate()
            try:
                server.wait(timeout=3)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait()
            output = server.stdout.read()
            server.stdout.close()
            if server.returncode not in (0,-15):
                print(output)
            app.processEvents()


if __name__ == '__main__':
    main()
