"""Read-only ordered-motion preview protocol and URDF forward kinematics."""
import math
import xml.etree.ElementTree as ET

import numpy as np

from .urdf import _origin


COLORS = {'ready':(.45,.35,1.,.85),'executing':(1.,.75,.1,1.),
          'done':(.2,.75,.4,.65),'failed':(1.,.15,.15,1.)}


class UrdfKinematics:
    def __init__(self,xml):
        root = ET.fromstring(xml)
        self.joints = {}
        self.names = {}
        for joint in root.findall('joint'):
            child,parent = joint.find('child'),joint.find('parent')
            if child is None or parent is None:
                raise ValueError('Joint missing parent/child')
            self.joints[child.get('link')] = joint
            self.names[joint.get('name')] = joint

    def _position(self,joint,positions,seen=()):
        name = joint.get('name')
        if name in seen:
            raise ValueError('Cyclic mimic joint')
        mimic = joint.find('mimic')
        if mimic is not None:
            source = self.names[mimic.get('joint')]
            return self._position(source,positions,(*seen,name))*float(mimic.get('multiplier','1'))+float(mimic.get('offset','0'))
        if name not in positions:
            raise ValueError(f'Preview missing joint position: {name}')
        return float(positions[name])

    def tip(self,base,tip,positions,tool=None):
        chain,seen = [],set()
        while tip != base:
            if tip in seen or tip not in self.joints:
                raise ValueError(f'No URDF chain from {base} to {tip}')
            seen.add(tip)
            joint = self.joints[tip]
            chain.append(joint)
            tip = joint.find('parent').get('link')
        result = np.eye(4)
        for joint in reversed(chain):
            result = result @ _origin(joint.find('origin'))
            kind = joint.get('type')
            if kind == 'fixed':
                continue
            if kind not in ('revolute','continuous','prismatic'):
                raise ValueError(f'Unsupported preview joint type: {kind}')
            axis_spec = joint.find('axis')
            axis = np.array([float(x) for x in (axis_spec.get('xyz','1 0 0') if axis_spec is not None else '1 0 0').split()])
            if axis.shape != (3,) or not np.isfinite(axis).all() or np.linalg.norm(axis) < 1e-12:
                raise ValueError('Invalid URDF joint axis')
            axis /= np.linalg.norm(axis)
            value = self._position(joint,positions)
            motion = np.eye(4)
            if kind == 'prismatic':
                motion[:3,3] = axis*value*1000
            else:
                x,y,z = axis
                cross = np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
                motion[:3,:3] = np.eye(3)+math.sin(value)*cross+(1-math.cos(value))*(cross@cross)
            result = result @ motion
        if tool is not None:
            offset = np.array(tool,dtype=float)
            if offset.shape != (4,4) or not np.isfinite(offset).all():
                raise ValueError('Invalid preview TCP transform')
            offset[:3,3] *= 1000
            result = result @ offset
        if not np.isfinite(result).all():
            raise ValueError('Nonfinite preview pose')
        return result[:3,3]


class TrajectoryPreview:
    def __init__(self):
        self.packet = None
        self.kinematics = None
        self.cache = {}

    def description(self,xml):
        self.kinematics = UrdfKinematics(xml)
        self.cache.clear()

    def update(self,packet):
        if packet.get('version') != 1 or not isinstance(packet.get('plan_id'),str):
            raise ValueError('Unsupported ordered preview message')
        if self.packet and packet['plan_id'] == self.packet['plan_id'] and packet['revision'] <= self.packet['revision']:
            return
        if not isinstance(packet.get('segments'),list):
            raise ValueError('Invalid preview segments')
        if self.packet is None or packet['plan_id'] != self.packet['plan_id']:
            self.cache.clear()
        self.packet = packet

    def paths(self):
        if not self.packet or self.kinematics is None:
            return []
        packet = self.packet
        results = []
        for segment in packet['segments']:
            positions = segment.get('positions',[])
            names = segment.get('joint_names',[])
            if not positions:
                continue
            key = (packet['plan_id'],segment['index'])
            cached = self.cache.get(key)
            if cached is None or cached[0] != positions:
                points = []
                for row in positions:
                    if len(row) != len(names) or not np.isfinite(np.asarray(row,dtype=float)).all():
                        raise ValueError('Invalid preview joint sample')
                    joints = {**packet.get('start_joints',{}),**dict(zip(names,row))}
                    points.append(self.kinematics.tip(packet['frame_id'],packet['tip_frame'],joints,packet.get('tool_matrix')))
                cached = positions,np.array(points)
                self.cache[key] = cached
            results.append((segment,cached[1]))
        return results

    def summary(self):
        if not self.packet:
            return 'No ordered-motion preview received.'
        packet = self.packet
        states = ', '.join(f'{s["index"]+1}: {s.get("label", "")} [{s["state"]}]' for s in packet['segments'])
        text = f'Plan {packet["plan_id"][:8]} · {packet.get("phase", "")}\n{states}'
        failure = packet.get('failure')
        if failure:
            index = failure.get('index')
            text += '\nFailure'+(f' at segment {index+1}' if index is not None else '')+': '+failure.get('reason','')
            text += '\nExact failure location unavailable.'
            if failure.get('target_xyz_mm') is not None:
                text += ' Red marker shows the requested target, not a confirmed collision point.'
        return text
