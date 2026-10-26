import unittest
import numpy as np
from src.applications.image_capture.processing.connected_fit import connect_primitives, scale_primitives
from src.applications.image_capture.processing.decompose import sample_primitive
from src.applications.image_capture.processing.decompose_contour import default_params, decompose_points


class ConnectedFitTests(unittest.TestCase):
    def test_shared_endpoints_close_every_join_including_wraparound(self):
        a=np.linspace(0,2*np.pi,120,endpoint=False)
        points=np.column_stack([50*np.cos(a),30*np.sin(a)])
        params=default_params()
        _,processed,primitives,_=decompose_points(points,params)
        joined=connect_primitives(processed,primitives,params.tol)
        samples=[sample_primitive(p) for p in joined]
        for i,sample in enumerate(samples):
            np.testing.assert_allclose(sample[-1], samples[(i+1)%len(samples)][0],atol=1e-8)
        for p in joined:
            self.assertEqual(p['within_tol'],p['max_err']<=params.tol)

    def test_scaling_preserves_angles_and_scales_lengths(self):
        original=[{'type':'arc','center':[2,3],'radius':4,'length':5,'max_err':.2,'start_deg':30,'sweep_deg':90}]
        scaled=scale_primitives(original,.3,np.array([100,200]))[0]
        self.assertAlmostEqual(scaled['radius'],1.2)
        self.assertEqual(scaled['sweep_deg'],90)
        self.assertEqual(original[0]['radius'],4)

    def test_refinement_checks_original_bump_hidden_by_smoothing(self):
        from src.applications.image_capture.processing.connected_fit import refit_original_contour, primitive_distances
        points=np.array([[0,0],[4,0],[5,2],[6,0],[10,0],[10,10],[0,10]],float)
        processed=np.array([[0,0],[10,0],[10,10],[0,10]],float)
        seeds=[{'start_idx':i} for i in range(4)]
        fitted=refit_original_contour(points,processed,seeds,.25)
        self.assertGreater(len(fitted),4)
        for i,p in enumerate(fitted):
            a,b=p['source_start_idx'],p['source_end_idx']
            if b<=a:b+=len(points)
            assigned=points[np.arange(a,b+1)%len(points)]
            self.assertLessEqual(primitive_distances(assigned,p).max(),.25+1e-9)
            self.assertTrue(p['within_tol'])
            np.testing.assert_allclose(sample_primitive(p)[-1],sample_primitive(fitted[(i+1)%len(fitted)])[0],atol=1e-8)

    def test_arc_distance_respects_finite_sweep(self):
        from src.applications.image_capture.processing.connected_fit import primitive_distances
        arc={'type':'arc','center':[0,0],'radius':1,'start_deg':0,'sweep_deg':90}
        distance=primitive_distances([[1,0],[0,1],[-1,0]],arc)
        np.testing.assert_allclose(distance,[0,0,np.sqrt(2)],atol=1e-9)
