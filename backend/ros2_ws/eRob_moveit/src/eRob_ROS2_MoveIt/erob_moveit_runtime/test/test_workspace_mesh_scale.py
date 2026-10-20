"""Exercise workspace extraction with a real millimetre STL, without ROS nodes."""
from pathlib import Path
import importlib.util
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

import trimesh

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/utils/workspace_extractor.py'


class WorkspaceMeshScaleTests(unittest.TestCase):
    def extract(self, dimensions, scale_attribute, mount_yaw=0.0, collision_xyz="0 0 0", geometry="mesh"):
        spec = importlib.util.spec_from_file_location('workspace_scale_test', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            trimesh.creation.box(extents=dimensions).export(Path(directory) / 'table.stl')
            shape = (f'<mesh filename="package://zeroerr/table.stl" {scale_attribute}/>'
                     if geometry == 'mesh' else f'<box size="{dimensions[0]} {dimensions[1]} {dimensions[2]}"/>')
            description = f'''<robot name="test"><link name="base_link"/>
              <link name="mounting_surface"><collision><origin xyz="{collision_xyz}"/><geometry>
                {shape}
              </geometry></collision></link>
              <joint name="mount" type="fixed"><parent link="base_link"/>
                <child link="mounting_surface"/><origin xyz="0.1 -0.2 0" rpy="0 0 {mount_yaw}"/>
              </joint></robot>'''
            robot = SimpleNamespace(get_logger=lambda: MagicMock(), destroy_subscription=MagicMock())

            def subscribe(_type, _topic, callback, _qos):
                callback(SimpleNamespace(data=description))
                return object()

            robot.create_subscription = subscribe
            with patch('ament_index_python.packages.get_package_share_directory', return_value=directory):
                return module._extract_workspace_from_urdf(robot, max_retries=1)

    def test_millimetre_mesh_matches_metre_mesh_workspace(self):
        millimetres = self.extract([200, 400, 6], 'scale="0.001 0.001 0.001"')
        metres = self.extract([0.2, 0.4, 0.006], '')
        for key in metres:
            self.assertAlmostEqual(millimetres[key], metres[key], places=7)
        self.assertAlmostEqual(millimetres['x_min'], 0.0)
        self.assertAlmostEqual(millimetres['x_max'], 0.2)
        self.assertAlmostEqual(millimetres['y_min'], -0.4)
        self.assertAlmostEqual(millimetres['y_max'], 0.0)


    def test_ccw_rotation_updates_workspace_in_base_frame(self):
        for geometry in ('mesh', 'box'):
            with self.subTest(geometry=geometry):
                result = self.extract([0.2, 0.4, 0.006], '',
                                      mount_yaw=1.5707963267948966, geometry=geometry)
                self.assertAlmostEqual(result['x_min'], -0.1)
                self.assertAlmostEqual(result['x_max'], 0.3)
                self.assertAlmostEqual(result['y_min'], -0.3)
                self.assertAlmostEqual(result['y_max'], -0.1)

    def test_collision_offset_rotates_with_the_mount(self):
        result = self.extract([0.2, 0.4, 0.006], '',
                              mount_yaw=1.5707963267948966, collision_xyz="0.3 0 0")
        self.assertAlmostEqual(result['x_min'], -0.1)
        self.assertAlmostEqual(result['x_max'], 0.3)
        self.assertAlmostEqual(result['y_min'], 0.0)
        self.assertAlmostEqual(result['y_max'], 0.2)


if __name__ == '__main__':
    unittest.main()
