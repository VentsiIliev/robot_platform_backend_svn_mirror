"""Opt-in read-only integration check against an already running ROS graph.

This test never starts a robot/backend or publishes scene/hardware commands.
It requires robot_description, TF, and the running GetPlanningScene service.
"""
import os
import argparse
from pathlib import Path
import sys
import tempfile
import time

import numpy as np
from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scene_editor.window import EditorWindow
from scene_editor.ros_connection import RosOptions
from scene_editor.model import load_scene


def wait_until(predicate, seconds=30):
    deadline = time.monotonic()+seconds
    while not predicate() and time.monotonic() < deadline:
        QTest.qWait(50)
    return predicate()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace-setup', default='')
    args = parser.parse_args()
    fmt = QSurfaceFormat()
    fmt.setVersion(3, 3)
    fmt.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    fmt.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(fmt)
    app = QApplication([])
    window = EditorWindow()
    window.show()
    errors = []
    window._error = errors.append
    options = RosOptions(domain=int(os.environ.get('ROS_DOMAIN_ID', '0')), workspace_setup=args.workspace_setup)
    window.begin_ros(options)
    try:
        assert wait_until(lambda: any(obj.id.startswith('robot/') for obj in window.scene.objects) or window._ros is None), window._ros_details
        assert window._live_received, window._ros_details
        assert 'rclpy' not in sys.modules, 'ROS imports must remain inside the helper process'
        assert window.scene.objects, window._ros_details
        assert any(obj.id.startswith('robot/') for obj in window.scene.objects)
        assert wait_until(lambda: 'Initial planning scene received: True' in window._ros_details, 15), window._ros_details
        assert not window.mode.isEnabled(), 'Transforms must be disabled in live view'
        assert not window.import_action.isEnabled()
        first = window.scene.objects[0]
        window._select(first.id)
        assert window.pose_fields['translation'][0].isReadOnly()
        assert not window.color_button.isEnabled()
        before = window.selected().pose
        window._change('Must be ignored in live view', pose=type(before)((999, 999, 999)))
        assert window.selected().pose == before
        QTest.qWait(1300)
        assert not window.viewport._error, window.viewport._error
        assert window.grab().save('/tmp/scene-editor-ros-live.png')
        print('LIVE:', len(window.scene.objects), 'objects;', sum(len(obj.mesh.vertices) for obj in window.scene.objects), 'triangles')
        print('STATUS:', window._ros_details)
        window.editable_snapshot()
        assert not window._live
        assert not window.history.isClean()
        assert wait_until(lambda: window._ros is None, 6), 'Helper did not stop'
        assert window.mode.isEnabled() and not window.pose_fields['translation'][0].isReadOnly()
        window.pose_fields['translation'][0].setValue(123)
        expected = window.selected().pose
        QTest.qWait(600)
        assert window.selected().pose == expected, 'Live update overwrote the editable snapshot'
        with tempfile.TemporaryDirectory() as directory:
            window.project_path = Path(directory)/'ros-snapshot.scene.json'
            assert window.save(), errors
            scene = load_scene(window.project_path)
            restored = next(obj for obj in scene.objects if obj.id == first.id)
            np.testing.assert_allclose(restored.matrix(), window.selected().matrix(), atol=1e-9)
        print('Snapshot edit/save/reload passed; no scene or motion commands sent')
        # A second connection followed by closing also must stop its helper.
        window.history.setClean()
        window.begin_ros(options)
        QTest.qWait(200)
        window.close()
        assert wait_until(lambda: not window.isVisible(), 6), 'Close did not stop the ROS helper'
        assert window._ros is None
        assert not errors, errors
        app.processEvents()
        print('Reconnect and close cleanup passed')
    finally:
        window.history.setClean()
        if window.isVisible():
            window.close()
            wait_until(lambda: not window.isVisible(), 6)


if __name__ == '__main__':
    main()
