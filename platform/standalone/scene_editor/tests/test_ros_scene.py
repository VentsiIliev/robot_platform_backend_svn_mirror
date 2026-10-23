"""Pure conversion/transport tests: no ROS graph, ROS imports or display needed."""
from pathlib import Path
from types import SimpleNamespace as NS
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scene_editor.geometry import Mesh,export_stl,make_box
from scene_editor.model import Pose, Scene, SceneObject, load_scene, save_scene
from scene_editor.ros_scene import SceneAssembler, FrameGraph, pose_matrix
from scene_editor.ros_helper import SceneWriter
from scene_editor.ros_connection import RosConnection, RosOptions, SceneDecoder


def xyz(x=0., y=0., z=0.):
    return NS(x=x, y=y, z=z)


def pose(x=0., y=0., z=0., yaw=0.):
    return NS(position=xyz(x, y, z), orientation=NS(x=0., y=0., z=np.sin(yaw/2), w=np.cos(yaw/2)))


def transform(parent, child, x=0., y=0., z=0., yaw=0.):
    p = pose(x, y, z, yaw)
    return NS(header=NS(frame_id=parent), child_frame_id=child,
              transform=NS(translation=p.position, rotation=p.orientation))


def collision(name='box', operation=0, frame='base', x=0., shape=True):
    return NS(id=name, operation=operation, header=NS(frame_id=frame), pose=pose(x),
              primitives=[NS(type=1, dimensions=[.1, .2, .3])] if shape else [],
              primitive_poses=[pose()] if shape else [], meshes=[], mesh_poses=[], planes=[])


def planning(objects=(), *, diff=False, attached=(), robot_diff=True, colors=()):
    return NS(is_diff=diff, world=NS(collision_objects=list(objects)), fixed_frame_transforms=[],
              robot_state=NS(is_diff=robot_diff, attached_collision_objects=list(attached)),
              object_colors=list(colors))


def marker(ns='axes', marker_id=1, **changes):
    values = dict(ns=ns, id=marker_id, action=0, type=1, mesh_resource='',
                  header=NS(frame_id='base'), pose=pose(), scale=xyz(.1, .2, .3),
                  color=NS(r=.2, g=.4, b=.8, a=1.), points=[], colors=[],
                  frame_locked=True, lifetime=NS(sec=0, nanosec=0))
    values.update(changes)
    return NS(**values)


class RosSceneTests(unittest.TestCase):
    def test_compound_cell_fixture_is_one_selectable_object_without_filling_gaps(self):
        message = collision(name='cell_fixture_dispenser')
        message.primitives.append(NS(type=1, dimensions=[.1,.2,.3]))
        message.primitive_poses.append(pose(.5, yaw=np.pi/2))
        self.scene.planning_scene(planning([message]))
        scene, _ = self.scene.build()
        self.assertEqual(len(scene.objects),1)
        obj = scene.objects[0]
        self.assertEqual(obj.id,'world/cell_fixture_dispenser/0')
        self.assertEqual(len(obj.mesh.vertices),24)
        np.testing.assert_allclose(obj.mesh.bounds, [[-50,-100,-150],[600,100,150]],atol=1e-4)
        self.assertIs(self.scene.build()[0].objects[0].mesh,obj.mesh)
        appended = collision(name='cell_fixture_dispenser',operation=2,x=1)
        self.scene.planning_scene(planning([appended],diff=True))
        changed = self.scene.build()[0].objects[0]
        self.assertEqual(len(changed.mesh.vertices),36)
        self.assertIsNot(changed.mesh,obj.mesh)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scene = SceneAssembler('base', self.root)

    def test_ros_quaternion_and_meters_to_mm(self):
        result = pose_matrix(pose(.1, -.2, .3, np.pi/2))
        np.testing.assert_allclose(result, Pose((100, -200, 300), (0, 0, 90)).matrix(), atol=1e-12)
        zero = pose()
        zero.orientation.w = 0
        np.testing.assert_array_equal(pose_matrix(zero), np.eye(4))
        zero.position.x = float('nan')
        with self.assertRaises(ValueError):
            pose_matrix(zero)

    def test_frame_chain_and_inverse_across_siblings(self):
        graph = FrameGraph()
        graph.update([transform('world', 'base', 1), transform('world', 'fixture', 0, 2), transform('fixture', 'tip', 0, 0, .3)])
        np.testing.assert_allclose(graph.lookup('base', 'tip')[:3, 3], (-1000, 2000, 300))
        np.testing.assert_allclose(graph.lookup('tip', 'base') @ graph.lookup('base', 'tip'), np.eye(4))
        self.assertIsNone(graph.lookup('base', 'missing'))
        np.testing.assert_array_equal(graph.lookup('/base', 'base'), np.eye(4))

    def test_frame_cycles_are_reported(self):
        graph = FrameGraph()
        graph.update([transform('a', 'b'), transform('b', 'a')])
        with self.assertRaises(ValueError):
            graph.lookup('base', 'a')

    def test_world_geometry_object_and_shape_poses(self):
        self.scene.frames.update([transform('base', 'fixture', .4)])
        obj = collision(frame='fixture', x=.1)
        obj.primitive_poses[0] = pose(0, .2)
        self.scene.planning_scene(planning([obj]))
        result, warnings = self.scene.build()
        self.assertFalse(warnings)
        np.testing.assert_allclose(result.objects[0].pose.translation, (500, 200, 0))
        np.testing.assert_allclose(result.objects[0].mesh.bounds[1]-result.objects[0].mesh.bounds[0], (100, 200, 300))

    def test_move_reuses_mesh_and_remove_and_full_snapshot_clear(self):
        self.scene.planning_scene(planning([collision()]))
        original = self.scene.build()[0].objects[0]
        self.scene.planning_scene(planning([collision(operation=3, x=.5, shape=False)], diff=True))
        moved = self.scene.build()[0].objects[0]
        self.assertIs(moved.mesh, original.mesh)
        self.assertEqual(moved.id, original.id)
        np.testing.assert_allclose(moved.pose.translation, (500, 0, 0))
        self.scene.planning_scene(planning([collision(operation=1, shape=False)], diff=True))
        self.assertFalse(self.scene.build()[0].objects)

    def test_real_ros_byte_collision_operations(self):
        obj = collision()
        obj.operation = b'\x00'
        self.scene.planning_scene(planning([obj]))
        self.assertEqual(len(self.scene.build()[0].objects), 1)
        obj = collision(operation=b'\x03', x=.5, shape=False)
        self.scene.planning_scene(planning([obj], diff=True))
        self.assertEqual(self.scene.build()[0].objects[0].pose.translation, (500.,0.,0.))
        obj.operation = b'\x01'
        self.scene.planning_scene(planning([obj], diff=True))
        self.assertFalse(self.scene.build()[0].objects)
        self.scene.planning_scene(planning([collision()]))
        self.scene.planning_scene(planning([]))
        self.assertFalse(self.scene.build()[0].objects)

    def test_append_retains_geometry_and_respects_object_origin(self):
        self.scene.planning_scene(planning([collision(x=.1)]))
        self.scene.planning_scene(planning([collision(operation=2, x=.4)], diff=True))
        objects = self.scene.build()[0].objects
        self.assertEqual(len(objects), 2)
        np.testing.assert_allclose([obj.pose.translation[0] for obj in objects], (100, 400))

    def test_attached_geometry_follows_link_and_detaches(self):
        self.scene.frames.update([transform('base', 'wrist', 0, 0, .5)])
        self.scene.planning_scene(planning([collision(name='tool')]))
        tool = collision(name='tool', frame='', x=.1)
        attached = NS(link_name='wrist', object=tool)
        self.scene.planning_scene(planning(diff=True, attached=[attached]))
        objects = self.scene.build()[0].objects
        self.assertEqual(len(objects), 1)
        self.assertTrue(objects[0].id.startswith('attached/'))
        np.testing.assert_allclose(objects[0].pose.translation, (100, 0, 500))
        self.scene.frames.update([transform('base', 'wrist', 0, 0, .8)])
        np.testing.assert_allclose(self.scene.build()[0].objects[0].pose.translation, (100, 0, 800))
        tool.operation = 1
        self.scene.planning_scene(planning(diff=True, attached=[attached]))
        self.assertFalse(self.scene.build()[0].objects)

    def test_collision_mesh_triangles_and_color(self):
        obj = collision(shape=False)
        obj.meshes = [NS(vertices=[xyz(), xyz(.1), xyz(0, .2)], triangles=[NS(vertex_indices=[0, 1, 2])])]
        obj.mesh_poses = [pose()]
        color = NS(id='box', color=NS(r=.1, g=.2, b=.3, a=.7))
        self.scene.planning_scene(planning([obj], colors=[color]))
        loaded = self.scene.build()[0].objects[0]
        self.assertEqual(loaded.color, (.1, .2, .3, .7))
        np.testing.assert_allclose(loaded.mesh.vertices, [[[0, 0, 0], [100, 0, 0], [0, 200, 0]]])
        obj.meshes[0].triangles[0].vertex_indices = [0, 1, 20]
        with self.assertRaises(ValueError):
            self.scene.planning_scene(planning([obj]))
        self.assertIs(self.scene.build()[0].objects[0].mesh, loaded.mesh)

    def test_missing_frames_are_skipped_and_recover(self):
        self.scene.planning_scene(planning([collision(frame='not_yet')]))
        objects, warnings = self.scene.build()
        self.assertFalse(objects.objects)
        self.assertIn('Waiting for TF: not_yet', warnings)
        self.scene.frames.update([transform('base', 'not_yet')])
        self.assertEqual(len(self.scene.build()[0].objects), 1)
        self.assertFalse(self.scene.build()[1])

    def test_robot_visuals_use_tf_with_visual_origin_not_zero_joint_pose(self):
        xml = '''<robot name="r"><link name="base"/><link name="wrist"><visual>
        <origin xyz="0.1 0 0"/><geometry><box size="0.1 0.2 0.3"/></geometry></visual></link>
        <joint name="joint" type="revolute"><parent link="base"/><child link="wrist"/>
        <origin xyz="0 0 9"/></joint></robot>'''
        self.scene.robot_description(xml)
        self.scene.frames.update([transform('base', 'wrist', 0, .5, 0, np.pi/2)])
        obj = self.scene.build()[0].objects[0]
        np.testing.assert_allclose(obj.pose.translation, (0, 600, 0), atol=1e-9)
        np.testing.assert_allclose(obj.pose.rotation, (0, 0, 90))
        self.assertEqual(obj.id, 'robot/wrist/visual/0')

    def test_marker_delete_scoped_to_topic_namespace_and_lifetime(self):
        first = marker(lifetime=NS(sec=1, nanosec=0))
        self.scene.marker_array('/a', NS(markers=[first, marker(ns='other')]), now=10)
        self.scene.marker_array('/b', NS(markers=[marker()]), now=10)
        self.assertEqual(len(self.scene.build(now=10.5)[0].objects), 3)
        self.assertEqual(len(self.scene.build(now=11.1)[0].objects), 2)
        self.scene.marker_array('/a', NS(markers=[marker(ns='axes', action=3)]))
        self.assertEqual(len(self.scene.build()[0].objects), 2)
        self.scene.marker_array('/a', NS(markers=[marker(ns='', action=3)]))
        self.assertEqual(len(self.scene.build()[0].objects), 1)
        self.scene.marker_array('/b', NS(markers=[marker(action=2)]))
        self.assertFalse(self.scene.build()[0].objects)

    def test_marker_frame_lock_and_immutable_geometry_reuse(self):
        self.scene.frames.update([transform('base', 'tool', .1)])
        locked = marker(marker_id=1, header=NS(frame_id='tool'), frame_locked=True)
        frozen = marker(marker_id=2, header=NS(frame_id='tool'), frame_locked=False)
        self.scene.marker_array('/markers', NS(markers=[locked, frozen]))
        first = self.scene.build()[0].objects
        self.scene.frames.update([transform('base', 'tool', .8)])
        second = self.scene.build()[0].objects
        np.testing.assert_allclose([obj.pose.translation[0] for obj in second], (800, 100))
        self.scene.marker_array('/markers', NS(markers=[locked]))
        third = self.scene.build()[0].objects
        self.assertIs(first[0].mesh, third[0].mesh)

    def test_marker_arrow_lines_triangles_and_shapes(self):
        for kind, changes in [
            (0, dict(points=[xyz(), xyz(0, 0, .2)])),
            (0, dict(points=[])), (1, {}), (2, {}), (3, {}),
            (4, dict(points=[xyz(), xyz(.1), xyz(.1, .1)])),
            (5, dict(points=[xyz(), xyz(.1)])),
            (6, dict(points=[xyz(), xyz(.1)])),
            (7, dict(points=[xyz()])), (8, dict(points=[xyz()])),
            (11, dict(points=[xyz(), xyz(.1), xyz(0, .1)])),
        ]:
            with self.subTest(type=kind, changes=changes):
                value = marker(type=kind, **changes)
                self.scene.marker_array('/m', NS(markers=[value]))
                obj = self.scene.build()[0].objects[0]
                self.assertGreater(len(obj.mesh.vertices), 0)
                self.assertTrue(np.isfinite(obj.matrix()).all())

    def test_snapshot_assets_survive_session_cache_deletion(self):
        mesh = Mesh(np.array([[[0, 0, 0], [100, 0, 0], [0, 200, 0]]], dtype=float))
        source = Scene([SceneObject('ROS mesh', mesh, Pose((10, 20, 30), (0, 0, 90)))])
        session = self.root/'session'
        session.mkdir()
        writer = SceneWriter(session)
        decoder = SceneDecoder(session)
        rows = writer.encode(source)
        captured = decoder.decode(rows)
        self.assertIsNone(captured.objects[0].mesh.source)
        self.assertIs(captured.objects[0].mesh, decoder.decode(rows).objects[0].mesh)
        project = self.root/'snapshot.scene.json'
        save_scene(captured, project)
        for path in session.iterdir():
            path.unlink()
        restored = load_scene(project)
        np.testing.assert_allclose(restored.objects[0].matrix(), source.objects[0].matrix())
        np.testing.assert_array_equal(restored.objects[0].mesh.vertices, source.objects[0].mesh.vertices)

    def test_decoder_refuses_cache_escape(self):
        decoder = SceneDecoder(self.root/'session')
        row = dict(id='a', name='bad', geometry={'npy': str(self.root/'outside.npy')},
                   translation=(0, 0, 0), rotation=(0, 0, 0), unit_scale=(1, 1, 1), color=(1, 1, 1, 1))
        with self.assertRaises(ValueError):
            decoder.decode([row])

    def test_setup_paths_are_separate_arguments_and_no_ros_write_services(self):
        options = RosOptions(ros_setup='/tmp/space name; do not execute/setup.bash',
                             workspace_setup='/tmp/$(literal)/local_setup.bash')
        mesh_root = str(self.root/'mesh package; literal')
        command = RosConnection(options,package_root=mesh_root)._command(str(self.root))
        self.assertEqual(command[command.index('--mesh-root')+1],mesh_root)
        self.assertIn(options.ros_setup, command)
        self.assertIn(options.workspace_setup, command)
        shell = command[4]
        self.assertNotIn(options.ros_setup, shell)
        self.assertNotIn(options.workspace_setup, shell)
        # Guard against accidentally turning this reader into a scene/hardware writer.
        import ast
        helper = Path(__file__).parents[1]/'scene_editor'/'ros_helper.py'
        tree = ast.parse(helper.read_text())
        publishers = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
                      and isinstance(node.func, ast.Attribute) and node.func.attr == 'create_publisher']
        clients = [node.args[0].id for node in ast.walk(tree) if isinstance(node, ast.Call)
                   and isinstance(node.func, ast.Attribute) and node.func.attr == 'create_client']
        self.assertFalse(publishers)
        self.assertEqual(clients, ['GetPlanningScene'])

    def test_live_robot_and_resource_use_selected_mesh_folder(self):
        mesh = self.root/'zeroerr/meshes/robots/zeroerr/common/Link_1.stl'
        mesh.parent.mkdir(parents=True)
        export_stl(make_box((1,2,3)),np.eye(4),mesh)
        uri = 'package://zeroerr/meshes/robots/zeroerr/common/Link_1.stl'
        cache = self.root/'cache'
        cache.mkdir()
        assembler = SceneAssembler('base_link',cache,lambda name:str(self.root/'stale_install'),
                                   package_root=self.root/'zeroerr')
        xml = ('<robot name="test"><link name="base_link"><visual><geometry>'
               f'<mesh filename="{uri}"/></geometry></visual></link></robot>')
        assembler.robot_description(xml)
        self.assertEqual(assembler.description,xml)
        self.assertEqual(len(assembler.robot),1)
        self.assertEqual(assembler._resource(uri).source,mesh)

    def test_robot_collision_geometry_has_independent_origins_scales_and_live_tf(self):
        mesh = self.root/'collision.stl'
        export_stl(make_box((1,2,3)),np.eye(4),mesh)
        xml = ('<robot name="test"><link name="wrist">'
               '<visual><origin xyz="0 0 .1"/><geometry><box size=".1 .2 .3"/></geometry></visual>'
               '<collision><origin xyz=".2 0 0" rpy="0 0 1.5707963267948966"/>'
               '<geometry><box size=".01 .02 .03"/></geometry></collision>'
               '<collision><origin xyz="0 .3 0"/><geometry><cylinder radius=".02" length=".1"/></geometry></collision>'
               '<collision><geometry><sphere radius=".04"/></geometry></collision>'
               f'<collision><geometry><mesh filename="{mesh}" scale="2 3 4"/></geometry></collision>'
               '</link></robot>')
        self.scene.robot_description(xml)
        self.scene.frames.update([transform('base','wrist',0,0,.5)])
        objects = {obj.id:obj for obj in self.scene.build()[0].objects}
        self.assertEqual(len(objects),5)
        visual = objects['robot/wrist/visual/0']
        box = objects['robot/wrist/collision/0']
        np.testing.assert_allclose(visual.pose.translation,(0,0,600))
        np.testing.assert_allclose(box.pose.translation,(200,0,500))
        np.testing.assert_allclose(box.pose.rotation,(0,0,90),atol=1e-10)
        np.testing.assert_allclose(box.mesh.vertices.max(axis=(0,1))-box.mesh.vertices.min(axis=(0,1)),(10,20,30))
        self.assertEqual(objects['robot/wrist/collision/1'].mesh.primitive['kind'],'cylinder')
        self.assertEqual(objects['robot/wrist/collision/2'].mesh.primitive['kind'],'sphere')
        self.assertEqual(objects['robot/wrist/collision/3'].unit_scale,(2000,3000,4000))
        self.assertIsNone(box.collision,'URDF collision must not become an authored world collision')
        self.scene.frames.update([transform('base','wrist',0,0,.8)])
        moved = {obj.id:obj for obj in self.scene.build()[0].objects}
        np.testing.assert_allclose(moved[box.id].pose.translation,(200,0,800))
        self.assertIs(moved[box.id].mesh,box.mesh)


if __name__ == '__main__':
    unittest.main()
