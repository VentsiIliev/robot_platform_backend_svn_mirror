from core.operation_state_management import IOperation, OperationState
from modules.shared.MessageBroker import MessageBroker
from communication_layer.api.v1.topics import SystemTopics
import threading
import time
import cv2
import numpy as np


class PaintingOperation(IOperation):
    def __init__(self):
        super().__init__()
        self.broker = MessageBroker()
        self.robot_service = None
        self.vision_service = None
        self.is_running = False
        self.execution_thread = None

        # Operation parameters (can be updated from dashboard)
        self.velocity = 20
        self.acceleration = 20
        self.z_offset = 6.0
        self.lift_z = 200.0
        self.alignment_mode = "Horizontal"  # Default alignment mode
        self.iterations = 1  # Number of times to repeat entire operation
        self.wait_time = 0.0  # Wait time in seconds between iterations
        self.center_samples = 5  # Number of images to capture for median center calculation

        # Rotation parameters
        self.rotation_step = 1.0  # degrees per waypoint during 90° edge rotation (smaller = smoother)
        self.joint_rotation_step = 3.0  # degrees per step for joint 6 rotation movements

        # Contour following parameters
        self.enable_contour_following = True  # Use actual contour path instead of rectangle corners
        self.contour_simplification_epsilon = 2.0  # Douglas-Peucker epsilon for simplification (mm)
        self.min_segment_length = 3.0  # Minimum segment length to process (mm)
        self.curve_detection_angle = 150.0  # Angles below this are considered corners (degrees)
        self.rotation_lookahead_points = 5  # Number of points to look ahead for rotation calculation

        # Pressure adjustment parameters
        self.enable_pressure_adjustment = True  # Enable dynamic pressure control
        self.target_force_x = 2.0  # Target X-axis force in Newtons (adjust based on robot)
        self.force_adjustment_gain = 0.1  # mm adjustment per Newton of error
        self.force_deadband = 0.5  # Deadband in Newtons (no adjustment if within this range)

        # Contact search parameters
        self.max_search_distance = 15.0  # mm - maximum distance to search for contact
        self.search_step_size = 0.5  # mm - incremental search step
        self.contact_threshold = 1.0  # N - force indicating contact
        self.search_velocity = 5  # % - slow speed for contact search
        self.search_at_all_corners = True  # Search before each corner (True) or only at start (False)

        # === PRECISION ENHANCEMENT PARAMETERS ===
        # Force averaging for noise reduction
        self.use_force_averaging = True  # Average force over multiple samples
        self.force_samples = 5  # Number of samples (5 * 50ms = 250ms)
        self.force_sample_delay = 0.05  # seconds between samples

        # Multi-stage contact search
        self.use_gradual_approach = True  # Two-stage: coarse + fine
        self.coarse_threshold_ratio = 0.4  # 40% threshold for coarse
        self.fine_search_distance = 3.0  # mm - fine search distance
        self.fine_search_step = 0.1  # mm - precision step size
        self.contact_settle_time = 0.3  # seconds - force settling

        # Contact validation
        self.max_contact_retries = 3  # Retry attempts
        self.force_consistency_check = True  # Check force stability
        self.force_consistency_tolerance = 0.3  # N - max variation
        self.min_consecutive_contact_readings = 3  # Stable readings needed

        # Position smoothing
        self.use_exponential_smoothing = True  # Smooth adjustments
        self.position_smoothing_alpha = 0.3  # Smoothing factor
        self.max_position_change_per_step = 0.5  # mm - rate limit

        # Advanced pressure parameters
        self.max_position_adjustment = 12.0  # mm - maximum position adjustment during painting
        self.enable_rotation_adjustment = True  # Enable rotation adjustment during painting
        self.rotation_coefficient = 0.05  # deg/(mm·N) - rotation compensation coefficient
        self.max_rotation_adjustment = 2.0  # degrees - maximum rotation adjustment

        # Runtime state - effort availability detection
        self.effort_available = None  # None=unknown, True=available, False=unavailable
        self.effort_check_done = False

    def set_alignment_mode(self, mode):
        """Set alignment mode: 'Horizontal' or 'Vertical'"""
        self.alignment_mode = mode
        print(f"[PaintingOperation] Alignment mode set to: {mode}")

    def get_params(self):
        """Get current operation parameters as dict"""
        return {
            'velocity': self.velocity,
            'acceleration': self.acceleration,
            'z_offset': self.z_offset,
            'lift_z': self.lift_z,
            'rotation_step': self.rotation_step,
            'joint_rotation_step': self.joint_rotation_step,
            'iterations': self.iterations,
            'wait_time': self.wait_time,
            'center_samples': self.center_samples,
            'enable_pressure_adjustment': self.enable_pressure_adjustment,
            'target_force_x': self.target_force_x,
            'force_adjustment_gain': self.force_adjustment_gain,
            'force_deadband': self.force_deadband,
            'max_search_distance': self.max_search_distance,
            'search_step_size': self.search_step_size,
            'contact_threshold': self.contact_threshold,
            'search_velocity': self.search_velocity,
            'search_at_all_corners': self.search_at_all_corners,
            'max_position_adjustment': self.max_position_adjustment,
            'enable_rotation_adjustment': self.enable_rotation_adjustment,
            'rotation_coefficient': self.rotation_coefficient,
            'max_rotation_adjustment': self.max_rotation_adjustment,
            'enable_contour_following': self.enable_contour_following,
            'contour_simplification_epsilon': self.contour_simplification_epsilon,
            'min_segment_length': self.min_segment_length,
            'curve_detection_angle': self.curve_detection_angle,
            'rotation_lookahead_points': self.rotation_lookahead_points
        }

    def set_params(self, velocity=None, acceleration=None, z_offset=None, lift_z=None, rotation_step=None,
                   joint_rotation_step=None, iterations=None, wait_time=None,
                   center_samples=None, enable_pressure_adjustment=None, target_force_x=None, force_adjustment_gain=None, force_deadband=None,
                   max_search_distance=None, search_step_size=None, contact_threshold=None, search_velocity=None,
                   search_at_all_corners=None, max_position_adjustment=None, enable_rotation_adjustment=None,
                   rotation_coefficient=None, max_rotation_adjustment=None,
                   enable_contour_following=None, contour_simplification_epsilon=None, min_segment_length=None,
                   curve_detection_angle=None, rotation_lookahead_points=None):
        """Update operation parameters"""
        if velocity is not None:
            self.velocity = velocity
        if acceleration is not None:
            self.acceleration = acceleration
        if z_offset is not None:
            self.z_offset = z_offset
        if lift_z is not None:
            self.lift_z = lift_z
        if rotation_step is not None:
            self.rotation_step = rotation_step
        if joint_rotation_step is not None:
            self.joint_rotation_step = joint_rotation_step
        if iterations is not None:
            self.iterations = iterations
        if wait_time is not None:
            self.wait_time = wait_time
        if center_samples is not None:
            self.center_samples = center_samples
        if enable_pressure_adjustment is not None:
            self.enable_pressure_adjustment = enable_pressure_adjustment
        if target_force_x is not None:
            self.target_force_x = target_force_x
        if force_adjustment_gain is not None:
            self.force_adjustment_gain = force_adjustment_gain
        if force_deadband is not None:
            self.force_deadband = force_deadband
        if max_search_distance is not None:
            self.max_search_distance = max_search_distance
        if search_step_size is not None:
            self.search_step_size = search_step_size
        if contact_threshold is not None:
            self.contact_threshold = contact_threshold
        if search_velocity is not None:
            self.search_velocity = search_velocity
        if search_at_all_corners is not None:
            self.search_at_all_corners = search_at_all_corners
        if max_position_adjustment is not None:
            self.max_position_adjustment = max_position_adjustment
        if enable_rotation_adjustment is not None:
            self.enable_rotation_adjustment = enable_rotation_adjustment
        if rotation_coefficient is not None:
            self.rotation_coefficient = rotation_coefficient
        if max_rotation_adjustment is not None:
            self.max_rotation_adjustment = max_rotation_adjustment
        if enable_contour_following is not None:
            self.enable_contour_following = enable_contour_following
        if contour_simplification_epsilon is not None:
            self.contour_simplification_epsilon = contour_simplification_epsilon
        if min_segment_length is not None:
            self.min_segment_length = min_segment_length
        if curve_detection_angle is not None:
            self.curve_detection_angle = curve_detection_angle
        if rotation_lookahead_points is not None:
            self.rotation_lookahead_points = rotation_lookahead_points
        print(f"[PaintingOperation] Updated params: vel={self.velocity}, acc={self.acceleration}, z_offset={self.z_offset}, "
              f"lift_z={self.lift_z}, iterations={self.iterations}, wait_time={self.wait_time}s, "
              f"pressure_adj={self.enable_pressure_adjustment}, target_force={self.target_force_x}N, "
              f"max_search={self.max_search_distance}mm, contact_threshold={self.contact_threshold}N, "
              f"search_at_all_corners={self.search_at_all_corners}, contour_following={self.enable_contour_following}")

    def set_services(self, robot_service, vision_service):
        """Set the robot and vision services"""
        self.robot_service = robot_service
        self.vision_service = vision_service

    def _get_x_axis_force(self):
        """
        Calculate estimated force in X direction from joint efforts.
        Uses simplified Jacobian transpose method to estimate Cartesian forces from joint torques.

        Returns:
            float: Estimated X-axis force in Newtons, or None if not available
        """
        if not hasattr(self.robot_service.robot, 'get_joint_efforts'):
            if not self.effort_check_done:
                print("[Pressure] WARNING: Robot does not support get_joint_efforts()")
                self.effort_available = False
                self.effort_check_done = True
            return None

        efforts = self.robot_service.robot.get_joint_efforts()
        if efforts is None or len(efforts) < 6:
            if not self.effort_check_done:
                print(f"[Pressure] WARNING: No effort data available (efforts={efforts})")
                self.effort_available = False
                self.effort_check_done = True
            return None

        # Check if all efforts are zero (robot/MoveIt not reporting actual torques)
        max_effort = max(abs(e) for e in efforts)
        if max_effort < 0.001:  # All efforts essentially zero
            if not self.effort_check_done:
                print(f"[Pressure] WARNING: All joint efforts are zero - torque sensing not available")
                print(f"[Pressure] Raw joint efforts: {[f'{e:.3f}' for e in efforts]}")
                print(f"[Pressure] Contact search will be DISABLED (no force feedback)")
                print(f"[Pressure] Manual pressure adjustment during painting will also be DISABLED")
                self.effort_available = False
                self.effort_check_done = True
            return None

        # Efforts are available and non-zero
        if not self.effort_check_done:
            print(f"[Pressure] ✓ Effort sensing available, max effort: {max_effort:.3f}")
            self.effort_available = True
            self.effort_check_done = True

        # Simplified X-force estimation from joint 1, 2, and 3 efforts
        # This is a rough approximation - adjust coefficients based on your robot
        # Joint 1 (base rotation) contributes to Y-direction forces primarily
        # Joint 2 & 3 (shoulder/elbow) contribute significantly to X-direction forces
        # Typical coefficients for collaborative robots:
        force_x = (efforts[1] * 0.3 + efforts[2] * 0.5 + efforts[3] * 0.2)


        return force_x

    def _get_averaged_force(self, num_samples=None, delay=None):
        """
        Get averaged force with outlier rejection for better stability.

        Args:
            num_samples: Number of samples (default: self.force_samples)
            delay: Delay between samples (default: self.force_sample_delay)

        Returns:
            float: Averaged force or None if unavailable
        """
        if num_samples is None:
            num_samples = self.force_samples
        if delay is None:
            delay = self.force_sample_delay

        samples = []
        for i in range(num_samples):
            force = self._get_x_axis_force()
            if force is not None:
                samples.append(force)
                if i < num_samples - 1 and delay > 0:
                    time.sleep(delay)
            else:
                return None

        if len(samples) == 0:
            return None

        # Remove outliers using median absolute deviation
        if len(samples) >= 3:
            median = float(np.median(samples))
            mad = float(np.median([abs(s - median) for s in samples]))
            if mad > 0:
                # Keep samples within 2*MAD of median
                samples = [s for s in samples if abs(s - median) <= 2.0 * mad]

        if len(samples) > 0:
            avg_force = np.mean(samples)
            return avg_force
        return None

    def _check_force_consistency(self, num_samples=None):
        """
        Check if force readings are consistent (low variation).

        Returns:
            tuple: (is_consistent, mean_force, std_dev)
        """
        if num_samples is None:
            num_samples = self.force_samples

        samples = []
        for _ in range(num_samples):
            force = self._get_x_axis_force()
            if force is not None:
                samples.append(force)
                time.sleep(self.force_sample_delay)
            else:
                return (False, None, None)

        if len(samples) < 3:
            return (False, None, None)

        mean_force = np.mean(samples)
        std_dev = np.std(samples)

        is_consistent = std_dev <= self.force_consistency_tolerance

        return (is_consistent, mean_force, std_dev)

    def _find_contact_point(self, current_x, current_y, current_z, current_rx, current_ry, current_rz,
                           search_direction='x-', max_search_distance=None):
        """
        Actively search for contact point by moving in specified direction until force threshold is reached.

        Args:
            current_x, current_y, current_z: Current TCP position
            current_rx, current_ry, current_rz: Current TCP orientation
            search_direction: Direction to search ('x-', 'y-', etc.)
            max_search_distance: Maximum distance to search in mm (uses instance variable if None)

        Returns:
            tuple: (contact_x, contact_y, contact_z, found) - contact position and whether contact was found
        """
        if not self.enable_pressure_adjustment:
            return (current_x, current_y, current_z, False)

        # Use instance variable if not specified
        if max_search_distance is None:
            max_search_distance = self.max_search_distance

        # Use instance variables for search parameters
        step_size = self.search_step_size
        contact_threshold = self.contact_threshold
        search_vel = self.search_velocity

        print(f"[Pressure] ====== CONTACT SEARCH REQUESTED ======")
        print(f"[Pressure] Current position: X={current_x:.1f}, Y={current_y:.1f}, Z={current_z:.1f}")
        print(f"[Pressure] Current orientation: rX={current_rx:.1f}, rY={current_ry:.1f}, rZ={current_rz:.1f}")
        print(f"[Pressure] Search direction: {search_direction}, Max distance: {max_search_distance}mm")

        # Test force reading availability BEFORE starting search
        baseline_force = self._get_x_axis_force()

        if baseline_force is None:
            # Effort sensing not available - skip contact search
            print(f"[Pressure] ⚠ Contact search SKIPPED - effort sensing unavailable")
            print(f"[Pressure] Continuing with current position (no automatic contact detection)")
            print(f"[Pressure] TIP: Manually position contour closer to shaft before starting operation")
            return (current_x, current_y, current_z, False)

        # Effort sensing is available - proceed with contact search
        # Store baseline force MAGNITUDE to avoid sign flip issues
        baseline_magnitude = abs(baseline_force)
        print(f"[Pressure] ✓ Effort sensing available, proceeding with contact search")
        print(f"[Pressure] Baseline force: {baseline_force:.3f}N (magnitude: {baseline_magnitude:.3f}N)")
        print(f"[Pressure] Contact threshold: {contact_threshold}N")
        print(f"[Pressure] Contact will be detected when force magnitude increases significantly")

        search_x = current_x
        search_y = current_y
        search_z = current_z
        distance_traveled = 0.0

        # Track previous force magnitude for detecting increasing trend
        prev_force_magnitude = baseline_magnitude

        # Require minimum travel distance before checking for contact
        # This avoids false triggers from initial force fluctuations
        min_travel_before_check = 0.1  # mm

        # Track consecutive steps with increasing force (contact confirmation)
        consecutive_increases = 0
        required_consecutive = 2  # Need 2 consecutive force increases

        # Move incrementally until contact or max distance
        while distance_traveled < max_search_distance:
            # Calculate next position based on search direction
            prev_x, prev_y, prev_z = search_x, search_y, search_z
            if search_direction == 'x-':
                search_x -= step_size
            elif search_direction == 'x+':
                search_x += step_size
            elif search_direction == 'y-':
                search_y -= step_size
            elif search_direction == 'y+':
                search_y += step_size
            elif search_direction == 'z-':
                search_z -= step_size
            elif search_direction == 'z+':
                search_z += step_size

            # Log the actual movement
            delta_x = search_x - prev_x
            delta_y = search_y - prev_y
            delta_z = search_z - prev_z
            if abs(delta_x) > 0.01:
                print(f"[Pressure] Moving X: {prev_x:.1f} → {search_x:.1f} (delta: {delta_x:+.2f}mm)")
            if abs(delta_y) > 0.01:
                print(f"[Pressure] Moving Y: {prev_y:.1f} → {search_y:.1f} (delta: {delta_y:+.2f}mm)")
            if abs(delta_z) > 0.01:
                print(f"[Pressure] Moving Z: {prev_z:.1f} → {search_z:.1f} (delta: {delta_z:+.2f}mm)")

            # Move to search position
            ret = self.robot_service.robot.moveCartesianPath(
                [[search_x, search_y, search_z, current_rx, current_ry, current_rz]],
                vel=search_vel,  # Use configurable search velocity
                acc=search_vel,  # Match acceleration to velocity
                decimate=False
            )

            if ret != 0:
                print(f"[Pressure] Movement failed during contact search at {distance_traveled:.1f}mm")
                return (search_x, search_y, search_z, False)

            # Check force
            force_x = self._get_x_axis_force()
            if force_x is not None:
                # Use MAGNITUDE to avoid sign flip issues when robot rotates
                current_magnitude = abs(force_x)

                # Calculate magnitude increase from baseline
                magnitude_increase = current_magnitude - baseline_magnitude

                # Track if force is increasing step-to-step
                step_increase = current_magnitude - prev_force_magnitude

                # Log force every step for debugging
                print(f"[Pressure]   Force: {force_x:.2f}N (mag: {current_magnitude:.2f}N, increase: {magnitude_increase:+.2f}N, step: {step_increase:+.2f}N)")

                # Only check for contact after minimum travel distance
                if distance_traveled >= min_travel_before_check:
                    # Count consecutive force increases
                    # Lower threshold for step increase to be more sensitive
                    if step_increase > 0.1:  # Force increasing (contact trend)
                        consecutive_increases += 1
                    else:
                        consecutive_increases = 0  # Reset if force decreases

                    # Contact detected when:
                    # 1. Force magnitude increased significantly from baseline, AND
                    # 2. We have consecutive increasing force readings (confirming contact)
                    if magnitude_increase >= contact_threshold and consecutive_increases >= required_consecutive:
                        print(f"[Pressure] ✓ Contact found at {distance_traveled:.1f}mm")
                        print(f"[Pressure]   Baseline: {baseline_force:.2f}N (|{baseline_magnitude:.2f}|N)")
                        print(f"[Pressure]   Current: {force_x:.2f}N (|{current_magnitude:.2f}|N)")
                        print(f"[Pressure]   Magnitude increase: {magnitude_increase:.2f}N")
                        print(f"[Pressure]   Consecutive increases: {consecutive_increases}")

                        # Calculate backoff distance to reach target force
                        # If current force > target, we need to back off
                        target_force_magnitude = abs(self.target_force_x)
                        force_overshoot = current_magnitude - target_force_magnitude

                        # Use configurable gain to convert force error to distance (mm)
                        # Default gain 0.1 means: 1N of force error = 0.1mm of movement needed
                        backoff_distance = abs(force_overshoot * self.force_adjustment_gain)

                        # Ensure minimum backoff to avoid staying in high-force contact
                        min_backoff = 0.1  # mm
                        if backoff_distance < min_backoff:
                            backoff_distance = min_backoff

                        # Cap maximum backoff to avoid going too far
                        max_backoff = step_size * 3  # Don't back off more than 3 steps
                        if backoff_distance > max_backoff:
                            backoff_distance = max_backoff

                        print(f"[Pressure]   Target force: {target_force_magnitude:.2f}N")
                        print(f"[Pressure]   Force overshoot: {force_overshoot:.2f}N")
                        print(f"[Pressure]   Calculated backoff: {abs(force_overshoot * self.force_adjustment_gain):.2f}mm")
                        print(f"[Pressure]   Final backoff: {backoff_distance:.2f}mm (min={min_backoff}, max={max_backoff:.2f})")

                        # Calculate backoff position (opposite to search direction)
                        backoff_x = search_x
                        backoff_y = search_y
                        backoff_z = search_z

                        if search_direction == 'x-':
                            backoff_x += backoff_distance
                        elif search_direction == 'x+':
                            backoff_x -= backoff_distance
                        elif search_direction == 'y-':
                            backoff_y += backoff_distance
                        elif search_direction == 'y+':
                            backoff_y -= backoff_distance
                        elif search_direction == 'z-':
                            backoff_z += backoff_distance
                        elif search_direction == 'z+':
                            backoff_z -= backoff_distance

                        # Move to backoff position
                        ret = self.robot_service.robot.moveCartesianPath(
                            [[backoff_x, backoff_y, backoff_z, current_rx, current_ry, current_rz]],
                            vel=search_vel, acc=search_vel, decimate=False
                        )

                        if ret != 0:
                            print(f"[Pressure] ⚠ Backoff movement failed, using contact position")
                            return (search_x, search_y, search_z, True)

                        # Verify final force after backoff
                        final_force = self._get_x_axis_force()
                        if final_force is not None:
                            final_magnitude = abs(final_force)
                            final_error = abs(final_magnitude - target_force_magnitude)
                            print(f"[Pressure] ✓ Final position: X={backoff_x:.2f}, Y={backoff_y:.2f}, Z={backoff_z:.2f}")
                            print(f"[Pressure]   Final force: {final_force:.2f}N (magnitude: {final_magnitude:.2f}N)")
                            print(f"[Pressure]   Force error from target: {final_error:.2f}N")

                            # Warn if significantly off target (> 5N or > 50% of target)
                            if final_error > 5.0 or (target_force_magnitude > 0 and final_error > target_force_magnitude * 0.5):
                                print(f"[Pressure] ⚠ WARNING: Final force significantly differs from target!")
                                print(f"[Pressure]   Consider adjusting: target_force_x={self.target_force_x}N or force_adjustment_gain={self.force_adjustment_gain}")

                        return (backoff_x, backoff_y, backoff_z, True)

                # Update previous magnitude for next iteration
                prev_force_magnitude = current_magnitude
            else:
                # Force unavailable - should not reach here due to pre-check
                print(f"[Pressure] ERROR: Force became unavailable during search at {distance_traveled:.1f}mm")
                return (search_x, search_y, search_z, False)

            distance_traveled += step_size

            # Safety check - don't continue if stopped
            if not self.is_running:
                return (search_x, search_y, search_z, False)

        print(f"[Pressure] ⚠ No contact found within {max_search_distance}mm")
        return (search_x, search_y, search_z, False)

    def _find_contact_point_precise(self, current_x, current_y, current_z,
                                     current_rx, current_ry, current_rz,
                                     search_direction='x-', max_search_distance=None):
        """
        IMPROVED precision contact search with two-stage approach and force averaging.

        Stage 1 (Coarse): Fast movement with standard step size until 40% threshold
        Stage 2 (Fine): Slow movement with 0.1mm steps for precise positioning

        Features:
        - Force averaging with outlier rejection
        - Consistency checking
        - Force settling time after contact
        - Automatic retry on failure
        - Exponential smoothing for final position

        Returns:
            tuple: (final_x, final_y, final_z, contact_found)
        """
        if not self.use_gradual_approach:
            # Fall back to standard method
            return self._find_contact_point(current_x, current_y, current_z,
                                           current_rx, current_ry, current_rz,
                                           search_direction, max_search_distance)

        if max_search_distance is None:
            max_search_distance = self.max_search_distance

        print(f"[PrecisionSearch] ====== PRECISION CONTACT SEARCH ======")
        print(f"[PrecisionSearch] Using two-stage approach with force averaging")

        # Retry loop
        for attempt in range(self.max_contact_retries):
            if attempt > 0:
                print(f"[PrecisionSearch] === Retry attempt {attempt + 1}/{self.max_contact_retries} ===")

            # Get baseline force with averaging
            if self.use_force_averaging:
                baseline_force = self._get_averaged_force()
                print(f"[PrecisionSearch] Baseline (averaged): {baseline_force:.3f}N")
            else:
                baseline_force = self._get_x_axis_force()

            if baseline_force is None:
                print(f"[PrecisionSearch] ⚠ Force sensing unavailable")
                return (current_x, current_y, current_z, False)

            # Check force consistency
            if self.force_consistency_check and attempt == 0:
                is_consistent, mean_force, std_dev = self._check_force_consistency()
                print(f"[PrecisionSearch] Baseline consistency: {is_consistent} (std={std_dev:.3f}N)")
                if not is_consistent:
                    print(f"[PrecisionSearch] ⚠ WARNING: Force readings are noisy")

            baseline_magnitude = abs(baseline_force)
            coarse_threshold = self.contact_threshold * self.coarse_threshold_ratio

            # === STAGE 1: COARSE SEARCH ===
            print(f"[PrecisionSearch] === Stage 1: Coarse Search ===")
            print(f"[PrecisionSearch] Threshold: {coarse_threshold:.2f}N (40% of {self.contact_threshold}N)")

            search_x, search_y, search_z = current_x, current_y, current_z
            distance_traveled = 0.0
            coarse_contact_found = False
            max_coarse_distance = max_search_distance - self.fine_search_distance

            consecutive_increases = 0
            prev_force_mag = baseline_magnitude
            current_force = None  # Initialize

            while distance_traveled < max_coarse_distance and not coarse_contact_found:
                # Calculate next position
                if search_direction == 'x-':
                    search_x -= self.search_step_size
                elif search_direction == 'x+':
                    search_x += self.search_step_size
                elif search_direction == 'y-':
                    search_y -= self.search_step_size
                elif search_direction == 'y+':
                    search_y += self.search_step_size
                elif search_direction == 'z-':
                    search_z -= self.search_step_size
                elif search_direction == 'z+':
                    search_z += self.search_step_size

                # Move
                ret = self.robot_service.robot.moveCartesianPath(
                    [[search_x, search_y, search_z, current_rx, current_ry, current_rz]],
                    vel=self.search_velocity, acc=self.search_velocity, decimate=False
                )

                if ret != 0:
                    break

                # Check force
                if self.use_force_averaging:
                    current_force = self._get_averaged_force(3, 0.03)  # Quick average
                else:
                    current_force = self._get_x_axis_force()

                if current_force is None:
                    break

                current_magnitude = abs(current_force)
                magnitude_increase = current_magnitude - baseline_magnitude
                step_increase = current_magnitude - prev_force_mag

                # Track consecutive increases
                if step_increase > 0.1:
                    consecutive_increases += 1
                else:
                    consecutive_increases = 0

                # Coarse contact detected
                if magnitude_increase >= coarse_threshold and consecutive_increases >= 2:
                    coarse_contact_found = True
                    print(f"[PrecisionSearch] ✓ Coarse contact at {distance_traveled:.1f}mm, force increase: {magnitude_increase:.2f}N")

                prev_force_mag = current_magnitude
                distance_traveled += self.search_step_size

                if not self.is_running:
                    return (search_x, search_y, search_z, False)

            if not coarse_contact_found and distance_traveled >= max_coarse_distance:
                print(f"[PrecisionSearch] No coarse contact found, trying fine search")

            # === STAGE 2: FINE SEARCH ===
            print(f"[PrecisionSearch] === Stage 2: Fine Positioning ===")
            print(f"[PrecisionSearch] Step size: {self.fine_search_step}mm, Distance: {self.fine_search_distance}mm")

            fine_distance = 0.0
            consecutive_stable = 0
            prev_force_mag = abs(current_force) if current_force else baseline_magnitude

            while fine_distance < self.fine_search_distance:
                # Fine step
                if search_direction == 'x-':
                    search_x -= self.fine_search_step
                elif search_direction == 'x+':
                    search_x += self.fine_search_step
                elif search_direction == 'y-':
                    search_y -= self.fine_search_step
                elif search_direction == 'y+':
                    search_y += self.fine_search_step
                elif search_direction == 'z-':
                    search_z -= self.fine_search_step
                elif search_direction == 'z+':
                    search_z += self.fine_search_step

                # Slow precise movement
                ret = self.robot_service.robot.moveCartesianPath(
                    [[search_x, search_y, search_z, current_rx, current_ry, current_rz]],
                    vel=self.search_velocity * 0.7,  # Even slower
                    acc=self.search_velocity * 0.7,
                    decimate=False
                )

                if ret != 0:
                    break

                # Precise force reading with averaging
                if self.use_force_averaging:
                    current_force = self._get_averaged_force()
                else:
                    current_force = self._get_x_axis_force()

                if current_force is None:
                    break

                current_magnitude = abs(current_force)
                magnitude_increase = current_magnitude - baseline_magnitude
                step_increase = current_magnitude - prev_force_mag

                # Count stable contact readings
                if abs(step_increase) < 0.1 and magnitude_increase >= self.contact_threshold:
                    consecutive_stable += 1
                else:
                    consecutive_stable = 0

                # Precise contact with stability check
                if magnitude_increase >= self.contact_threshold and consecutive_stable >= self.min_consecutive_contact_readings:
                    print(f"[PrecisionSearch] ✓ Precise contact! Force: {current_force:.2f}N, Increase: {magnitude_increase:.2f}N")

                    # Wait for force to settle
                    if self.contact_settle_time > 0:
                        print(f"[PrecisionSearch] Settling for {self.contact_settle_time}s...")
                        time.sleep(self.contact_settle_time)
                        settled_force = self._get_averaged_force()
                        if settled_force:
                            print(f"[PrecisionSearch] Settled force: {settled_force:.2f}N")
                            current_force = settled_force
                            current_magnitude = abs(settled_force)

                    # Verify consistency
                    if self.force_consistency_check:
                        is_consistent, mean_force, std_dev = self._check_force_consistency()
                        if not is_consistent:
                            print(f"[PrecisionSearch] ⚠ Force not consistent after contact (std={std_dev:.3f}N)")
                            if attempt < self.max_contact_retries - 1:
                                print(f"[PrecisionSearch] Retrying...")
                                continue  # Retry outer loop
                            else:
                                print(f"[PrecisionSearch] Proceeding despite inconsistency")

                    # Calculate precise backoff to target force
                    target_magnitude = abs(self.target_force_x)
                    force_error = current_magnitude - target_magnitude
                    backoff_distance = force_error * self.force_adjustment_gain

                    # Clamp backoff
                    backoff_distance = max(0.05, min(backoff_distance, 2.0))  # 0.05mm to 2mm

                    print(f"[PrecisionSearch] Target: {target_magnitude:.2f}N, Error: {force_error:.2f}N, Backoff: {backoff_distance:.3f}mm")

                    # Apply backoff
                    backoff_x, backoff_y, backoff_z = search_x, search_y, search_z
                    if search_direction == 'x-':
                        backoff_x += backoff_distance
                    elif search_direction == 'x+':
                        backoff_x -= backoff_distance
                    elif search_direction == 'y-':
                        backoff_y += backoff_distance
                    elif search_direction == 'y+':
                        backoff_y -= backoff_distance
                    elif search_direction == 'z-':
                        backoff_z += backoff_distance
                    elif search_direction == 'z+':
                        backoff_z -= backoff_distance

                    ret = self.robot_service.robot.moveCartesianPath(
                        [[backoff_x, backoff_y, backoff_z, current_rx, current_ry, current_rz]],
                        vel=self.search_velocity * 0.5, acc=self.search_velocity * 0.5, decimate=False
                    )

                    # Final verification
                    if ret == 0:
                        time.sleep(0.1)  # Brief settle
                        final_force = self._get_averaged_force()
                        if final_force:
                            final_magnitude = abs(final_force)
                            final_error = abs(final_magnitude - target_magnitude)
                            print(f"[PrecisionSearch] ✓ FINAL: Force={final_force:.2f}N, Error={final_error:.2f}N")
                            print(f"[PrecisionSearch] Position: X={backoff_x:.2f}, Y={backoff_y:.2f}, Z={backoff_z:.2f}")
                        return (backoff_x, backoff_y, backoff_z, True)
                    else:
                        return (search_x, search_y, search_z, True)

                prev_force_mag = current_magnitude
                fine_distance += self.fine_search_step

                if not self.is_running:
                    return (search_x, search_y, search_z, False)

            # If we reach here, this attempt failed
            if attempt < self.max_contact_retries - 1:
                print(f"[PrecisionSearch] Attempt {attempt + 1} failed, retrying...")
                # Reset to start position for retry
                search_x, search_y, search_z = current_x, current_y, current_z
            else:
                print(f"[PrecisionSearch] All attempts failed")

        print(f"[PrecisionSearch] ⚠ No precise contact found after {self.max_contact_retries} attempts")
        return (current_x, current_y, current_z, False)

    def _calculate_pressure_adjustment(self, current_force_x):
        """
        Calculate X position adjustment based on measured force vs target.
        Used during painting to maintain constant pressure against shaft.

        Args:
            current_force_x: Current force in X direction (Newtons)

        Returns:
            float: X position adjustment in mm (positive = move in +X direction, toward shaft)
        """
        if current_force_x is None or not self.enable_pressure_adjustment:
            return 0.0

        # Calculate force error
        force_error = self.target_force_x - current_force_x

        # Apply deadband to avoid oscillations
        if abs(force_error) < self.force_deadband:
            return 0.0

        # Calculate adjustment: if measured force is too low, move toward shaft (+X in most cases)
        # if measured force is too high, move away from shaft (-X)
        adjustment = -force_error * self.force_adjustment_gain

        # Allow larger adjustments (configurable via settings)
        adjustment = max(-self.max_position_adjustment, min(self.max_position_adjustment, adjustment))

        return adjustment

    def _calculate_rotation_adjustment(self, current_force_x, x_adjustment):
        """
        Calculate rZ rotation adjustment to compensate for contour rotation when pressing onto shaft.

        When the robot presses the contour onto the shaft (X+ movement), the contour may rotate
        slightly due to friction and contact geometry. This method calculates a counter-rotation
        to keep the contour stable.

        Args:
            current_force_x: Current force in X direction (Newtons)
            x_adjustment: Current X position adjustment in mm

        Returns:
            float: rZ rotation adjustment in degrees (positive = CCW, negative = CW)
        """
        if current_force_x is None or not self.enable_pressure_adjustment or not self.enable_rotation_adjustment or abs(x_adjustment) < 0.01:
            return 0.0

        # Rotation correction is proportional to:
        # 1. Force magnitude (higher force = more friction = more rotation tendency)
        # 2. X adjustment magnitude (larger movement = more chance for rotation)

        # Use configurable coefficient
        rotation_adjustment = x_adjustment * abs(current_force_x) * self.rotation_coefficient

        # Limit rotation adjustment using configurable max
        rotation_adjustment = max(-self.max_rotation_adjustment, min(self.max_rotation_adjustment, rotation_adjustment))

        return rotation_adjustment

    def _do_start(self, *args, **kwargs):
        print(f"[PaintingOperation] Starting painting operation")

        if not self.robot_service or not self.vision_service:
            print("[PaintingOperation] ERROR: Services not set!")
            self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.ERROR)
            return

        # Start execution in background thread
        self.is_running = True
        self.execution_thread = threading.Thread(target=self._execute_painting, daemon=True)
        self.execution_thread.start()

    def _execute_painting(self):
        """Execute painting in background thread"""
        try:
            import time

            # Execute the painting fsequence for the specified number of iterations
            for iteration in range(self.iterations):
                if not self.is_running:
                    print(f"[PaintingOperation] Operation stopped before iteration {iteration + 1}")
                    break

                print(f"[PaintingOperation] Starting iteration {iteration + 1}/{self.iterations}")
                self._run_painting_sequence()

                # Wait between iterations (except after the last one)
                if iteration < self.iterations - 1 and self.wait_time > 0:
                    print(f"[PaintingOperation] Waiting {self.wait_time}s before next iteration...")
                    time.sleep(self.wait_time)

            print(f"[PaintingOperation] Completed all {self.iterations} iteration(s)")
        except Exception as e:
            print(f"[PaintingOperation] Error during execution: {e}")
            import traceback
            traceback.print_exc()
            self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.ERROR)
        finally:
            if self.is_running:
                # Only publish IDLE if we weren't stopped
                self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.IDLE)
                self.is_running = False

    def _run_painting_sequence(self):
        """Main painting sequence - move around contours in XZ plane while rotating rZ"""
        # Store initial position to return to after operation
        initial_position = self.robot_service.robot.get_current_position()
        if initial_position is None:
            print("[PaintingOperation] Warning: Could not get initial robot position")
            initial_position = None
        else:
            print(f"[PaintingOperation] Stored initial position: X={initial_position[0]:.2f}, Y={initial_position[1]:.2f}, Z={initial_position[2]:.2f}")

        # Check Joint 6 and rotate to 203 degrees if needed
        if not self._ensure_joint6_at_target():
            print("[PaintingOperation] Failed to ensure Joint 6 at target position")
            return

        # Get contours from vision system
        contours = self.vision_service.contours
        if not contours or len(contours) == 0:
            print("[PaintingOperation] No contours detected!")
            return

        print(f"[PaintingOperation] Found {len(contours)} contours")

        # Get PAINTING_POS from robot settings
        painting_pos = self._get_painting_pos()
        if painting_pos is None:
            print("[PaintingOperation] ERROR: PAINTING_POS not configured in robot settings!")
            return

        # Initialize pickup_position to store where contour was picked up
        pickup_position = None

        # Execute each contour
        for i, contour in enumerate(contours):
            # Check if operation was stopped/paused
            if not self.is_running:
                print("[PaintingOperation] Operation stopped/paused")
                break

            print(f"[PaintingOperation] Processing contour {i+1}/{len(contours)}")

            # Calculate median center point of contour from multiple samples
            if self.center_samples > 1:
                center_point = self._get_median_contour_center(i)
            else:
                # Single sample - use traditional method
                center_point = self._calculate_contour_center(contour)

            if center_point is None:
                print(f"[PaintingOperation] Skipping contour {i+1} - could not calculate center")
                continue

            print(f"[PaintingOperation] Contour center: camera_x={center_point[0]:.2f}, camera_y={center_point[1]:.2f}")

            # Convert center point to robot coordinates
            robot_center = self._camera_to_robot_point(center_point)
            if robot_center is None:
                print(f"[PaintingOperation] Skipping contour {i+1} - could not convert center to robot coordinates")
                continue

            # Get current robot orientation
            current_pose = self.robot_service.robot.get_current_position()
            if current_pose is None or len(current_pose) < 6:
                print("[PaintingOperation] ERROR: Could not get current robot position!")
                return

            rx, ry = current_pose[3], current_pose[4]

            # Calculate the contour's current angle for pickup
            contour_angle = self._calculate_contour_angle(contour)
            print(f"[PaintingOperation] Contour angle from minAreaRect: {contour_angle:.2f}°")

            # Match Pick and Place logic: final_orientation = rz - orientation
            # We want to align with the contour, so we negate the angle
            pickup_rz = -contour_angle
            print(f"[PaintingOperation] Pickup rZ (negated): {pickup_rz:.2f}°")

            # Store pickup position for later dropoff
            pickup_position = [robot_center[0], robot_center[1], self.z_offset, rx, ry, pickup_rz]

            # Activate Y0 relay BEFORE moving to pickup (vacuum pump ON)
            from modules.modbusCommunication.ModbusController import ModbusController
            relay = ModbusController.get_relay_controller()
            if relay:
                relay.write_output(0, True)
                print(f"[PaintingOperation] Y0 ON - Vacuum pump activated")

            # Create waypoint at center with z_offset and pickup angle as rZ
            center_waypoint = [robot_center[0], robot_center[1], self.z_offset, rx, ry, pickup_rz]
            print(f"[PaintingOperation] Moving to center: X={center_waypoint[0]:.2f}, Y={center_waypoint[1]:.2f}, Z={center_waypoint[2]:.2f}, rZ={pickup_rz:.2f}°")

            # Move to center point with contour-aligned orientation
            ret = self.robot_service.robot.moveCartesianPath([center_waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to move to center point: {ret}")
                if not self.is_running:
                    break
                continue


            # Check if still running
            if not self.is_running:
                print("[PaintingOperation] Operation stopped/paused")
                break

            # Lift Z to lift_z height (maintaining pickup angle)
            lift_waypoint = [robot_center[0], robot_center[1], self.lift_z, rx, ry, pickup_rz]
            print(f"[PaintingOperation] Lifting Z to {self.lift_z}mm")

            ret = self.robot_service.robot.moveCartesianPath([lift_waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to lift Z: {ret}")
                if not self.is_running:
                    break
                continue

            # Y0 stays ON to maintain vacuum during painting operation

            # Check if still running
            if not self.is_running:
                print("[PaintingOperation] Operation stopped/paused")
                break

            # Rotate rZ to straighten the contour based on alignment mode
            current_pose = self.robot_service.robot.get_current_position()
            straightened_rz = 90.0  # Default to horizontal

            if current_pose and len(current_pose) >= 6:
                # Horizontal alignment = 90°, Vertical alignment = 0°
                if self.alignment_mode == "Horizontal":
                    straightened_rz = 90.0
                else:  # Vertical
                    straightened_rz = 0.0

                print(f"[PaintingOperation] Rotating rZ to {straightened_rz}° to straighten contour ({self.alignment_mode})")
                straighten_waypoint = [current_pose[0], current_pose[1], current_pose[2],
                                      current_pose[3], current_pose[4], straightened_rz]
                ret = self.robot_service.robot.moveCartesianPath([straighten_waypoint],
                                                                vel=self.velocity,
                                                                acc=self.acceleration,
                                                                decimate=False)
                if ret != 0:
                    print(f"[PaintingOperation] Failed to straighten contour: {ret}")
                else:
                    print(f"[PaintingOperation] Contour straightened successfully to {self.alignment_mode}")

            # Check if still running
            if not self.is_running:
                print("[PaintingOperation] Operation stopped/paused")
                break

            # Get current position after straightening (this is where the center is now)
            current_pose = self.robot_service.robot.get_current_position()
            if current_pose is None or len(current_pose) < 6:
                print("[PaintingOperation] ERROR: Could not get current position after straightening")
                continue

            current_center = (current_pose[0], current_pose[1])

            # Decide painting strategy based on contour complexity
            if self.enable_contour_following:
                # Analyze contour to determine painting method
                analysis = self._analyze_contour_complexity(contour)
                print(f"[PaintingOperation] Contour complexity: corners={analysis['corner_count']}, rectangular={analysis['is_rectangular']}, curves={analysis['has_curves']}")

                # Use contour following for non-rectangular or curved shapes
                if not analysis['is_rectangular'] or analysis['has_curves']:
                    print(f"[PaintingOperation] Using contour-following mode for complex shape")
                    ret = self._execute_contour_following_painting(contour, painting_pos, current_pose, robot_center)
                    if ret != 0:
                        print(f"[PaintingOperation] Failed to execute contour following: {ret}")
                        if not self.is_running:
                            break
                        continue

                    print(f"[PaintingOperation] Contour {i+1} completed using contour-following")
                    rotation_count = 0  # No corner rotations needed
                else:
                    print(f"[PaintingOperation] Using traditional corner painting for rectangular shape")
                    # Get contour corners for traditional corner painting
                    corners_robot = self._get_straightened_contour_corners(contour, robot_center, straightened_rz, current_center)
                    if corners_robot is None or len(corners_robot) != 4:
                        print(f"[PaintingOperation] Failed to get contour corners")
                        continue

                    ret, rotation_count = self._execute_corner_painting(corners_robot, painting_pos, straightened_rz, current_pose)
                    if ret != 0:
                        print(f"[PaintingOperation] Failed to execute corner painting: {ret}")
                        if not self.is_running:
                            break
                        continue

                    print(f"[PaintingOperation] Contour {i+1} completed - painted all corners")
            else:
                # Traditional corner painting only
                print(f"[PaintingOperation] Using traditional corner painting (contour following disabled)")
                corners_robot = self._get_straightened_contour_corners(contour, robot_center, straightened_rz, current_center)
                if corners_robot is None or len(corners_robot) != 4:
                    print(f"[PaintingOperation] Failed to get contour corners")
                    continue

                # Execute corner painting sequence
                # Returns (status, rotation_count) where rotation_count is number of 90° rotations performed
                ret, rotation_count = self._execute_corner_painting(corners_robot, painting_pos, straightened_rz, current_pose)
                if ret != 0:
                    print(f"[PaintingOperation] Failed to execute corner painting: {ret}")
                    if not self.is_running:
                        break
                    continue

                print(f"[PaintingOperation] Contour {i+1} completed - painted all corners")

            # Move back to initial position before reversing rotations
            if self.is_running and initial_position is not None:
                current_pose_after_painting = self.robot_service.robot.get_current_position()
                if current_pose_after_painting and len(current_pose_after_painting) >= 6:
                    print(f"[PaintingOperation] Moving to initial position before reversing rotations")
                    move_to_initial = [initial_position[0], initial_position[1], initial_position[2],
                                      initial_position[3], initial_position[4], current_pose_after_painting[5]]
                    ret = self.robot_service.robot.moveCartesianPath([move_to_initial],
                                                                    vel=self.velocity,
                                                                    acc=self.acceleration,
                                                                    decimate=False)
                    if ret != 0:
                        print(f"[PaintingOperation] Warning: Failed to move to initial position before reverse rotation: {ret}")
                else:
                    print(f"[PaintingOperation] Warning: Could not get current position after painting")

            # Reverse the rotations to return to original orientation
            # Corner painting performs 3 rotations of +90° each, so we need 3 rotations of -90° each
            if rotation_count > 0 and self.is_running:
                print(f"[PaintingOperation] Reversing {rotation_count} x 90° rotations with incremental -90° steps")

                # Determine which rotation axis was used
                plane, rotation_axis = self._detect_painting_mode(painting_pos)

                # Perform incremental reverse rotations
                for step in range(rotation_count):
                    if not self.is_running:
                        break

                    current_pose = self.robot_service.robot.get_current_position()
                    if not current_pose or len(current_pose) < 6:
                        print(f"[PaintingOperation] Failed to get current position for reverse rotation")
                        break

                    if rotation_axis == 'rZ':
                        # Single -90° rotation in rZ
                        current_rz = current_pose[5]
                        target_rz = current_rz - 90.0
                        while target_rz > 180:
                            target_rz -= 360
                        while target_rz < -180:
                            target_rz += 360

                        print(f"[PaintingOperation] Reverse rotation {step+1}/{rotation_count}: rZ {current_rz:.1f}° → {target_rz:.1f}°")
                        reverse_waypoint = [current_pose[0], current_pose[1], current_pose[2],
                                          current_pose[3], current_pose[4], target_rz]
                        ret = self.robot_service.robot.moveCartesianPath([reverse_waypoint],
                                                                        vel=self.velocity,
                                                                        acc=self.acceleration,
                                                                        decimate=False)
                        if ret != 0:
                            print(f"[PaintingOperation] Warning: Failed reverse rotation {step+1}")

                    elif rotation_axis == 'rY':
                        # Single -90° rotation in rY
                        current_ry = current_pose[4]
                        target_ry = current_ry - 90.0
                        while target_ry > 180:
                            target_ry -= 360
                        while target_ry < -180:
                            target_ry += 360

                        print(f"[PaintingOperation] Reverse rotation {step+1}/{rotation_count}: rY {current_ry:.1f}° → {target_ry:.1f}°")
                        reverse_waypoint = [current_pose[0], current_pose[1], current_pose[2],
                                          current_pose[3], target_ry, current_pose[5]]
                        ret = self.robot_service.robot.moveCartesianPath([reverse_waypoint],
                                                                        vel=self.velocity,
                                                                        acc=self.acceleration,
                                                                        decimate=False)
                        if ret != 0:
                            print(f"[PaintingOperation] Warning: Failed reverse rotation {step+1}")

                print(f"[PaintingOperation] Completed {rotation_count} incremental reverse rotations")


            # # COMMENTED OUT: Rotation painting movements
            # # Move to PAINTING_POS
            # print(f"[PaintingOperation] Moving to PAINTING_POS: {painting_pos}")
            # ret = self.robot_service.robot.moveCartesianPath([painting_pos], vel=self.velocity, acc=self.acceleration, decimate=False)
            # if ret != 0:
            #     print(f"[PaintingOperation] Failed to move to PAINTING_POS: {ret}")
            #     if not self.is_running:
            #         break
            #     continue
            #
            # # Check if still running
            # if not self.is_running:
            #     print("[PaintingOperation] Operation stopped/paused")
            #     break
            #
            # # Use PAINTING_POS orientation for painting movements
            # paint_rx, paint_ry, paint_rz = painting_pos[3], painting_pos[4], painting_pos[5]
            # paint_z = painting_pos[2]  # Z position from PAINTING_POS (shaft axis)
            #
            # # Paint all 4 edges of the contour with smaller rotation increments
            # # Edge 1: Top edge
            # print(f"[PaintingOperation] Painting top edge")
            # top_waypoints = self._generate_edge_waypoints(contour, paint_z, paint_rx, paint_ry, paint_rz, edge='top')
            # if len(top_waypoints) > 0:
            #     ret = self.robot_service.robot.moveCartesianPath(top_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            #     if ret != 0:
            #         print(f"[PaintingOperation] Failed to execute top edge: {ret}")
            #         if not self.is_running:
            #             break
            #         continue
            #     else:
            #         print(f"[PaintingOperation] Top edge completed successfully")
            #
            # if not self.is_running:
            #     break
            #
            # # Rotate rZ by 90 degrees
            # current_pose = self.robot_service.robot.get_current_position()
            # if current_pose and len(current_pose) >= 6:
            #     paint_rz += 90
            #     while paint_rz > 180:
            #         paint_rz -= 360
            #     print(f"[PaintingOperation] Rotating rZ to {paint_rz}°")
            #     rotate_waypoint = [current_pose[0], current_pose[1], current_pose[2], paint_rx, paint_ry, paint_rz]
            #     self.robot_service.robot.moveCartesianPath([rotate_waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            #
            # # Edge 2: Right edge
            # print(f"[PaintingOperation] Painting right edge")
            # right_waypoints = self._generate_edge_waypoints(contour, paint_z, paint_rx, paint_ry, paint_rz, edge='right')
            # if len(right_waypoints) > 0:
            #     ret = self.robot_service.robot.moveCartesianPath(right_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            #     if ret != 0:
            #         print(f"[PaintingOperation] Failed to execute right edge: {ret}")
            #         if not self.is_running:
            #             break
            #         continue
            #     else:
            #         print(f"[PaintingOperation] Right edge completed successfully")
            #
            # if not self.is_running:
            #     break
            #
            # # Rotate rZ by 90 degrees
            # current_pose = self.robot_service.robot.get_current_position()
            # if current_pose and len(current_pose) >= 6:
            #     paint_rz += 90
            #     while paint_rz > 180:
            #         paint_rz -= 360
            #     print(f"[PaintingOperation] Rotating rZ to {paint_rz}°")
            #     rotate_waypoint = [current_pose[0], current_pose[1], current_pose[2], paint_rx, paint_ry, paint_rz]
            #     self.robot_service.robot.moveCartesianPath([rotate_waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            #
            # # Edge 3: Bottom edge
            # print(f"[PaintingOperation] Painting bottom edge")
            # bottom_waypoints = self._generate_edge_waypoints(contour, paint_z, paint_rx, paint_ry, paint_rz, edge='bottom')
            # if len(bottom_waypoints) > 0:
            #     ret = self.robot_service.robot.moveCartesianPath(bottom_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            #     if ret != 0:
            #         print(f"[PaintingOperation] Failed to execute bottom edge: {ret}")
            #         if not self.is_running:
            #             break
            #         continue
            #     else:
            #         print(f"[PaintingOperation] Bottom edge completed successfully")
            #
            # if not self.is_running:
            #     break
            #
            # # Rotate rZ by 90 degrees
            # current_pose = self.robot_service.robot.get_current_position()
            # if current_pose and len(current_pose) >= 6:
            #     paint_rz += 90
            #     while paint_rz > 180:
            #         paint_rz -= 360
            #     print(f"[PaintingOperation] Rotating rZ to {paint_rz}°")
            #     rotate_waypoint = [current_pose[0], current_pose[1], current_pose[2], paint_rx, paint_ry, paint_rz]
            #     self.robot_service.robot.moveCartesianPath([rotate_waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            #
            # # Edge 4: Left edge
            # print(f"[PaintingOperation] Painting left edge")
            # left_waypoints = self._generate_edge_waypoints(contour, paint_z, paint_rx, paint_ry, paint_rz, edge='left')
            # if len(left_waypoints) > 0:
            #     ret = self.robot_service.robot.moveCartesianPath(left_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            #     if ret != 0:
            #         print(f"[PaintingOperation] Failed to execute left edge: {ret}")
            #         if not self.is_running:
            #             break
            #         continue
            #     else:
            #         print(f"[PaintingOperation] Left edge completed successfully")
            #
            # print(f"[PaintingOperation] Contour {i+1} completed - painted all 4 edges")

        # After all contours complete, return to initial position using moveCartesianPath
        # Apply TCP X offset to this first return
        if self.is_running and initial_position is not None:
            # Get TCP X offset from robot config
            robot_config = self.robot_service.robot_config
            tcp_x_offset = getattr(robot_config, 'tcp_x_offset', 0.0)
            #go to contour center with robot center transformation applied instead of at initial position
            #return_position = list(robot_center)
            #return_position[0] = robot_center[0]
            #rx, ry = current_pose[3], current_pose[4]
            # Apply TCP X offset to initial position
            return_position = list(initial_position)
            return_position[0] = initial_position[0]

            print(f"[PaintingOperation] Returning to initial position with TCP X offset ({tcp_x_offset}mm): X={return_position[0]:.2f}, Y={return_position[1]:.2f}, Z={return_position[2]:.2f}")
            return_waypoints = [return_position]
            return_ret = self.robot_service.robot.moveCartesianPath(return_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if return_ret != 0:
                print(f"[PaintingOperation] Warning: Failed to return to initial position: {return_ret}")
            else:
                print(f"[PaintingOperation] Successfully returned to initial position with TCP offset")

        # Drop off at z_offset height at the same position where contour was picked up
        if self.is_running and pickup_position is not None:
            print(f"[PaintingOperation] Dropping to z_offset height at pickup position: {self.z_offset}mm")
            dropoff_waypoint = pickup_position
            ret = self.robot_service.robot.moveCartesianPath([dropoff_waypoint],
                                                            vel=self.velocity,
                                                            acc=self.acceleration,
                                                            decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to drop off: {ret}")
            else:
                print(f"[PaintingOperation] Dropped off at pickup position successfully")

                # Deactivate Y0 relay to release vacuum
                from modules.modbusCommunication.ModbusController import ModbusController
                relay = ModbusController.get_relay_controller()
                if relay:
                    relay.write_output(0, False)
                    print(f"[PaintingOperation] Y0 deactivated - vacuum released, part dropped")

        # Return to initial position again after dropoff
        if self.is_running and initial_position is not None:
            print(f"[PaintingOperation] Returning to initial position again after dropoff")
            return_waypoints = [initial_position]
            return_ret = self.robot_service.robot.moveCartesianPath(return_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if return_ret != 0:
                print(f"[PaintingOperation] Warning: Failed to return to initial position after dropoff: {return_ret}")
            else:
                print(f"[PaintingOperation] Successfully returned to initial position after dropoff")

        if self.is_running:
            print("[PaintingOperation] All contours completed successfully")
        else:
            print("[PaintingOperation] Operation was stopped/paused before completion")

    def _calculate_contour_center(self, contour):
        """Calculate the center point of a contour"""
        try:
            # Calculate moments to find centroid
            M = cv2.moments(contour)
            if M["m00"] == 0:
                print("[PaintingOperation] Warning: Contour has zero area")
                return None

            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])

            return (cx, cy)
        except Exception as e:
            print(f"[PaintingOperation] Error calculating contour center: {e}")
            return None

    def _get_median_contour_center(self, contour_index):
        """
        Capture multiple images and calculate the median center position for a contour.

        Args:
            contour_index: Index of the contour to track

        Returns:
            tuple: (median_cx, median_cy) or None if failed
        """
        if self.center_samples < 1:
            print(f"[PaintingOperation] Invalid center_samples: {self.center_samples}, using 1")
            self.center_samples = 1

        print(f"[PaintingOperation] Capturing {self.center_samples} images for median center calculation...")

        centers_x = []
        centers_y = []

        for sample in range(self.center_samples):
            if not self.is_running:
                return None

            # Get a fresh frame from vision service
            frame = self.vision_service.getLatestFrame()
            if frame is None:
                print(f"[PaintingOperation] Warning: Failed to get frame {sample + 1}/{self.center_samples}")
                time.sleep(0.05)
                continue

            # Import contour detection handler
            from modules.VisionSystem.handlers.contour_detection_handler import handle_contour_detection

            # Temporarily store the frame in vision service and run contour detection
            old_image = self.vision_service.image
            self.vision_service.image = frame

            # Detect contours using the vision system's handler
            contours, _, _ = handle_contour_detection(self.vision_service)

            # Restore original image
            self.vision_service.image = old_image

            if contours is None or len(contours) == 0:
                print(f"[PaintingOperation] Warning: No contours found in image {sample + 1}/{self.center_samples}")
                time.sleep(0.05)
                continue

            if contour_index >= len(contours):
                print(f"[PaintingOperation] Warning: Contour index {contour_index} out of range (found {len(contours)} contours) in image {sample + 1}/{self.center_samples}")
                time.sleep(0.05)
                continue

            # Get the contour at the specified index
            contour = contours[contour_index]

            # Calculate center
            center = self._calculate_contour_center(contour)
            if center is None:
                print(f"[PaintingOperation] Warning: Failed to calculate center for image {sample + 1}/{self.center_samples}")
                time.sleep(0.05)
                continue

            centers_x.append(center[0])
            centers_y.append(center[1])

            print(f"[PaintingOperation] Sample {sample + 1}/{self.center_samples}: center=({center[0]}, {center[1]})")

            # Small delay between captures to allow for any camera settling
            if sample < self.center_samples - 1:
                time.sleep(0.05)

        # Calculate median
        if len(centers_x) == 0:
            print(f"[PaintingOperation] Error: No valid centers found across {self.center_samples} samples")
            return None

        median_cx = int(np.median(centers_x))
        median_cy = int(np.median(centers_y))

        # Calculate statistics
        std_x = np.std(centers_x) if len(centers_x) > 1 else 0
        std_y = np.std(centers_y) if len(centers_y) > 1 else 0

        print(f"[PaintingOperation] Median center: ({median_cx}, {median_cy})")
        print(f"[PaintingOperation] Center variation: X±{std_x:.2f}px, Y±{std_y:.2f}px across {len(centers_x)} samples")

        return (median_cx, median_cy)

    def _calculate_contour_angle(self, contour):
        """
        Calculate the current angle/orientation of the contour using minAreaRect.
        This matches the calculation used in the Pick and Place process.

        Args:
            contour: OpenCV contour in camera coordinates

        Returns:
            Angle in degrees of the contour's orientation from minAreaRect
        """
        try:
            # Use cv2.minAreaRect to get the minimum area bounding rectangle
            # Returns: ((center_x, center_y), (width, height), angle)
            min_rect = cv2.minAreaRect(contour)
            angle = min_rect[2]  # Angle in degrees

            # cv2.minAreaRect returns angle in range [-90, 0)
            # Normalize to our coordinate system
            print(f"[PaintingOperation] minAreaRect angle: {angle:.2f}°")

            return angle

        except Exception as e:
            print(f"[PaintingOperation] Error calculating contour angle: {e}")
            import traceback
            traceback.print_exc()
            return 0.0

    def _calculate_contour_straightening_angle(self, contour):
        """
        Calculate the angle needed to straighten (align) the contour.
        Uses PCA (Principal Component Analysis) to find the principal axis of the contour.
        Aligns to nearest horizontal (0°) or vertical (90°) orientation.

        Args:
            contour: OpenCV contour in camera coordinates

        Returns:
            Angle in degrees to rotate the contour to align it horizontally or vertically
        """
        try:
            # Reshape contour to 2D array of points
            contour_points = contour.reshape(-1, 2).astype(np.float32)

            if len(contour_points) < 2:
                print("[PaintingOperation] Not enough points for PCA")
                return 0.0

            # Calculate mean
            mean = np.mean(contour_points, axis=0)

            # Center the data
            centered = contour_points - mean

            # Calculate covariance matrix
            cov = np.cov(centered.T)

            # Get eigenvalues and eigenvectors
            eigenvalues, eigenvectors = np.linalg.eig(cov)

            # Sort by eigenvalue (largest first)
            idx = eigenvalues.argsort()[::-1]
            eigenvectors = eigenvectors[:, idx]

            # The first eigenvector is the principal axis (direction of maximum variance)
            principal_axis = eigenvectors[:, 0]

            # Calculate angle of principal axis
            angle_rad = np.arctan2(principal_axis[1], principal_axis[0])
            angle_deg = np.degrees(angle_rad)

            # Normalize to [-180, 180]
            while angle_deg > 180:
                angle_deg -= 360
            while angle_deg < -180:
                angle_deg += 360

            # Determine nearest cardinal direction (0°, 90°, -90°, 180°)
            # 0° = horizontal (right), 90° = vertical (up), -90° = vertical (down), 180° = horizontal (left)

            # Calculate distance to each cardinal angle
            dist_to_0 = abs(angle_deg - 0)
            dist_to_90 = abs(angle_deg - 90)
            dist_to_neg90 = abs(angle_deg - (-90))
            dist_to_180 = min(abs(angle_deg - 180), abs(angle_deg - (-180)))

            # Find nearest cardinal direction
            min_dist = min(dist_to_0, dist_to_90, dist_to_neg90, dist_to_180)

            if min_dist == dist_to_0:
                target_angle = 0.0
                direction = "horizontal (0°)"
            elif min_dist == dist_to_90:
                target_angle = 90.0
                direction = "vertical (90°)"
            elif min_dist == dist_to_neg90:
                target_angle = -90.0
                direction = "vertical (-90°)"
            else:  # dist_to_180
                target_angle = 180.0
                direction = "horizontal (180°)"

            # Calculate rotation needed to reach target
            straightening_angle = target_angle - angle_deg

            # Normalize to [-180, 180]
            while straightening_angle > 180:
                straightening_angle -= 360
            while straightening_angle < -180:
                straightening_angle += 360

            print(f"[PaintingOperation] Contour angle: {angle_deg:.2f}°, Target: {direction}, Rotation needed: {straightening_angle:.2f}°")

            return straightening_angle

        except Exception as e:
            print(f"[PaintingOperation] Error calculating straightening angle: {e}")
            import traceback
            traceback.print_exc()
            return 0.0

    def _camera_to_robot_point(self, camera_point):
        """Convert a single camera point to robot coordinates"""
        try:
            # Get camera to robot transformation matrix
            camera_to_robot = self.vision_service.cameraToRobotMatrix
            if camera_to_robot is None:
                print("[PaintingOperation] ERROR: No camera to robot calibration!")
                return None

            # Get TCP offsets from robot config
            robot_config = self.robot_service.robot_config
            tcp_x_offset = getattr(robot_config, 'tcp_x_offset', 0.0)
            tcp_y_offset = getattr(robot_config, 'tcp_y_offset', 0.0)

            # Transform to robot coordinates
            camera_x, camera_y = camera_point
            camera_pt = np.array([[camera_x, camera_y]], dtype=np.float32).reshape(-1, 1, 2)
            robot_pt = cv2.perspectiveTransform(camera_pt, camera_to_robot)

            # Apply TCP offsets
            robot_x = float(robot_pt[0][0][0]) - tcp_x_offset
            robot_y = float(robot_pt[0][0][1]) + tcp_y_offset

            return (robot_x, robot_y)
        except Exception as e:
            print(f"[PaintingOperation] Error converting camera point to robot: {e}")
            return None

    def _get_painting_pos(self):
        """Get PAINTING_POS from robot settings"""
        try:
            # Access robot config from robot service
            robot_config = self.robot_service.robot_config
            if robot_config is None:
                print("[PaintingOperation] ERROR: Robot config not available")
                return None

            # Get PAINTING_POS position as parsed list
            painting_pos = robot_config.getPaintingPositionParsed()
            if painting_pos is None:
                print("[PaintingOperation] ERROR: PAINTING_POS not configured")
                return None

            return painting_pos

        except Exception as e:
            print(f"[PaintingOperation] Error getting PAINTING_POS: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _generate_edge_waypoints(self, contour, paint_z, rx, ry, rz, edge='top', num_points=20, paint_range=30.0):
        """
        Generate waypoints along one edge of the contour for painting.
        Extracts actual contour segment and places it at PAINTING_POS in XY plane.

        Args:
            contour: OpenCV contour in camera coordinates
            paint_z: Z position from PAINTING_POS (shaft axis)
            rx, ry, rz: Current robot orientation
            edge: Which edge to paint ('top', 'right', 'bottom', 'left')
            num_points: Number of waypoints along the edge
            paint_range: Range of motion in mm (not used, kept for compatibility)

        Returns:
            List of waypoints [x, y, z, rx, ry, rz]
        """
        waypoints = []

        try:
            # Find the extreme points of the contour in camera coordinates
            contour_points = contour.reshape(-1, 2)

            top_idx = np.argmin(contour_points[:, 1])  # Minimum Y (top)
            bottom_idx = np.argmax(contour_points[:, 1])  # Maximum Y (bottom)
            left_idx = np.argmin(contour_points[:, 0])  # Minimum X (left)
            right_idx = np.argmax(contour_points[:, 0])  # Maximum X (right)

            # Extract contour segment based on edge
            # Get points along the actual contour between extreme points
            if edge == 'top':
                # Get contour segment from left-top to right-top
                start_idx = left_idx
                end_idx = top_idx
                print(f"[PaintingOperation] Top edge: extracting contour from left ({left_idx}) to top ({top_idx})")
            elif edge == 'right':
                # Get contour segment from top-right to bottom-right
                start_idx = top_idx
                end_idx = right_idx
                print(f"[PaintingOperation] Right edge: extracting contour from top ({top_idx}) to right ({right_idx})")
            elif edge == 'bottom':
                # Get contour segment from right-bottom to left-bottom
                start_idx = right_idx
                end_idx = bottom_idx
                print(f"[PaintingOperation] Bottom edge: extracting contour from right ({right_idx}) to bottom ({bottom_idx})")
            elif edge == 'left':
                # Get contour segment from bottom-left to top-left
                start_idx = bottom_idx
                end_idx = left_idx
                print(f"[PaintingOperation] Left edge: extracting contour from bottom ({bottom_idx}) to left ({left_idx})")
            else:
                print(f"[PaintingOperation] Invalid edge: {edge}")
                return []

            # Extract segment points (handle wraparound)
            if start_idx <= end_idx:
                segment_points = contour_points[start_idx:end_idx+1]
            else:
                # Wrap around the contour
                segment_points = np.concatenate([contour_points[start_idx:], contour_points[:end_idx+1]])

            if len(segment_points) == 0:
                print(f"[PaintingOperation] No points in {edge} segment")
                return []

            # Get PAINTING_POS as the reference point
            painting_pos = self._get_painting_pos()
            if painting_pos is None:
                return []

            paint_x = painting_pos[0]
            paint_y = painting_pos[1]

            # Convert first point of segment to robot coordinates to get offset
            first_camera_point = segment_points[0]
            first_robot = self._camera_to_robot_point(first_camera_point)
            if first_robot is None:
                print(f"[PaintingOperation] Could not convert first point to robot coordinates")
                return []

            # Calculate offset so first point is at PAINTING_POS
            offset_x = paint_x - first_robot[0]
            offset_y = paint_y - first_robot[1]

            print(f"[PaintingOperation] Offset: X={offset_x:.2f}, Y={offset_y:.2f}")

            # Sample points along the segment
            step = max(1, len(segment_points) // num_points)
            sampled_indices = range(0, len(segment_points), step)

            for idx in sampled_indices:
                camera_point = segment_points[idx]
                robot_point = self._camera_to_robot_point(camera_point)

                if robot_point is None:
                    continue

                # Apply offset to place segment at PAINTING_POS
                x = robot_point[0] + offset_x
                y = robot_point[1] + offset_y
                z = paint_z  # Z stays constant (shaft axis)

                waypoint = [x, y, z, rx, ry, rz]
                waypoints.append(waypoint)

            print(f"[PaintingOperation] Generated {len(waypoints)} waypoints for {edge} edge following actual contour shape")

        except Exception as e:
            print(f"[PaintingOperation] Error generating edge waypoints: {e}")
            import traceback
            traceback.print_exc()
            return []

        return waypoints

    def _contour_to_waypoints(self, contour):
        """Convert a contour to robot waypoints with TCP offset applied"""
        waypoints = []

        # Validate contour data structure first
        if contour is None:
            print("[PaintingOperation] ERROR: Contour is None!")
            return waypoints, 0.0, 0.0

        try:
            if not isinstance(contour, (list, np.ndarray)):
                print(f"[PaintingOperation] ERROR: Contour is not a list or numpy array: {type(contour)}")
                return waypoints, 0.0, 0.0

            if len(contour) == 0:
                print("[PaintingOperation] ERROR: Contour is empty!")
                return waypoints, 0.0, 0.0

            # Convert to numpy array if it's a list
            if isinstance(contour, list):
                contour = np.array(contour)

            print(f"[PaintingOperation] Contour shape: {contour.shape}, dtype: {contour.dtype}")

        except Exception as e:
            print(f"[PaintingOperation] ERROR: Failed to validate contour structure: {e}")
            import traceback
            traceback.print_exc()
            return waypoints, 0.0, 0.0

        # Get camera to robot transformation matrix
        camera_to_robot = self.vision_service.cameraToRobotMatrix

        if camera_to_robot is None:
            print("[PaintingOperation] ERROR: No camera to robot calibration!")
            return waypoints, 0.0, 0.0

        # Validate the transformation matrix
        try:
            if not isinstance(camera_to_robot, np.ndarray):
                print("[PaintingOperation] ERROR: camera_to_robot is not a numpy array!")
                return waypoints, 0.0, 0.0

            if camera_to_robot.shape != (3, 3):
                print(f"[PaintingOperation] ERROR: camera_to_robot has invalid shape: {camera_to_robot.shape} (expected 3x3)")
                return waypoints, 0.0, 0.0

            print(f"[PaintingOperation] Camera to robot matrix validated: {camera_to_robot.shape}")
        except Exception as e:
            print(f"[PaintingOperation] ERROR: Failed to validate camera_to_robot matrix: {e}")
            return waypoints, 0.0, 0.0

        # TCP offsets are already applied in _convert_camera_point_to_robot()
        # Do NOT apply them again here to avoid double offset
        tcp_x_offset = 0.0
        tcp_y_offset = 0.0

        print(f"[PaintingOperation] TCP offsets already applied in coordinate conversion (not applying again)")

        # Get current robot orientation (we'll maintain this throughout the path)
        current_pose = self.robot_service.robot.get_current_position()
        if current_pose is None or len(current_pose) < 6:
            print("[PaintingOperation] ERROR: Could not get current robot position for orientation!")
            print("[PaintingOperation] Please ensure robot is connected and reporting position")
            return waypoints, tcp_x_offset, tcp_y_offset

        # Always use current orientation - never hardcoded
        rx, ry, rz = current_pose[3], current_pose[4], current_pose[5]
        print(f"[PaintingOperation] Using current robot orientation: RX={rx:.2f}°, RY={ry:.2f}°, RZ={rz:.2f}°")

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
        print(f"[PaintingOperation] Normalized orientation: RX={rx:.2f}°, RY={ry:.2f}°, RZ={rz:.2f}°")

        # Use z_offset from parameters
        z_offset = self.z_offset
        print(f"[PaintingOperation] Using Z offset: {z_offset}mm above surface")

        # Workspace bounds for validation (in mm)
        # These should match your robot's reachable workspace
        workspace_bounds = {
            'x_min': -500, 'x_max': 500,
            'y_min': -500, 'y_max': 500,
            'z_min': -2, 'z_max': 400
        }

        points_filtered = 0

        print(f"[PaintingOperation] Processing {len(contour)} contour points...")

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
                    print(f"[PaintingOperation] Warning: Transform failed for point {idx}: {e}")
                    continue

                # Extract robot coordinates and apply TCP offsets
                try:
                    # Note: X coordinate is negated because robot coordinate system is flipped
                    robot_x = float(robot_point[0][0][0]) - tcp_x_offset  # Negate X offset
                    robot_y = float(robot_point[0][0][1]) + tcp_y_offset
                    robot_z = z_offset  # Fixed height above surface
                except (IndexError, TypeError, ValueError) as e:
                    print(f"[PaintingOperation] Warning: Error extracting coordinates for point {idx}: {e}")
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
                    print(f"[PaintingOperation] Warning: Skipped point {idx} due to error: {e}")
                continue

        if points_filtered > 0:
            print(f"[PaintingOperation] Filtered {points_filtered} points outside workspace bounds")

        print(f"[PaintingOperation] Generated {len(waypoints)} valid waypoints from {len(contour)} contour points")
        return waypoints, tcp_x_offset, tcp_y_offset

    def _do_stop(self, *args, **kwargs):
        print("[PaintingOperation] Stopping painting operation")

        # Set flag first to stop the painting loop
        self.is_running = False

        if self.robot_service:
            # Stop robot motion - this sets command_in_progress=False in ZeroErrRobot
            # which will cause any ongoing motion commands to complete
            self.robot_service.robot.stop_motion()
            print("[PaintingOperation] Robot stop_motion() called")

        # Wait for thread to finish (with timeout)
        if self.execution_thread and self.execution_thread.is_alive():
            print("[PaintingOperation] Waiting for execution thread to stop...")
            self.execution_thread.join(timeout=3.0)
            if self.execution_thread.is_alive():
                print("[PaintingOperation] Warning: Execution thread did not stop within timeout")
            else:
                print("[PaintingOperation] Execution thread stopped successfully")

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

    def _get_straightened_contour_corners(self, contour, robot_center, straightened_rz, current_center):
        """
        Get the 4 corners of the contour after it has been straightened.
        Since the contour was rotated from pickup_rz to straightened_rz,
        we need to calculate where the corners are now in robot coordinates.

        Args:
            contour: Original contour in camera coordinates
            robot_center: Original center point in robot coordinates (x, y) before rotation
            straightened_rz: The rZ angle after straightening (90° or 0°)
            current_center: Current center position after straightening (x, y)

        Returns:
            List of 4 corner points in robot coordinates, ordered as:
            [top_left, top_right, bottom_right, bottom_left]
        """
        try:
            # Get minAreaRect to find the oriented bounding box
            min_rect = cv2.minAreaRect(contour)
            box_points = cv2.boxPoints(min_rect)  # Get 4 corners in camera coords

            # Convert to robot coordinates
            corners_robot = []
            for corner in box_points:
                robot_pt = self._camera_to_robot_point(corner)
                if robot_pt is None:
                    return None
                corners_robot.append(robot_pt)

            # Now we need to figure out which corner is which after straightening
            # The contour was at pickup_rz angle, then rotated to straightened_rz
            # We need to rotate the corner offsets accordingly

            # Calculate angle difference
            contour_angle = self._calculate_contour_angle(contour)
            pickup_rz = -contour_angle
            angle_diff = straightened_rz - pickup_rz
            angle_diff_rad = np.radians(angle_diff)

            # Rotate each corner offset around the center
            straightened_corners = []
            for robot_pt in corners_robot:
                # Get offset from original center
                dx = robot_pt[0] - robot_center[0]
                dy = robot_pt[1] - robot_center[1]

                # Rotate offset by angle_diff
                cos_a = np.cos(angle_diff_rad)
                sin_a = np.sin(angle_diff_rad)

                new_dx = dx * cos_a - dy * sin_a
                new_dy = dx * sin_a + dy * cos_a

                # Add to CURRENT center position (where the robot actually is now)
                new_x = current_center[0] + new_dx
                new_y = current_center[1] + new_dy

                straightened_corners.append((new_x, new_y))

            # Order corners: top_left, top_right, bottom_right, bottom_left
            # After straightening to horizontal (90°) or vertical (0°), we know the orientation
            # For horizontal (90°): X is down, Y is right, so top = min X, left = min Y
            # For vertical (0°): X is down, Y is right, so top = min X, left = min Y

            # Sort by Y (right direction) to get left and right
            sorted_by_y = sorted(straightened_corners, key=lambda p: p[1])
            left_corners = sorted_by_y[:2]  # 2 leftmost
            right_corners = sorted_by_y[2:]  # 2 rightmost

            # Sort each pair by X (down direction) to get top and bottom
            top_left = min(left_corners, key=lambda p: p[0])
            bottom_left = max(left_corners, key=lambda p: p[0])
            top_right = min(right_corners, key=lambda p: p[0])
            bottom_right = max(right_corners, key=lambda p: p[0])

            ordered_corners = [top_left, top_right, bottom_right, bottom_left]

            print(f"[PaintingOperation] Straightened corners:")
            print(f"  Top-left: X={top_left[0]:.2f}, Y={top_left[1]:.2f}")
            print(f"  Top-right: X={top_right[0]:.2f}, Y={top_right[1]:.2f}")
            print(f"  Bottom-right: X={bottom_right[0]:.2f}, Y={bottom_right[1]:.2f}")
            print(f"  Bottom-left: X={bottom_left[0]:.2f}, Y={bottom_left[1]:.2f}")

            return ordered_corners

        except Exception as e:
            print(f"[PaintingOperation] Error getting straightened corners: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _detect_painting_mode(self, painting_pos):
        """
        Detect which painting mode to use based on PAINTING_POS orientation.

        Returns:
            tuple: (plane, rotation_axis)
                - plane: 'XY' or 'YZ'
                - rotation_axis: 'rZ' or 'rY'
        """
        rx, ry, rz = painting_pos[3], painting_pos[4], painting_pos[5]

        # Normalize angles to [-180, 180]
        def normalize_angle(angle):
            while angle > 180:
                angle -= 360
            while angle < -180:
                angle += 360
            return angle

        rx = normalize_angle(rx)
        ry = normalize_angle(ry)
        rz = normalize_angle(rz)

        # Check if angle is close to 90° (within 30° tolerance)
        def is_close_to_90(angle):
            return abs(abs(angle) - 90) < 30

        # Mode 1: XY plane with rZ rotation
        # Condition: rZ close to 90°, rX not close to 90°
        if is_close_to_90(rz) and not is_close_to_90(rx):
            print(f"[PaintingOperation] Detected mode: XY plane with rZ rotation (rZ={rz:.1f}°)")
            return ('XY', 'rZ')

        # Mode 2: YZ plane with rY rotation
        # Condition: Both rX and rZ close to 90°
        elif is_close_to_90(rx) and is_close_to_90(rz):
            print(f"[PaintingOperation] Detected mode: YZ plane with rY rotation (rX={rx:.1f}°, rZ={rz:.1f}°)")
            return ('YZ', 'rY')

        # Default: Use XY plane with rZ rotation
        else:
            print(f"[PaintingOperation] Default mode: XY plane with rZ rotation (rX={rx:.1f}°, rY={ry:.1f}°, rZ={rz:.1f}°)")
            return ('XY', 'rZ')

    def _analyze_contour_complexity(self, contour):
        """
        Analyze contour to determine if it's a simple rectangle or complex shape.

        Returns:
            dict: {
                'is_rectangular': bool,
                'has_curves': bool,
                'corner_count': int,
                'total_points': int,
                'perimeter': float
            }
        """
        # Simplify contour using Douglas-Peucker algorithm
        epsilon = self.contour_simplification_epsilon
        simplified = cv2.approxPolyDP(contour, epsilon, True)

        corner_count = len(simplified)
        total_points = len(contour)
        perimeter = cv2.arcLength(contour, True)

        # Check if it's approximately rectangular (4 corners, ~90° angles)
        is_rectangular = False
        if corner_count == 4:
            # Check if angles are close to 90°
            angles = []
            for i in range(4):
                p1 = simplified[i][0]
                p2 = simplified[(i+1)%4][0]
                p3 = simplified[(i+2)%4][0]

                v1 = np.array([p1[0] - p2[0], p1[1] - p2[1]], dtype=np.float64)
                v2 = np.array([p3[0] - p2[0], p3[1] - p2[1]], dtype=np.float64)

                norm1 = float(np.linalg.norm(v1))
                norm2 = float(np.linalg.norm(v2))
                if norm1 < 1e-6 or norm2 < 1e-6:
                    continue

                dot_product = float(np.dot(v1, v2))
                cos_angle = max(-1.0, min(1.0, dot_product / (norm1 * norm2)))
                angle = abs(np.arccos(cos_angle))
                angles.append(float(np.degrees(angle)))

            # Check if all angles are close to 90°
            if all(abs(angle - 90) < 15 for angle in angles):
                is_rectangular = True

        # Detect curves by checking if contour has many more points than simplified
        has_curves = (total_points > corner_count * 10) or (corner_count > 4)

        return {
            'is_rectangular': is_rectangular,
            'has_curves': has_curves,
            'corner_count': corner_count,
            'total_points': total_points,
            'perimeter': perimeter
        }

    def _convert_contour_to_robot_path(self, contour, painting_pos, current_pose, robot_center):
        """
        Convert contour points to robot waypoints with proper orientation for each segment.

        Args:
            contour: OpenCV contour in camera coordinates
            painting_pos: PAINTING_POS configuration [x, y, z, rx, ry, rz]
            current_pose: Current robot pose [x, y, z, rx, ry, rz]
            robot_center: Center of contour in robot coordinates (x, y)

        Returns:
            list: Waypoints with calculated orientations [[x, y, z, rx, ry, rz], ...]
        """
        waypoints = []

        # Simplify contour slightly to remove noise but keep shape
        epsilon = self.contour_simplification_epsilon
        simplified_contour = cv2.approxPolyDP(contour, epsilon, True)

        print(f"[ContourFollowing] Simplified contour: {len(contour)} -> {len(simplified_contour)} points")

        # Convert each point to robot coordinates
        robot_points = []
        for point in simplified_contour:
            robot_pt = self._camera_to_robot_point(point[0])
            if robot_pt is not None:
                robot_points.append(robot_pt)

        if len(robot_points) < 3:
            print(f"[ContourFollowing] ERROR: Not enough valid points ({len(robot_points)})")
            return []

        # Close the path by adding first point at end
        robot_points.append(robot_points[0])

        paint_rx, paint_ry, paint_rz = painting_pos[3], painting_pos[4], painting_pos[5]
        paint_z = painting_pos[2]

        # Calculate offset to position contour relative to PAINTING_POS
        # The contour center should be offset so that when we "paint" it,
        # the tool follows the contour with the first point near PAINTING_POS
        first_point = robot_points[0]

        # Calculate offset from current center to first point
        center_to_first_x = first_point[0] - current_pose[0]
        center_to_first_y = first_point[1] - current_pose[1]

        print(f"[ContourFollowing] Center to first point offset: X={center_to_first_x:.2f}, Y={center_to_first_y:.2f}")

        # Calculate where TCP center should be so first point is at PAINTING_POS
        tcp_center_x = painting_pos[0] - center_to_first_x
        tcp_center_y = painting_pos[1] - center_to_first_y

        # Offset all points by this amount
        offset_x = tcp_center_x - current_pose[0]
        offset_y = tcp_center_y - current_pose[1]

        print(f"[ContourFollowing] Applying offset to all points: X={offset_x:.2f}, Y={offset_y:.2f}")

        # Track previous rotation to prevent overshoots beyond 360 degrees
        prev_rz = paint_rz
        cumulative_rotation = 0.0  # Track total rotation from start

        # Calculate orientation for each segment based on direction to next point
        for i in range(len(robot_points) - 1):
            curr_pt = robot_points[i]
            next_pt = robot_points[i + 1]

            # Apply offset
            curr_pt_offset = (curr_pt[0] + offset_x, curr_pt[1] + offset_y)

            # Calculate direction vector
            dx = next_pt[0] - curr_pt[0]
            dy = next_pt[1] - curr_pt[1]

            segment_length = np.sqrt(dx**2 + dy**2)

            # Skip very short segments
            if segment_length < self.min_segment_length:
                continue

            # Calculate rotation based on segment direction
            # Look ahead multiple points for smoother rotation transitions
            lookahead_idx = min(i + self.rotation_lookahead_points, len(robot_points) - 1)
            lookahead_pt = robot_points[lookahead_idx]

            dx_lookahead = lookahead_pt[0] - curr_pt[0]
            dy_lookahead = lookahead_pt[1] - curr_pt[1]

            # Calculate angle from positive Y axis (robot's "right" direction)
            angle_rad = np.arctan2(dx_lookahead, dy_lookahead)
            angle_deg = np.degrees(angle_rad)

            # Calculate target rZ based on path direction
            target_rz = paint_rz + angle_deg

            # Normalize target angle to [-180, 180]
            while target_rz > 180:
                target_rz -= 360
            while target_rz < -180:
                target_rz += 360

            # Calculate rotation delta from previous waypoint
            delta_rz = target_rz - prev_rz

            # Normalize delta to smallest rotation [-180, 180]
            while delta_rz > 180:
                delta_rz -= 360
            while delta_rz < -180:
                delta_rz += 360

            # Update cumulative rotation
            cumulative_rotation += delta_rz

            # Check if we're approaching 360 degree limit
            if abs(cumulative_rotation) > 330:  # 330 degrees as warning threshold
                print(f"[ContourFollowing] WARNING: Cumulative rotation at {cumulative_rotation:.1f}°, approaching limit")

            # Prevent overshooting 360 degrees total rotation
            if abs(cumulative_rotation) > 360:
                print(f"[ContourFollowing] ERROR: Would exceed 360° rotation limit (current: {cumulative_rotation:.1f}°)")
                print(f"[ContourFollowing] Stopping at waypoint {i} to prevent cable wrap")
                break

            # Use the target_rz which ensures smooth transitions
            rz_adjusted = target_rz

            waypoint = [curr_pt_offset[0], curr_pt_offset[1], paint_z, paint_rx, paint_ry, rz_adjusted]
            waypoints.append(waypoint)

            prev_rz = rz_adjusted

        print(f"[ContourFollowing] Generated {len(waypoints)} waypoints, total rotation: {cumulative_rotation:.1f}°")
        return waypoints

    def _execute_contour_following_painting(self, contour, painting_pos, current_pose, robot_center):
        """
        Execute painting by following the actual contour path with dynamic rotation.
        This handles complex shapes including circles, ovals, fillets, and chamfers.

        Args:
            contour: OpenCV contour in camera coordinates
            painting_pos: PAINTING_POS configuration [x, y, z, rx, ry, rz]
            current_pose: Current robot pose [x, y, z, rx, ry, rz]
            robot_center: Center of contour in robot coordinates (x, y)

        Returns:
            int: 0 on success, -1 on failure
        """
        try:
            print(f"[ContourFollowing] Starting contour-following painting mode")

            # Analyze contour complexity
            analysis = self._analyze_contour_complexity(contour)
            print(f"[ContourFollowing] Contour analysis:")
            print(f"  - Is rectangular: {analysis['is_rectangular']}")
            print(f"  - Has curves: {analysis['has_curves']}")
            print(f"  - Corners: {analysis['corner_count']}")
            print(f"  - Total points: {analysis['total_points']}")
            print(f"  - Perimeter: {analysis['perimeter']:.2f}mm")

            # Convert contour to robot waypoints with orientation
            waypoints = self._convert_contour_to_robot_path(contour, painting_pos, current_pose, robot_center)

            if len(waypoints) < 2:
                print(f"[ContourFollowing] ERROR: Not enough waypoints generated")
                return -1

            # Get painting position parameters
            paint_rx, paint_ry, paint_rz = painting_pos[3], painting_pos[4], painting_pos[5]
            paint_z = painting_pos[2]

            # Move to start position
            start_waypoint = waypoints[0]
            print(f"[ContourFollowing] Moving to start position: X={start_waypoint[0]:.2f}, Y={start_waypoint[1]:.2f}, rZ={start_waypoint[5]:.2f}°")
            ret = self.robot_service.robot.moveCartesianPath([start_waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[ContourFollowing] Failed to move to start position")
                return ret

            if not self.is_running:
                return -1

            # Optional: Search for contact at start
            if self.enable_pressure_adjustment:
                print(f"[ContourFollowing] Searching for initial contact...")
                # Determine search direction based on painting mode
                plane, _ = self._detect_painting_mode(painting_pos)
                search_dir = 'y-' if plane == 'YZ' else 'x-'

                contact_x, contact_y, contact_z, contact_found = self._find_contact_point(
                    start_waypoint[0], start_waypoint[1], paint_z,
                    paint_rx, paint_ry, start_waypoint[5],
                    search_direction=search_dir
                )

                if contact_found:
                    print(f"[ContourFollowing] ✓ Initial contact established")
                    # Update all waypoint positions with offset
                    offset_x = contact_x - start_waypoint[0]
                    offset_y = contact_y - start_waypoint[1]
                    print(f"[ContourFollowing] Applying contact offset: X={offset_x:.2f}, Y={offset_y:.2f}")
                    for wp in waypoints:
                        wp[0] += offset_x
                        wp[1] += offset_y

            if not self.is_running:
                return -1

            # Execute the contour path with smooth motion
            print(f"[ContourFollowing] Executing contour path with {len(waypoints)} waypoints")
            ret = self.robot_service.robot.moveCartesianPath(waypoints, vel=self.velocity, acc=self.acceleration, decimate=True)

            if ret != 0:
                print(f"[ContourFollowing] Failed to execute contour path")
                return ret

            print(f"[ContourFollowing] ✓ Contour following painting completed successfully")
            return 0

        except Exception as e:
            print(f"[ContourFollowing] Error during contour following: {e}")
            import traceback
            traceback.print_exc()
            return -1

    def _execute_corner_painting(self, corners_robot, painting_pos, current_rz, current_pose):
        """
        Execute corner painting sequence with automatic plane/rotation detection.

        Automatically detects whether to use:
        - XY plane with rZ rotation (when rZ ≈ 90°)
        - YZ plane with rY rotation (when rX ≈ 90° and rZ ≈ 90°)

        Args:
            corners_robot: List of 4 corners [top_left, top_right, bottom_right, bottom_left]
            painting_pos: PAINTING_POS configuration [x, y, z, rx, ry, rz]
            current_rz: Current rZ orientation after straightening
            current_pose: Current robot pose [x, y, z, rx, ry, rz]

        Returns:
            tuple: (status, rotation_count) where status is 0 on success, rotation_count is number of 90° rotations
        """
        # Detect which mode to use
        plane, rotation_axis = self._detect_painting_mode(painting_pos)

        # Route to appropriate implementation
        if plane == 'YZ' and rotation_axis == 'rY':
            return self._execute_corner_painting_yz_ry(corners_robot, painting_pos, current_rz, current_pose)
        else:
            return self._execute_corner_painting_xy_rz(corners_robot, painting_pos, current_rz, current_pose)

    def _execute_corner_painting_xy_rz(self, corners_robot, painting_pos, current_rz, current_pose):
        """
        Execute corner painting in XY plane with rZ rotation.
        Original implementation for horizontal shaft orientation.
        """
        try:
            top_left, top_right, bottom_right, bottom_left = corners_robot

            # Calculate edge lengths based on actual corner positions
            top_edge_length = abs(top_right[1] - top_left[1])  # Y direction
            right_edge_length = abs(bottom_right[0] - top_right[0])  # X direction

            print(f"[PaintingOperation] Edge lengths: top={top_edge_length:.2f}mm, right={right_edge_length:.2f}mm")

            # Get orientation from PAINTING_POS
            paint_rx, paint_ry = painting_pos[3], painting_pos[4]
            paint_z = painting_pos[2]

            # Calculate offset from current center to top_left corner
            # The corners are already in absolute robot coordinates
            center_to_top_left_x = top_left[0] - current_pose[0]
            center_to_top_left_y = top_left[1] - current_pose[1]

            print(f"[PaintingOperation] Center to top_left offset: X={center_to_top_left_x:.2f}, Y={center_to_top_left_y:.2f}")

            # === Step 1: Move so that top_left corner is at PAINTING_POS ===
            # If top_left is at offset (dx, dy) from current center,
            # we need to move center to (painting_pos - offset)
            print(f"[PaintingOperation] Step 1: Moving so top_left corner is at PAINTING_POS")
            new_center_x = painting_pos[0] - center_to_top_left_x
            new_center_y = painting_pos[1] - center_to_top_left_y

            waypoint = [new_center_x, new_center_y, paint_z, paint_rx, paint_ry, current_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to move top_left to PAINTING_POS")
                return ret, 0

            # Update tracked center position
            current_center_x = new_center_x
            current_center_y = new_center_y

            if not self.is_running:
                return -1, 0

            # === Step 1.5: Search for exact contact point with shaft BEFORE painting ===
            if self.enable_pressure_adjustment:
                print(f"[PaintingOperation] Step 1.5: Searching for contact point with shaft")
                # Current position has top_left at PAINTING_POS
                # Search in X- direction to find shaft contact
                contact_x, contact_y, contact_z, contact_found = self._find_contact_point(
                    current_center_x, current_center_y, paint_z,
                    paint_rx, paint_ry, current_rz,
                    search_direction='x-'
                )

                if contact_found:
                    print(f"[PaintingOperation] ✓ Contact established, offset: {current_center_x - contact_x:.2f}mm")
                    current_center_x = contact_x
                    current_center_y = contact_y
                else:
                    print(f"[PaintingOperation] ⚠ Contact not found, continuing with current position")

            if not self.is_running:
                return -1, 0

            # === Step 2: Move right so top_right is at PAINTING_POS (painting top edge) ===
            # Recalculate top_right offset from CURRENT center position
            center_to_top_right_x = top_right[0] - current_pose[0]  # Original offset
            center_to_top_right_y = top_right[1] - current_pose[1]

            print(f"[PaintingOperation] Step 2: Painting top edge - moving so top_right is at PAINTING_POS")
            new_center_x = painting_pos[0] - center_to_top_right_x
            new_center_y = painting_pos[1] - center_to_top_right_y

            waypoint = [new_center_x, new_center_y, paint_z, paint_rx, paint_ry, current_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to paint top edge")
                return ret, 0

            # Update tracked center position
            current_center_x = new_center_x
            current_center_y = new_center_y


            if not self.is_running:
                return -1, 0


            # === Step 3: Rotate rZ by 90° while keeping top_right at PAINTING_POS ===
            # To keep corner at PAINTING_POS during rotation, we need multiple waypoints
            # that trace an arc as the TCP rotates
            print(f"[PaintingOperation] Step 3: Rotating rZ by 90° around top_right corner")
            new_rz = current_rz + 90.0
            while new_rz > 180:
                new_rz -= 360
            while new_rz < -180:
                new_rz += 360

            # Current offset from TCP center to corner
            corner_offset_x = painting_pos[0] - current_center_x
            corner_offset_y = painting_pos[1] - current_center_y

            print(f"[PaintingOperation] Corner offset from TCP: ({corner_offset_x:.2f}, {corner_offset_y:.2f})")

            # Generate waypoints for smooth rotation
            num_steps = max(1, int(90.0 / self.rotation_step))  # Calculate steps based on rotation_step parameter
            rotation_waypoints = []

            for step in range(1, num_steps + 1):
                # Interpolate rotation
                interp_angle = current_rz + (90.0 * step / num_steps)
                while interp_angle > 180:
                    interp_angle -= 360
                while interp_angle < -180:
                    interp_angle += 360

                # Calculate how much we've rotated from start
                delta_angle = (90.0 * step / num_steps)
                delta_rad = np.radians(delta_angle)
                cos_delta = np.cos(delta_rad)
                sin_delta = np.sin(delta_rad)

                # Rotate the corner offset by this amount
                rotated_offset_x = corner_offset_x * cos_delta - corner_offset_y * sin_delta
                rotated_offset_y = corner_offset_x * sin_delta + corner_offset_y * cos_delta

                # Calculate TCP position to keep corner at PAINTING_POS
                tcp_x = painting_pos[0] - rotated_offset_x
                tcp_y = painting_pos[1] - rotated_offset_y

                # Initialize adjustment tracking
                x_adjustment = 0.0
                rz_adjustment = 0.0

                # Apply pressure and rotation adjustments if enabled (every 10th waypoint to avoid excessive queries)
                if self.enable_pressure_adjustment and step % 10 == 0:
                    force_x = self._get_x_axis_force()
                    if force_x is not None:
                        # Calculate X position adjustment
                        x_adjustment = self._calculate_pressure_adjustment(force_x)

                        # Calculate rZ rotation adjustment to prevent contour rotation (only if enabled)
                        if self.enable_rotation_adjustment:
                            rz_adjustment = self._calculate_rotation_adjustment(force_x, x_adjustment)
                        else:
                            rz_adjustment = 0.0

                        if abs(x_adjustment) > 0.01 or abs(rz_adjustment) > 0.01:  # Only log significant adjustments
                            print(f"[Pressure] Step {step}: Force={force_x:.2f}N, X_adj={x_adjustment:.3f}mm, rZ_adj={rz_adjustment:.3f}°")

                        tcp_x += x_adjustment

                # Apply rotation adjustment to interpolated angle
                adjusted_angle = interp_angle + rz_adjustment
                while adjusted_angle > 180:
                    adjusted_angle -= 360
                while adjusted_angle < -180:
                    adjusted_angle += 360

                rotation_waypoints.append([tcp_x, tcp_y, paint_z, paint_rx, paint_ry, adjusted_angle])

            print(f"[PaintingOperation] Executing rotation with {len(rotation_waypoints)} waypoints")
            ret = self.robot_service.robot.moveCartesianPath(rotation_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to rotate at top_right")
                return ret, 0

            # Update current rotation and center position to final values
            current_rz = new_rz
            current_center_x = rotation_waypoints[-1][0]
            current_center_y = rotation_waypoints[-1][1]

            if not self.is_running:
                return -1, 0

            # === Step 3.5: Search for contact after first corner rotation (if enabled) ===
            if self.enable_pressure_adjustment and self.search_at_all_corners:
                print(f"[PaintingOperation] Step 3.5: Searching for contact after top_right corner rotation")
                print(f"[PaintingOperation] Current center: X={current_center_x:.2f}, Y={current_center_y:.2f}")
                print(f"[PaintingOperation] Current rotation: rZ={current_rz:.2f}°")
                print(f"[PaintingOperation] PAINTING_POS: X={painting_pos[0]:.2f}, Y={painting_pos[1]:.2f}")

                # After rotation, search for contact with the shaft
                contact_x, contact_y, contact_z, contact_found = self._find_contact_point(
                    current_center_x, current_center_y, paint_z,
                    paint_rx, paint_ry, current_rz,
                    search_direction='x-'  # Shaft is always X- from PAINTING_POS
                )

                if contact_found:
                    print(f"[PaintingOperation] ✓ Contact re-established at X={contact_x:.2f}, Y={contact_y:.2f}")
                    print(f"[PaintingOperation] Movement: ΔX={contact_x - current_center_x:.2f}mm, ΔY={contact_y - current_center_y:.2f}mm")
                    current_center_x = contact_x
                    current_center_y = contact_y

            if not self.is_running:
                return -1, 0

            # === Step 4: Move down so bottom_right is at PAINTING_POS (painting right edge) ===
            # After 1 rotation (90°), calculate where bottom_right is now
            print(f"[PaintingOperation] Step 4: Painting right edge - moving so bottom_right is at PAINTING_POS")

            # Calculate bottom_right's original offset from initial center, then rotate by 90°
            original_br_offset_x = bottom_right[0] - current_pose[0]
            original_br_offset_y = bottom_right[1] - current_pose[1]

            # Apply 90° rotation
            angle_90 = np.radians(90.0)
            cos_90 = np.cos(angle_90)
            sin_90 = np.sin(angle_90)

            rotated_br_x = original_br_offset_x * cos_90 - original_br_offset_y * sin_90
            rotated_br_y = original_br_offset_x * sin_90 + original_br_offset_y * cos_90

            # Position TCP so bottom_right is at PAINTING_POS
            new_center_x = painting_pos[0] - rotated_br_x
            new_center_y = painting_pos[1] - rotated_br_y

            waypoint = [new_center_x, new_center_y, paint_z, paint_rx, paint_ry, current_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to paint right edge")
                return ret, 0

            # Update tracked center position
            current_center_x = new_center_x
            current_center_y = new_center_y


            if not self.is_running:
                return -1, 0

            # === Step 5: Rotate rZ by 90° around bottom_right corner ===
            print(f"[PaintingOperation] Step 5: Rotating rZ by 90° around bottom_right corner")
            new_rz = current_rz + 90.0
            while new_rz > 180:
                new_rz -= 360
            while new_rz < -180:
                new_rz += 360

            # Current offset from TCP to corner at PAINTING_POS
            corner_offset_x = painting_pos[0] - current_center_x
            corner_offset_y = painting_pos[1] - current_center_y

            # Generate waypoints for smooth rotation
            num_steps = max(1, int(90.0 / self.rotation_step))  # Calculate steps based on rotation_step parameter
            rotation_waypoints = []

            for step in range(1, num_steps + 1):
                interp_angle = current_rz + (90.0 * step / num_steps)
                while interp_angle > 180:
                    interp_angle -= 360
                while interp_angle < -180:
                    interp_angle += 360

                delta_angle = (90.0 * step / num_steps)
                delta_rad = np.radians(delta_angle)
                cos_delta = np.cos(delta_rad)
                sin_delta = np.sin(delta_rad)

                rotated_offset_x = corner_offset_x * cos_delta - corner_offset_y * sin_delta
                rotated_offset_y = corner_offset_x * sin_delta + corner_offset_y * cos_delta

                tcp_x = painting_pos[0] - rotated_offset_x
                tcp_y = painting_pos[1] - rotated_offset_y

                # Initialize adjustment tracking
                x_adjustment = 0.0
                rz_adjustment = 0.0

                # Apply pressure and rotation adjustments if enabled
                if self.enable_pressure_adjustment and step % 10 == 0:
                    force_x = self._get_x_axis_force()
                    if force_x is not None:
                        # Calculate X position adjustment
                        x_adjustment = self._calculate_pressure_adjustment(force_x)

                        # Calculate rZ rotation adjustment to prevent contour rotation
                        if self.enable_rotation_adjustment:
                            rz_adjustment = self._calculate_rotation_adjustment(force_x, x_adjustment)
                        else:
                            rz_adjustment = 0.0

                        if abs(x_adjustment) > 0.01 or abs(rz_adjustment) > 0.01:
                            print(f"[Pressure] Step {step}: Force={force_x:.2f}N, X_adj={x_adjustment:.3f}mm, rZ_adj={rz_adjustment:.3f}°")

                        tcp_x += x_adjustment

                # Apply rotation adjustment to interpolated angle
                adjusted_angle = interp_angle + rz_adjustment
                while adjusted_angle > 180:
                    adjusted_angle -= 360
                while adjusted_angle < -180:
                    adjusted_angle += 360

                rotation_waypoints.append([tcp_x, tcp_y, paint_z, paint_rx, paint_ry, adjusted_angle])

            ret = self.robot_service.robot.moveCartesianPath(rotation_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to rotate at bottom_right")
                return ret, 0

            # Update current rotation and center position
            current_rz = new_rz
            current_center_x = rotation_waypoints[-1][0]
            current_center_y = rotation_waypoints[-1][1]
            current_rz = new_rz

            if not self.is_running:
                return -1, 0

            # === Step 5.5: Search for contact after second corner rotation (if enabled) ===
            if self.enable_pressure_adjustment and self.search_at_all_corners:
                print(f"[PaintingOperation] Step 5.5: Searching for contact after bottom_right corner rotation")
                print(f"[PaintingOperation] Current center: X={current_center_x:.2f}, Y={current_center_y:.2f}")
                print(f"[PaintingOperation] Current rotation: rZ={current_rz:.2f}°")

                # After rotation, search for contact with the shaft
                contact_x, contact_y, contact_z, contact_found = self._find_contact_point(
                    current_center_x, current_center_y, paint_z,
                    paint_rx, paint_ry, current_rz,
                    search_direction='x-'  # Shaft is always X- from PAINTING_POS
                )

                if contact_found:
                    print(f"[PaintingOperation] ✓ Contact re-established, offset: {current_center_x - contact_x:.2f}mm")
                    current_center_x = contact_x
                    current_center_y = contact_y

            if not self.is_running:
                return -1, 0

            # === Step 6: Move left so bottom_left is at PAINTING_POS (painting bottom edge) ===
            # After 2 rotations (180° total), calculate bottom_left's new position
            print(f"[PaintingOperation] Step 6: Painting bottom edge - moving so bottom_left is at PAINTING_POS")

            # Calculate bottom_left's original offset, then rotate by 180° (2 x 90°)
            original_bl_offset_x = bottom_left[0] - current_pose[0]
            original_bl_offset_y = bottom_left[1] - current_pose[1]

            # Apply 180° rotation (easier: just negate both offsets)
            rotated_bl_x = -original_bl_offset_x
            rotated_bl_y = -original_bl_offset_y

            # Position TCP so bottom_left is at PAINTING_POS
            new_center_x = painting_pos[0] - rotated_bl_x
            new_center_y = painting_pos[1] - rotated_bl_y

            waypoint = [new_center_x, new_center_y, paint_z, paint_rx, paint_ry, current_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to paint bottom edge")
                return ret, 0

            # Update tracked center position
            current_center_x = new_center_x
            current_center_y = new_center_y


            if not self.is_running:
                return -1, 0

            # === Step 7: Rotate rZ by 90° around bottom_left corner ===
            print(f"[PaintingOperation] Step 7: Rotating rZ by 90° around bottom_left corner")
            new_rz = current_rz + 90.0
            while new_rz > 180:
                new_rz -= 360
            while new_rz < -180:
                new_rz += 360

            # Current offset from TCP to corner at PAINTING_POS
            corner_offset_x = painting_pos[0] - current_center_x
            corner_offset_y = painting_pos[1] - current_center_y

            # Generate waypoints for smooth rotation
            num_steps = max(1, int(90.0 / self.rotation_step))  # Calculate steps based on rotation_step parameter
            rotation_waypoints = []

            for step in range(1, num_steps + 1):
                interp_angle = current_rz + (90.0 * step / num_steps)
                while interp_angle > 180:
                    interp_angle -= 360
                while interp_angle < -180:
                    interp_angle += 360

                delta_angle = (90.0 * step / num_steps)
                delta_rad = np.radians(delta_angle)
                cos_delta = np.cos(delta_rad)
                sin_delta = np.sin(delta_rad)

                rotated_offset_x = corner_offset_x * cos_delta - corner_offset_y * sin_delta
                rotated_offset_y = corner_offset_x * sin_delta + corner_offset_y * cos_delta

                tcp_x = painting_pos[0] - rotated_offset_x
                tcp_y = painting_pos[1] - rotated_offset_y

                # Initialize adjustment tracking
                x_adjustment = 0.0
                rz_adjustment = 0.0

                # Apply pressure and rotation adjustments if enabled
                if self.enable_pressure_adjustment and step % 10 == 0:
                    force_x = self._get_x_axis_force()
                    if force_x is not None:
                        # Calculate X position adjustment
                        x_adjustment = self._calculate_pressure_adjustment(force_x)

                        # Calculate rZ rotation adjustment to prevent contour rotation
                        if self.enable_rotation_adjustment:
                            rz_adjustment = self._calculate_rotation_adjustment(force_x, x_adjustment)
                        else:
                            rz_adjustment = 0.0

                        if abs(x_adjustment) > 0.01 or abs(rz_adjustment) > 0.01:
                            print(f"[Pressure] Step {step}: Force={force_x:.2f}N, X_adj={x_adjustment:.3f}mm, rZ_adj={rz_adjustment:.3f}°")

                        tcp_x += x_adjustment

                # Apply rotation adjustment to interpolated angle
                adjusted_angle = interp_angle + rz_adjustment
                while adjusted_angle > 180:
                    adjusted_angle -= 360
                while adjusted_angle < -180:
                    adjusted_angle += 360

                rotation_waypoints.append([tcp_x, tcp_y, paint_z, paint_rx, paint_ry, adjusted_angle])

            ret = self.robot_service.robot.moveCartesianPath(rotation_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to rotate at bottom_left")
                return ret, 0

            # Update current rotation and center position
            current_rz = new_rz
            current_center_x = rotation_waypoints[-1][0]
            current_center_y = rotation_waypoints[-1][1]

            if not self.is_running:
                return -1, 0

            # === Step 7.5: Search for contact after third corner rotation (if enabled) ===
            if self.enable_pressure_adjustment and self.search_at_all_corners:
                print(f"[PaintingOperation] Step 7.5: Searching for contact after bottom_left corner rotation")
                print(f"[PaintingOperation] Current center: X={current_center_x:.2f}, Y={current_center_y:.2f}")
                print(f"[PaintingOperation] Current rotation: rZ={current_rz:.2f}°")

                # After rotation, search for contact with the shaft
                contact_x, contact_y, contact_z, contact_found = self._find_contact_point(
                    current_center_x, current_center_y, paint_z,
                    paint_rx, paint_ry, current_rz,
                    search_direction='x-'  # Shaft is always X- from PAINTING_POS
                )

                if contact_found:
                    print(f"[PaintingOperation] ✓ Contact re-established, offset: {current_center_x - contact_x:.2f}mm")
                    current_center_x = contact_x
                    current_center_y = contact_y

            if not self.is_running:
                return -1, 0

            # === Step 8: Move up so top_left is at PAINTING_POS (painting left edge, completing the loop) ===
            # After 3 rotations (270° total), calculate top_left's new position
            print(f"[PaintingOperation] Step 8: Painting left edge - moving so top_left is back at PAINTING_POS")

            # Calculate top_left's original offset, then rotate by 270° (3 x 90° = -90° = 270°)
            original_tl_offset_x = top_left[0] - current_pose[0]
            original_tl_offset_y = top_left[1] - current_pose[1]

            # Apply 270° rotation (= -90° rotation: swap and negate one)
            # 270° rotation: (x, y) → (y, -x)
            rotated_tl_x = original_tl_offset_y
            rotated_tl_y = -original_tl_offset_x

            # Position TCP so top_left is at PAINTING_POS
            new_center_x = painting_pos[0] - rotated_tl_x
            new_center_y = painting_pos[1] - rotated_tl_y

            waypoint = [new_center_x, new_center_y, paint_z, paint_rx, paint_ry, current_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to paint left edge")
                return ret, 0

            print(f"[PaintingOperation] Corner painting sequence completed successfully")
            # Return success (0) and rotation count (3 rotations of 90° each)
            return 0, 3

        except Exception as e:
            print(f"[PaintingOperation] Error executing corner painting: {e}")
            import traceback
            traceback.print_exc()
            return -1, 0

    def _execute_corner_painting_yz_ry(self, corners_robot, painting_pos, current_rz, current_pose):
        """
        Execute corner painting in YZ plane with rY rotation.
        Used when PAINTING_POS has both rX and rZ close to 90 degrees (vertical shaft orientation).
        Movement plane: YZ, Rotation axis: rY
        Same logic as XY/rZ mode but using Y/Z coordinates and rY rotation.
        """
        try:
            top_left, top_right, bottom_right, bottom_left = corners_robot

            # Calculate edge lengths based on actual corner positions
            # In YZ mode: Y is horizontal, X difference represents vertical (Z) movement
            top_edge_length = abs(top_right[1] - top_left[1])  # Y direction (horizontal)
            right_edge_length = abs(bottom_right[0] - top_right[0])  # X diff = Z movement (vertical)

            print(f"[PaintingOperation] YZ mode - Edge lengths: top={top_edge_length:.2f}mm, right={right_edge_length:.2f}mm")

            # Get orientation from PAINTING_POS
            paint_rx, paint_rz = painting_pos[3], painting_pos[5]
            paint_y = painting_pos[1]
            paint_z = painting_pos[2]
            current_ry = current_pose[4]

            # Track current center position in YZ plane
            current_center_y = current_pose[1]
            current_center_z = current_pose[2]

            # Calculate offsets from current center to corners in YZ plane
            # corners are (x, y) from camera, we map: camera_y -> robot_Y, camera_x_diff -> robot_Z
            center_to_top_left_y = top_left[1] - current_pose[1]
            center_to_top_left_z = 0.0  # Start at current Z (will add X offset for vertical)

            print(f"[PaintingOperation] Center to top_left offset: Y={center_to_top_left_y:.2f}, Z={center_to_top_left_z:.2f}")

            print(f"[PaintingOperation] Center to top_left offset: Y={center_to_top_left_y:.2f}, Z={center_to_top_left_z:.2f}")

            # === Step 1: Move so that top_left corner is at PAINTING_POS ===
            print(f"[PaintingOperation] Step 1: Moving so top_left corner is at PAINTING_POS")
            new_center_y = paint_y - center_to_top_left_y
            new_center_z = paint_z - center_to_top_left_z

            waypoint = [current_pose[0], new_center_y, new_center_z, paint_rx, current_ry, paint_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to move top_left to PAINTING_POS")
                return ret, 0

            # Update tracked center position
            current_center_y = new_center_y
            current_center_z = new_center_z

            if not self.is_running:
                return -1, 0

            # === Step 1.5: Search for exact contact point with shaft BEFORE painting (YZ mode) ===
            if self.enable_pressure_adjustment:
                print(f"[PaintingOperation] Step 1.5: Searching for contact point with shaft (YZ mode)")
                # Current position has top_left at PAINTING_POS
                # In YZ mode, search in Y- direction to find shaft contact
                contact_x, contact_y, contact_z, contact_found = self._find_contact_point(
                    current_pose[0], current_center_y, current_center_z,
                    paint_rx, current_ry, paint_rz,
                    search_direction='y-'
                )

                if contact_found:
                    print(f"[PaintingOperation] ✓ Contact established, offset: {current_center_y - contact_y:.2f}mm")
                    current_center_y = contact_y
                    current_center_z = contact_z
                else:
                    print(f"[PaintingOperation] ⚠ Contact not found, continuing with current position")

            if not self.is_running:
                return -1, 0

            # === Step 2: Move right so top_right is at PAINTING_POS (painting top edge) ===
            # Recalculate top_right offset from CURRENT center position (using original corners)
            center_to_top_right_y = top_right[1] - current_pose[1]  # Original offset
            center_to_top_right_z = 0.0

            print(f"[PaintingOperation] Step 2: Painting top edge - moving so top_right is at PAINTING_POS")
            new_center_y = paint_y - center_to_top_right_y
            new_center_z = paint_z - center_to_top_right_z

            waypoint = [current_pose[0], new_center_y, new_center_z, paint_rx, current_ry, paint_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to paint top edge")
                return ret, 0

            # Update tracked center position
            current_center_y = new_center_y
            current_center_z = new_center_z


            if not self.is_running:
                return -1, 0

            # === Step 3: Rotate rY by 90° while keeping top_right at PAINTING_POS ===
            print(f"[PaintingOperation] Step 3: Rotating rY by 90° around top_right corner")
            new_ry = current_ry + 90.0
            while new_ry > 180:
                new_ry -= 360
            while new_ry < -180:
                new_ry += 360

            # Current offset from TCP center to corner (top_right at PAINTING_POS)
            # TCP center is NOW at (current_center_y, current_center_z)
            corner_offset_y = paint_y - current_center_y
            corner_offset_z = paint_z - current_center_z

            print(f"[PaintingOperation] Corner offset from TCP: Y={corner_offset_y:.2f}, Z={corner_offset_z:.2f}")

            # Generate waypoints for smooth rotation
            num_steps = max(1, int(90.0 / self.rotation_step))  # Calculate steps based on rotation_step parameter
            rotation_waypoints = []

            for step in range(1, num_steps + 1):
                # Interpolate rotation
                interp_angle = current_ry + (90.0 * step / num_steps)
                while interp_angle > 180:
                    interp_angle -= 360
                while interp_angle < -180:
                    interp_angle += 360

                # Calculate how much we've rotated from start
                delta_angle = (90.0 * step / num_steps)
                delta_rad = np.radians(delta_angle)
                cos_delta = np.cos(delta_rad)
                sin_delta = np.sin(delta_rad)

                # Rotate the corner offset in YZ plane
                rotated_offset_y = corner_offset_y * cos_delta - corner_offset_z * sin_delta
                rotated_offset_z = corner_offset_y * sin_delta + corner_offset_z * cos_delta

                # Calculate TCP position to keep corner at PAINTING_POS
                tcp_y = paint_y - rotated_offset_y
                tcp_z = paint_z - rotated_offset_z

                # Initialize adjustment tracking
                y_adjustment = 0.0
                ry_adjustment = 0.0

                # Apply pressure and rotation adjustments if enabled (adjust Y in YZ mode)
                if self.enable_pressure_adjustment and step % 10 == 0:
                    force_x = self._get_x_axis_force()
                    if force_x is not None:
                        # Calculate Y position adjustment
                        y_adjustment = self._calculate_pressure_adjustment(force_x)

                        # Calculate rY rotation adjustment to prevent contour rotation
                        ry_adjustment = self._calculate_rotation_adjustment(force_x, y_adjustment)

                        if abs(y_adjustment) > 0.01 or abs(ry_adjustment) > 0.01:
                            print(f"[Pressure] Step {step}: Force={force_x:.2f}N, Y_adj={y_adjustment:.3f}mm, rY_adj={ry_adjustment:.3f}°")

                        tcp_y += y_adjustment

                # Apply rotation adjustment to interpolated angle
                adjusted_angle = interp_angle + ry_adjustment
                while adjusted_angle > 180:
                    adjusted_angle -= 360
                while adjusted_angle < -180:
                    adjusted_angle += 360

                rotation_waypoints.append([current_pose[0], tcp_y, tcp_z, paint_rx, adjusted_angle, paint_rz])

            print(f"[PaintingOperation] Executing rotation with {len(rotation_waypoints)} waypoints")
            ret = self.robot_service.robot.moveCartesianPath(rotation_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to rotate at top_right")
                return ret, 0

            # Update current rotation and center position to final values
            current_ry = new_ry
            current_center_y = rotation_waypoints[-1][1]
            current_center_z = rotation_waypoints[-1][2]

            current_center_z = rotation_waypoints[-1][2]

            if not self.is_running:
                return -1, 0

            # === Step 3.5: Search for contact after first corner rotation (if enabled) ===
            if self.enable_pressure_adjustment and self.search_at_all_corners:
                print(f"[PaintingOperation] Step 3.5: Searching for contact after top_right corner rotation (YZ mode)")
                print(f"[PaintingOperation] Current center: Y={current_center_y:.2f}, Z={current_center_z:.2f}")
                print(f"[PaintingOperation] Current rotation: rY={current_ry:.2f}°")

                # After rotation, search for contact with the shaft
                contact_x, contact_y, contact_z, contact_found = self._find_contact_point(
                    current_pose[0], current_center_y, current_center_z,
                    paint_rx, current_ry, paint_rz,
                    search_direction='y-'  # Shaft is always Y- from PAINTING_POS
                )

                if contact_found:
                    print(f"[PaintingOperation] ✓ Contact re-established, offset: {current_center_y - contact_y:.2f}mm")
                    current_center_y = contact_y
                    current_center_z = contact_z

            if not self.is_running:
                return -1, 0

            # === Step 4: Move down so bottom_right is at PAINTING_POS (painting right edge) ===
            # After 1 rotation (90°), calculate where bottom_right is now
            print(f"[PaintingOperation] Step 4: Painting right edge - moving so bottom_right is at PAINTING_POS")

            # Calculate bottom_right's original offset from initial center, then rotate by 90°
            # Use X difference to determine Z offset (vertical movement)
            original_br_offset_y = top_right[1] - current_pose[1]  # Y offset same as top_right
            original_br_offset_z = right_edge_length  # Z offset = height of contour

            # Apply 90° rotation in YZ plane
            angle_90 = np.radians(90.0)
            cos_90 = np.cos(angle_90)
            sin_90 = np.sin(angle_90)

            rotated_br_y = original_br_offset_y * cos_90 - original_br_offset_z * sin_90
            rotated_br_z = original_br_offset_y * sin_90 + original_br_offset_z * cos_90

            # Position TCP so bottom_right is at PAINTING_POS
            new_center_y = paint_y - rotated_br_y
            new_center_z = paint_z - rotated_br_z

            waypoint = [current_pose[0], new_center_y, new_center_z, paint_rx, current_ry, paint_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to paint right edge")
                return ret, 0

            # Update tracked center position
            current_center_y = new_center_y
            current_center_z = new_center_z


            if not self.is_running:
                return -1, 0

            # === Step 5: Rotate rY by 90° around bottom_right corner ===
            print(f"[PaintingOperation] Step 5: Rotating rY by 90° around bottom_right corner")
            new_ry = current_ry + 90.0
            while new_ry > 180:
                new_ry -= 360
            while new_ry < -180:
                new_ry += 360

            # Rotate around bottom_right (which is at PAINTING_POS)
            # Use CURRENT center position
            corner_offset_y = paint_y - current_center_y
            corner_offset_z = paint_z - current_center_z

            num_steps = max(1, int(90.0 / self.rotation_step))  # Calculate steps based on rotation_step parameter
            rotation_waypoints = []

            for step in range(1, num_steps + 1):
                interp_angle = current_ry + (90.0 * step / num_steps)
                while interp_angle > 180:
                    interp_angle -= 360
                while interp_angle < -180:
                    interp_angle += 360

                delta_angle = (90.0 * step / num_steps)
                delta_rad = np.radians(delta_angle)
                cos_delta = np.cos(delta_rad)
                sin_delta = np.sin(delta_rad)

                rotated_offset_y = corner_offset_y * cos_delta - corner_offset_z * sin_delta
                rotated_offset_z = corner_offset_y * sin_delta + corner_offset_z * cos_delta

                tcp_y = paint_y - rotated_offset_y
                tcp_z = paint_z - rotated_offset_z

                # Initialize adjustment tracking
                y_adjustment = 0.0
                ry_adjustment = 0.0

                # Apply pressure and rotation adjustments if enabled
                if self.enable_pressure_adjustment and step % 10 == 0:
                    force_x = self._get_x_axis_force()
                    if force_x is not None:
                        # Calculate Y position adjustment
                        y_adjustment = self._calculate_pressure_adjustment(force_x)

                        # Calculate rY rotation adjustment to prevent contour rotation
                        ry_adjustment = self._calculate_rotation_adjustment(force_x, y_adjustment)

                        if abs(y_adjustment) > 0.01 or abs(ry_adjustment) > 0.01:
                            print(f"[Pressure] Step {step}: Force={force_x:.2f}N, Y_adj={y_adjustment:.3f}mm, rY_adj={ry_adjustment:.3f}°")

                        tcp_y += y_adjustment

                # Apply rotation adjustment to interpolated angle
                adjusted_angle = interp_angle + ry_adjustment
                while adjusted_angle > 180:
                    adjusted_angle -= 360
                while adjusted_angle < -180:
                    adjusted_angle += 360

                rotation_waypoints.append([current_pose[0], tcp_y, tcp_z, paint_rx, adjusted_angle, paint_rz])

            ret = self.robot_service.robot.moveCartesianPath(rotation_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to rotate at bottom_right")
                return ret, 0

            # Update current rotation and center position
            current_ry = new_ry
            current_center_y = rotation_waypoints[-1][1]
            current_center_z = rotation_waypoints[-1][2]

            if not self.is_running:
                return -1, 0

            # === Step 5.5: Search for contact after second corner rotation (if enabled) ===
            if self.enable_pressure_adjustment and self.search_at_all_corners:
                print(f"[PaintingOperation] Step 5.5: Searching for contact after bottom_right corner rotation (YZ mode)")
                print(f"[PaintingOperation] Current center: Y={current_center_y:.2f}, Z={current_center_z:.2f}")
                print(f"[PaintingOperation] Current rotation: rY={current_ry:.2f}°")

                # After rotation, search for contact with the shaft
                contact_x, contact_y, contact_z, contact_found = self._find_contact_point(
                    current_pose[0], current_center_y, current_center_z,
                    paint_rx, current_ry, paint_rz,
                    search_direction='y-'  # Shaft is always Y- from PAINTING_POS
                )

                if contact_found:
                    print(f"[PaintingOperation] ✓ Contact re-established, offset: {current_center_y - contact_y:.2f}mm")
                    current_center_y = contact_y
                    current_center_z = contact_z

            if not self.is_running:
                return -1, 0

            # === Step 6: Move left so bottom_left is at PAINTING_POS (painting bottom edge) ===
            # After 2 rotations (180° total), calculate bottom_left's new position
            print(f"[PaintingOperation] Step 6: Painting bottom edge - moving so bottom_left is at PAINTING_POS")

            # Calculate bottom_left's original offset, then rotate by 180° (2 x 90°)
            original_bl_offset_y = bottom_left[1] - current_pose[1]
            original_bl_offset_z = right_edge_length  # Z offset = height

            # Apply 180° rotation (easier: just negate both offsets)
            rotated_bl_y = -original_bl_offset_y
            rotated_bl_z = -original_bl_offset_z

            # Position TCP so bottom_left is at PAINTING_POS
            new_center_y = paint_y - rotated_bl_y
            new_center_z = paint_z - rotated_bl_z

            waypoint = [current_pose[0], new_center_y, new_center_z, paint_rx, current_ry, paint_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to paint bottom edge")
                return ret, 0

            # Update tracked center position
            current_center_y = new_center_y
            current_center_z = new_center_z


            if not self.is_running:
                return -1, 0

            # === Step 7: Rotate rY by 90° around bottom_left corner ===
            print(f"[PaintingOperation] Step 7: Rotating rY by 90° around bottom_left corner")
            new_ry = current_ry + 90.0
            while new_ry > 180:
                new_ry -= 360
            while new_ry < -180:
                new_ry += 360

            # Rotate around bottom_left (which is at PAINTING_POS)
            # Use CURRENT center position
            corner_offset_y = paint_y - current_center_y
            corner_offset_z = paint_z - current_center_z

            num_steps = max(1, int(90.0 / self.rotation_step))  # Calculate steps based on rotation_step parameter
            rotation_waypoints = []

            for step in range(1, num_steps + 1):
                interp_angle = current_ry + (90.0 * step / num_steps)
                while interp_angle > 180:
                    interp_angle -= 360
                while interp_angle < -180:
                    interp_angle += 360

                delta_angle = (90.0 * step / num_steps)
                delta_rad = np.radians(delta_angle)
                cos_delta = np.cos(delta_rad)
                sin_delta = np.sin(delta_rad)

                rotated_offset_y = corner_offset_y * cos_delta - corner_offset_z * sin_delta
                rotated_offset_z = corner_offset_y * sin_delta + corner_offset_z * cos_delta

                tcp_y = paint_y - rotated_offset_y
                tcp_z = paint_z - rotated_offset_z

                # Initialize adjustment tracking
                y_adjustment = 0.0
                ry_adjustment = 0.0

                # Apply pressure and rotation adjustments if enabled
                if self.enable_pressure_adjustment and step % 10 == 0:
                    force_x = self._get_x_axis_force()
                    if force_x is not None:
                        # Calculate Y position adjustment
                        y_adjustment = self._calculate_pressure_adjustment(force_x)

                        # Calculate rY rotation adjustment to prevent contour rotation
                        ry_adjustment = self._calculate_rotation_adjustment(force_x, y_adjustment)

                        if abs(y_adjustment) > 0.01 or abs(ry_adjustment) > 0.01:
                            print(f"[Pressure] Step {step}: Force={force_x:.2f}N, Y_adj={y_adjustment:.3f}mm, rY_adj={ry_adjustment:.3f}°")

                        tcp_y += y_adjustment

                # Apply rotation adjustment to interpolated angle
                adjusted_angle = interp_angle + ry_adjustment
                while adjusted_angle > 180:
                    adjusted_angle -= 360
                while adjusted_angle < -180:
                    adjusted_angle += 360

                rotation_waypoints.append([current_pose[0], tcp_y, tcp_z, paint_rx, adjusted_angle, paint_rz])

            ret = self.robot_service.robot.moveCartesianPath(rotation_waypoints, vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to rotate at bottom_left")
                return ret, 0

            # Update current rotation and center position
            current_ry = new_ry
            current_center_y = rotation_waypoints[-1][1]
            current_center_z = rotation_waypoints[-1][2]

            if not self.is_running:
                return -1, 0

            # === Step 7.5: Search for contact after third corner rotation (if enabled) ===
            if self.enable_pressure_adjustment and self.search_at_all_corners:
                print(f"[PaintingOperation] Step 7.5: Searching for contact after bottom_left corner rotation (YZ mode)")
                print(f"[PaintingOperation] Current center: Y={current_center_y:.2f}, Z={current_center_z:.2f}")
                print(f"[PaintingOperation] Current rotation: rY={current_ry:.2f}°")

                # After rotation, search for contact with the shaft
                contact_x, contact_y, contact_z, contact_found = self._find_contact_point(
                    current_pose[0], current_center_y, current_center_z,
                    paint_rx, current_ry, paint_rz,
                    search_direction='y-'  # Shaft is always Y- from PAINTING_POS
                )

                if contact_found:
                    print(f"[PaintingOperation] ✓ Contact re-established, offset: {current_center_y - contact_y:.2f}mm")
                    current_center_y = contact_y
                    current_center_z = contact_z

            if not self.is_running:
                return -1, 0

            # === Step 8: Move up so top_left is at PAINTING_POS (painting left edge, completing the loop) ===
            # After 3 rotations (270° total), calculate top_left's new position
            print(f"[PaintingOperation] Step 8: Painting left edge - moving so top_left is back at PAINTING_POS")

            # Calculate top_left's original offset, then rotate by 270° (3 x 90° = -90° = 270°)
            original_tl_offset_y = top_left[1] - current_pose[1]
            original_tl_offset_z = 0.0  # Started at Z=0

            # Apply 270° rotation (= -90° rotation: swap and negate one)
            # 270° rotation in YZ: (y, z) → (z, -y)
            rotated_tl_y = original_tl_offset_z
            rotated_tl_z = -original_tl_offset_y

            # Position TCP so top_left is at PAINTING_POS
            new_center_y = paint_y - rotated_tl_y
            new_center_z = paint_z - rotated_tl_z

            waypoint = [current_pose[0], new_center_y, new_center_z, paint_rx, current_ry, paint_rz]
            ret = self.robot_service.robot.moveCartesianPath([waypoint], vel=self.velocity, acc=self.acceleration, decimate=False)
            if ret != 0:
                print(f"[PaintingOperation] Failed to paint left edge")
                return ret, 0

            print(f"[PaintingOperation] YZ corner painting sequence completed successfully")
            return 0

        except Exception as e:
            print(f"[PaintingOperation] Error executing YZ corner painting: {e}")
            import traceback
            traceback.print_exc()
            return -1

    def _ensure_joint6_at_target(self):
        try:
            if not self.robot_service or not self.robot_service.robot:
                print("[PaintingOperation] Robot service not available")
                return False

            if not hasattr(self.robot_service.robot, 'current_joint_state') or not self.robot_service.robot.current_joint_state:
                print("[PaintingOperation] Joint state not available")
                return False

            joints = self.robot_service.robot.current_joint_state.position[:6]
            joint6_rad = joints[5]
            joint6_deg = np.degrees(joint6_rad)

            print(f"[PaintingOperation] Current Joint 6: {joint6_deg:.1f}°")

            target_deg = 203.0
            tolerance = 5.0

            if abs(joint6_deg - target_deg) < tolerance:
                print(f"[PaintingOperation] Joint 6 already at target ({joint6_deg:.1f}° ≈ {target_deg}°)")
                return True

            print(f"[PaintingOperation] Joint 6 needs adjustment: {joint6_deg:.1f}° → {target_deg}°")

            current_pose = self.robot_service.robot.get_current_position()
            if not current_pose or len(current_pose) < 6:
                print("[PaintingOperation] Failed to get current position")
                return False

            diff_deg = target_deg - joint6_deg

            if abs(diff_deg) > 180:
                if diff_deg > 0:
                    diff_deg -= 360
                else:
                    diff_deg += 360

            num_steps = max(1, int(abs(diff_deg) / self.joint_rotation_step))
            step_size = diff_deg / num_steps

            print(f"[PaintingOperation] Rotating Joint 6 in {num_steps} steps of {step_size:.1f}°")

            for step in range(num_steps):
                if not self.is_running:
                    return False

                intermediate_rz = current_pose[5] + step_size * (step + 1)
                while intermediate_rz > 180:
                    intermediate_rz -= 360
                while intermediate_rz < -180:
                    intermediate_rz += 360

                waypoint = [current_pose[0], current_pose[1], current_pose[2],
                           current_pose[3], current_pose[4], intermediate_rz]

                ret = self.robot_service.robot.moveCartesianPath([waypoint],
                                                                vel=self.velocity,
                                                                acc=self.acceleration,
                                                                decimate=False)
                if ret != 0:
                    print(f"[PaintingOperation] Failed to rotate Joint 6 at step {step+1}")
                    return False

            print(f"[PaintingOperation] Joint 6 rotated to target position")
            return True

        except Exception as e:
            print(f"[PaintingOperation] Error ensuring Joint 6 position: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _do_pause(self, *args, **kwargs):
        print(f"[PaintingOperation] Pausing painting operation")

        # Set flag first to pause the painting loop
        self.is_running = False

        if self.robot_service:
            # Stop robot motion - this sets command_in_progress=False in ZeroErrRobot
            # which will cause any ongoing motion commands to complete
            self.robot_service.robot.stop_motion()
            print("[PaintingOperation] Robot stop_motion() called")

        # Wait for thread to finish (with timeout)
        if self.execution_thread and self.execution_thread.is_alive():
            print("[PaintingOperation] Waiting for execution thread to pause...")
            self.execution_thread.join(timeout=3.0)
            if self.execution_thread.is_alive():
                print("[PaintingOperation] Warning: Execution thread did not pause within timeout")
            else:
                print("[PaintingOperation] Execution thread paused successfully")

        self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.PAUSED)

    def _do_resume(self, *args, **kwargs):
        print(f"[PaintingOperation] Resuming painting operation")
        # For now, just transition back to idle since we don't have resume capability yet
        # In a full implementation, we'd resume from where we paused
        self.broker.publish(SystemTopics.OPERATION_STATE, OperationState.IDLE)
