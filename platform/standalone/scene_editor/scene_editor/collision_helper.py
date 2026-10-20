#!/usr/bin/env python3
"""One explicit collision request; no motion/hardware clients or publishers."""
import argparse
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scene_editor.collision import validate_request
from scene_editor.ros_scene import pose_matrix


def set_pose(message, matrix):
    """mm matrix to meters/quaternion. ROS imports stay in the helper process."""
    import numpy as np
    from scene_editor.model import euler_degrees
    x, y, z = np.radians(euler_degrees(np.asarray(matrix)))/2
    sx, sy, sz = np.sin([x,y,z])
    cx, cy, cz = np.cos([x,y,z])
    message.position.x, message.position.y, message.position.z = [float(v)/1000 for v in np.asarray(matrix)[:3,3]]
    message.orientation.x = float(sx*cy*cz-cx*sy*sz)
    message.orientation.y = float(cx*sy*cz+sx*cy*sz)
    message.orientation.z = float(cx*cy*sz-sx*sy*cz)
    message.orientation.w = float(cx*cy*cz+sx*sy*sz)


def make_apply_request(data):
    from moveit_msgs.msg import CollisionObject, ObjectColor
    from moveit_msgs.srv import ApplyPlanningScene
    from shape_msgs.msg import SolidPrimitive
    from geometry_msgs.msg import Pose
    data = validate_request(data)
    request = ApplyPlanningScene.Request()
    request.scene.is_diff = True
    request.scene.robot_state.is_diff = True
    obj = CollisionObject()
    obj.id, obj.header.frame_id = data['object_id'], data['frame']
    obj.operation = CollisionObject.REMOVE if data['operation'] == 'remove' else CollisionObject.ADD
    if data['operation'] != 'remove':
        primitive, spec = SolidPrimitive(), data['primitive']
        if spec['kind'] == 'box':
            primitive.type, primitive.dimensions = SolidPrimitive.BOX, [value/1000 for value in spec['size_mm']]
        elif spec['kind'] == 'cylinder':
            primitive.type, primitive.dimensions = SolidPrimitive.CYLINDER, [spec['length_mm']/1000, spec['radius_mm']/1000]
        else:
            primitive.type, primitive.dimensions = SolidPrimitive.SPHERE, [spec['radius_mm']/1000]
        set_pose(obj.pose, data['pose_mm'])
        shape_pose = Pose()
        shape_pose.orientation.w = 1.
        obj.primitives = [primitive]
        obj.primitive_poses = [shape_pose]
        color = ObjectColor()
        color.id = obj.id
        color.color.r, color.color.g, color.color.b, color.color.a = data['color']
        request.scene.object_colors = [color]
    request.scene.world.collision_objects = [obj]
    return request


def run(data, args):
    import rclpy
    from rclpy.node import Node
    from rclpy.time import Time
    from tf2_ros import Buffer, TransformListener
    from moveit_msgs.srv import GetPlanningScene, ApplyPlanningScene

    rclpy.init(args=[])
    node = Node('scene_editor_collision_'+str(os.getpid()), enable_rosout=False, start_parameter_services=False,
                cli_args=['--ros-args', '-r', '/tf:='+args.tf_topic, '-r', '/tf_static:='+args.tf_static_topic])
    buffer = Buffer()
    listener = TransformListener(buffer, node, spin_thread=False)

    def wait_for(predicate, timeout, message):
        deadline = time.monotonic()+timeout
        while not predicate():
            if time.monotonic() >= deadline:
                raise RuntimeError(message)
            rclpy.spin_once(node, timeout_sec=.05)

    def lookup(target, source):
        if target == source:
            import numpy as np
            return np.eye(4)
        wait_for(lambda: buffer.can_transform(target, source, Time()), 5,
                 f'No TF transform from {source} to {target}. Preview was not changed.')
        return pose_matrix(buffer.lookup_transform(target, source, Time()).transform)

    def call(client, request, write=False):
        wait_for(client.service_is_ready, 4, 'ROS service is unavailable: '+client.srv_name)
        future = client.call_async(request)
        try:
            wait_for(future.done, 5, ('Apply result is unknown. Inspect the live scene before retrying.' if write else 'Timed out reading planning scene.'))
            return future.result()
        finally:
            if not future.done():
                future.cancel()

    try:
        if data['operation'] == 'resolve':
            matrix = lookup(data['editor_frame'], data['frame'])
            return dict(success=True, frame_to_editor=matrix.tolist())
        client = node.create_client(GetPlanningScene, args.scene_service)
        request = GetPlanningScene.Request()
        request.components.components = 8|4  # World IDs + attached IDs.
        current = call(client, request).scene
        identifier = data['object_id']
        world = {obj.id for obj in current.world.collision_objects}
        attached = {obj.object.id for obj in current.robot_state.attached_collision_objects}
        if identifier in attached:
            raise ValueError(f'{identifier} is attached to the robot. This editor only changes world collision objects.')
        if data['operation'] == 'add' and identifier in world:
            raise ValueError(f'Object ID {identifier} already exists. Choose a new ID or use Update in ROS.')
        if data['operation'] == 'update' and identifier not in world:
            raise ValueError(f'Object ID {identifier} does not exist. Use Add to ROS first.')
        if data['operation'] == 'remove' and identifier not in world:
            return dict(success=True, message=f'{identifier} is already absent from the planning scene.')
        if data['operation'] != 'remove':
            # Resolve before applying so an unknown reference frame cannot silently
            # create an object in an unintended location.
            lookup(args.fixed_frame, data['frame'])
        apply = node.create_client(ApplyPlanningScene, args.apply_service)
        response = call(apply, make_apply_request(data), write=True)
        if not response.success:
            raise RuntimeError('MoveIt rejected the planning scene diff. No success was acknowledged.')
        return dict(success=True, message=f'{data["operation"].title()} acknowledged by MoveIt for {identifier}.')
    finally:
        listener.unregister()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene-service', default='/get_planning_scene')
    parser.add_argument('--apply-service', default='/apply_planning_scene')
    parser.add_argument('--fixed-frame', default='base_link')
    parser.add_argument('--tf-topic', default='/tf')
    parser.add_argument('--tf-static-topic', default='/tf_static')
    args = parser.parse_args()
    try:
        data = validate_request(json.loads(sys.stdin.readline()))
        result = run(data, args)
    except Exception as exc:
        result = dict(success=False, message=str(exc) or type(exc).__name__)
    print(json.dumps(dict(protocol='scene-editor-collision-v1', **result)), flush=True)
    return 0 if result['success'] else 1


if __name__ == '__main__':
    sys.exit(main())
