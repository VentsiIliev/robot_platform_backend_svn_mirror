"""
New RobotService implementation with proper State Machine pattern
for robust pause/resume functionality and clean state management.
"""

import threading
import time

from typing import Optional

from modules.shared.MessageBroker import MessageBroker
from modules.shared.shared.settings.robotConfig.robotConfigModel import RobotConfig
from modules.robot.enums.axis import RobotAxis, Direction
from modules.robot.RobotUtils import calculate_distance_between_points
from modules.robot.robotService.RobotServiceMessagePublisher import RobotServiceMessagePublisher
from modules.robot.robotService.RobotServiceStateManager import RobotServiceStateManager
from modules.robot.robotService.RobotServiceSubscriptionManager import RobotServiceSubscriptionManager
from modules.robot.robotService.RobotStateManager import RobotStateManager
from modules.robot.robotService.enums.RobotServiceState import RobotServiceState
from robot_application.glue_dispensing_application.tools.Laser import Laser
from robot_application.glue_dispensing_application.tools.ToolChanger import ToolChanger
from robot_application.glue_dispensing_application.tools.VacuumPump import VacuumPump
from backend.system.utils.custom_logging import setup_logger, \
    LoggerContext, log_info_message, log_debug_message

ENABLE_ROBOT_SERVICE_LOGGING = True

if ENABLE_ROBOT_SERVICE_LOGGING:
    robot_service_logger = setup_logger("RobotService")
else:
    robot_service_logger = None

class CancellationToken:
    """
    Cancellation token for controlling robot operations.

    This provides a clean way to cancel robot operations without
    directly coupling to state machines.
    """

    def __init__(self):
        self._cancelled = threading.Event()
        self._reason = None
        self._timestamp = None

    def cancel(self, reason: str = "cancelled"):
        """Cancel the operation."""
        self._cancelled.set()
        self._reason = reason
        self._timestamp = time.time()

    def is_cancelled(self) -> bool:
        """Check if the operation has been cancelled."""
        return self._cancelled.is_set()

    def reset(self):
        """Reset the cancellation token."""
        self._cancelled.clear()
        self._reason = None
        self._timestamp = None

    def get_cancellation_reason(self) -> Optional[str]:
        """Get the reason for cancellation."""
        return self._reason

    def get_cancellation_timestamp(self) -> Optional[float]:
        """Get the timestamp when cancellation occurred."""
        return self._timestamp

class RobotService:
    """
    New RobotService implementation with proper state machine pattern
    for robust pause/resume functionality and clean state management.
    """

    RX_VALUE = 180
    RY_VALUE = 0
    RZ_VALUE = 0

    def __init__(self, robot, settingsService):
        """Initialize the new robot service"""
        self.robot_service_logger_context = LoggerContext(enabled=ENABLE_ROBOT_SERVICE_LOGGING,
                                            logger=robot_service_logger)
        # Initialize state machine
        self.state_machine = RobotStateManager(RobotServiceState.INITIALIZING, self)

        # Robot and settings
        self.robot = robot
        self.robot.printSdkVersion()
        self.settingsService = settingsService
        self.robot_config: RobotConfig = self.settingsService.robot_config

        # Robot state monitoring
        self.robot_state_manager_cycle_time = 0.03  # 30ms cycle time
        self.robotStateManager = RobotStateManager(robot_ip=self.robot_config.robot_ip,
                                                   cycle_time=self.robot_state_manager_cycle_time)
        self.robotStateManager.start_monitoring()

        self.broker = MessageBroker()
        self.message_publisher = RobotServiceMessagePublisher(self.broker)
        self.state_manager= RobotServiceStateManager(RobotServiceState.INITIALIZING,self.message_publisher,self)
        self.subscription_manager = RobotServiceSubscriptionManager(self,self.broker)
        self.state_manager.start_state_publisher_thread()
        self.subscription_manager.subscribe_robot_state_topic()
        self.subscription_manager.subscribe_glue_process_state_topic()
        self.state_topic = self.message_publisher.state_topic

        # Tools and peripherals
        self.pump = VacuumPump()
        self.laser = Laser()
        self.toolChanger = ToolChanger()
        self.currentGripper = None



        # Thread safety
        self._operation_lock = threading.Lock()
        self._stop_thread = threading.Event()

        # Resume flag for tracking when we're resuming vs starting new


        # Debouncing for pause/resume commands
        # self._last_pause_time = 0
        # self._pause_debounce_interval = 0.5  # 500ms debounce

    def _stop_robot_motion(self):
        """Stop robot motion safely"""
        with self._operation_lock:
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    result = self.robot.stopMotion()
                    log_info_message(self.robot_service_logger_context,message =f"Robot motion stopped, result: {result}")

                    break
                except Exception as e:
                    if "Request-sent" in str(e) and attempt < max_attempts - 1:
                        time.sleep(0.1)  # Wait and retry
                        continue
                    else:
                        raise

    def _waitForRobotToReachPosition(self, endPoint, threshold, delay, timeout=30, cancellation_token=None):
        """Wait for robot to reach target position with state awareness"""
        start_time = time.time()
        log_info_message(self.robot_service_logger_context, message=f"_waitForRobotToReachPosition CALLED WITH  endPoint={endPoint}, threshold={threshold}, delay={delay}, timeout={timeout}")
        print(f"[RobotService] Waiting for position {endPoint} with threshold {threshold}mm, timeout {timeout}s")

        last_distance_log_time = start_time
        command_completion_check_started = False

        while True:
            # Check cancellation token (replaces state machine dependency)
            if cancellation_token is not None and cancellation_token.is_cancelled():
                log_debug_message(self.robot_service_logger_context, message=f"Operation cancelled via cancellation token: {cancellation_token.get_cancellation_reason()}")
                return False

            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                log_debug_message(self.robot_service_logger_context, message=f"Timeout reached ({elapsed:.2f}s > {timeout}s) while waiting for robot position {endPoint}")
                print(f"[RobotService] TIMEOUT after {elapsed:.2f}s waiting for position {endPoint}")
                return False

            # After 1 second, start checking for command completion failures
            # (gives MoveIt time to accept/reject the goal)
            if elapsed > 1.0 and not command_completion_check_started:
                command_completion_check_started = True

            if command_completion_check_started:
                # Check if MoveIt rejected the command (no IK solution, collision, etc)
                if hasattr(self.robot, 'last_command_success') and not self.robot.last_command_success:
                    log_debug_message(self.robot_service_logger_context,
                                    message=f"Movement command failed (MoveIt rejected or execution error)")
                    print(f"[RobotService] ✗ Movement FAILED - MoveIt rejected command or execution error")
                    return False

            # Check position
            current_position = self.getCurrentPosition()
            if current_position is None:
                time.sleep(0.1)
                continue

            distance = calculate_distance_between_points(current_position, endPoint)

            # Log distance every second
            if time.time() - last_distance_log_time >= 1.0:
                print(f"[RobotService] Current: {current_position[:3]}, Target: {endPoint[:3]}, Distance: {distance:.2f}mm, Elapsed: {elapsed:.1f}s")
                last_distance_log_time = time.time()

            if distance < threshold:
                log_debug_message(self.robot_service_logger_context, message=f"Robot reached target position {endPoint} within threshold {threshold}mm")
                print(f"[RobotService] ✓ Reached position within {threshold}mm threshold (actual: {distance:.2f}mm)")
                return True

            time.sleep(0.01)

    def move_to_nesting_capture_position(self, z_offset=0):
        ret = self.moveToStartPosition(z_offset=z_offset)

        if ret != 0:
            return ret

        target_pose = self.robot_config.getHomePositionParsed()
        target_pose[2] += z_offset  # apply z_offset
        self._waitForRobotToReachPosition(target_pose, 1, 0.1)
        return  ret

    def move_to_spray_capture_position(self, z_offset=0):
        ret = self.moveToCalibrationPosition(z_offset=z_offset)

        if ret != 0:
            return ret

        target_pose = self.robot_config.getCalibrationPositionParsed()
        target_pose[2] += z_offset  # apply z_offset
        self._waitForRobotToReachPosition(target_pose, 1, 0.1)
        return ret
    # Movement methods
    def moveToCalibrationPosition(self,z_offset=0):
        """Move robot to calibration position"""
        try:
            position = self.robot_config.getCalibrationPositionParsed()
            # apply the z offset to account for the calibration pattern thickness
            position[2] += z_offset
            config = self.robot_config.getCalibrationPosConfig()

            ret = self.robot.moveCart(
                position=position,
                tool=self.robot_config.robot_tool,
                user=self.robot_config.robot_user,
                vel=config.velocity,
                acc=config.acceleration
            )

            self.message_publisher.publish_threshold_region_topic("spray")
            return ret

        except Exception as e:
            print(f"Error moving to calibration position: {e}")
            return -1

    def moveToLoginPosition(self):
        ret = None
        currentPos = self.getCurrentPosition()
        x, y, z, rx, ry, rz = currentPos

        if y > 350:
            ret = self.moveToCalibrationPosition()
            if ret != 0:
                return ret

            ret = self.moveToStartPosition()
            if ret != 0:
                return ret
        else:
            ret = self.moveToStartPosition()
            if ret != 0:
                return ret

        position = self.robot_config.getLoginPositionParsed()  # This already handles None case
        loginPositionConfig = self.robot_config.getLoginPosConfig()
        velocity = loginPositionConfig.velocity
        acceleration = loginPositionConfig.acceleration
        ret = self.robot.moveCart(position=position,
                                  tool=self.robot_config.robot_tool,
                                  user=self.robot_config.robot_user,
                                  vel=velocity,
                                  acc=acceleration)
        return ret

    def moveToStartPosition(self,z_offset=0):
        """Move robot to start position"""
        try:
            position = self.robot_config.getHomePositionParsed()
            print(f"Position before z offset: {position}")
            # apply the z offset to account for the calibration pattern thickness
            position[2] += z_offset
            print(f"Position with z offset: {position}")
            config = self.robot_config.getHomePosConfig()

            ret = self.robot.moveCart(
                position=position,
                tool=self.robot_config.robot_tool,
                user=self.robot_config.robot_user,
                vel=config.velocity,
                acc=config.acceleration
            )

            print(f"Moving to start position, result: {ret}")
            self.message_publisher.publish_threshold_region_topic("pickup")
            return ret

        except Exception as e:
            print(f"Error moving to start position: {e}")
            return -1

    def get_current_velocity(self):
        """Get current robot velocity"""
        return self.robotStateManager.velocity

    def get_current_acceleration(self):
        """Get current robot acceleration"""
        return self.robotStateManager.acceleration

    def getCurrentPosition(self):
        """Get current robot position from MoveIt FK via robot wrapper"""
        # Use cached position (updated at 10Hz by FK timer) to avoid blocking
        # Synchronous FK queries in tight loops cause performance issues and prevent robot motion
        return self.robot.getCurrentPosition(use_cached=True)

    def enableRobot(self):
        """Enable robot motion"""
        self.robot.enable()
        print("Robot enabled")

    def disableRobot(self):
        """Disable robot motion"""
        self.robot.disable()
        print("Robot disabled")

    def stopRobot(self):
        """Stop robot motion"""
        return self.robot.stopMotion()

    def is_within_safety_limits(self, position):
        """Check if position is within safety limits"""
        safety_config = self.robot_config.safety_limits
        pos_x, pos_y, pos_z = position[0], position[1], position[2]

        if pos_z > safety_config.z_max:
            print(f"Position Z {pos_z} exceeds maximum limit of {safety_config.z_max}")
            return False

        if pos_z < safety_config.z_min:
            print(f"Position Z {pos_z} is below minimum limit of {safety_config.z_min}")
            return False

        return True

    def pickupGripper(self, gripperId, callBack=None):
        """
              Picks up a gripper from the tool changer.

              Args:
                  gripperId (int): ID of the gripper to pick
                  callBack (function, optional): Optional callback after pickup

              Returns:
                  tuple: (bool, message)
              """

        # check if gripper is not already picked
        if self.currentGripper == gripperId:
            message = f"Gripper {gripperId} is already picked"
            print(message)
            return False, message

        slotId = self.toolChanger.getSlotIdByGrippedId(gripperId)
        # if not self.toolChanger.isSlotOccupied(slotId):
        #     message = f"Slot {slotId} is empty"
        #     print(message)
        #     return False, message

        self.toolChanger.setSlotAvailable(slotId)

        # ret = self.robot.moveCart([-206.239, -180.406, 726.327, 180, 0, 101], 0, 0, 30, 30)
        # print("move before pickup: ",ret)
        if gripperId == 0:
            config = self.robot_config.getSlot0PickupConfig()
            positions = self.robot_config.getSlot0PickupPointsParsed()
        elif gripperId == 1:
            config = self.robot_config.getSlot1PickupConfig()
            positions = self.robot_config.getSlot1PickupPointsParsed()
        # elif gripperId == 2:
        #     """ADD LOGIC FOR DROPPING OFF TOOL 2 -> LASER"""
        #     config = self.robot_config.getSlot2PickupConfig()
        #     positions = self.robot_config.getSlot2DropoffPointsParsed()
        elif gripperId == 4:
            """ADD LOGIC FOR DROPPING OFF TOOL 4 -> DOUBLE GRIPPER"""
            config = self.robot_config.getSlot4PickupConfig()
            positions = self.robot_config.getSlot4PickupPointsParsed()
        else:
            raise ValueError("UNSUPPORTED GRIPPER ID: ", gripperId)

        try:
            for pos in positions:
                print("Moving to position: ", pos)

                # Send movement command
                ret = self.robot.moveL(position=pos,
                                      tool=self.robot_config.robot_tool,
                                      user=self.robot_config.robot_tool,
                                      vel=config.velocity,
                                      acc=config.acceleration,
                                      blendR=1)

                if ret != 0:
                    print(f"Failed to send movement command to {pos}")
                    self.toolChanger.setSlotNotAvailable(slotId)  # Mark slot as occupied on failure
                    return False, f"Failed to move to position {pos}"

                # CRITICAL FIX: Wait for motion to complete before sending next command
                import time
                time.sleep(0.1)  # Allow command to be processed
                success = self.robot.wait_for_motion_complete(timeout=15.0)

                if not success:
                    print(f"Timeout waiting for robot to reach {pos}")
                    self.toolChanger.setSlotNotAvailable(slotId)  # Mark slot as occupied on failure
                    return False, f"Timeout reaching position {pos}"

                # Verify position reached
                self._waitForRobotToReachPosition(pos, 2, 0, timeout=2)

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.toolChanger.setSlotNotAvailable(slotId)  # Mark slot as occupied on failure
            return False, f"Exception during pickup: {str(e)}"

        self.moveToStartPosition()
        self.currentGripper = gripperId
        return True, None

    def dropOffGripper(self, gripperId, callBack=None):
        """
              Drops off the currently held gripper into a specified slot.

              Args:
                  slotId (int): Target slot ID
                  callBack (function, optional): Optional callback after drop off

              Returns:
                  tuple: (bool, message)
              """
        gripperId = int(gripperId)
        slotId = self.toolChanger.getSlotIdByGrippedId(gripperId)
        # print("Drop off gripper: ", gripperId)
        if self.toolChanger.isSlotOccupied(slotId):
            message = f"Slot {slotId} is taken"
            print(message)
            return False, message


        self.toolChanger.setSlotNotAvailable(slotId)

        if gripperId == 0:
            config = self.robot_config.getSlot0DropoffConfig()
            positions = self.robot_config.getSlot0DropoffPointsParsed()
        elif gripperId == 1:
            print("RobotService.dropOffGripper: Dropping off gripper 1")
            config = self.robot_config.getSlot1DropoffConfig()
            positions = self.robot_config.getSlot1DropoffPointsParsed()
        # elif gripperId == 2:
        #     """ADD LOGIC FOR DROPPING OFF TOOL 2 -> LASER"""
        #     config = self.robot_config.getSlot2DropoffConfig()
        #     positions = self.robot_config.getSlot2DropoffPointsParsed()
        elif gripperId == 4:
            """ADD LOGIC FOR DROPPING OFF TOOL 4 -> DOUBLE GRIPPER"""
            config = self.robot_config.getSlot4DropoffConfig()
            positions = self.robot_config.getSlot4DropoffPointsParsed()
        else:
            raise ValueError("UNSUPPORTED GRIPPER ID: ", gripperId)

        for pos in positions:
            # Send movement command
            ret = self.robot.moveL(position=pos,
                                  tool=self.robot_config.robot_tool,
                                  user=self.robot_config.robot_user,
                                  vel=config.velocity,
                                  acc=config.acceleration,
                                  blendR=1)
            print("move before drop off: ", ret)

            if ret != 0:
                print(f"Failed to send movement command to {pos}")
                self.toolChanger.setSlotAvailable(slotId)  # Release slot on failure
                return False, f"Failed to move to position {pos}"

            # CRITICAL FIX: Wait for motion to complete before sending next command
            import time
            time.sleep(0.1)  # Allow command to be processed
            success = self.robot.wait_for_motion_complete(timeout=15.0)

            if not success:
                print(f"Timeout waiting for robot to reach {pos}")
                self.toolChanger.setSlotAvailable(slotId)  # Release slot on failure
                return False, f"Timeout reaching position {pos}"

            # Verify position reached
            self._waitForRobotToReachPosition(pos, 2, 0, timeout=2)

        # self.moveToStartPosition()

        self.currentGripper = None
        return True, None

    def execute_tool_changer_trajectory(self):
        """
        Execute the tool changer trajectory.

        Returns:
            int: 0 on success, non-zero on failure
        """
        print("RobotService: Executing tool changer trajectory")

        try:
            config = self.robot_config.getToolChangerConfig()
            positions = self.robot_config.getToolChangerPointsParsed()

            if not positions:
                print("No positions defined for tool changer trajectory")
                return -1

            print(f"Tool changer trajectory has {len(positions)} positions")

            for i, pos in enumerate(positions):
                print(f"Moving to tool changer position {i+1}/{len(positions)}: {pos}")

                ret = self.robot.moveL(
                    position=pos,
                    tool=self.robot_config.robot_tool,
                    user=self.robot_config.robot_user,
                    vel=config.velocity,
                    acc=config.acceleration,
                    blendR=1
                )

                if ret != 0:
                    print(f"Failed to send movement command to position {i+1}: {pos}")
                    return -1

                import time
                time.sleep(0.1)

                success = self.robot.wait_for_motion_complete(timeout=15.0)

                if not success:
                    print(f"Timeout waiting for robot to reach position {i+1}")
                    return -1

                self._waitForRobotToReachPosition(pos, 2, 0, timeout=2)

            print("Tool changer trajectory completed successfully")
            return 0

        except Exception as e:
            print(f"Error executing tool changer trajectory: {e}")
            import traceback
            traceback.print_exc()
            return -1

    def startJog(self, axis, direction, step):
        step = float(step)
        # Set sign based on direction - FIXED: Plus = positive, Minus = negative
        if direction == Direction.MINUS:
            temp_step = -abs(step)  # FIXED: Minus direction should be negative
            print(f"Direction minus, step set to {temp_step}")
        else:
            temp_step = abs(step)  # FIXED: Plus direction should be positive
            print(f"Direction plus, step set to {temp_step}")

        if axis == axis.Z:
            currentPos = self.getCurrentPosition()
            proposedZ = currentPos[2] + temp_step
            print(f"RobotService: startJog: current Z: {currentPos[2]}, proposed Z: {proposedZ}")
            if proposedZ < self.robot_config.safety_limits.z_min:
                print(
                    f"Jog Z to {proposedZ}mm exceeds minimum limit of {self.robot_config.safety_limits.z_min}mm. Jog cancelled.")
                return -1
            if proposedZ > self.robot_config.safety_limits.z_max:
                print(
                    f"Jog Z to {proposedZ}mm exceeds maximum limit of {self.robot_config.safety_limits.z_max}mm. Jog cancelled.")
                return -1

        result = self.robot.startJog(axis=axis,
                                     direction=direction,
                                     step=step,
                                     vel=self.robot_config.getJogConfig().velocity,
                                     acc=self.robot_config.getJogConfig().acceleration)
        print(f"RobotService: startJog: result: {result}")
        return result

    def moveToPosition(self, position, tool, workpiece, velocity, acceleration, waitToReachPosition=False, timeout=30):
        """
        Moves the robot to a specified position with optional waiting.

        Args:
            position (list): Target Cartesian position
            tool (int): Tool frame ID
            workpiece (int): Workpiece frame ID
            velocity (float): Speed
            acceleration (float): Acceleration
            waitToReachPosition (bool): If True, waits for robot to reach position
            timeout (float): Maximum time to wait for position (seconds)
        """
        current_pos = self.getCurrentPosition()
        print(f"[RobotService] moveToPosition called:")
        print(f"  Current: {current_pos}")
        print(f"  Target:  {position}")
        print(f"  Delta X: {position[0] - current_pos[0]:.2f}mm, Delta Y: {position[1] - current_pos[1]:.2f}mm, Delta Z: {position[2] - current_pos[2]:.2f}mm")
        print(f"  Wait: {waitToReachPosition}, Timeout: {timeout}s, Vel: {velocity}, Acc: {acceleration}")

        # check if position is within safety limits
        result = self.is_within_safety_limits(position)
        if not result:
            print(f"[RobotService] ✗ Position {position} is outside safety limits!")
            return False

        ret = self.robot.moveCart(position, tool, workpiece, vel=velocity, acc=acceleration)
        print(f"[RobotService] moveCart returned: {ret}")

        if waitToReachPosition:
            success = self._waitForRobotToReachPosition(position, 2, delay=0.1, timeout=timeout)
            print(f"[RobotService] waitForRobotToReachPosition returned: {success}")
            return 0 if success else -1

        return ret

    def stop(self):
        """Gracefully stop the service"""
        print("Stopping NewRobotService...")
        self._stop_thread.set()
        if hasattr(self, 'robotStateManager'):
            self.robotStateManager.stop_monitoring()
        if hasattr(self, 'state_manager'):
            self.state_manager.stop_state_publisher_thread()
        print("NewRobotService stopped")

    def __del__(self):
        """Cleanup when service is destroyed"""
        try:
            self.stop()
        except:
            pass

    def loadConfig(self):
        try:
            self.robot_config = self.settingsService.load_robot_config()
            print("Robot Config reloaded in RobotService: ", self.robot_config)
            return True
        except:
            print("Failed to reload robot config in RobotService")
            return False

    def executePatternMovement(self, shape, width, height, num_points, plane="xy", repetitions=1, velocity=50, acceleration=50):
        import math
        import time

        log_info_message(self.robot_service_logger_context, f"Executing {shape} pattern in {plane.upper()} plane: {width}x{height}mm with {num_points} points, {repetitions} repetition(s), vel={velocity}%, acc={acceleration}%")

        current_pos = self.getCurrentPosition()
        if not current_pos:
            print("Failed to get current position")
            return -1

        start_x, start_y, start_z = current_pos[0], current_pos[1], current_pos[2]
        rx, ry, rz = current_pos[3], current_pos[4], current_pos[5]

        positions = []

        if shape.lower() == "rectangle":
            points_per_side = max(2, num_points // 4)
            half_width = width / 2
            half_height = height / 2

            # Generate points based on plane
            if plane == "xy":
                # Horizontal: X-Y plane (Z constant)
                # Right side (going up)
                for i in range(points_per_side):
                    t = i / (points_per_side - 1) if points_per_side > 1 else 0
                    positions.append([start_x + half_width, start_y - half_height + height * t, start_z, rx, ry, rz])
                # Top side (going left)
                for i in range(1, points_per_side):
                    t = i / (points_per_side - 1)
                    positions.append([start_x + half_width - width * t, start_y + half_height, start_z, rx, ry, rz])
                # Left side (going down)
                for i in range(1, points_per_side):
                    t = i / (points_per_side - 1)
                    positions.append([start_x - half_width, start_y + half_height - height * t, start_z, rx, ry, rz])
                # Bottom side (going right)
                for i in range(1, points_per_side):
                    t = i / (points_per_side - 1)
                    positions.append([start_x - half_width + width * t, start_y - half_height, start_z, rx, ry, rz])

            elif plane == "xz":
                # Vertical: X-Z plane (Y constant)
                # Right side (going up)
                for i in range(points_per_side):
                    t = i / (points_per_side - 1) if points_per_side > 1 else 0
                    positions.append([start_x + half_width, start_y, start_z - half_height + height * t, rx, ry, rz])
                # Top side (going left)
                for i in range(1, points_per_side):
                    t = i / (points_per_side - 1)
                    positions.append([start_x + half_width - width * t, start_y, start_z + half_height, rx, ry, rz])
                # Left side (going down)
                for i in range(1, points_per_side):
                    t = i / (points_per_side - 1)
                    positions.append([start_x - half_width, start_y, start_z + half_height - height * t, rx, ry, rz])
                # Bottom side (going right)
                for i in range(1, points_per_side):
                    t = i / (points_per_side - 1)
                    positions.append([start_x - half_width + width * t, start_y, start_z - half_height, rx, ry, rz])

            elif plane == "yz":
                # Vertical: Y-Z plane (X constant)
                # Right side (going up)
                for i in range(points_per_side):
                    t = i / (points_per_side - 1) if points_per_side > 1 else 0
                    positions.append([start_x, start_y + half_width, start_z - half_height + height * t, rx, ry, rz])
                # Top side (going left)
                for i in range(1, points_per_side):
                    t = i / (points_per_side - 1)
                    positions.append([start_x, start_y + half_width - width * t, start_z + half_height, rx, ry, rz])
                # Left side (going down)
                for i in range(1, points_per_side):
                    t = i / (points_per_side - 1)
                    positions.append([start_x, start_y - half_width, start_z + half_height - height * t, rx, ry, rz])
                # Bottom side (going right)
                for i in range(1, points_per_side):
                    t = i / (points_per_side - 1)
                    positions.append([start_x, start_y - half_width + width * t, start_z - half_height, rx, ry, rz])

        elif shape.lower() == "circle":
            radius_x = width / 2
            radius_y = height / 2

            if plane == "xy":
                # Horizontal: X-Y plane (Z constant)
                for i in range(num_points):
                    angle = 2 * math.pi * i / num_points
                    x = start_x + radius_x * math.cos(angle)
                    y = start_y + radius_y * math.sin(angle)
                    positions.append([x, y, start_z, rx, ry, rz])

            elif plane == "xz":
                # Vertical: X-Z plane (Y constant)
                for i in range(num_points):
                    angle = 2 * math.pi * i / num_points
                    x = start_x + radius_x * math.cos(angle)
                    z = start_z + radius_y * math.sin(angle)
                    positions.append([x, start_y, z, rx, ry, rz])

            elif plane == "yz":
                # Vertical: Y-Z plane (X constant)
                for i in range(num_points):
                    angle = 2 * math.pi * i / num_points
                    y = start_y + radius_x * math.cos(angle)
                    z = start_z + radius_y * math.sin(angle)
                    positions.append([start_x, y, z, rx, ry, rz])
        else:
            print(f"Unknown pattern shape: {shape}")
            return -1

        # Find the closest point to current position and start from there
        if positions:
            min_dist = float('inf')
            closest_idx = 0
            for idx, pos in enumerate(positions):
                dist = math.sqrt((pos[0] - start_x)**2 + (pos[1] - start_y)**2 + (pos[2] - start_z)**2)
                if dist < min_dist:
                    min_dist = dist
                    closest_idx = idx

            # Reorder positions to start from the closest point
            single_pattern = positions[closest_idx:] + positions[:closest_idx]
            log_info_message(self.robot_service_logger_context, f"Starting pattern from point {closest_idx + 1} (closest to current position, distance: {min_dist:.2f}mm)")

            # Build the full path with repetitions
            positions = []
            for rep in range(repetitions):
                positions.extend(single_pattern)
                if rep < repetitions - 1:
                    # Add transition back to start of pattern for next repetition (except after last repetition)
                    log_debug_message(self.robot_service_logger_context, f"Adding repetition {rep + 2} starting point")

            # Add the initial starting position as the final waypoint to return to start
            initial_position = [start_x, start_y, start_z, rx, ry, rz]
            positions.append(initial_position)
            log_info_message(self.robot_service_logger_context, f"Pattern with {repetitions} repetition(s): {len(positions)} total waypoints (returning to start)")

        if not positions:
            print("No positions generated for pattern")
            return -1

        # Use Cartesian path for smooth continuous movement
        log_info_message(self.robot_service_logger_context, f"Executing smooth Cartesian path with {len(positions)} waypoints")

        result = self.robot.moveCartesianPath(
            waypoints=positions,
            vel=velocity,
            acc=acceleration
        )

        if result != 0:
            print(f"Failed to execute Cartesian path for pattern movement")
            return -1

        # Wait for the entire path to complete
        time.sleep(0.5)  # Small delay for command to be processed

        # Calculate approximate total path length for timeout estimation
        total_distance = 0
        for i in range(len(positions) - 1):
            dx = positions[i+1][0] - positions[i][0]
            dy = positions[i+1][1] - positions[i][1]
            dz = positions[i+1][2] - positions[i][2]
            total_distance += math.sqrt(dx*dx + dy*dy + dz*dz)

        # Estimate timeout: distance(mm) / velocity(mm/s) + safety margin
        # Assuming velocity of ~50mm/s for vel=50%
        estimated_time = (total_distance / 50.0) * 2  # 2x safety margin
        timeout = max(30.0, estimated_time)  # At least 30 seconds

        log_debug_message(self.robot_service_logger_context, f"Total path distance: {total_distance:.1f}mm, timeout: {timeout:.1f}s")

        success = self.robot.wait_for_motion_complete(timeout=timeout)
        if not success:
            print(f"Timeout waiting for Cartesian path to complete")
            return -1

        log_info_message(self.robot_service_logger_context, f"Pattern movement completed successfully")
        return 0


if __name__ == "__main__":
    robot_state_manager = RobotStateManager(robot_ip="192.168.58.2")
    robot_state_manager.start_thread()
