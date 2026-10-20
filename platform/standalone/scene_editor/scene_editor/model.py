"""Scene coordinates are mm. Rotations use Rz(yaw) @ Ry(pitch) @ Rx(roll)."""
from dataclasses import dataclass, field, replace
from pathlib import Path
import json
import hashlib
import os
import tempfile
import uuid

import numpy as np

from .geometry import Mesh, export_stl, mesh_from_primitive, read_stl


def vector(value, label, length=3):
    if not isinstance(value, (list, tuple, np.ndarray)) or len(value) != length:
        raise ValueError(f'{label} must have {length} components.')
    if any(isinstance(component, bool) for component in value):
        raise ValueError(f'{label} must contain numbers.')
    result = tuple(float(component) for component in value)
    if not np.isfinite(result).all():
        raise ValueError(f'{label} must contain finite numbers.')
    return result


def rotation_matrix(degrees):
    x, y, z = np.radians(degrees)
    sx, sy, sz = np.sin([x,y,z]); cx, cy, cz = np.cos([x,y,z])
    return np.array([[cz*cy,cz*sy*sx-sz*cx,cz*sy*cx+sz*sx],
                     [sz*cy,sz*sy*sx+cz*cx,sz*sy*cx-cz*sx],[-sy,cy*sx,cy*cx]],dtype=float)


def euler_degrees(matrix):
    r = np.asarray(matrix)[:3,:3]
    pitch = np.arctan2(-r[2,0], np.hypot(r[0,0],r[1,0]))
    if np.hypot(r[0,0],r[1,0]) > 1e-9:
        roll, yaw = np.arctan2(r[2,1],r[2,2]), np.arctan2(r[1,0],r[0,0])
    else:
        roll, yaw = np.arctan2(-r[1,2],r[1,1]), 0
    return tuple(np.degrees([roll,pitch,yaw]))


@dataclass(frozen=True)
class Pose:
    translation: tuple = (0.,0.,0.)
    rotation: tuple = (0.,0.,0.)
    pivot: tuple = (0.,0.,0.)

    def __post_init__(self):
        for name in ('translation','rotation','pivot'):
            object.__setattr__(self, name, vector(getattr(self,name),name))

    def matrix(self):
        result = np.eye(4)
        result[:3,:3] = rotation_matrix(self.rotation)
        pivot = np.asarray(self.pivot)
        result[:3,3] = np.asarray(self.translation) + pivot - result[:3,:3] @ pivot
        return result

    def with_pivot(self, pivot):
        """Changing the editing pivot must not move geometry already in place."""
        pivot = np.asarray(vector(pivot,'pivot'))
        matrix = self.matrix()
        translation = matrix[:3,3] - pivot + matrix[:3,:3] @ pivot
        return replace(self, translation=tuple(translation), pivot=tuple(pivot))


@dataclass(eq=False)
class SceneObject:
    name: str
    mesh: Mesh
    pose: Pose = field(default_factory=Pose)
    unit_scale: tuple = (1.,1.,1.)
    color: tuple = (0.65,0.55,0.77,1.)
    visible: bool = True
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    collision: dict | None = None
    locked: bool = False

    def __post_init__(self):
        self.unit_scale = vector(self.unit_scale,'mesh unit scale')
        if min(self.unit_scale) <= 0: raise ValueError('Mesh unit scales must be positive.')
        self.color = vector(self.color,'color',4)
        if min(self.color) < 0 or max(self.color) > 1: raise ValueError('Color components must be between 0 and 1.')
        if not isinstance(self.visible,bool): raise ValueError('Visibility must be boolean.')
        if not isinstance(self.locked,bool): raise ValueError('Object lock state must be boolean.')
        if not isinstance(self.name,str) or not isinstance(self.id,str) or not self.id:
            raise ValueError('Object names and IDs must be strings; IDs cannot be empty.')
        if self.collision is not None:
            from .collision import validate_metadata
            self.collision = validate_metadata(self.collision)

    def matrix(self):
        return self.parent_matrix() @ self.pose.matrix() @ np.diag([*self.unit_scale,1.])

    def parent_matrix(self):
        return np.asarray(self.collision['frame_to_editor'], dtype=float) if self.collision else np.eye(4)

    def local_center(self):
        return self.mesh.bounds.mean(axis=0) * self.unit_scale

    def world_pivot(self):
        local = np.asarray(self.pose.translation) + self.pose.pivot
        parent = self.parent_matrix()
        return parent[:3,:3] @ local + parent[:3,3]

    def world_bounds(self):
        low, high = self.mesh.bounds
        corners = np.array([[x,y,z] for x in (low[0],high[0]) for y in (low[1],high[1]) for z in (low[2],high[2])])
        matrix = self.matrix()
        corners = corners @ matrix[:3,:3].T + matrix[:3,3]
        return np.array([corners.min(axis=0),corners.max(axis=0)])

    def world_origin(self):
        """Source geometry's local (0, 0, 0), distinct from its editing pivot."""
        return self.matrix()[:3,3].copy()

    def pose_snapped_to(self, target):
        """Translate source origin onto target origin, retaining orientation."""
        if self.locked:
            raise ValueError('Unlock the source object before snapping it.')
        delta = target.world_origin() - self.world_origin()
        local_delta = self.parent_matrix()[:3,:3].T @ delta
        return replace(self.pose, translation=tuple(np.asarray(self.pose.translation)+local_delta))


@dataclass
class Scene:
    objects: list = field(default_factory=list)
    reference_frame: str | None = None

    def bounds(self):
        visible = [obj.world_bounds() for obj in self.objects if obj.visible]
        if not visible: return np.array([[-100.,-100.,-100.],[100.,100.,100.]])
        return np.array([np.min([b[0] for b in visible],axis=0),np.max([b[1] for b in visible],axis=0)])


def translated_poses(objects, delta):
    """Move a complete selection by one world-space mm vector, preserving offsets."""
    delta = np.asarray(vector(delta, 'Group translation'), dtype=float)
    objects = list(objects)
    if any(obj.locked for obj in objects):
        raise ValueError('Unlock or deselect locked objects before moving the group.')
    return {obj.id: replace(obj.pose, translation=tuple(np.asarray(obj.pose.translation)+obj.parent_matrix()[:3,:3].T @ delta))
            for obj in objects}


def save_scene(scene, destination):
    destination = Path(destination).resolve()
    if any(obj.mesh.source == destination for obj in scene.objects):
        raise ValueError('Save the scene to a separate file; source meshes cannot be overwritten.')
    objects = []
    generated_assets = {}
    for obj in scene.objects:
        if obj.mesh.source:
            geometry = {'stl': os.path.relpath(obj.mesh.source, destination.parent)}
        elif obj.mesh.primitive:
            geometry = {'primitive': obj.mesh.primitive}
        else:
            # ROS meshes have no source file. Persist a full-resolution companion
            # asset so snapshots survive after the ROS session cache is removed.
            asset = generated_assets.get(obj.mesh)
            if asset is None:
                vertices = np.ascontiguousarray(obj.mesh.vertices)
                digest = hashlib.sha256(memoryview(vertices).cast('B')).hexdigest()
                assets = destination.parent / (destination.stem + '.assets')
                assets.mkdir(exist_ok=True)
                asset = assets / (digest + '.stl')
                if not asset.exists():
                    export_stl(obj.mesh, np.eye(4), asset)
                generated_assets[obj.mesh] = asset
            geometry = {'stl': os.path.relpath(asset, destination.parent)}
        objects.append({'id':obj.id,'name':obj.name,'geometry':geometry,'unit_scale_to_mm':obj.unit_scale,
                        'translation_mm':obj.pose.translation,'rotation_deg':obj.pose.rotation,'pivot_mm':obj.pose.pivot,
                        'color':obj.color,'visible':obj.visible, 'collision':obj.collision, 'locked':obj.locked})
    payload = {'format':'standalone-scene-editor','version':1,'units':'mm','rotation_order':'Rz Ry Rx','objects':objects, 'reference_frame':scene.reference_frame}
    descriptor, temporary = tempfile.mkstemp(prefix='.scene-',dir=destination.parent)
    try:
        with os.fdopen(descriptor,'w',encoding='utf-8') as stream:
            json.dump(payload,stream,indent=2,allow_nan=False); stream.write('\n');stream.flush();os.fsync(stream.fileno())
        os.replace(temporary,destination)
    finally:
        Path(temporary).unlink(missing_ok=True)


def load_scene(path):
    path = Path(path).resolve()
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload,dict) or payload.get('format') != 'standalone-scene-editor' or payload.get('version') != 1:
        raise ValueError('Unsupported scene file format or version.')
    if payload.get('units') != 'mm' or payload.get('rotation_order') != 'Rz Ry Rx':
        raise ValueError('Unsupported scene units or rotation convention.')
    rows = payload.get('objects')
    if not isinstance(rows,list): raise ValueError('Scene objects must be a list.')
    scene, cache, ids = Scene(), {}, set()
    if payload.get('reference_frame') is not None:
        from .collision import frame_name
        scene.reference_frame = frame_name(payload['reference_frame'])
    for row in rows:
        geometry = row['geometry']
        if 'stl' in geometry:
            source = (path.parent / geometry['stl']).resolve()
            if source not in cache: cache[source] = read_stl(source)
            mesh = cache[source]
        else:
            mesh = mesh_from_primitive(geometry['primitive'])
        obj = SceneObject(name=row['name'],mesh=mesh,id=row['id'],
            pose=Pose(row['translation_mm'],row['rotation_deg'],row['pivot_mm']),
            unit_scale=row['unit_scale_to_mm'],color=row['color'],visible=row['visible'], collision=row.get('collision'), locked=row.get('locked',False))
        if obj.id in ids: raise ValueError('Scene object IDs must be unique.')
        ids.add(obj.id);scene.objects.append(obj)
    return scene
