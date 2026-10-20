"""Exact surface contact, orientation and rigid-shape preservation."""
from dataclasses import replace
from pathlib import Path
import sys
import unittest
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.geometry import make_box,Mesh,make_cylinder
from scene_editor.model import SceneObject,Pose
from scene_editor.collision import make_draft,primitive_spec
from scene_editor.surface_mating import SurfaceHit,mate_pose,ray_hit,align_normals,planar_region


class SurfaceMateTests(unittest.TestCase):
    def test_box_faces_group_triangles_without_crossing_sharp_edges(self):
        mesh = make_box((10,20,30))
        for seed in range(12):
            region = planar_region(mesh,seed)
            self.assertEqual(len(region.triangles),2)
            self.assertEqual(region.boundary.shape,(8,3))
            self.assertIn(seed,region.triangles)
            other = next(i for i in region.triangles if i != seed)
            np.testing.assert_allclose(planar_region(mesh,other).center,region.center)
        np.testing.assert_allclose(planar_region(mesh,2).center,(0,0,15))

    def test_coplanar_islands_and_parallel_planes_stay_separate(self):
        first = make_box((10,10,2)).vertices[2:4].copy()
        island = first+np.array([30,0,0])
        upper = first+np.array([0,0,5])
        mesh = Mesh(np.concatenate((first,island,upper)))
        np.testing.assert_array_equal(planar_region(mesh,0).triangles,[0,1])
        np.testing.assert_array_equal(planar_region(mesh,2).triangles,[2,3])
        np.testing.assert_array_equal(planar_region(mesh,4).triangles,[4,5])

    def test_mixed_winding_group_and_area_center_ignore_tessellation(self):
        triangles = np.array([[[0,0,0],[4,0,0],[4,2,0]],[[0,0,0],[0,2,0],[4,2,0]]])
        mesh = Mesh(triangles)
        region = planar_region(mesh,0)
        self.assertEqual(len(region.triangles),2)
        np.testing.assert_allclose(region.center,(2,1,0))
        # An unequal split must weight areas rather than triangle centers equally.
        split = Mesh(np.array([[[0,0,0],[4,0,0],[1,1,0]],
                               [[4,0,0],[0,4,0],[1,1,0]],
                               [[0,4,0],[0,0,0],[1,1,0]]]))
        np.testing.assert_allclose(planar_region(split,0).center,(4/3,4/3,0))

    def test_cylinder_cap_is_one_region_but_curved_wall_stays_faceted(self):
        mesh = make_cylinder(20,40,segments=24)
        self.assertEqual(len(planar_region(mesh,3).triangles),24)
        wall = planar_region(mesh,0)
        self.assertEqual(len(wall.triangles),2)
        self.assertEqual(wall.boundary.shape,(8,3))

    def test_contact_opposed_normals_preserves_shape_scale_pivot_and_origin(self):
        source = SceneObject('Source',make_box((2,3,4)),Pose((10,20,30),(13,27,59),(4,5,6)),
                             (10,20,30),origin_source=(.1,.2,.3))
        target = SceneObject('Target',make_box((100,200,300)),Pose((800,900,1000),(11,22,33)),locked=True)
        a,b = SurfaceHit(source.id,2,(.2,-.3,2)),SurfaceHit(target.id,2,(10,-20,150))
        original = source.matrix().copy()
        target_matrix = target.matrix().copy()
        for flip in (False,True):
            for offset in (0,12.5,-7):
                with self.subTest(flip=flip,offset=offset):
                    pose = mate_pose(source,a,target,b,offset,flip,35)
                    moved = replace(source,pose=pose)
                    np.testing.assert_allclose(a.world_point(moved),b.world_point(target)+b.world_normal(target)*offset,atol=1e-9)
                    np.testing.assert_allclose(a.world_normal(moved),b.world_normal(target)*(1 if flip else -1),atol=1e-10)
                    np.testing.assert_allclose(moved.matrix()[:3,:3].T@moved.matrix()[:3,:3],original[:3,:3].T@original[:3,:3],atol=1e-10)
                    self.assertEqual(pose.pivot,source.pose.pivot)
                    self.assertEqual(moved.origin_source,source.origin_source)
        np.testing.assert_array_equal(source.matrix(),original)
        np.testing.assert_array_equal(target.matrix(),target_matrix)

    def test_rotated_parent_frames_and_antiparallel_normals(self):
        source = make_draft('source','a','fixture_a',primitive_spec('box',(100,100,100)),
                            Pose((10,20,30),(30,60,90),(5,6,7)),Pose((100,200,300),(10,20,30)).matrix().tolist())
        target = make_draft('target','b','fixture_b',primitive_spec('box',(200,200,200)),
                            Pose((-20,50,70),(60,20,10)),Pose((-100,500,600),(40,50,60)).matrix().tolist())
        a,b = SurfaceHit(source.id,0,(10,20,-50)),SurfaceHit(target.id,2,(30,40,100))
        moved = replace(source,pose=mate_pose(source,a,target,b))
        np.testing.assert_allclose(a.world_point(moved),b.world_point(target),atol=1e-9)
        np.testing.assert_allclose(a.world_normal(moved),-b.world_normal(target),atol=1e-10)
        for normal in ([1,0,0],[0,1,0],[0,0,1]):
            rotation = align_normals(normal,-np.array(normal))
            np.testing.assert_allclose(rotation@normal,-np.array(normal),atol=1e-12)
            self.assertAlmostEqual(np.linalg.det(rotation),1)

    def test_ray_triangle_point_with_rotated_scaled_object(self):
        obj = SceneObject('Source',make_box((2,4,6)),Pose((10,20,30),(30,40,50)),(10,20,30))
        matrix = obj.matrix()
        near = (matrix@np.array([.2,-.3,10,1]))[:3]
        far = (matrix@np.array([.2,-.3,-10,1]))[:3]
        hits = [ray_hit(obj,i,near,far) for i in (2,3)]
        hit = next(hit for hit in hits if hit is not None)
        np.testing.assert_allclose(hit.point,(.2,-.3,3),atol=1e-10)
        self.assertIsNone(ray_hit(obj,-1,near,far))

    def test_invalid_source_and_normals_are_rejected(self):
        obj = SceneObject('Source',make_box((10,10,10)))
        target = SceneObject('Target',make_box((10,10,10)))
        a,b = SurfaceHit(obj.id,2,(0,0,5)),SurfaceHit(target.id,2,(0,0,5))
        obj.locked = True
        with self.assertRaisesRegex(ValueError,'Unlock'):
            mate_pose(obj,a,target,b)
        obj.locked = False
        with self.assertRaises(ValueError):
            mate_pose(obj,a,obj,a)
        with self.assertRaises(ValueError):
            mate_pose(obj,a,target,b,float('nan'))
        with self.assertRaises(ValueError):
            align_normals([0,0,0],[0,0,1])


if __name__ == '__main__':
    unittest.main()
