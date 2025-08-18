from moveit_configs_utils import MoveItConfigsBuilder
from moveit_configs_utils.launches import generate_demo_launch
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("eRobo3", package_name="erobo3_control").to_moveit_configs()
    demo_launch = generate_demo_launch(moveit_config)

    gui_bridge_node = Node(
        package="25488",
        executable="gui_bridge",
        output="screen"
    )

    # If you want to also launch ros2_control node, add it here (example, adjust as needed):
    # ros2_control_node = Node(
    #     package="controller_manager",
    #     executable="ros2_control_node",
    #     parameters=[...],
    #     output="screen"
    # )

    return LaunchDescription([
        *demo_launch.entities,
        gui_bridge_node,
        # ros2_control_node,  # Uncomment if needed
    ])
