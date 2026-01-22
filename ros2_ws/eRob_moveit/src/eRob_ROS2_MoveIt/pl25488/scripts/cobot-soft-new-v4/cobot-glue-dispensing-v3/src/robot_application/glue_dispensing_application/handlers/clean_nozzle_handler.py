from modules.robot.robotService.RobotService import RobotService
import time

def clean_nozzle(robot_service:RobotService):
    pos1, pos2 = robot_service.robot_config.getNozzleCleanPointsParsed()
    config = robot_service.robot_config.getNozzleCleanConfig()

    def move_to_nozzle_clean_point(robot_service, point):
        # Send movement command
        result = robot_service.robot.moveCart(position=point,
                                             vel=100,
                                             acc=80,
                                             tool=robot_service.robot_config.robot_tool,
                                             user=robot_service.robot_config.robot_user)

        if result != 0:
            print(f"Failed to send movement command to {point}")
            return -1

        # Wait for command to be accepted and motion to start
        time.sleep(0.1)  # Small delay for command to be processed

        # Wait for motion to complete (blocks until robot finishes moving)
        success = robot_service.robot.wait_for_motion_complete(timeout=10.0)

        if not success:
            print(f"Timeout waiting for robot to reach {point}")
            return -1

        # Verify we reached the target position
        robot_service._waitForRobotToReachPosition(point, 1, 0, timeout=2)
        return 0

    # Move to first cleaning position and wait
    print("Moving to first nozzle cleaning position...")
    move_to_nozzle_clean_point(robot_service, pos1)

    iterations = config.iterations
    print(f"Starting nozzle cleaning with {iterations} iterations.")
    while iterations > 0:
        move_to_nozzle_clean_point(robot_service, pos2)
        move_to_nozzle_clean_point(robot_service, pos1)
        iterations -= 1

    move_to_nozzle_clean_point(robot_service, pos2)

    # Move to calibration position
    print("Moving to calibration position...")
    robot_service.moveToCalibrationPosition()
    robot_service._waitForRobotToReachPosition(robot_service.robot_config.getCalibrationPositionParsed(), 1, 0)
    ret = 0
    return ret



