"""Verify profile composition offline; never starts ROS nodes or sends motion."""
from pathlib import Path
import importlib.util
import os
import shutil
import struct
import sys
import tempfile
from types import ModuleType
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import yaml

PACKAGE = Path(__file__).resolve().parents[1]
RUNTIME = PACKAGE.parent / 'erob_moveit_runtime' / 'scripts' / 'config.py'
sys.path.insert(0, str(PACKAGE))
from zeroerr_configuration import load_yaml_layers, resolve_robot_description


def normalized(node):
    attrs = {k: v for k, v in node.attrib.items()
             if not (k == 'name' and not v and node.tag in ('visual', 'collision'))}
    return node.tag, attrs, (node.text or '').strip(), [normalized(c) for c in node]


def module_at(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ProfileCompositionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.cache_env = patch.dict(os.environ, {
            'XDG_CACHE_HOME': self.tmp.name, 'EROB_CONFIG_PACKAGE': 'zeroerr',
        })
        self.cache_env.start()
        self.addCleanup(self.cache_env.stop)
        packages = ModuleType('ament_index_python.packages')
        packages.get_package_share_directory = lambda name: str(PACKAGE)
        parent = ModuleType('ament_index_python')
        parent.packages = packages
        self.modules = patch.dict(sys.modules, {'ament_index_python': parent, 'ament_index_python.packages': packages})
        self.modules.start()
        self.addCleanup(self.modules.stop)

    def profile(self, name):
        path = PACKAGE / 'config' / name / 'runtime.yaml'
        return path, load_yaml_layers(path)

    def test_existing_profiles_preserve_every_urdf_value(self):
        for profile in ('paint', 'paint_short_links', 'welding'):
            with self.subTest(profile=profile):
                path, config = self.profile(profile)
                legacy_files = {'paint': 'erob_arm_small.with_mounting_stl.urdf', 'paint_short_links': 'erob_arm_short_links.with_mounting_stl.urdf', 'welding': 'erob_arm_family_motor_masses.urdf'}
                legacy = ET.parse(path.parent / 'urdfs' / legacy_files[profile]).getroot()
                expanded = ET.parse(resolve_robot_description(path, config)).getroot()
                self.assertEqual(normalized(legacy), normalized(expanded))

    def test_launch_and_runtime_resolve_the_same_description(self):
        launch = module_at('test_launch_config', PACKAGE / 'launch/zeroerr_launch/runtime_config.py')
        for profile in ('paint', 'paint_short_links', 'welding', 'paint_tray_dry', 'paint_auto_dry', 'development_short_links', 'development_extended_links'):
            with self.subTest(profile=profile), patch.dict(os.environ, {'ZEROERR_ACTIVE_PROFILE': profile}):
                runtime = module_at('test_runtime_config', RUNTIME)
                self.assertEqual(runtime.URDF_PATH, launch.urdf_path_from_runtime(str(PACKAGE)))
                expected = load_yaml_layers(PACKAGE / 'config' / profile / 'runtime.yaml')
                launched = launch.load_runtime_config(str(PACKAGE))
                for key, value in expected.items():
                    if key in ('URDF_PATH', 'SRDF_PATH'):
                        continue
                    self.assertEqual(launched[key], value, key)
                    self.assertEqual(runtime._CONFIG[key], value, key)
                self.assertEqual(runtime.ACTIVE_PROFILE, profile)

    def test_tray_profile_uses_compact_cell_without_changing_arm_or_calibration(self):
        tray_path, tray = self.profile('paint_tray_dry')
        old_path, old = self.profile('paint_short_links')
        self.assertEqual(tray['TOOL_REGISTRY'], old['TOOL_REGISTRY'])
        tray_root = ET.parse(resolve_robot_description(tray_path, tray)).getroot()
        old_root = ET.parse(resolve_robot_description(old_path, old)).getroot()
        cell = tray_root.find("link[@name='mounting_surface']")
        mount = tray_root.find("joint[@name='mounting_surface_joint']/origin")
        self.assertEqual(mount.get('rpy'), '0 0 1.5707963267948966')
        meshes = {'visual': 'paint_tray_dry_compact.stl',
                  'collision': 'paint_tray_dry_compact.surface_3levels_above.stl'}
        for kind, filename in meshes.items():
            mesh = cell.find(f'{kind}/geometry/mesh')
            self.assertTrue(mesh.get('filename').endswith('/' + filename))
            self.assertEqual(mesh.get('scale'), '0.001 0.001 0.001')
        # A surface-only mesh would resolve successfully but drop the raised
        # fixtures from collision checking. Verify the selected asset has
        # geometry above the 9 mm front surface as well as the lower dryer.
        mesh = cell.find('collision/geometry/mesh')
        asset = PACKAGE / mesh.get('filename').removeprefix('package://zeroerr/')
        data = asset.read_bytes()
        facets = struct.unpack_from('<I', data, 80)[0]
        self.assertEqual(len(data), 84 + 50 * facets)
        z = [struct.unpack_from('<f', data, 84 + 50 * face + 12 + vertex * 12 + 8)[0]
             for face in range(facets) for vertex in range(3)]
        self.assertGreater(max(z), 300.0)
        self.assertAlmostEqual(min(z), -26.0)
        self.assertIsNotNone(old_root.find("link[@name='mounting_surface']/collision/geometry/box"))
        for name in ('Joint_1', 'Joint_2', 'Joint_3', 'Joint_4', 'Joint_5', 'Joint_6'):
            self.assertEqual(normalized(tray_root.find(f"joint[@name='{name}']")),
                             normalized(old_root.find(f"joint[@name='{name}']")))
        self.assertNotEqual((tray_path.parent / tray['CALIBRATION_PATH']).resolve(),
                            (old_path.parent / old['CALIBRATION_PATH']).resolve())

    def test_automatic_dryer_preserves_legacy_paint_cell_with_independent_calibration(self):
        auto_path, auto = self.profile('paint_auto_dry')
        legacy_path, legacy = self.profile('paint')
        self.assertEqual(Path(resolve_robot_description(auto_path, auto)).read_bytes(),
                         Path(resolve_robot_description(legacy_path, legacy)).read_bytes())
        self.assertNotEqual(auto_path.parent / auto['CALIBRATION_PATH'],
                            legacy_path.parent / legacy['CALIBRATION_PATH'])

    def test_development_profiles_have_square_cells_and_distinct_arm_lengths(self):
        for profile, expected_length in (('development_short_links', 0.2435),
                                         ('development_extended_links', 0.3635)):
            with self.subTest(profile=profile):
                path, config = self.profile(profile)
                root = ET.parse(resolve_robot_description(path, config)).getroot()
                cell = root.find("link[@name='mounting_surface']")
                for kind in ('visual', 'collision'):
                    self.assertEqual(cell.find(f'{kind}/geometry/box').get('size'), '2.0 2.0 0.03')
                joint = root.find("joint[@name='Joint_3']/origin")
                self.assertAlmostEqual(float(joint.get('xyz').split()[2]), expected_length)
                self.assertEqual(config['MOTION_PASSAGES'], [])
                self.assertEqual(root.find("joint[@name='mounting_surface_joint']/origin").get('rpy'), '0 0 0')

    def test_tool_and_workobject_save_only_update_profile_calibration(self):
        # A copied package prevents writes to source or installed configuration.
        copy = Path(self.tmp.name) / 'zeroerr'
        shutil.copytree(PACKAGE / 'config', copy / 'config')
        import ament_index_python.packages as packages
        with patch.object(packages, 'get_package_share_directory', return_value=str(copy)), \
                patch.dict(os.environ, {'ZEROERR_ACTIVE_PROFILE': 'paint_tray_dry'}):
            runtime = module_at('test_runtime_persistence', RUNTIME)
            shared = copy / 'config/paint_short_links/calibration.yaml'
            shared_before = shared.read_bytes()
            profile_path = copy / 'config/paint_tray_dry/runtime.yaml'
            profile_before = profile_path.read_bytes()
            runtime.update_tool_registry(1, None, [1, 2, 3, 4, 5, 6], persist=True)
            runtime.update_workobject_registry(1, None, [6, 5, 4, 3, 2, 1], persist=True)
            calibration = load_yaml_layers(copy / 'config/paint_tray_dry/calibration.yaml')
            self.assertEqual(calibration['TOOL_REGISTRY']['TOOL_1'], [1, 2, 3, 4, 5, 6])
            self.assertEqual(calibration['WORKOBJECT_REGISTRY']['WOBJ_1'], [6, 5, 4, 3, 2, 1])
            self.assertEqual(shared.read_bytes(), shared_before)
            self.assertEqual(profile_path.read_bytes(), profile_before)
            reloaded = module_at('test_runtime_persisted', RUNTIME)
            self.assertEqual(reloaded.TOOL_REGISTRY['TOOL_1'], [1, 2, 3, 4, 5, 6])

    def test_missing_component_and_include_cycle_fail_clearly(self):
        path = Path(self.tmp.name) / 'runtime.yaml'
        path.write_text('RUNTIME_INCLUDES: [missing.yaml]\n')
        with self.assertRaises(FileNotFoundError):
            load_yaml_layers(path)
        path.write_text('RUNTIME_INCLUDES: [runtime.yaml]\n')
        with self.assertRaisesRegex(ValueError, 'include cycle'):
            load_yaml_layers(path)

    def test_missing_macro_fails_instead_of_reusing_cached_description(self):
        path, config = self.profile('paint_short_links')
        resolve_robot_description(path, config)
        with self.assertRaises(FileNotFoundError):
            resolve_robot_description(path, {**config, 'URDF_PATH': 'missing.xacro'})

    def test_shared_change_updates_all_profiles_and_profile_mount_stays_local(self):
        copy = Path(self.tmp.name) / 'zeroerr'
        shutil.copytree(PACKAGE / 'config', copy / 'config')
        paths = [copy / 'config' / name / 'runtime.yaml' for name in ('paint', 'paint_short_links', 'paint_tray_dry', 'welding')]
        before = [resolve_robot_description(p, load_yaml_layers(p)) for p in paths]
        macro = copy / 'config/shared/urdf/zeroerr_arm.xacro'
        macro.write_text(macro.read_text().replace('damping="0.7"', 'damping="0.75"'))
        after = [resolve_robot_description(p, load_yaml_layers(p)) for p in paths]
        self.assertTrue(all(a != b for a, b in zip(before, after)))
        entry = copy / 'config/paint_tray_dry/urdfs/robot.urdf.xacro'
        entry.write_text(entry.read_text().replace('paint_tray_dry_compact mount_xyz="0 0 0"', 'paint_tray_dry_compact mount_xyz="0.1 0 0"'))
        final = [resolve_robot_description(p, load_yaml_layers(p)) for p in paths]
        self.assertEqual(final[:2], after[:2])
        self.assertEqual(final[3], after[3])
        self.assertNotEqual(final[2], after[2])


if __name__ == '__main__':
    unittest.main()
