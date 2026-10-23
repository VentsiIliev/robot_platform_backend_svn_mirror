"""Planned TCP paths are computed independently of live robot TF."""
from copy import deepcopy
from pathlib import Path
import sys
import tempfile
import unittest

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scene_editor.trajectory_preview import TrajectoryPreview,UrdfKinematics
from scene_editor.ros_scene import SceneAssembler

XML = '''<robot name="test"><link name="base"/><link name="arm"/><link name="tip"/>
<joint name="rotate" type="continuous"><parent link="base"/><child link="arm"/><axis xyz="0 0 1"/></joint>
<joint name="slide" type="prismatic"><parent link="arm"/><child link="tip"/><axis xyz="1 0 0"/>
<origin xyz="1 0 0"/></joint></robot>'''


def packet(plan='a',revision=1):
    return dict(version=1,plan_id=plan,revision=revision,frame_id='base',tip_frame='tip',
                phase='executing',start_joints={'slide':.2},tool_matrix=None,failure=None,
                segments=[dict(index=0,label='approach',state='ready',joint_names=['rotate'],positions=[[0],[np.pi/2]])])


class PreviewTests(unittest.TestCase):
    def test_fk_rotation_prismatic_offset_and_missing_joint(self):
        kinematics = UrdfKinematics(XML)
        np.testing.assert_allclose(kinematics.tip('base','tip',{'rotate':np.pi/2,'slide':.2}),[0,1200,0],atol=1e-10)
        tool = np.eye(4)
        tool[2,3] = .1
        np.testing.assert_allclose(kinematics.tip('base','tip',{'rotate':0,'slide':0},tool),[1000,0,100])
        with self.assertRaisesRegex(ValueError,'missing joint'):
            kinematics.tip('base','tip',{'rotate':0})

    def test_plans_revisions_late_description_and_replacement(self):
        preview = TrajectoryPreview()
        preview.update(packet())
        self.assertEqual(preview.paths(),[])
        preview.description(XML)
        segment,points = preview.paths()[0]
        np.testing.assert_allclose(points,[[1200,0,0],[0,1200,0]],atol=1e-10)
        preview.update(packet(revision=0))
        self.assertEqual(preview.packet['revision'],1)
        replacement = packet('b')
        replacement['segments'] = []
        preview.update(replacement)
        self.assertEqual(preview.paths(),[])

    def test_failure_target_is_explicitly_inexact_and_preserves_path(self):
        with tempfile.TemporaryDirectory() as directory:
            assembler = SceneAssembler('base',directory)
            assembler.preview.description(XML)
            failed = packet()
            failed['segments'][0]['state'] = 'failed'
            failed['failure'] = dict(index=0,reason='IK failed',target_xyz_mm=[200,300,400],exact_location=False)
            assembler.preview.update(failed)
            scene,warnings = assembler.build()
            self.assertFalse(warnings)
            self.assertEqual(len(scene.objects),2)
            self.assertIn('requested target',scene.objects[-1].name)
            self.assertEqual(scene.objects[-1].pose.translation,(200,300,400))
            self.assertIn('Exact failure location unavailable',assembler.preview.summary())
            self.assertIn('IK failed',assembler.preview.summary())
            self.assertTrue(all(obj.collision is None for obj in scene.objects))
            old_mesh = scene.objects[0].mesh
            self.assertIs(assembler.build()[0].objects[0].mesh,old_mesh)
            status_only = deepcopy(failed)
            status_only['revision'] = 2
            status_only['segments'][0]['state'] = 'done'
            assembler.preview.update(status_only)
            self.assertIs(assembler.build()[0].objects[0].mesh,old_mesh,'Status changes must reuse path mesh buffers')
            cleared = packet(revision=3)
            cleared['segments'] = []
            assembler.preview.update(cleared)
            self.assertFalse(assembler.build()[0].objects)

    def test_no_failure_marker_for_unknown_location(self):
        preview = TrajectoryPreview()
        failed = packet()
        failed['failure'] = dict(index=None,reason='drive disabled',target_xyz_mm=None)
        preview.update(failed)
        self.assertIn('drive disabled',preview.summary())
        self.assertIn('Exact failure location unavailable',preview.summary())

    def test_bad_joint_data_does_not_hide_live_scene(self):
        with tempfile.TemporaryDirectory() as directory:
            assembler = SceneAssembler('base',directory)
            assembler.preview.description(XML)
            bad = packet()
            bad['segments'][0]['positions'] = [[float('nan')]]
            assembler.preview.update(bad)
            scene,warnings = assembler.build()
            self.assertIn('Invalid preview joint sample',warnings[0])


if __name__ == '__main__':
    unittest.main()
