"""Ordered preview diagnostics do not execute or alter robot trajectories."""
import importlib.util
from pathlib import Path
from types import SimpleNamespace as NS
import unittest
import ast

root=Path(__file__).resolve().parents[1]
module_path=root/'scripts/motion/scheduling/ordered_preview.py'
if not module_path.exists():
    module_path=root/'motion/scheduling/ordered_preview.py'
spec=importlib.util.spec_from_file_location('ordered_preview_under_test',module_path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def trajectory(count=4):
    return NS(joint_names=['j'],points=[NS(positions=[float(i)]) for i in range(count)])


class PreviewStateTests(unittest.TestCase):
    def setUp(self):
        self.messages=[]
        self.preview=module.PreviewState(lambda p,s,t:self.messages.append((p,s,t)),frame='base',tip='tip')

    def test_publish_before_execution_with_robot_start_state(self):
        state=NS(joint_state=NS(name=['j','other'],position=[0.,1.]))
        self.preview.planning(0,{'label':'first'},state)
        planned=trajectory()
        self.preview.planned(0,{'label':'first','trajectory':planned})
        packet,start,trajectories=self.messages[-1]
        self.assertEqual(packet['segments'][0]['state'],'ready')
        self.assertEqual(packet['start_joints'],{'j':0.,'other':1.})
        self.assertIs(start,state)
        self.assertIs(trajectories[0],planned)
        self.assertEqual(planned.points[0].positions,[0.])

    def test_failure_retains_prior_plan_and_exact_member_context(self):
        self.preview.planned(0,{'trajectory':trajectory()})
        self.preview.planning(1,{'label':'bad target'},None)
        self.preview.failed(1,'IK failed',target=[10,20,30,0,0,0])
        self.preview.failed(0,'group failed',scope='planning_group')
        packet=self.messages[-1][0]
        self.assertEqual(packet['failure']['index'],1)
        self.assertEqual(packet['failure']['target_xyz_mm'],[10,20,30])
        self.assertFalse(packet['failure']['exact_location'])
        self.assertTrue(packet['segments'][0]['positions'])
        self.assertEqual(packet['phase'],'planning_failed')

    def test_execution_failure_status_and_snapshot_immutability(self):
        self.preview.planned(0,{'trajectory':trajectory()})
        previous=self.messages[-1][0]
        self.preview.status({'phase':'executing','current_segment_index':0})
        self.preview.status({'phase':'segment_failed','current_segment_index':0,'result':-3})
        packet=self.messages[-1][0]
        self.assertEqual(previous['segments'][0]['state'],'ready')
        self.assertEqual(packet['segments'][0]['state'],'failed')
        self.assertEqual(packet['failure']['scope'],'execution')
        self.assertIsNone(packet['failure']['target_xyz_mm'])

    def test_sampling_keeps_endpoints_and_cancel_clears_paths(self):
        self.preview.planned(0,{'trajectory':trajectory(5000)})
        segment=self.messages[-1][0]['segments'][0]
        self.assertLessEqual(len(segment['positions']),512)
        self.assertEqual(segment['positions'][0],[0.])
        self.assertEqual(segment['positions'][-1],[4999.])
        self.preview.status({'phase':'stopped'})
        self.assertEqual(self.messages[-1][0]['segments'],[])
        self.assertEqual(self.messages[-1][2],[])

    def test_noop_has_no_duplicate_path_and_observer_failure_does_not_raise(self):
        self.preview.planned(0,{'trajectory':None})
        self.assertFalse(self.messages)
        broken=NS(planned=lambda *a:(_ for _ in ()).throw(RuntimeError('transport broken')))
        module.observe(broken,'planned',0,{'trajectory':trajectory()})

    def test_plan_identity_changes_between_chains(self):
        other=module.PreviewState(lambda *a:None,frame='base',tip='tip')
        self.assertNotEqual(other.packet['plan_id'],self.preview.packet['plan_id'])

    def test_real_backend_wrapper_rethrows_original_failure_with_member_target(self):
        backend_path=root/'scripts/backend/moveit_robot_backend.py'
        if not backend_path.exists():
            backend_path=root/'backend/moveit_robot_backend.py'
        tree=ast.parse(backend_path.read_text())
        callback=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)
                      and n.name=='plan_ordered_segment_callback')
        original=RuntimeError('collision check rejected')
        def raw(*args,**kwargs):
            raise original
        namespace=dict(raw_plan_ordered_segment_callback=raw,preview=self.preview,observe=module.observe,
                       self=NS(apply_workobject=lambda pose,**kw:[pose[0]+100,*pose[1:]]),user=2)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[callback],type_ignores=[])),str(backend_path),'exec'),namespace)
        with self.assertRaises(RuntimeError) as failure:
            namespace['plan_ordered_segment_callback'](3,{'position':[1,2,3,0,0,0]},[0]*6,None)
        self.assertIs(failure.exception,original)
        packet=self.messages[-1][0]
        self.assertEqual(packet['failure']['index'],3)
        self.assertEqual(packet['failure']['target_xyz_mm'],[101,2,3])

    def test_ros_topics_are_visualization_only(self):
        from unittest.mock import patch
        import sys
        class Message:
            def __init__(self,**kwargs):
                self.__dict__.update(kwargs)
                self.trajectory=[]
        messages={}
        def publisher(cls,topic,qos):
            messages[topic]=[]
            return NS(publish=messages[topic].append)
        fake_modules={'std_msgs.msg':NS(String=Message),'moveit_msgs.msg':NS(DisplayTrajectory=Message,RobotTrajectory=Message),
                      'rclpy.qos':NS(QoSProfile=lambda **kw:kw,DurabilityPolicy=NS(TRANSIENT_LOCAL=1),ReliabilityPolicy=NS(RELIABLE=1))}
        with patch.dict(sys.modules,fake_modules):
            transport=module.RosPreviewTransport(NS(create_publisher=publisher,
                context=NS(on_shutdown=lambda cb:None),get_logger=lambda:NS(warning=lambda text:None)))
            try:
                transport.send({'version':1,'plan_id':'test'},None,[trajectory()])
                transport.pool.submit(lambda:None).result(timeout=5)
                self.assertEqual(set(messages),{'/ordered_motion/preview','/ordered_motion/display_planned_path'})
                self.assertIn('test',messages['/ordered_motion/preview'][0].data)
                display=messages['/ordered_motion/display_planned_path'][0]
                self.assertEqual(display.trajectory[0].joint_trajectory.joint_names,['j'])
            finally:
                transport.close()


if __name__=='__main__':
    unittest.main()
