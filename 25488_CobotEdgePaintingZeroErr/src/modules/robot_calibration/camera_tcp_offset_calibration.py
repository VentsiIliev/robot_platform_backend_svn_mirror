"""
Camera-to-TCP Offset Calibration Module

This module performs a standalone calibration to determine the physical offset
between the camera optical center and the TCP (Tool Center Point).

Method:
1. User positions TCP EXACTLY at chessboard center
2. System captures initial TCP position
3. Robot moves incrementally in X and Y directions
4. System detects when camera sees chessboard center
5. Offset = final_position - initial_position
"""

import time
import numpy as np
from modules.robot_calibration.CalibrationVision import CalibrationVision
from modules.robot_calibration.robot_controller import CalibrationRobotController
from modules.utils.custom_logging import log_info_message, log_debug_message, log_warning_message, LoggerContext


def detect_chessboard_center(system, calibration_vision, max_attempts=3):
    """
    Detect chessboard and return if center is visible in camera.

    Returns:
        tuple: (found, center_x_px, center_y_px, distance_from_image_center)
    """
    for _ in range(max_attempts):
        frame = system.getLatestFrame()
        if frame is None:
            continue

        result = calibration_vision.find_chessboard_and_compute_ppm(frame)

        if result.found and hasattr(calibration_vision, 'chessboard_center_px') and calibration_vision.chessboard_center_px:
            # Get image center
            frame_height, frame_width = frame.shape[:2]
            image_center_x = frame_width / 2.0
            image_center_y = frame_height / 2.0

            # Get chessboard center
            cb_center_x, cb_center_y = calibration_vision.chessboard_center_px

            # Calculate distance from image center
            dx = cb_center_x - image_center_x
            dy = cb_center_y - image_center_y
            distance = np.sqrt(dx**2 + dy**2)

            return True, cb_center_x, cb_center_y, distance

    return False, 0, 0, float('inf')


def start_camera_tcp_offset_calibration(controller_service):
    """
    Main entry point for camera-to-TCP offset calibration.

    Args:
        controller_service: The controller service providing access to robot and vision

    Returns:
        dict: Result with success status and offset values
    """
    logger_context = LoggerContext(enabled=True, logger=None)

    try:
        log_info_message(logger_context, "=== Starting Camera-to-TCP Offset Calibration ===")
        print("[Camera-TCP Calibration] Starting calibration procedure")

        # Get controller
        controller = controller_service.get_controller()
        print(f"[Camera-TCP Calibration] Controller: {controller}")
        if not controller:
            error_msg = "Controller not available"
            print(f"[Camera-TCP Calibration] ERROR: {error_msg}")
            return {"success": False, "error": error_msg}

        # Get requestSender which has access to RequestHandler which has application
        request_sender = getattr(controller, 'requestSender', None)
        print(f"[Camera-TCP Calibration] RequestSender: {request_sender}")
        if not request_sender:
            error_msg = "RequestSender not available"
            print(f"[Camera-TCP Calibration] ERROR: {error_msg}")
            return {"success": False, "error": error_msg}

        # Get request handler which has application
        request_handler = getattr(request_sender, 'request_handler', None)
        print(f"[Camera-TCP Calibration] Request handler: {request_handler}")
        if not request_handler:
            error_msg = "Request handler not available"
            print(f"[Camera-TCP Calibration] ERROR: {error_msg}")
            return {"success": False, "error": error_msg}

        # Get application from request handler
        application = getattr(request_handler, 'application', None)
        print(f"[Camera-TCP Calibration] Application: {application}")
        if not application:
            error_msg = "Application not available in request handler"
            print(f"[Camera-TCP Calibration] ERROR: {error_msg}")
            return {"success": False, "error": error_msg}

        # Get robot service from application
        robot_service = getattr(application, 'robot_service', None)
        print(f"[Camera-TCP Calibration] Robot service: {robot_service}")
        if not robot_service:
            error_msg = "Robot service not available in application"
            print(f"[Camera-TCP Calibration] ERROR: {error_msg}")
            return {"success": False, "error": error_msg}

        # Get vision service from application
        vision_service = getattr(application, 'vision_service', None)
        print(f"[Camera-TCP Calibration] Vision service: {vision_service}")
        if not vision_service:
            error_msg = "Vision service not available in application"
            print(f"[Camera-TCP Calibration] ERROR: {error_msg}")
            return {"success": False, "error": error_msg}

        # The vision_service itself IS the vision system (_VisionService extends VisionSystem)
        vision_system = vision_service
        print(f"[Camera-TCP Calibration] Vision system: {vision_system}")

        # Get camera settings
        camera_settings = vision_system.camera_settings
        print(f"[Camera-TCP Calibration] Camera settings: {camera_settings}")
        chessboard_size = (
            camera_settings.get_chessboard_width(),
            camera_settings.get_chessboard_height()
        )
        square_size_mm = camera_settings.get_square_size_mm()
        print(f"[Camera-TCP Calibration] Chessboard size: {chessboard_size}, square size: {square_size_mm}mm")

        # Create calibration vision instance
        print("[Camera-TCP Calibration] Creating CalibrationVision instance...")
        calibration_vision = CalibrationVision(
            vision_system,
            chessboard_size,
            square_size_mm,
            set(),  # No marker IDs needed
            logger_context,
            debug_draw=False,
            debug=False
        )
        print("[Camera-TCP Calibration] CalibrationVision created successfully")

        # Create robot controller wrapper
        print("[Camera-TCP Calibration] Creating CalibrationRobotController...")
        calib_robot_controller = CalibrationRobotController(
            robot_service,
            None,  # No adaptive movement config needed
            logger_context
        )
        print("[Camera-TCP Calibration] CalibrationRobotController created successfully")

        log_info_message(logger_context, "Step 1: Capturing initial TCP position (TCP should be at chessboard center)")

        # Capture initial TCP position
        initial_position = robot_service.robot.get_current_position()
        if not initial_position or len(initial_position) < 2:
            return {"success": False, "error": "Could not get initial TCP position"}

        tcp_start_x = initial_position[0]
        tcp_start_y = initial_position[1]

        log_info_message(logger_context, f"  Initial TCP at chessboard center: X={tcp_start_x:.2f}mm, Y={tcp_start_y:.2f}mm")

        # Constants for incremental movement
        INITIAL_MOVE_MM = 60  # Move camera away from center initially so it can see whole board
        MOVE_STEP_MM = 10  # Move 10mm at a time
        MAX_MOVES = 20     # Max 200mm total movement
        DELAY_AFTER_MOVE = 0.5
        CENTER_THRESHOLD_PX = 20  # Consider "centered" if within 20 pixels

        log_info_message(logger_context, "Step 2: Finding position where camera can see whole chessboard")

        # Try to detect chessboard at current position first
        found, cb_x, cb_y, distance = detect_chessboard_center(vision_system, calibration_vision)

        if found:
            log_info_message(logger_context, f"  ✓ Chessboard already visible at current position!")
        else:
            log_info_message(logger_context, f"  Chessboard not visible at current position (TCP at center)")

            # Step 2a: Move in +X direction first
            log_info_message(logger_context, f"  Step 2a: Moving +{INITIAL_MOVE_MM}mm in X direction...")
            ret = calib_robot_controller.move_x_relative(INITIAL_MOVE_MM, blocking=True)
            if ret != 0:
                return {"success": False, "error": "Failed to move in X+ direction"}

            # Wait for camera to stabilize
            log_info_message(logger_context, f"  Waiting for camera to stabilize...")
            time.sleep(1.0)  # Wait for camera stabilization

            # Try to detect after X+ movement with more attempts
            log_info_message(logger_context, f"  Attempting to detect chessboard after X+ movement (50 attempts)...")
            found, cb_x, cb_y, distance = detect_chessboard_center(vision_system, calibration_vision, max_attempts=50)

            if found:
                log_info_message(logger_context, f"  ✓ Chessboard found after X+ movement!")
            else:
                log_info_message(logger_context, f"  Chessboard not found after X+, trying Y+ as backup...")

                # Step 2b: Move in +Y direction as backup
                log_info_message(logger_context, f"  Step 2b: Moving +{INITIAL_MOVE_MM}mm in Y direction...")
                ret = calib_robot_controller.move_y_relative(INITIAL_MOVE_MM, blocking=True)
                if ret != 0:
                    return {"success": False, "error": "Failed to move in Y+ direction"}
                time.sleep(1.0)  # Wait for stabilization

                # Try to detect after Y+ movement with 50 attempts
                log_info_message(logger_context, f"  Attempting to detect chessboard after Y+ movement (50 attempts)...")
                found, cb_x, cb_y, distance = detect_chessboard_center(vision_system, calibration_vision, max_attempts=50)

                if found:
                    log_info_message(logger_context, f"  ✓ Chessboard found after X+Y+ movement!")
                else:
                    # Last attempt - move back to start and try negative directions
                    log_info_message(logger_context, f"  Chessboard still not found, moving back to try negative directions...")

                    # Move back to start
                    calib_robot_controller.move_x_relative(-INITIAL_MOVE_MM, blocking=True)
                    calib_robot_controller.move_y_relative(-INITIAL_MOVE_MM, blocking=True)
                    time.sleep(DELAY_AFTER_MOVE)

                    # Try -X direction
                    log_info_message(logger_context, f"  Step 2c: Trying -{INITIAL_MOVE_MM}mm in X direction...")
                    ret = calib_robot_controller.move_x_relative(-INITIAL_MOVE_MM, blocking=True)
                    if ret == 0:
                        time.sleep(1.0)
                        found, cb_x, cb_y, distance = detect_chessboard_center(vision_system, calibration_vision, max_attempts=50)

                        if found:
                            log_info_message(logger_context, f"  ✓ Chessboard found after X- movement!")
                        else:
                            # Try -Y as final attempt
                            log_info_message(logger_context, f"  Step 2d: Trying -{INITIAL_MOVE_MM}mm in Y direction...")
                            calib_robot_controller.move_x_relative(INITIAL_MOVE_MM, blocking=True)  # Back to start
                            time.sleep(1.0)
                            ret = calib_robot_controller.move_y_relative(-INITIAL_MOVE_MM, blocking=True)
                            if ret == 0:
                                time.sleep(1.0)
                                found, cb_x, cb_y, distance = detect_chessboard_center(vision_system, calibration_vision, max_attempts=50)

                                if found:
                                    log_info_message(logger_context, f"  ✓ Chessboard found after Y- movement!")

        # Final check - if still not found after all attempts, fail
        if not found:
            return {"success": False, "error": "Could not detect chessboard after trying all directions. Ensure chessboard is on the table and properly lit."}

        # ✅ Board detected! Calculate offset NOW before any centering movements
        log_info_message(logger_context, "Step 3: Calculating camera-to-TCP offset from first detection position")

        # Get current position (where camera can see the board)
        camera_detection_position = robot_service.robot.get_current_position()
        if not camera_detection_position or len(camera_detection_position) < 2:
            return {"success": False, "error": "Could not get camera position after detection"}

        camera_at_detection_x = camera_detection_position[0]
        camera_at_detection_y = camera_detection_position[1]

        # Calculate offset: TCP was at start, camera is now at detection position
        offset_x = tcp_start_x - camera_at_detection_x
        offset_y = tcp_start_y - camera_at_detection_y

        log_info_message(logger_context, f"  TCP at chessboard center: X={tcp_start_x:.2f}mm, Y={tcp_start_y:.2f}mm")
        log_info_message(logger_context, f"  Camera first detected board at: X={camera_at_detection_x:.2f}mm, Y={camera_at_detection_y:.2f}mm")
        log_info_message(logger_context, f"  📐 Camera-to-TCP offset: X={offset_x:.2f}mm, Y={offset_y:.2f}mm")

        log_info_message(logger_context, "Step 4: Moving camera until chessboard is centered (for verification)")
        log_info_message(logger_context, f"  Chessboard detected! Distance from image center: {distance:.1f}px")

        # Get image dimensions for determining move direction
        frame = vision_system.getLatestFrame()
        frame_height, frame_width = frame.shape[:2]
        image_center_x = frame_width / 2.0
        image_center_y = frame_height / 2.0

        total_x_movement = 0
        total_y_movement = 0

        # Move until chessboard center is at image center
        for iteration in range(MAX_MOVES):
            found, cb_x, cb_y, distance = detect_chessboard_center(vision_system, calibration_vision, max_attempts=1)

            if not found:
                log_warning_message(logger_context, f"  Iteration {iteration+1}: Lost chessboard detection")
                break

            log_debug_message(logger_context, f"  Iteration {iteration+1}: Chessboard at ({cb_x:.1f}, {cb_y:.1f})px, distance={distance:.1f}px")

            if distance < CENTER_THRESHOLD_PX:
                log_info_message(logger_context, f"  ✅ Chessboard center is now at image center! (distance={distance:.1f}px)")
                break

            # Calculate movement direction
            dx_px = cb_x - image_center_x
            dy_px = cb_y - image_center_y

            # Determine which axis to move and in what direction
            # If chessboard is to the right of image center (dx_px > 0), move robot left (negative X)
            # If chessboard is below image center (dy_px > 0), move robot down (negative Y)

            move_x_mm = 0
            move_y_mm = 0

            if abs(dx_px) > abs(dy_px):
                # Move in X direction
                move_x_mm = -MOVE_STEP_MM if dx_px > 0 else MOVE_STEP_MM
            else:
                # Move in Y direction
                move_y_mm = -MOVE_STEP_MM if dy_px > 0 else MOVE_STEP_MM

            log_debug_message(logger_context, f"  Moving: X={move_x_mm:+.1f}mm, Y={move_y_mm:+.1f}mm")

            # Execute movement
            if move_x_mm != 0:
                ret = calib_robot_controller.move_x_relative(move_x_mm, blocking=True)
                if ret != 0:
                    return {"success": False, "error": f"Robot movement failed at iteration {iteration+1}"}
                total_x_movement += move_x_mm

            if move_y_mm != 0:
                ret = calib_robot_controller.move_y_relative(move_y_mm, blocking=True)
                if ret != 0:
                    return {"success": False, "error": f"Robot movement failed at iteration {iteration+1}"}
                total_y_movement += move_y_mm

            time.sleep(DELAY_AFTER_MOVE)

        # Get final centered position (for logging/verification only)
        final_position = robot_service.robot.get_current_position()
        if not final_position or len(final_position) < 2:
            log_warning_message(logger_context, "Could not get final centered position")
            camera_at_center_x = camera_at_detection_x
            camera_at_center_y = camera_at_detection_y
        else:
            camera_at_center_x = final_position[0]
            camera_at_center_y = final_position[1]

        # Offset was already calculated in Step 3, log verification info
        log_info_message(logger_context, "Step 5: Calibration complete - verification")
        log_info_message(logger_context, f"  Final centered position: X={camera_at_center_x:.2f}mm, Y={camera_at_center_y:.2f}mm")
        log_info_message(logger_context, f"  Total centering movement: X={total_x_movement:.2f}mm, Y={total_y_movement:.2f}mm")
        log_info_message(logger_context, f"  ✅ Using offset calculated at first detection: X={offset_x:.2f}mm, Y={offset_y:.2f}mm")

        log_info_message(logger_context, "=== Camera-to-TCP Offset Calibration Complete ===")

        return {
            "success": True,
            "offset_x_mm": offset_x,
            "offset_y_mm": offset_y,
            "tcp_start": {"x": tcp_start_x, "y": tcp_start_y},
            "camera_at_detection": {"x": camera_at_detection_x, "y": camera_at_detection_y},
            "camera_at_center": {"x": camera_at_center_x, "y": camera_at_center_y},
            "total_movement": {"x": total_x_movement, "y": total_y_movement}
        }

    except Exception as e:
        import traceback
        error_msg = f"Calibration error: {str(e)}\n{traceback.format_exc()}"
        log_warning_message(logger_context, error_msg)
        return {"success": False, "error": str(e)}

