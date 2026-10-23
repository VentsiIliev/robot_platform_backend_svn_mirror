"""ROS message → local scene conversion. No ROS, Qt or transport imports.

Message objects are duck typed so frame math and diff handling can be tested
without a ROS installation. Every coordinate crossing the boundary becomes mm.
"""
from dataclasses import dataclass, field, replace
from pathlib import Path
import time

import numpy as np

from .geometry import Mesh, make_box, make_cylinder, make_sphere, read_stl, combine_meshes
from .model import Pose, Scene, SceneObject, euler_degrees
from .urdf import load_urdf, resolve_mesh
from .trajectory_preview import TrajectoryPreview,COLORS


def pose_matrix(message):
    """ROS geometry_msgs/Pose (meters, quaternion) to a rigid mm matrix."""
    position = message.position if hasattr(message, 'position') else message.translation
    rotation = message.orientation if hasattr(message, 'orientation') else message.rotation
    quaternion = np.array([rotation.x, rotation.y, rotation.z, rotation.w], dtype=float)
    if not np.isfinite(quaternion).all():
        raise ValueError('Nonfinite ROS quaternion')
    length = np.linalg.norm(quaternion)
    # Some producers leave the identity orientation as four zeros.
    x, y, z, w = quaternion/length if length > 1e-12 else (0, 0, 0, 1)
    result = np.eye(4)
    result[:3, :3] = [
        [1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
        [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
        [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)],
    ]
    result[:3, 3] = np.array([position.x, position.y, position.z])*1000
    if not np.isfinite(result).all():
        raise ValueError('Nonfinite ROS position')
    return result


def matrix_pose(matrix):
    return Pose(tuple(matrix[:3, 3]), euler_degrees(matrix))


class FrameGraph:
    """Latest parent→child transforms, with lookup through their common ancestor."""
    def __init__(self):
        self.edges = {}

    def update(self, transforms):
        for transform in transforms:
            parent = transform.header.frame_id.lstrip('/')
            child = transform.child_frame_id.lstrip('/')
            if parent and child and parent != child:
                self.edges[child] = (parent, pose_matrix(transform.transform))

    def _ancestors(self, frame):
        result, matrix = {}, np.eye(4)
        while frame:
            if frame in result:
                raise ValueError('Cycle in ROS frame tree')
            result[frame] = matrix
            if frame not in self.edges:
                break
            parent, edge = self.edges[frame]
            matrix, frame = edge @ matrix, parent
        return result

    def lookup(self, target, source):
        target, source = target.lstrip('/'), source.lstrip('/')
        if target == source:
            return np.eye(4)
        targets, sources = self._ancestors(target), self._ancestors(source)
        for ancestor, source_matrix in sources.items():
            if ancestor in targets:
                return np.linalg.inv(targets[ancestor]) @ source_matrix
        return None


@dataclass
class Framed:
    obj: SceneObject
    frame: str
    local: np.ndarray
    frame_locked: bool = True
    frozen: np.ndarray | None = None


@dataclass
class Collision:
    frame: str
    origin: np.ndarray
    parts: list = field(default_factory=list)
    combined: Mesh | None = None


def _operation(message):
    value = message.operation
    return value[0] if isinstance(value, (bytes, bytearray)) else value


def _cone(radius, height, segments=40):
    angles = np.arange(segments)*2*np.pi/segments
    ring = np.column_stack([radius*np.cos(angles), radius*np.sin(angles), np.full(segments, -height/2)])
    vertices = []
    for index in range(segments):
        other = (index+1) % segments
        vertices.extend([[ring[index], ring[other], [0, 0, height/2]],
                         [[0, 0, -height/2], ring[other], ring[index]]])
    return Mesh(np.asarray(vertices))


def _segment(start, end, radius):
    """A small cylinder representing one marker line segment, in mm."""
    direction = np.asarray(end)-start
    length = np.linalg.norm(direction)
    if length < 1e-9:
        return None
    z = direction/length
    reference = [0, 0, 1] if abs(z[2]) < .9 else [1, 0, 0]
    x = np.cross(reference, z)
    x /= np.linalg.norm(x)
    matrix = np.eye(4)
    matrix[:3, :3] = np.column_stack([x, np.cross(z, x), z])
    matrix[:3, 3] = (np.asarray(start)+end)/2
    return make_cylinder(radius, length, segments=8), matrix


def _combine(parts):
    return combine_meshes(parts)


class SceneAssembler:
    def __init__(self, fixed_frame, cache_directory, package_resolver=None, *, package_root=None):
        self.fixed_frame = fixed_frame.lstrip('/')
        self.cache_directory = Path(cache_directory)
        self.package_resolver = package_resolver
        self.package_root = package_root
        self.preview = TrajectoryPreview()
        self._preview_geometry_revision = None
        self._preview_geometry = []
        self._preview_path_meshes = {}
        self.frames = FrameGraph()
        self.robot, self.world, self.attached, self.markers = {}, {}, {}, {}
        self.colors, self.mesh_cache = {}, {}
        self.warnings = set()
        self.description = None
        self.scene_received = False

    def robot_description(self, xml):
        if xml == self.description:
            return
        path = self.cache_directory/'description.urdf'
        path.write_text(xml, encoding='utf-8')
        visuals = load_urdf(path, self.package_root,local_visuals=True, package_resolver=self.package_resolver,include_collisions=True)
        robot = {}
        for frame, obj in visuals:
            robot[obj.id] = Framed(obj, frame, obj.pose.matrix())
        self.robot, self.description = robot, xml
        self.preview.description(xml)
        self._preview_geometry_revision = None

    def _planned_geometry(self):
        packet = self.preview.packet
        if packet is None:
            return []
        revision = packet['plan_id'],packet['revision']
        if revision == self._preview_geometry_revision:
            return self._preview_geometry
        geometry = []
        path_meshes = {}
        for segment,points in self.preview.paths():
            key = packet['plan_id'],segment['index']
            cached = self._preview_path_meshes.get(key)
            if cached is None or cached[0] is not points:
                parts = [part for start,end in zip(points[:-1],points[1:]) if (part := _segment(start,end,2.)) is not None]
                mesh = _combine(parts) if parts else make_sphere(3.,rings=8,segments=12)
                matrix = np.eye(4)
                if not parts:
                    matrix[:3,3] = points[0]
                cached = points,mesh,matrix
            _,mesh,matrix = cached
            path_meshes[key] = cached
            name = f'Plan segment {segment["index"]+1}: {segment.get("label", "")} [{segment["state"]}]'
            obj = SceneObject(name,mesh,color=COLORS.get(segment['state'],COLORS['ready']),
                              id=f'preview/{packet["plan_id"]}/{segment["index"]}')
            geometry.append(Framed(obj,packet['frame_id'],matrix))
        failure = packet.get('failure')
        if failure and failure.get('target_xyz_mm') is not None:
            target = np.asarray(failure['target_xyz_mm'],dtype=float)
            if target.shape != (3,) or not np.isfinite(target).all():
                raise ValueError('Invalid failure target')
            matrix = np.eye(4)
            matrix[:3,3] = target
            obj = SceneObject('Failed segment requested target — exact failure point unknown',
                              make_sphere(12.,rings=12,segments=16),color=COLORS['failed'],
                              id=f'preview/{packet["plan_id"]}/failure')
            geometry.append(Framed(obj,packet['frame_id'],matrix))
        self._preview_geometry_revision,self._preview_geometry = revision,geometry
        self._preview_path_meshes = path_meshes
        return geometry

    def _resource(self, uri):
        path = resolve_mesh(uri, self.cache_directory/'description.urdf',self.package_root, package_resolver=self.package_resolver)
        if path.suffix.lower() != '.stl':
            raise ValueError(f'Unsupported mesh resource: {path.name} (STL required)')
        key = str(path)
        if key not in self.mesh_cache:
            self.mesh_cache[key] = read_stl(path)
        return self.mesh_cache[key]

    def _primitive(self, message):
        dimensions = np.asarray(message.dimensions, dtype=float)*1000
        if not np.isfinite(dimensions).all() or (dimensions <= 0).any():
            raise ValueError('Invalid collision primitive dimensions')
        if message.type == 1 and len(dimensions) == 3:
            return make_box(dimensions)
        if message.type == 2 and len(dimensions) == 1:
            return make_sphere(dimensions[0])
        if message.type == 3 and len(dimensions) == 2:
            return make_cylinder(dimensions[1], dimensions[0])
        if message.type == 4 and len(dimensions) == 2:
            return _cone(dimensions[1], dimensions[0])
        raise ValueError(f'Unsupported collision primitive type {message.type}')

    def _collision_parts(self, message):
        parts = []
        if len(message.primitives) != len(message.primitive_poses) or len(message.meshes) != len(message.mesh_poses):
            raise ValueError(f'Missing geometry poses in collision object {message.id}')
        for primitive, pose in zip(message.primitives, message.primitive_poses):
            parts.append((self._primitive(primitive), pose_matrix(pose)))
        for mesh, pose in zip(message.meshes, message.mesh_poses):
            vertices = np.array([[point.x, point.y, point.z] for point in mesh.vertices])*1000
            indices = np.array([triangle.vertex_indices for triangle in mesh.triangles], dtype=int)
            if indices.ndim != 2 or indices.shape[1] != 3 or not len(indices) or indices.min() < 0 or indices.max() >= len(vertices):
                raise ValueError(f'Invalid triangle indices in collision object {message.id}')
            parts.append((Mesh(vertices[indices]), pose_matrix(pose)))
        if message.planes:
            self.warnings.add('Infinite collision planes are not displayed')
        return parts

    def _collision(self, store, message, default_frame):
        key = message.id
        operation = _operation(message)
        if operation == 1:  # REMOVE
            store.pop(key, None)
            return
        previous = store.get(key)
        frame = message.header.frame_id.lstrip('/') or (previous.frame if previous else default_frame)
        origin = pose_matrix(message.pose) if hasattr(message, 'pose') else np.eye(4)
        if operation == 3:  # MOVE: retain geometry
            if previous is None:
                self.warnings.add(f'MOVE received for unknown collision object {key}')
                return
            previous.frame, previous.origin = frame, origin
            poses = [*message.primitive_poses, *message.mesh_poses]
            if poses:
                if len(poses) != len(previous.parts):
                    raise ValueError(f'MOVE pose count mismatch for {key}')
                previous.parts = [(part[0], pose_matrix(pose)) for part, pose in zip(previous.parts, poses)]
                previous.combined = None
            return
        parts = self._collision_parts(message)
        if operation == 2 and previous:  # APPEND
            transform = self.frames.lookup(previous.frame, frame)
            if transform is None:
                raise ValueError(f'Cannot append geometry across unresolved frames for {key}')
            adjustment = np.linalg.inv(previous.origin) @ transform @ origin
            previous.parts.extend((mesh, adjustment @ pose) for mesh, pose in parts)
            previous.combined = None
        elif operation in (0, 2):
            store[key] = Collision(frame, origin, parts)
        else:
            self.warnings.add(f'Unsupported collision operation {operation}')

    def planning_scene(self, message):
        # Keep the last complete scene if one malformed geometry message fails.
        previous = self.world, self.attached, self.colors, self.frames.edges
        self.world = {key: Collision(item.frame, item.origin, list(item.parts), item.combined) for key, item in self.world.items()}
        self.attached = {key: Collision(item.frame, item.origin, list(item.parts), item.combined) for key, item in self.attached.items()}
        self.colors, self.frames.edges = dict(self.colors), dict(self.frames.edges)
        try:
            self._apply_planning_scene(message)
        except Exception:
            self.world, self.attached, self.colors, self.frames.edges = previous
            raise

    def _apply_planning_scene(self, message):
        if not message.is_diff:
            self.world.clear()
            self.colors.clear()
        if not message.is_diff or not message.robot_state.is_diff:
            self.attached.clear()
        self.frames.update(message.fixed_frame_transforms)
        for color in message.object_colors:
            self.colors[color.id] = (color.color.r, color.color.g, color.color.b, color.color.a)
        for obj in message.world.collision_objects:
            self._collision(self.world, obj, self.fixed_frame)
        for attached in message.robot_state.attached_collision_objects:
            self._collision(self.attached, attached.object, attached.link_name)
            if _operation(attached.object) != 1:
                self.world.pop(attached.object.id, None)
        self.scene_received = True

    def _marker_parts(self, marker):
        scale = np.array([marker.scale.x, marker.scale.y, marker.scale.z], dtype=float)
        identity = np.eye(4)
        if not np.isfinite(scale).all():
            raise ValueError('Invalid marker scale')
        if marker.type == 1:  # CUBE
            return [(make_box(scale*1000), identity, (1, 1, 1))]
        if marker.type == 2:  # SPHERE / ellipsoid
            return [(make_sphere(500), identity, tuple(scale))]
        if marker.type == 3:  # CYLINDER (can have an elliptical cross section)
            return [(make_cylinder(500, 1000), identity, tuple(scale))]
        if marker.type == 10:
            return [(self._resource(marker.mesh_resource), identity, tuple(scale*1000))]
        points = np.array([[point.x, point.y, point.z] for point in marker.points], dtype=float).reshape(-1, 3)*1000
        if marker.type == 11:  # TRIANGLE_LIST
            if not len(points) or len(points) % 3:
                raise ValueError('Incomplete triangle marker')
            return [(Mesh(points.reshape(-1, 3, 3)), identity, tuple(scale))]
        if marker.type in (4, 5):  # LINE_STRIP / LINE_LIST
            pairs = zip(points[:-1], points[1:]) if marker.type == 4 else zip(points[::2], points[1::2])
            radius = max(scale[0]*500, .05)
            parts = [part for start, end in pairs if (part := _segment(start, end, radius)) is not None]
            mesh = _combine(parts)
            return [(mesh, identity, (1, 1, 1))] if mesh else []
        if marker.type == 0:  # ARROW
            if len(points) == 2:
                start, end = points
                length = np.linalg.norm(end-start)
                head = min(scale[2]*1000 if scale[2] > 0 else length*.23, length)
                shaft_radius, head_radius = max(scale[0]*500, .05), max(scale[1]*500, .1)
            elif not len(points):
                start, end = np.zeros(3), np.array([scale[0]*1000, 0, 0])
                length, head = scale[0]*1000, scale[0]*230
                shaft_radius, head_radius = max(scale[1]*100, .05), max(scale[2]*100, .1)
            else:
                raise ValueError('Arrow markers need zero or two points')
            if length <= 0:
                return []
            direction = (end-start)/length
            parts = []
            shaft = _segment(start, end-direction*head, shaft_radius)
            if shaft:
                parts.append(shaft)
            tip = _segment(end-direction*head, end, head_radius)
            if tip:
                parts.append((_cone(head_radius, head), tip[1]))
            return [(_combine(parts), identity, (1, 1, 1))]
        if marker.type in (6, 7, 8):  # CUBE_LIST, SPHERE_LIST, POINTS
            parts = []
            for point in points:
                matrix = identity.copy()
                matrix[:3, 3] = point
                mesh = make_box(np.maximum(scale*1000, .1)) if marker.type == 6 else make_sphere(max(scale[0]*500, .1), rings=8, segments=12)
                parts.append((mesh, matrix))
            mesh = _combine(parts)
            return [(mesh, identity, (1, 1, 1))] if mesh else []
        self.warnings.add(f'Marker type {marker.type} is not displayed (text/unsupported display)')
        return []

    def marker_array(self, topic, message, now=None):
        now = time.monotonic() if now is None else now
        for marker in message.markers:
            key = (topic, marker.ns, marker.id)
            if marker.action == 3:  # DELETEALL is scoped to this display/topic.
                self.markers = {k: value for k, value in self.markers.items()
                                if k[0] != topic or (marker.ns and k[1] != marker.ns)}
                continue
            if marker.action == 2:
                self.markers.pop(key, None)
                continue
            if marker.action != 0:
                continue
            # Geometry and color usually stay constant while frame/pose change.
            signature = (marker.type, marker.mesh_resource, tuple((p.x, p.y, p.z) for p in marker.points),
                         marker.scale.x, marker.scale.y, marker.scale.z,
                         marker.color.r, marker.color.g, marker.color.b, marker.color.a)
            previous = self.markers.get(key)
            if previous and previous[2] == signature:
                templates = previous[3]
            else:
                templates = self._marker_parts(marker)
            color = (marker.color.r, marker.color.g, marker.color.b, marker.color.a)
            if getattr(marker, 'colors', []):
                self.warnings.add('Per-point marker colors are displayed using the marker color')
            origin = pose_matrix(marker.pose)
            framed = []
            for index, (mesh, local, unit_scale) in enumerate(templates):
                obj = SceneObject(f'Marker: {marker.ns} / {marker.id}', mesh, unit_scale=unit_scale,
                                  color=color, id=f'marker/{topic}/{marker.ns}/{marker.id}/{index}')
                framed.append(Framed(obj, marker.header.frame_id.lstrip('/') or self.fixed_frame,
                                     origin @ local, bool(marker.frame_locked)))
            lifetime = marker.lifetime.sec+marker.lifetime.nanosec/1e9
            self.markers[key] = (framed, now+lifetime if lifetime > 0 else None, signature, templates)

    def build(self, now=None):
        now = time.monotonic() if now is None else now
        framed, missing = list(self.robot.values()), set()
        preview_warning = None
        try:
            framed.extend(self._planned_geometry())
        except (ValueError,KeyError,TypeError) as exc:
            preview_warning = 'Planned preview: '+str(exc)
        for category, store in (('world', self.world), ('attached', self.attached)):
            for key, collision in store.items():
                color = self.colors.get(key, (.35, .65, .72, .5) if category == 'world' else (.85, .55, .25, 1))
                parts = collision.parts
                if category == 'world' and key.startswith('cell_fixture_') and len(parts) > 1:
                    if collision.combined is None:
                        collision.combined = combine_meshes(parts)
                    parts = [(collision.combined, np.eye(4))]
                for index, (mesh, local) in enumerate(parts):
                    obj = SceneObject(f'{category.title()}: {key} / {index+1}', mesh,
                                      color=color, id=f'{category}/{key}/{index}')
                    framed.append(Framed(obj, collision.frame, collision.origin @ local))
        for key, (objects, expiry, _, _) in list(self.markers.items()):
            if expiry is not None and now >= expiry:
                del self.markers[key]
            else:
                framed.extend(objects)
        scene = Scene()
        for item in framed:
            transform = item.frozen if item.frozen is not None else self.frames.lookup(self.fixed_frame, item.frame)
            if transform is None:
                missing.add(item.frame)
                continue
            if not item.frame_locked and item.frozen is None:
                item.frozen = transform.copy()
            scene.objects.append(replace(item.obj, pose=matrix_pose(transform @ item.local)))
        warnings = sorted(self.warnings)
        if preview_warning:
            warnings.append(preview_warning)
        if missing:
            warnings.append('Waiting for TF: '+', '.join(sorted(missing)))
        return scene, warnings
