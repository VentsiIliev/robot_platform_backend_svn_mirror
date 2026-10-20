import json
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scene_editor.collision import make_draft, primitive_spec, request_for, validate_request, validate_metadata
from scene_editor.model import Pose, Scene, load_scene, save_scene


class CollisionTests(unittest.TestCase):
    def test_precise_dimensions_and_validation(self):
        self.assertEqual(primitive_spec('box', (100.25, 200, 300))['size_mm'], [100.25, 200, 300])
        self.assertEqual(primitive_spec('cylinder', (12.5, 180)), dict(kind='cylinder', radius_mm=12.5, length_mm=180))
        self.assertEqual(primitive_spec('sphere', (25,)), dict(kind='sphere', radius_mm=25))
        for kind, dimensions in [('box', (0,1,1)), ('box', (1,2)), ('sphere', (float('nan'),)), ('cylinder', (-1,2)), ('unknown', ())]:
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                primitive_spec(kind, dimensions)

    def test_relative_pose_preview_and_publish_use_correct_frames(self):
        parent = Pose((1000, 2000, 0), (0,0,90)).matrix()
        obj = make_draft('fixture', 'fixture_frame', 'base_link', primitive_spec('box', (10,20,30)),
                         Pose((100,0,0), (0,30,0)), parent.tolist())
        np.testing.assert_allclose(obj.matrix(), parent @ obj.pose.matrix())
        np.testing.assert_allclose(obj.world_pivot(), (1000,2100,0), atol=1e-10)
        request = validate_request(request_for(obj, 'add'))
        self.assertEqual(request['frame'], 'fixture_frame')
        np.testing.assert_allclose(request['pose_mm'], obj.pose.matrix())
        self.assertNotEqual(request['pose_mm'], obj.matrix().tolist())

    def test_publish_bakes_pivot_without_mutating_draft(self):
        obj = make_draft('tool', 'base_link', 'base_link', primitive_spec('cylinder', (10,100)), Pose((10,20,30),(45,20,90),(0,0,50)))
        request = request_for(obj, 'update')
        np.testing.assert_allclose(request['pose_mm'], obj.pose.matrix())
        self.assertEqual(obj.pose.pivot, (0,0,50))
        self.assertNotIn('primitive', request_for(obj, 'remove'))

    def test_scene_roundtrip_keeps_draft_identity_dimensions_frame_and_pose(self):
        obj = make_draft('obstacle', 'fixture', 'base_link', primitive_spec('sphere', (45.5,)), Pose((1,2,3),(10,20,30)), Pose((100,200,300),(0,0,90)).matrix().tolist())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'test.scene.json'
            save_scene(Scene([obj], 'base_link'), path)
            saved = json.loads(path.read_text())
            self.assertEqual(saved['objects'][0]['collision']['frame'], 'fixture')
            scene = load_scene(path)
            self.assertEqual(scene.reference_frame, 'base_link')
            self.assertEqual(request_for(scene.objects[0], 'add'), request_for(obj, 'add'))
            np.testing.assert_allclose(scene.objects[0].matrix(), obj.matrix())

    def test_no_invalid_identity_transform_or_operation_crosses_boundary(self):
        obj = make_draft('obstacle', 'base_link', 'base_link', primitive_spec('box',(1,2,3)))
        for identifier in ('', ' bad', 'bad\n'):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                make_draft(identifier, 'base_link', 'base_link', primitive_spec('sphere',(1,)))
        for frame in ('', 'bad frame', '$(shell)'):
            with self.subTest(frame=frame), self.assertRaises(ValueError):
                make_draft('valid', frame, 'base_link', primitive_spec('sphere',(1,)))
        for operation in ('clear_all','attach','move_robot'):
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                request_for(obj, operation)
        invalid = request_for(obj,'add')
        invalid['pose_mm'][0][0] = 2
        with self.assertRaises(ValueError):
            validate_request(invalid)
        with self.assertRaises(ValueError):
            validate_metadata(dict(obj.collision, frame_to_editor=np.diag([-1,1,1,1]).tolist()))


if __name__ == '__main__':
    unittest.main()
