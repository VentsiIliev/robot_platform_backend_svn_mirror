from moveit_commander import MoveGroupCommander
import rclpy
from geometry_msgs.msg import Pose

rclpy.init()

group = MoveGroupCommander("arm")

pose = Pose()
pose.position.x = 0.4
pose.position.y = 0.1
pose.position.z = 0.3

pose.orientation.w = 1.0  # assume no rotation

group.set_pose_target(pose)
plan = group.go(wait=True)
group.stop()
group.clear_pose_targets()
