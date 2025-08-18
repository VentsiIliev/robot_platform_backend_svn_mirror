#!/usr/bin/env python3

import rclpy
import moveit_commander
from rclpy.node import Node
from moveit_commander import MoveGroupCommander, PlanningSceneInterface, RobotCommander
from geometry_msgs.msg import Pose
import sys

def main():
    rclpy.init()
    node = rclpy.create_node("manual_xyz_control")

    robot = RobotCommander()
    group_name = "manipulator"  # смени ако твоята група е с друго име
    move_group = MoveGroupCommander(group_name)

    while rclpy.ok():
        # Вземаме текуща позиция
        current_pose = move_group.get_current_pose().pose
        print(f"\nТекуща позиция:")
        print(f"X: {current_pose.position.x:.3f}")
        print(f"Y: {current_pose.position.y:.3f}")
        print(f"Z: {current_pose.position.z:.3f}")

        # Избор на ос
        axis = input("\nКоя ос искаш да преместиш? (x / y / z или 'q' за изход): ").strip().lower()
        if axis == 'q':
            print("Изход.")
            break
        if axis not in ['x', 'y', 'z']:
            print("Моля, избери между x, y, z.")
            continue

        # Въведи стойност
        try:
            delta = float(input(f"С колко метра да преместим по {axis}? (напр. 0.01): "))
        except ValueError:
            print("Невалидна стойност.")
            continue

        # Променяме желаната ос
        target_pose = Pose()
        target_pose.orientation = current_pose.orientation  # запазваме ориентацията
        target_pose.position.x = current_pose.position.x
        target_pose.position.y = current_pose.position.y
        target_pose.position.z = current_pose.position.z

        if axis == 'x':
            target_pose.position.x += delta
        elif axis == 'y':
            target_pose.position.y += delta
        elif axis == 'z':
            target_pose.position.z += delta

        # Изпращаме новата позиция
        move_group.set_pose_target(target_pose)
        success = move_group.go(wait=True)
        move_group.stop()
        move_group.clear_pose_targets()

        if success:
            print("✅ Успешно движение.")
        else:
            print("⚠️ Неуспешно планиране.")

    rclpy.shutdown()

if __name__ == "__main__":
    main()
