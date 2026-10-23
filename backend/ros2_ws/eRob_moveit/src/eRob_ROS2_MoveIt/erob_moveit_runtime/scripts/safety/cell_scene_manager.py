"""Apply profile-owned cell fixtures to MoveIt without changing robot geometry."""
from copy import deepcopy
from threading import Event, Lock

from geometry_msgs.msg import Pose
from moveit_msgs.msg import CollisionObject
from moveit_msgs.srv import ApplyPlanningScene, GetPlanningScene
from shape_msgs.msg import SolidPrimitive, Mesh, MeshTriangle
from geometry_msgs.msg import Point

from configuration.cell_scene import validate_cell_scene
from utils.transformation_utils import TransformationUtils


class CellSceneManager:
    def __init__(self, node, document, *, surface_mesh=None):
        self._node = node
        self._document = deepcopy(validate_cell_scene(document))
        self._applied = None
        self._lock = Lock()
        self._client = node.create_client(ApplyPlanningScene, '/apply_planning_scene')
        self._reader = node.create_client(GetPlanningScene, '/get_planning_scene')
        self._starting = None
        self._initialized = False
        self._pending_future = None
        self._surface = self._load_surface(surface_mesh) if surface_mesh else None

    @staticmethod
    def _load_surface(uri):
        # Profile-owned immutable table surfaces. STL coordinates are millimetres.
        from pathlib import Path
        from ament_index_python.packages import get_package_share_directory
        import trimesh
        if not uri.startswith('package://'):
            raise ValueError('Cell surface must use a package:// mesh resource')
        package, relative = uri[len('package://'):].split('/', 1)
        base = Path(get_package_share_directory(package)).resolve()
        if Path(relative).is_absolute() or '..' in Path(relative).parts:
            raise ValueError('Cell surface resource escapes its package')
        path = (base / relative).resolve()
        source = trimesh.load(path, force='mesh', process=False)
        mesh = Mesh()
        for vertex in source.vertices:
            point = Point()
            point.x, point.y, point.z = [float(v) / 1000.0 for v in vertex]
            mesh.vertices.append(point)
        for indices in source.faces:
            triangle = MeshTriangle()
            triangle.vertex_indices = [int(i) for i in indices]
            mesh.triangles.append(triangle)
        obj = CollisionObject()
        obj.id = 'cell_surface_tray'
        obj.header.frame_id = 'mounting_surface'
        obj.pose.orientation.w = 1.0
        pose = Pose()
        pose.orientation.w = 1.0
        obj.meshes = [mesh]
        obj.mesh_poses = [pose]
        obj.operation = CollisionObject.ADD
        return obj

    def is_ready(self):
        with self._lock:
            return self._applied is not None

    def snapshot(self):
        with self._lock:
            return deepcopy(self._applied)

    def _request(self, document, existing_ids):
        validate_cell_scene(document)
        request = ApplyPlanningScene.Request()
        request.scene.is_diff = True
        request.scene.robot_state.is_diff = True
        previous = self._document['CELL_COLLISION_OBJECTS']
        objects = document['CELL_COLLISION_OBJECTS']
        for identifier in sorted(set(previous) | set(objects)):
            obj = CollisionObject()
            obj.id = identifier
            item = objects.get(identifier)
            if item is None or not item['enabled']:
                if identifier not in existing_ids:
                    continue
                obj.operation = CollisionObject.REMOVE
            else:
                obj.header.frame_id = item['frame']
                parts = item.get('parts', [item])
                for part in parts:
                    shape = SolidPrimitive()
                    shape.type = SolidPrimitive.BOX
                    shape.dimensions = [value / 1000.0 for value in part['size_mm']]
                    matrix = TransformationUtils.pose_to_transform(part['pose'])
                    quat = TransformationUtils.matrix_to_quaternion(matrix[:3, :3])
                    pose = Pose()
                    pose.position.x, pose.position.y, pose.position.z = map(float, matrix[:3, 3])
                    pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w = map(float, quat)
                    obj.primitives.append(shape)
                    obj.primitive_poses.append(pose)
                obj.pose.orientation.w = 1.0
                obj.operation = CollisionObject.ADD
            request.scene.world.collision_objects.append(obj)
        if self._surface is not None:
            request.scene.world.collision_objects.append(deepcopy(self._surface))
        return request

    def _confirmed(self, document):
        with self._lock:
            self._initialized = True
            self._document = deepcopy(document)
            self._applied = deepcopy(document)

    @staticmethod
    def _read_request():
        request = GetPlanningScene.Request()
        request.components.components = 8  # WORLD_OBJECT_NAMES
        return request

    @staticmethod
    def _existing_ids(reply):
        if reply is None:
            raise RuntimeError('MoveIt returned no planning scene')
        return {obj.id for obj in reply.scene.world.collision_objects}

    def initialize(self):
        """Read first, then apply asynchronously; absent REMOVE is rejected by MoveIt."""
        if self._initialized:
            return True
        if (self._starting is not None or not self._client.service_is_ready()
                or not self._reader.service_is_ready()):
            return False
        document = deepcopy(self._document)
        def applied(future):
            try:
                if not future.result().success:
                    raise RuntimeError('MoveIt rejected initial cell fixtures')
                self._confirmed(document)
            except Exception as error:
                self._node.get_logger().error(f'[CellScene] Initialization failed: {error}')
            finally:
                self._starting = None
        def read(future):
            try:
                existing = self._existing_ids(future.result())
                self._starting = self._client.call_async(self._request(document, existing))
                self._starting.add_done_callback(applied)
            except Exception as error:
                self._node.get_logger().error(f'[CellScene] Could not read initial scene: {error}')
                self._starting = None
        self._starting = self._reader.call_async(self._read_request())
        self._starting.add_done_callback(read)
        return False

    def apply(self, document):
        """Called from the HTTP worker while the runtime execution lock is held."""
        if self._starting is not None or not self._initialized or self._pending_future is not None:
            raise RuntimeError('Cell collision scene is still initializing; retry application')
        if not self._client.service_is_ready():
            raise RuntimeError('MoveIt scene application is unavailable')
        if not self._reader.service_is_ready():
            raise RuntimeError('MoveIt scene query is unavailable')
        read = self._reader.call_async(self._read_request())
        read_event = Event()
        read.add_done_callback(lambda _reply: read_event.set())
        if not read_event.wait(2.0):
            raise RuntimeError('Timed out reading the scene; no collision changes were sent')
        request = self._request(document, self._existing_ids(read.result()))
        with self._lock:
            self._applied = None
        future = self._client.call_async(request)
        self._pending_future = future
        event = Event()
        def done(reply):
            try:
                if reply.result().success:
                    self._confirmed(document)
            except Exception:
                # A transport failure cannot establish whether the diff was applied.
                pass
            finally:
                self._pending_future = None
                event.set()
        future.add_done_callback(done)
        if not event.wait(4.0):
            # Do not claim the old state is still applied after an uncertain write.
            error = TimeoutError('Cell scene application timed out; result is unknown. Reload before retrying')
            error.outcome_unknown = True
            error.retryable = True
            raise error
        response = future.result()
        if not response.success:
            raise RuntimeError('MoveIt rejected the cell collision scene')
