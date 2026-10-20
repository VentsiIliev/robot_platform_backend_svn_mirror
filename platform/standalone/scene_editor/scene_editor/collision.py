"""Validated collision drafts and ROS-boundary data, with no Qt/ROS imports."""
import re

import numpy as np

from .geometry import mesh_from_primitive
from .model import Pose, SceneObject, vector


def frame_name(value):
    if not isinstance(value, str):
        raise ValueError('Reference frame must be a string.')
    value = value.strip().lstrip('/')
    if not value or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_/]*', value):
        raise ValueError('Reference frame must be a nonempty ROS frame name without spaces.')
    return value


def object_id(value):
    if not isinstance(value, str) or not value.strip() or value != value.strip() or any(ord(c) < 32 for c in value):
        raise ValueError('Collision ID must be nonempty, without surrounding whitespace or control characters.')
    return value


def validate_metadata(value):
    if not isinstance(value, dict):
        raise ValueError('Collision metadata must be an object.')
    matrix = np.asarray(value['frame_to_editor'], dtype=float)
    if matrix.shape != (4, 4) or not np.isfinite(matrix).all():
        raise ValueError('Invalid collision preview frame transform.')
    if not np.allclose(matrix[3], (0, 0, 0, 1)) or not np.allclose(matrix[:3,:3].T @ matrix[:3,:3], np.eye(3), atol=1e-7) or not np.isclose(np.linalg.det(matrix[:3,:3]), 1):
        raise ValueError('Collision preview frame transform must be rigid.')
    return dict(object_id=object_id(value['object_id']), frame=frame_name(value['frame']),
                editor_frame=frame_name(value['editor_frame']), frame_to_editor=matrix.tolist())


def primitive_spec(kind, dimensions):
    dimensions = vector(dimensions, 'Dimensions', {'box':3, 'cylinder':2, 'sphere':1}.get(kind, 0))
    if min(dimensions, default=0) <= 0:
        raise ValueError('Every dimension must be greater than zero.')
    if kind == 'box':
        return {'kind':'box', 'size_mm':list(dimensions)}
    if kind == 'cylinder':
        return {'kind':'cylinder', 'radius_mm':dimensions[0], 'length_mm':dimensions[1]}
    if kind == 'sphere':
        return {'kind':'sphere', 'radius_mm':dimensions[0]}
    raise ValueError('Choose a box, cylinder or sphere.')


def make_draft(identifier, frame, editor_frame, spec, pose=None, frame_to_editor=None):
    return SceneObject('Collision: '+object_id(identifier), mesh_from_primitive(spec), pose or Pose(),
                       color=(.25,.7,.85,.7), collision=dict(object_id=identifier, frame=frame,
                       editor_frame=editor_frame, frame_to_editor=np.eye(4).tolist() if frame_to_editor is None else frame_to_editor))


def request_for(obj, operation):
    if operation not in ('add', 'update', 'remove') or obj.collision is None:
        raise ValueError('Select an authored collision primitive and an Add, Update or Remove action.')
    metadata = validate_metadata(obj.collision)
    result = dict(operation=operation, object_id=metadata['object_id'], frame=metadata['frame'])
    if operation != 'remove':
        if obj.mesh.primitive is None or obj.unit_scale != (1.,1.,1.):
            raise ValueError('Only unscaled box, cylinder and sphere drafts can be applied.')
        spec = obj.mesh.primitive
        kind = spec['kind']
        dimensions = spec['size_mm'] if kind == 'box' else ([spec['radius_mm'],spec['length_mm']] if kind == 'cylinder' else [spec['radius_mm']])
        result.update(primitive=primitive_spec(kind, dimensions), pose_mm=obj.pose.matrix().tolist(), color=list(obj.color))
    return result


def validate_request(data):
    operation = data.get('operation')
    if operation == 'resolve':
        return dict(operation=operation, frame=frame_name(data['frame']), editor_frame=frame_name(data['editor_frame']))
    if operation not in ('add', 'update', 'remove'):
        raise ValueError('Unsupported collision operation.')
    result = dict(operation=operation, object_id=object_id(data['object_id']), frame=frame_name(data['frame']))
    if operation != 'remove':
        spec = data['primitive']
        kind = spec['kind']
        if kind == 'box':
            dimensions = spec['size_mm']
        elif kind == 'cylinder':
            dimensions = [spec['radius_mm'], spec['length_mm']]
        elif kind == 'sphere':
            dimensions = [spec['radius_mm']]
        else:
            raise ValueError('Unsupported primitive.')
        matrix = data['pose_mm']
        validate_metadata(dict(object_id=result['object_id'], frame=result['frame'], editor_frame=result['frame'], frame_to_editor=matrix))
        color = vector(data['color'], 'Color', 4)
        if min(color) < 0 or max(color) > 1:
            raise ValueError('Color must be in the range 0–1.')
        result.update(primitive=primitive_spec(kind, dimensions), pose_mm=matrix, color=color)
    return result
