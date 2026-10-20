"""Mesh face picking and rigid surface mating, independent of Qt and ROS."""
from dataclasses import dataclass
import math
import numpy as np

from .model import Pose,euler_degrees


@dataclass(eq=False,frozen=True)
class PlanarRegion:
    triangles: np.ndarray
    boundary: np.ndarray
    center: tuple


def planar_region(mesh,seed):
    """Connected, coplanar triangles; sharp edges and separate islands stay apart.

    All comparisons use the seed plane, avoiding gradual growth around curves.
    Vertex welding tolerates floating-point STL noise, not mechanical gaps.
    """
    if not 0 <= seed < len(mesh.vertices):
        raise ValueError('Invalid surface triangle.')
    normal = unit(mesh.normals[seed])
    tolerance = max(float(np.linalg.norm(mesh.bounds[1]-mesh.bounds[0]))*1e-7,1e-9)
    candidates = np.flatnonzero(np.abs(mesh.normals@normal) >= math.cos(math.radians(.1)))
    plane = mesh.vertices[seed,0].astype(float)
    distance = np.max(np.abs((mesh.vertices[candidates].astype(float)-plane)@normal),axis=1)
    candidates = candidates[distance <= tolerance]
    vertices = mesh.vertices[candidates].astype(float)
    _,welded = np.unique(np.rint((vertices.reshape(-1,3)-mesh.bounds[0])/tolerance).astype(np.int64),axis=0,return_inverse=True)
    welded = welded.reshape(-1,3)
    edges = np.sort(welded[:,[(0,1),(1,2),(2,0)]].reshape(-1,2),axis=1)
    _,inverse = np.unique(edges,axis=0,return_inverse=True)
    owners = {}
    for edge,triangle in zip(inverse,np.repeat(np.arange(len(candidates)),3)):
        owners.setdefault(int(edge),[]).append(int(triangle))
    selected = {int(np.flatnonzero(candidates == seed)[0])}
    pending = list(selected)
    while pending:
        triangle = pending.pop()
        for edge in inverse[triangle*3:triangle*3+3]:
            for other in owners[int(edge)]:
                if other not in selected:
                    selected.add(other)
                    pending.append(other)
    chosen = np.array(sorted(selected),dtype=int)
    indices = candidates[chosen]
    triangles = mesh.vertices[indices].astype(float)
    weights = np.linalg.norm(np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0]),axis=1)
    center = np.average(triangles.mean(axis=1),axis=0,weights=weights)
    counts = np.bincount(inverse.reshape(-1,3)[chosen].ravel(),minlength=len(owners))
    boundary = []
    for local,triangle in zip(chosen,triangles):
        for edge,pair in zip(inverse[local*3:local*3+3],((0,1),(1,2),(2,0))):
            if counts[edge] == 1:
                boundary.extend(triangle[list(pair)])
    return PlanarRegion(indices,np.asarray(boundary).reshape(-1,3),tuple(center))


def unit(value):
    value = np.asarray(value,dtype=float)
    length = np.linalg.norm(value)
    if not np.isfinite(length) or length < 1e-12:
        raise ValueError('The selected triangle has no usable surface normal.')
    return value/length


@dataclass(frozen=True)
class SurfaceHit:
    object_id: str
    triangle: int
    point: tuple  # Native mesh coordinates, before units/pose/parent transforms.
    region: PlanarRegion | None = None

    def world_point(self,obj):
        return (obj.matrix() @ np.r_[self.point,1.])[:3]

    def world_normal(self,obj):
        normal = obj.mesh.normals[self.triangle]
        return unit(np.linalg.solve(obj.matrix()[:3,:3].T,normal))


def ray_hit(obj,triangle,near,far):
    """Intersect a GPU-picked triangle exactly along the clicked pixel ray."""
    if not 0 <= triangle < len(obj.mesh.vertices):
        return None
    inverse = np.linalg.inv(obj.matrix())
    origin = (inverse @ np.r_[near,1.])[:3]
    direction = unit((inverse @ np.r_[far,1.])[:3]-origin)
    a,b,c = obj.mesh.vertices[triangle].astype(float)
    edge1,edge2 = b-a,c-a
    cross = np.cross(direction,edge2)
    determinant = float(edge1@cross)
    if abs(determinant) < max(np.linalg.norm(edge1)*np.linalg.norm(edge2)*1e-12,1e-30):
        return None
    delta = origin-a
    u = float(delta@cross)/determinant
    q = np.cross(delta,edge1)
    v = float(direction@q)/determinant
    t = float(edge2@q)/determinant
    if u < -1e-5 or v < -1e-5 or u+v > 1+1e-5 or t < 0:
        return None
    return SurfaceHit(obj.id,triangle,tuple(origin+t*direction))


def axis_rotation(axis,angle):
    axis = unit(axis)
    x,y,z = axis
    cross = np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    return np.eye(3)+math.sin(angle)*cross+(1-math.cos(angle))*(cross@cross)


def align_normals(source,target):
    a,b = unit(source),unit(target)
    cross = np.cross(a,b)
    sine,cosine = np.linalg.norm(cross),float(np.clip(a@b,-1,1))
    if sine < 1e-10:
        if cosine > 0:
            return np.eye(3)
        perpendicular = np.cross(a,np.eye(3)[np.argmin(np.abs(a))])
        return axis_rotation(perpendicular,math.pi)
    return axis_rotation(cross,math.atan2(sine,cosine))


def mate_pose(source,source_hit,target,target_hit,offset_mm=0.,flip=False,twist_deg=0.):
    """Coincide picked points and oppose face normals with a rigid transform."""
    if source.locked:
        raise ValueError('Unlock the moving object before mating surfaces.')
    if source.id == target.id or source_hit.object_id != source.id or target_hit.object_id != target.id:
        raise ValueError('Pick surfaces on two different objects.')
    offset_mm,twist_deg = float(offset_mm),float(twist_deg)
    if not np.isfinite([offset_mm,twist_deg]).all():
        raise ValueError('Mate offset and rotation must be finite.')
    target_normal = target_hit.world_normal(target)
    destination_normal = target_normal if flip else -target_normal
    rotation = axis_rotation(target_normal,math.radians(twist_deg)) @ align_normals(source_hit.world_normal(source),destination_normal)
    transform = np.eye(4)
    transform[:3,:3] = rotation
    transform[:3,3] = target_hit.world_point(target)+target_normal*offset_mm-rotation@source_hit.world_point(source)
    # Strip the parent and source-unit transforms, preserving the editing pivot.
    local = np.linalg.solve(source.parent_matrix(),transform@source.matrix()) @ np.diag([*(1/np.asarray(source.unit_scale)),1.])
    pivot = np.asarray(source.pose.pivot)
    translation = local[:3,3]-pivot+local[:3,:3]@pivot
    return Pose(tuple(translation),euler_degrees(local),source.pose.pivot)
