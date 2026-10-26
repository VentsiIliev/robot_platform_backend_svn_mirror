import json
import unittest
from unittest.mock import Mock

import numpy as np
from scipy.interpolate import PPoly
from src.applications.image_capture.processing.sampled_path import build_sampled_result
from src.robot_systems.paint.processes.paint.planning.contours.interpolation import resample_contour_xy


class SampledPathTests(unittest.TestCase):
    def circle(self):
        a=np.linspace(0,2*np.pi,100,endpoint=False)
        return {'contours':[{'contour_index':0,'status':'ok','tolerance_mm':.5,
                            'points':np.column_stack([30*np.cos(a),30*np.sin(a)]).tolist(),
                            'primitives':[{'type':'arc','center':[0,0],'radius':30,
                                           'start_deg':0,'sweep_deg':360}]}]}

    def test_uses_paint_sampler_and_periodic_c2_curve(self):
        sampler=Mock(wraps=resample_contour_xy)
        raw,_=build_sampled_result(self.circle(),sampler)
        entry=json.loads(raw)['contours'][0]
        self.assertEqual(entry['status'],'ok')
        sampler.assert_called_once()
        self.assertEqual(sampler.call_args.kwargs,{'spacing':1.0,'closed':True})
        np.testing.assert_allclose(entry['points'][0],entry['points'][-1])
        spline=PPoly(np.asarray(entry['spline_coefficients']),np.asarray(entry['spline_knots']))
        first,last=entry['spline_knots'][0],entry['spline_knots'][-1]
        for derivative in (0,1,2):
            np.testing.assert_allclose(spline(first,nu=derivative),spline(last,nu=derivative),atol=1e-8)
        for i in range(1,len(spline.x)-1):
            span=spline.x[i]-spline.x[i-1]
            left=3*spline.c[0,i-1]*span**2+2*spline.c[1,i-1]*span+spline.c[2,i-1]
            np.testing.assert_allclose(left,spline.c[2,i],atol=1e-8)
        self.assertGreater(entry['minimum_evaluated_speed'],.9)
        self.assertLessEqual(entry['max_segment_mm'],1.00001)

    def test_geometry_failure_is_visible_not_silently_accepted(self):
        doc=self.circle();doc['contours'][0]['primitives'][0]['radius']=32
        raw,_=build_sampled_result(doc,resample_contour_xy)
        self.assertEqual(json.loads(raw)['contours'][0]['status'],'outside_tolerance')

    def test_failed_and_empty_contours_are_reported(self):
        raw,_=build_sampled_result({'contours':[]},resample_contour_xy)
        self.assertEqual(json.loads(raw)['contours'],[])
        raw,_=build_sampled_result({'contours':[{'contour_index':0,'status':'error'}]},resample_contour_xy)
        self.assertEqual(json.loads(raw)['contours'][0]['status'],'error')
