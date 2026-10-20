"""One-shot description transport; no ROS dependency or running graph needed."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.ros_connection import RosOptions,RobotDescriptionUnavailable,resolved_robot_snapshot


class DescriptionTests(unittest.TestCase):
    @staticmethod
    def result(**packet):
        payload = dict(protocol='scene-editor-description-v1',**packet)
        return subprocess.CompletedProcess([],0,'ROS diagnostic\n'+json.dumps(payload)+'\n')

    def test_resolved_robot_is_loaded_without_ros_in_gui_process(self):
        xml = ('<robot name="robot"><link name="base"><visual><origin xyz="1 2 3"/>'
               '<geometry><box size=".1 .2 .3"/></geometry></visual></link></robot>')
        with patch('scene_editor.ros_connection.subprocess.run',return_value=self.result(success=True,xml=xml,packages={})) as run:
            scene = resolved_robot_snapshot(RosOptions(domain=173,description_topic='/test/description'))
        self.assertEqual(len(scene.objects),1)
        self.assertEqual(scene.objects[0].id,'robot/resolved/0')
        self.assertEqual(scene.objects[0].pose.translation,(1000.,2000.,3000.))
        self.assertEqual(run.call_args.kwargs['env']['ROS_DOMAIN_ID'],'173')
        self.assertIn('/test/description',run.call_args.args[0])
        self.assertNotIn('rclpy',sys.modules)

    def test_unavailable_and_timeout_trigger_typed_fallback(self):
        with patch('scene_editor.ros_connection.subprocess.run',return_value=self.result(success=False,unavailable=True,message='No publisher')):
            with self.assertRaisesRegex(RobotDescriptionUnavailable,'No publisher'):
                resolved_robot_snapshot(RosOptions())
        with patch('scene_editor.ros_connection.subprocess.run',side_effect=subprocess.TimeoutExpired([],12)):
            with self.assertRaises(RobotDescriptionUnavailable):
                resolved_robot_snapshot(RosOptions())

    def test_invalid_description_is_not_reported_as_missing_ros(self):
        with patch('scene_editor.ros_connection.subprocess.run',return_value=self.result(success=False,unavailable=False,message='Malformed robot description')):
            with self.assertRaises(RuntimeError) as context:
                resolved_robot_snapshot(RosOptions())
            self.assertNotIsInstance(context.exception,RobotDescriptionUnavailable)


if __name__ == '__main__':
    unittest.main()
