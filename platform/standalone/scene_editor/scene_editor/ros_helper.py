#!/usr/bin/env python3
"""Optional read-only ROS subprocess. Run with the ROS distribution's Python.

Only subscriptions and GetPlanningScene are used. There are no scene-apply,
motion, hardware, parameter-write, or other command clients in this process.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time
import weakref

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scene_editor.ros_scene import SceneAssembler

PROTOCOL = 'scene-editor-ros-v1'


def emit(kind, **payload):
    print(json.dumps({'protocol': PROTOCOL, 'type': kind, **payload}, allow_nan=False), flush=True)


class SceneWriter:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.meshes = weakref.WeakKeyDictionary()
        self.counter = 0

    def encode(self, scene):
        import numpy as np
        objects = []
        for obj in scene.objects:
            geometry = self.meshes.get(obj.mesh)
            if geometry is None:
                if obj.mesh.source:
                    geometry = {'stl': str(obj.mesh.source)}
                elif obj.mesh.primitive:
                    geometry = {'primitive': obj.mesh.primitive}
                else:
                    self.counter += 1
                    path = self.directory/f'mesh-{self.counter}.npy'
                    np.save(path, obj.mesh.vertices, allow_pickle=False)
                    geometry = {'npy': str(path)}
                self.meshes[obj.mesh] = geometry
            objects.append({'id': obj.id, 'name': obj.name, 'geometry': geometry,
                            'translation': obj.pose.translation, 'rotation': obj.pose.rotation,
                            'unit_scale': obj.unit_scale, 'color': obj.color})
        return objects


def run(args):
    import rclpy
    from rclpy.node import Node
    from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
    from rclpy.executors import ExternalShutdownException
    from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
    from std_msgs.msg import String
    from tf2_msgs.msg import TFMessage
    from moveit_msgs.msg import PlanningScene
    from moveit_msgs.srv import GetPlanningScene
    from visualization_msgs.msg import MarkerArray

    def package(name):
        try:
            return get_package_share_directory(name)
        except PackageNotFoundError as exc:
            raise LookupError(name) from exc

    assembler = SceneAssembler(args.fixed_frame, args.cache, package,package_root=args.mesh_root)
    writer = SceneWriter(args.cache)
    rclpy.init(args=[])

    class Reader(Node):
        def __init__(self):
            super().__init__('scene_editor_reader_'+str(os.getpid()), enable_rosout=False,
                             start_parameter_services=False)
            transient = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                                   reliability=ReliabilityPolicy.RELIABLE)
            latest = QoSProfile(depth=100, reliability=ReliabilityPolicy.BEST_EFFORT)
            self.create_subscription(String, args.description_topic, self.description, transient)
            self.create_subscription(TFMessage, args.tf_topic, self.transforms, latest)
            self.create_subscription(TFMessage, args.tf_static_topic, self.transforms,
                                     QoSProfile(depth=100, durability=DurabilityPolicy.TRANSIENT_LOCAL))
            self.create_subscription(PlanningScene, args.scene_topic, self.planning, 10)
            self.create_subscription(String,args.preview_topic,self.preview,transient)
            self.marker_subs = []
            for topic in args.marker_topics:
                # Store each bound callback strongly; no Qt objects cross here.
                callback = MarkerCallback(self, topic)
                self.marker_subs.append(callback)
                self.create_subscription(MarkerArray, topic, callback.receive, latest)
            self.client = self.create_client(GetPlanningScene, args.scene_service)
            self.future = None
            self.initial_scene = False
            self.request_at = 0
            self.pending_diffs = []
            self.errors, self.last_tf = {}, None
            self.last_payload = None
            self.last_status = 0
            self.create_timer(.2, self.tick)

        def guarded(self, function, message):
            key = function.__name__
            try:
                function(message)
                self.errors.pop(key, None)
            except Exception as exc:
                self.errors[key] = str(exc) or type(exc).__name__

        def description(self, message):
            self.guarded(assembler.robot_description, message.data)

        def preview(self,message):
            try:
                assembler.preview.update(json.loads(message.data))
                self.errors.pop('preview',None)
            except Exception as exc:
                self.errors['preview'] = 'Planned trajectory: '+str(exc)

        def transforms(self, message):
            self.guarded(assembler.frames.update, message.transforms)
            self.last_tf = time.monotonic()

        def planning(self, message):
            if not self.initial_scene and message.is_diff:
                if len(self.pending_diffs) < 100:
                    self.pending_diffs.append(message)
                return
            self.guarded(assembler.planning_scene, message)
            if not message.is_diff:
                self.initial_scene = True
                self.pending_diffs.clear()

        def tick(self):
            now = time.monotonic()
            if not self.initial_scene:
                if self.future is None and self.client.service_is_ready():
                    request = GetPlanningScene.Request()
                    # Geometry, attached bodies, transforms and colors; no octomap.
                    request.components.components = 1|2|4|8|16|64|512
                    self.future = self.client.call_async(request)
                    self.request_at = now
                if self.future is not None and self.future.done():
                    try:
                        response = self.future.result()
                        assembler.planning_scene(response.scene)
                        for message in self.pending_diffs:
                            assembler.planning_scene(message)
                        self.pending_diffs.clear()
                        self.initial_scene = True
                        self.errors.pop('snapshot', None)
                    except Exception as exc:
                        self.errors['snapshot'] = 'Scene snapshot: '+str(exc)
                    self.future = None
                elif self.future is not None and now-self.request_at > 5:
                    self.future.cancel()
                    self.future = None
                    self.errors['snapshot'] = 'Timed out waiting for the initial planning scene'
            try:
                scene, warnings = assembler.build(now)
                warnings.extend(self.errors.values())
                objects = writer.encode(scene)
                if objects != self.last_payload:
                    emit('scene', objects=objects, fixed_frame=args.fixed_frame)
                    self.last_payload = objects
                if now-self.last_status >= 1:
                    emit('status', objects=len(objects), robot=bool(assembler.robot),
                         preview=assembler.preview.summary(),
                         planning=self.initial_scene, warnings=warnings[:20],
                         tf_age=None if self.last_tf is None else round(now-self.last_tf, 1),
                         domain=os.environ.get('ROS_DOMAIN_ID', '0'))
                    self.last_status = now
            except Exception as exc:
                emit('warning', message=str(exc))

    class MarkerCallback:
        def __init__(self, node, topic):
            self.node, self.topic = node, topic

        def receive(self, message):
            try:
                assembler.marker_array(self.topic, message)
                self.node.errors.pop(self.topic, None)
            except Exception as exc:
                self.node.errors[self.topic] = str(exc)

    reader = Reader()
    emit('ready', domain=os.environ.get('ROS_DOMAIN_ID', '0'))
    try:
        rclpy.spin(reader)
    except (KeyboardInterrupt, ExternalShutdownException):
        pass
    finally:
        reader.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mesh-root',help='Local mesh package or workspace folder')
    parser.add_argument('--preview-topic',default='/ordered_motion/preview')
    parser.add_argument('--cache', required=True)
    parser.add_argument('--fixed-frame', default='base_link')
    parser.add_argument('--scene-topic', default='/monitored_planning_scene')
    parser.add_argument('--scene-service', default='/get_planning_scene')
    parser.add_argument('--description-topic', default='/robot_description')
    parser.add_argument('--tf-topic', default='/tf')
    parser.add_argument('--tf-static-topic', default='/tf_static')
    parser.add_argument('--marker-topics', nargs='*', default=[])
    args = parser.parse_args()
    try:
        run(args)
    except Exception as exc:
        emit('error', message=f'{type(exc).__name__}: {exc}')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
