from core.operation_state_management import IOperation, OperationState
from modules.shared.MessageBroker import MessageBroker
from communication_layer.api.v1.topics import SystemTopics
import threading
import cv2
import numpy as np
class GlueOperation(IOperation):
    def __init__(self):
        super().__init__()
        self.broker = MessageBroker()
        self.robot_service = None
        self.vision_service = None
        self.is_running = False
        self.execution_thread = None
        # Operation parameters (can be updated from dashboard)
        self.velocity = 60
        self.acceleration = 40
        self.z_offset = 2.0
    def set_params(self, velocity=None, acceleration=None, z_offset=None):
        """Update operation parameters"""
        if velocity is not None:
            self.velocity = velocity
        if acceleration is not None:
            self.acceleration = acceleration
        if z_offset is not None:
            self.z_offset = z_offset
        print(f"[GlueOperation] Updated params: vel={self.velocity}, acc={self.acceleration}, z_offset={self.z_offset}")
    def set_services(self, robot_service, vision_service):
        """Set the robot and vision services"""
        self.robot_service = robot_service
        self.vision_service = vision_service
    def _do_start(self, *args, **kwargs):
        print(f"[GlueOperation] Starting glue operation")
        if not self.robot_service or not self.vision_service:
            print("[GlueOperation] ERROR: Services not set!")
            self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.ERROR)
            return
        # Start execution in background thread
        self.is_running = True
        self.execution_thread = threading.Thread(target=self._execute_glueing, daemon=True)
        self.execution_thread.start()
    def _execute_glueing(self):
        """Execute glueing in background thread"""
        try:
            self._run_glue_sequence()
        except Exception as e:
            print(f"[GlueOperation] Error during execution: {e}")
            import traceback
            traceback.print_exc()
            self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.ERROR)
        finally:
            if self.is_running:
                # Only publish IDLE if we weren't stopped
                self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.IDLE)
                self.is_running = False
    def _run_glue_sequence(self):
        """Main glue sequence"""
        # Store initial robot position to return to after glueing
        initial_position = self.robot_service.robot.get_current_position()
        if initial_position is None or len(initial_position) < 6:
            print("[GlueOperation] Warning: Could not get initial robot position")
            initial_position = None
        else:
            print(f"[GlueOperation] Stored initial position: X={initial_position[0]:.2f}, Y={initial_position[1]:.2f}, Z={initial_position[2]:.2f}")
        # Get contours from vision system
        contours = self.vision_service.contours
        if not contours or len(contours) == 0:
            print("[GlueOperation] No contours detected!")
            return
        print(f"[GlueOperation] Found {len(contours)} contours")

        # Store pickup position (first waypoint of first contour at z_offset)
        pickup_position = None

        # Execute each contour
        for i, contour in enumerate(contours):
            # Check if operation was stopped/paused
            if not self.is_running:
                print("[GlueOperation] Operation stopped/paused")
                break
            print(f"[GlueOperation] Executing contour {i+1}/{len(contours)}")
            # Convert contour to robot waypoints (with TCP offset applied)
            waypoints, tcp_x_offset, tcp_y_offset = self._contour_to_waypoints(contour)

            # Store first waypoint as pickup position (only for first contour)
            if i == 0 and len(waypoints) > 0:
                pickup_position = waypoints[0]
                print(f"[GlueOperation] Stored pickup position: {[round(w, 2) for w in pickup_position]}")
            if len(waypoints) < 2:
                print(f"[GlueOperation] Skipping contour {i+1} - not enough points")
                continue
            print(f"[GlueOperation] Executing {len(waypoints)} waypoints using moveCartesianPath for smooth movement")
            # Apply Gaussian smoothing to waypoints for ultra-smooth motion
            if len(waypoints) > 5:
                waypoints = self._smooth_waypoints(waypoints)
                print(f"[GlueOperation] Applied Gaussian smoothing to waypoints")
            # Log first and last waypoints for debugging
            if len(waypoints) > 0:
                print(f"[GlueOperation] First waypoint: {[round(w, 2) for w in waypoints[0]]}")
                print(f"[GlueOperation] Last waypoint: {[round(w, 2) for w in waypoints[-1]]}")
            # Check if still running before executing path
            if not self.is_running:
                print("[GlueOperation] Operation stopped/paused before path execution")
                break
            # Execute the entire path using moveCartesianPath for smooth, fast movement
            # Using velocity and acceleration from dashboard parameters
            # Decimation disabled to preserve all waypoints for maximum smoothness
            print(f"[GlueOperation] Executing ultra-smooth path with {len(waypoints)} points (vel={self.velocity}, acc={self.acceleration})...")
            ret = self.robot_service.robot.moveCartesianPath(waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            # Check if operation was stopped during execution
            if not self.is_running:
                print("[GlueOperation] Operation stopped/paused during path execution")
                break
            if ret != 0:
                print(f"[GlueOperation] Path execution failed with error code: {ret}")
                if not self.is_running:
                    break
                continue
            # Path completed successfully
            print(f"[GlueOperation] Contour {i+1} completed - executed {len(waypoints)} waypoints in smooth path")
        # After all contours complete, return to initial position using moveCartesianPath
        if self.is_running and initial_position is not None:
            print(f"[GlueOperation] Returning to initial position: X={initial_position[0]:.2f}, Y={initial_position[1]:.2f}, Z={initial_position[2]:.2f}")
            return_waypoints = [initial_position]
            return_ret = self.robot_service.robot.moveCartesianPath(return_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if return_ret != 0:
                print(f"[GlueOperation] Warning: Failed to return to initial position: {return_ret}")
            else:
                print(f"[GlueOperation] Successfully returned to initial position")

        # Drop off at z_offset height at the same position where contour was picked up
        if self.is_running and pickup_position is not None:
            print(f"[GlueOperation] Dropping to z_offset height at pickup position: {self.z_offset}mm")
            dropoff_waypoint = pickup_position
            ret = self.robot_service.robot.moveCartesianPath([dropoff_waypoint],
                                                            vel=self.velocity,
                                                            acc=self.acceleration,
                                                            decimate=False)
            if ret != 0:
                print(f"[GlueOperation] Failed to drop off: {ret}")
            else:
                print(f"[GlueOperation] Dropped off at pickup position successfully")

        # Return to initial position again after dropoff
        if self.is_running and initial_position is not None:
            print(f"[GlueOperation] Returning to initial position again after dropoff")
            return_waypoints = [initial_position]
            return_ret = self.robot_service.robot.moveCartesianPath(return_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if return_ret != 0:
                print(f"[GlueOperation] Warning: Failed to return to initial position after dropoff: {return_ret}")
            else:
                print(f"[GlueOperation] Successfully returned to initial position after dropoff")

        if self.is_running:
            print("[GlueOperation] All contours completed successfully")
        else:
            print("[GlueOperation] Operation was stopped/paused before completion")
    def _contour_to_waypoints(self, contour):
        """Convert a contour to robot waypoints with TCP offset applied"""
        waypoints = []
        # Validate contour data structure first
        if contour is None:
            print("[GlueOperation] ERROR: Contour is None!")
            return waypoints, 0.0, 0.0
        try:
            if not isinstance(contour, (list, np.ndarray)):
                print(f"[GlueOperation] ERROR: Contour is not a list or numpy array: {type(contour)}")
                return waypoints, 0.0, 0.0
            if len(contour) == 0:
                print("[GlueOperation] ERROR: Contour is empty!")
                return waypoints, 0.0, 0.0
            # Convert to numpy array if it's a list
            if isinstance(contour, list):
                contour = np.array(contour)
            print(f"[GlueOperation] Contour shape: {contour.shape}, dtype: {contour.dtype}")
        except Exception as e:
            print(f"[GlueOperation] ERROR: Failed to validate contour structure: {e}")
            import traceback
            traceback.print_exc()
            return waypoints, 0.0, 0.0
        # Get camera to robot transformation matrix
        camera_to_robot = self.vision_service.cameraToRobotMatrix
        if camera_to_robot is None:
            print("[GlueOperation] ERROR: No camera to robot calibration!")
            return waypoints, 0.0, 0.0
        # Validate the transformation matrix
        try:
            if not isinstance(camera_to_robot, np.ndarray):
                print("[GlueOperation] ERROR: camera_to_robot is not a numpy array!")
                return waypoints, 0.0, 0.0
            if camera_to_robot.shape != (3, 3):
                print(f"[GlueOperation] ERROR: camera_to_robot has invalid shape: {camera_to_robot.shape} (expected 3x3)")
                return waypoints, 0.0, 0.0
            print(f"[GlueOperation] Camera to robot matrix validated: {camera_to_robot.shape}")
        except Exception as e:
            print(f"[GlueOperation] ERROR: Failed to validate camera_to_robot matrix: {e}")
            return waypoints, 0.0, 0.0
        # Get TCP offsets from robot config (camera tool offset)
        robot_config = self.robot_service.robot_config
        tcp_x_offset = getattr(robot_config, 'tcp_x_offset', 0.0)
        tcp_y_offset = getattr(robot_config, 'tcp_y_offset', 0.0)
        print(f"[GlueOperation] Applying TCP offsets: X={tcp_x_offset}mm, Y={tcp_y_offset}mm")
        # Get current robot orientation (we'll maintain this throughout the path)
        current_pose = self.robot_service.robot.get_current_position()
        if current_pose is None or len(current_pose) < 6:
            print("[GlueOperation] ERROR: Could not get current robot position for orientation!")
            print("[GlueOperation] Please ensure robot is connected and reporting position")
            return waypoints, tcp_x_offset, tcp_y_offset
        # Always use current orientation - never hardcoded
        rx, ry, rz = current_pose[3], current_pose[4], current_pose[5]
        print(f"[GlueOperation] Using current robot orientation: RX={rx:.2f}°, RY={ry:.2f}°, RZ={rz:.2f}°")
        # Normalize angles to prevent wrapping issues (keep within -180 to +180)
        def normalize_angle(angle):
            """Normalize angle to [-180, 180] range"""
            while angle > 180:
                angle -= 360
            while angle < -180:
                angle += 360
            return angle
        rx = normalize_angle(rx)
        ry = normalize_angle(ry)
        rz = normalize_angle(rz)
        print(f"[GlueOperation] Normalized orientation: RX={rx:.2f}°, RY={ry:.2f}°, RZ={rz:.2f}°")
        # Use z_offset from parameters
        z_offset = self.z_offset
        print(f"[GlueOperation] Using Z offset: {z_offset}mm above surface")
        # Workspace bounds for validation (in mm)
        # These should match your robot's reachable workspace
        workspace_bounds = {
            'x_min': -500, 'x_max': 500,
            'y_min': -500, 'y_max': 500,
            'z_min': 1, 'z_max': 400
        }
        points_filtered = 0
        print(f"[GlueOperation] Processing {len(contour)} contour points...")
        # Process each point in the contour with maximum safety
        for idx in range(len(contour)):
            try:
                # Get point using index to avoid iterator issues
                point = contour[idx]
                if point is None:
                    continue
                # Handle different contour formats
                # OpenCV contours can be: shape (N, 1, 2) or (N, 2)
                camera_x = None
                camera_y = None
                try:
                    # Try to access as numpy array first
                    point_array = np.asarray(point)
                    if point_array.ndim == 2 and point_array.shape == (1, 2):
                        # Format: [[x, y]]
                        camera_x = float(point_array[0, 0])
                        camera_y = float(point_array[0, 1])
                    elif point_array.ndim == 1 and len(point_array) == 2:
                        # Format: [x, y]
                        camera_x = float(point_array[0])
                        camera_y = float(point_array[1])
                    elif point_array.ndim == 1 and len(point_array) > 0:
                        # Try to extract from first element
                        inner = np.asarray(point_array[0])
                        if len(inner) >= 2:
                            camera_x = float(inner[0])
                            camera_y = float(inner[1])
                    if camera_x is None or camera_y is None:
                        continue
                except Exception as e:
                    # Skip this point if we can't extract coordinates
                    continue
                # Transform to robot coordinates using homography
                try:
                    camera_point = np.array([[camera_x, camera_y]], dtype=np.float32).reshape(-1, 1, 2)
                    robot_point = cv2.perspectiveTransform(camera_point, camera_to_robot)
                    if robot_point is None or len(robot_point) == 0:
                        continue
                except Exception as e:
                    print(f"[GlueOperation] Warning: Transform failed for point {idx}: {e}")
                    continue
                # Extract robot coordinates and apply TCP offsets
                try:
                    # Note: X coordinate is negated because robot coordinate system is flipped
                    robot_x = float(robot_point[0][0][0]) - tcp_x_offset  # Negate X offset
                    robot_y = float(robot_point[0][0][1]) + tcp_y_offset
                    robot_z = z_offset  # Fixed height above surface
                except (IndexError, TypeError, ValueError) as e:
                    print(f"[GlueOperation] Warning: Error extracting coordinates for point {idx}: {e}")
                    continue
                # Validate waypoint is within workspace bounds
                if not (workspace_bounds['x_min'] <= robot_x <= workspace_bounds['x_max'] and
                        workspace_bounds['y_min'] <= robot_y <= workspace_bounds['y_max'] and
                        workspace_bounds['z_min'] <= robot_z <= workspace_bounds['z_max']):
                    points_filtered += 1
                    continue  # Skip this point
                # Create waypoint [x, y, z, rx, ry, rz]
                waypoint = [robot_x, robot_y, robot_z, rx, ry, rz]
                waypoints.append(waypoint)
            except Exception as e:
                # Skip any point that causes an error
                if idx % 100 == 0:  # Only log every 100th error to avoid spam
                    print(f"[GlueOperation] Warning: Skipped point {idx} due to error: {e}")
                continue
        if points_filtered > 0:
            print(f"[GlueOperation] Filtered {points_filtered} points outside workspace bounds")
        print(f"[GlueOperation] Generated {len(waypoints)} valid waypoints from {len(contour)} contour points")
        return waypoints, tcp_x_offset, tcp_y_offset
    def _do_stop(self, *args, **kwargs):
        print("[GlueOperation] Stopping glue operation")
        # Set flag first to stop the glue loop
        self.is_running = False
        if self.robot_service:
            # Stop robot motion - this sets command_in_progress=False in ZeroErrRobot
            # which will cause any ongoing motion commands to complete
            self.robot_service.robot.stop_motion()
            print("[GlueOperation] Robot stop_motion() called")
        # Wait for thread to finish (with timeout)
        if self.execution_thread and self.execution_thread.is_alive():
            print("[GlueOperation] Waiting for execution thread to stop...")
            self.execution_thread.join(timeout=3.0)
            if self.execution_thread.is_alive():
                print("[GlueOperation] Warning: Execution thread did not stop within timeout")
            else:
                print("[GlueOperation] Execution thread stopped successfully")
        self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.STOPPED)
    def _smooth_waypoints(self, waypoints, sigma=1.5):
        """
        Apply Gaussian smoothing to waypoints for ultra-smooth motion.
        Only smooths XYZ coordinates, preserves orientation.
        Args:
            waypoints: List of [x, y, z, rx, ry, rz] waypoints
            sigma: Gaussian kernel sigma (higher = more smoothing)
        Returns:
            Smoothed waypoints list
        """
        from scipy.ndimage import gaussian_filter1d
        if len(waypoints) < 5:
            return waypoints
        # Convert to numpy array for processing
        waypoints_array = np.array(waypoints)
        # Apply Gaussian filter to XYZ coordinates only
        waypoints_array[:, 0] = gaussian_filter1d(waypoints_array[:, 0], sigma=sigma)  # X
        waypoints_array[:, 1] = gaussian_filter1d(waypoints_array[:, 1], sigma=sigma)  # Y
        waypoints_array[:, 2] = gaussian_filter1d(waypoints_array[:, 2], sigma=sigma)  # Z
        # Keep orientation unchanged (RX, RY, RZ remain constant)
        # Convert back to list
        return waypoints_array.tolist()
    def _do_pause(self, *args, **kwargs):
        print(f"[GlueOperation] Pausing glue operation")
        # Set flag first to pause the glue loop
        self.is_running = False
        if self.robot_service:
            # Stop robot motion - this sets command_in_progress=False in ZeroErrRobot
            # which will cause any ongoing motion commands to complete
            self.robot_service.robot.stop_motion()
            print("[GlueOperation] Robot stop_motion() called")
        # Wait for thread to finish (with timeout)
        if self.execution_thread and self.execution_thread.is_alive():
            print("[GlueOperation] Waiting for execution thread to pause...")
            self.execution_thread.join(timeout=3.0)
            if self.execution_thread.is_alive():
                print("[GlueOperation] Warning: Execution thread did not pause within timeout")
            else:
                print("[GlueOperation] Execution thread paused successfully")
        self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.PAUSED)
    def _do_resume(self, *args, **kwargs):
        print(f"[GlueOperation] Resuming glue operation")
        # For now, just transition back to idle since we don't have resume capability yet
        # In a full implementation, we'd resume from where we paused
        self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.IDLE)
