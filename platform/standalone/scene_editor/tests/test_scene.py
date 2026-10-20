"""Geometry, frame, units, persistence and source-protection regression checks."""
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scene_editor.geometry import Mesh, read_stl, export_stl, make_box
from scene_editor.model import Pose, Scene, SceneObject, rotation_matrix, euler_degrees, save_scene, load_scene
from scene_editor.urdf import load_urdf, resolve_mesh


class SceneTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_export_bakes_units_rotation_translation_without_changing_source(self):
        original = self.root / 'original.stl'
        export_stl(make_box((.2, .1, .05)), np.eye(4), original)
        original_bytes = original.read_bytes()
        mesh = read_stl(original)
        obj = SceneObject('tool', mesh, Pose((100, 200, 300), (0, 0, 90)), (1000,)*3)
        exported = self.root / 'moved.stl'
        export_stl(mesh, obj.matrix(), exported)
        moved = read_stl(exported)
        expected = mesh.vertices @ obj.matrix()[:3, :3].T + obj.matrix()[:3, 3]
        np.testing.assert_allclose(moved.vertices, expected, atol=2e-5)
        np.testing.assert_allclose(np.linalg.norm(moved.normals, axis=1), 1)
        self.assertEqual(len(moved.vertices), len(mesh.vertices))
        self.assertEqual(exported.stat().st_size, 84 + 50*len(mesh.vertices))
        self.assertEqual(original.read_bytes(), original_bytes)
        with self.assertRaises(ValueError):
            export_stl(mesh, obj.matrix(), original)

    def test_ascii_and_binary_header_starting_solid(self):
        path = self.root / 'ascii.stl'
        path.write_text('solid shape\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\nendsolid\n')
        mesh = read_stl(path)
        np.testing.assert_array_equal(mesh.vertices, [[[0, 0, 0], [1, 0, 0], [0, 1, 0]]])
        binary = self.root / 'binary.stl'
        export_stl(mesh, np.eye(4), binary)
        data = binary.read_bytes()
        binary.write_bytes(b'solid binary'.ljust(80, b' ') + data[80:])
        np.testing.assert_array_equal(read_stl(binary).vertices, mesh.vertices)

    def test_invalid_and_truncated_meshes_rejected(self):
        for data in (b'no mesh', b' '*80+struct.pack('<I', 3), b'solid s\nvertex 1 2 3\n', b'solid s\nvertex nan 0 0\nvertex 1 0 0\nvertex 0 1 0\n'):
            path = self.root / 'bad.stl'
            path.write_bytes(data)
            with self.subTest(data=data[:12]), self.assertRaises(ValueError):
                read_stl(path)
        with self.assertRaises(ValueError):
            Mesh(np.zeros((3, 3)))

    def test_pivot_change_preserves_entire_transform(self):
        pose = Pose((10, 20, 30), (27, -42, 120), (9, 8, 7))
        changed = pose.with_pivot((100, -200, 400))
        np.testing.assert_allclose(changed.matrix(), pose.matrix(), atol=1e-12)
        np.testing.assert_allclose(changed.with_pivot((0, 0, 0)).matrix(), pose.matrix(), atol=1e-12)

    def test_origin_snap_across_frames_pivots_and_scales_preserves_rotation(self):
        from scene_editor.collision import make_draft, primitive_spec
        source = make_draft('source', 'fixture', 'base', primitive_spec('box',(100,200,300)),
                            Pose((40,50,60),(30,-20,70),(10,20,30)), Pose((500,-100,300),(0,30,80)).matrix().tolist())
        source.unit_scale = (2,3,4)
        target = SceneObject('target', make_box((10,20,30)), Pose((-100,200,50),(15,25,35),(50,60,70)), locked=True)
        before_rotation = source.matrix()[:3,:3].copy()
        target_matrix = target.matrix().copy()
        snapped = source.pose_snapped_to(target)
        from dataclasses import replace
        result = replace(source, pose=snapped)
        np.testing.assert_allclose(result.world_origin(), target.world_origin(), atol=1e-10)
        np.testing.assert_allclose(result.matrix()[:3,:3], before_rotation, atol=1e-12)
        np.testing.assert_array_equal(target.matrix(), target_matrix)
        self.assertEqual(snapped.rotation, source.pose.rotation)
        self.assertEqual(snapped.pivot, source.pose.pivot)
        with self.assertRaises(ValueError):
            replace(source, locked=True).pose_snapped_to(target)

    def test_lock_persistence_and_legacy_default(self):
        scene = Scene([SceneObject('locked', make_box((1,2,3)), locked=True)])
        project = self.root/'locked.scene.json'
        save_scene(scene, project)
        self.assertTrue(load_scene(project).objects[0].locked)
        payload = json.loads(project.read_text())
        del payload['objects'][0]['locked']
        project.write_text(json.dumps(payload))
        self.assertFalse(load_scene(project).objects[0].locked)
        payload['objects'][0]['locked'] = 'yes'
        project.write_text(json.dumps(payload))
        with self.assertRaises(ValueError):
            load_scene(project)

    def test_group_translation_keeps_relative_positions_across_frames(self):
        from scene_editor.model import translated_poses
        from scene_editor.collision import make_draft, primitive_spec
        from dataclasses import replace
        first = make_draft('a','fixture','base',primitive_spec('box',(10,20,30)),
                           Pose((20,30,40),(10,20,30),(5,6,7)),Pose((100,200,300),(30,60,90)).matrix().tolist())
        second = SceneObject('b',make_box((10,20,30)),Pose((-40,80,200),(-10,70,15),(3,2,1)),unit_scale=(2,3,4))
        before = [obj.matrix().copy() for obj in (first,second)]
        delta = (15.25,-100,30)
        poses = translated_poses([first,second],delta)
        after = [replace(obj,pose=poses[obj.id]) for obj in (first,second)]
        for index,obj in enumerate(after):
            np.testing.assert_allclose(obj.matrix()[:3,3]-before[index][:3,3],delta,atol=1e-10)
            np.testing.assert_allclose(obj.matrix()[:3,:3],before[index][:3,:3],atol=1e-12)
        np.testing.assert_allclose(after[0].world_origin()-after[1].world_origin(), first.world_origin()-second.world_origin(),atol=1e-10)
        second.locked = True
        with self.assertRaises(ValueError):
            translated_poses([first,second],delta)
        np.testing.assert_array_equal(first.matrix(),before[0])
        np.testing.assert_array_equal(second.matrix(),before[1])

    def test_rotations_round_trip_including_gimbal_lock(self):
        for angles in ((12, 31, -40), (90, 0, 0), (45, 90, 72), (-32, -90, 11)):
            matrix = rotation_matrix(angles)
            np.testing.assert_allclose(rotation_matrix(euler_degrees(matrix)), matrix, atol=1e-12)

    def test_scene_round_trip_external_relative_and_primitive(self):
        mesh_path = self.root / 'mesh.stl'
        export_stl(make_box((1, 2, 3)), np.eye(4), mesh_path)
        mesh = read_stl(mesh_path)
        source = SceneObject('Source', mesh, Pose((10, -20, 30), (20, 30, 40), (1, 2, 3)), (1000,)*3, (.1, .2, .3, .4), False)
        scene = Scene([source, SceneObject('Box', make_box((100, 200, 300)))])
        project = self.root / 'test.scene.json'
        save_scene(scene, project)
        self.assertEqual(json.loads(project.read_text())['objects'][0]['geometry']['stl'], 'mesh.stl')
        loaded = load_scene(project)
        self.assertEqual(len(loaded.objects), 2)
        for before, after in zip(scene.objects, loaded.objects):
            self.assertEqual(before.id, after.id)
            self.assertEqual(before.name, after.name)
            self.assertEqual(before.visible, after.visible)
            self.assertEqual(before.color, after.color)
            np.testing.assert_allclose(before.matrix(), after.matrix())
            np.testing.assert_array_equal(before.mesh.vertices, after.mesh.vertices)
        with self.assertRaises(ValueError):
            save_scene(scene, mesh_path)

    def test_scene_validation_and_missing_reference(self):
        project = self.root / 'test.scene.json'
        scene = Scene([SceneObject('Box', make_box((1, 2, 3)))])
        save_scene(scene, project)
        payload = json.loads(project.read_text())
        for key, value in [('units', 'm'), ('version', 999), ('objects', None)]:
            changed = dict(payload, **{key: value})
            project.write_text(json.dumps(changed))
            with self.subTest(key=key), self.assertRaises(ValueError):
                load_scene(project)
        payload['objects'] *= 2
        project.write_text(json.dumps(payload))
        with self.assertRaises(ValueError):
            load_scene(project)
        for kwargs in ({'unit_scale': (0, 1, 1)}, {'color': (2, 0, 0, 1)}, {'visible': 'false'}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                SceneObject('invalid', make_box((1, 1, 1)), **kwargs)

    def test_urdf_hierarchy_visual_origin_units_material(self):
        path = self.root / 'robot.urdf'
        path.write_text('''<robot name="test"><material name="purple"><color rgba="0.5 0.2 0.7 1"/></material>
        <link name="base"/><link name="tool"><visual><origin xyz="1 0 0"/>
        <geometry><box size="0.1 0.2 0.3"/></geometry><material name="purple"/></visual></link>
        <joint name="fixed" type="fixed"><parent link="base"/><child link="tool"/>
        <origin xyz="0 2 0" rpy="0 0 1.5707963267948966"/></joint></robot>''')
        scene = load_urdf(path)
        obj = scene.objects[0]
        np.testing.assert_allclose(obj.pose.translation, (0, 3000, 0), atol=1e-9)
        np.testing.assert_allclose(obj.mesh.bounds[1]-obj.mesh.bounds[0], (100, 200, 300))
        np.testing.assert_allclose(obj.pose.rotation, (0, 0, 90))
        self.assertEqual(obj.color, (.5, .2, .7, 1))

    def test_urdf_package_and_mesh_scale(self):
        package = self.root / 'description'
        package.mkdir()
        mesh = package / 'tool.stl'
        export_stl(make_box((.1, .2, .3)), np.eye(4), mesh)
        urdf = self.root / 'tool.urdf'
        urdf.write_text('''<robot name="test"><link name="tool"><visual><geometry>
        <mesh filename="package://description/tool.stl" scale="1 2 3"/>
        </geometry></visual></link></robot>''')
        self.assertEqual(resolve_mesh('package://description/tool.stl', urdf), mesh)
        obj = load_urdf(urdf).objects[0]
        np.testing.assert_allclose(obj.world_bounds()[1]-obj.world_bounds()[0], (100, 400, 900), atol=5e-5)
        with self.assertRaises(ValueError):
            resolve_mesh('$(find package)/tool.stl', urdf)

    def test_urdf_cycles_are_rejected(self):
        path = self.root / 'cycle.urdf'
        path.write_text('''<robot name="test"><link name="a"/><link name="b"/>
        <joint name="ab" type="fixed"><parent link="a"/><child link="b"/></joint>
        <joint name="ba" type="fixed"><parent link="b"/><child link="a"/></joint></robot>''')
        with self.assertRaises(ValueError):
            load_urdf(path)


if __name__ == '__main__':
    unittest.main()
