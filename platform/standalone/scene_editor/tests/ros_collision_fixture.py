"""Isolated fake MoveIt services for tests; never connects to a robot."""
import copy
import json
import sys

import rclpy
from rclpy.node import Node
from tf2_ros.static_transform_broadcaster import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
from moveit_msgs.msg import CollisionObject, AttachedCollisionObject
from moveit_msgs.srv import GetPlanningScene, ApplyPlanningScene


class Fixture(Node):
    def __init__(self, prefix, journal):
        super().__init__('scene_editor_collision_fixture', enable_rosout=False, start_parameter_services=False)
        self.objects, self.journal = {}, journal
        self.create_service(GetPlanningScene, prefix+'/get', self.get)
        self.create_service(ApplyPlanningScene, prefix+'/apply', self.apply)
        self.broadcaster = StaticTransformBroadcaster(self)
        transform = TransformStamped()
        transform.header.frame_id = 'base_link'
        transform.child_frame_id = 'fixture'
        transform.transform.translation.x = 1.
        transform.transform.translation.y = 2.
        transform.transform.rotation.w = 1.
        self.broadcaster.sendTransform(transform)

    def get(self, request, response):
        response.scene.is_diff = False
        response.scene.world.collision_objects = list(self.objects.values())
        attached = AttachedCollisionObject()
        attached.link_name = 'tool_link'
        attached.object.id = 'attached_tool'
        response.scene.robot_state.attached_collision_objects = [attached]
        return response

    def apply(self, request, response):
        scene = request.scene
        assert scene.is_diff and scene.robot_state.is_diff
        assert len(scene.world.collision_objects) == 1
        obj = scene.world.collision_objects[0]
        operation = obj.operation[0] if isinstance(obj.operation, bytes) else obj.operation
        row = dict(id=obj.id, operation=operation, frame=obj.header.frame_id,
                   scene_diff=scene.is_diff, robot_diff=scene.robot_state.is_diff,
                   position=[obj.pose.position.x,obj.pose.position.y,obj.pose.position.z],
                   quaternion=[obj.pose.orientation.x,obj.pose.orientation.y,obj.pose.orientation.z,obj.pose.orientation.w],
                   dimensions=list(obj.primitives[0].dimensions) if obj.primitives else [],
                   primitive_type=obj.primitives[0].type if obj.primitives else None)
        if obj.id == 'reject_me':
            response.success = False
        else:
            if obj.operation == CollisionObject.REMOVE:
                self.objects.pop(obj.id, None)
            else:
                self.objects[obj.id] = copy.deepcopy(obj)
            response.success = True
        row['success'], row['world_ids'] = response.success, sorted(self.objects)
        with open(self.journal, 'a') as stream:
            stream.write(json.dumps(row)+'\n')
        return response


if __name__ == '__main__':
    rclpy.init(args=[])
    node = Fixture(sys.argv[1], sys.argv[2])
    print('READY', flush=True)
    try:
        rclpy.spin(node)
    except (KeyboardInterrupt, rclpy.executors.ExternalShutdownException):
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()
