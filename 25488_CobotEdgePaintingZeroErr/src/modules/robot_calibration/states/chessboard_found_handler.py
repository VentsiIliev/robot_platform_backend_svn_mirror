"""
Chessboard Found State Handler

Handles the state when a chessboard has been successfully detected.
This is a transition state that prepares for ArUco marker detection.
"""

from modules.utils.custom_logging import log_debug_message
from modules.robot_calibration.states.robot_calibration_states import RobotCalibrationStates


def handle_chessboard_found_state(context) -> RobotCalibrationStates:
    """
    Handle the CHESSBOARD_FOUND state.
    
    CRITICAL FOR CAMERA-TO-TCP OFFSET CALCULATION:

    For precise offset measurement, follow this workflow:
    1. Position TCP EXACTLY at the center of the chessboard (use a pointer/stylus)
    2. Start calibration - TCP position is captured
    3. Robot moves to detect markers with the camera
    4. System calculates: offset = tcp_position - camera_position
    5. This gives the exact physical mounting offset

    The more precisely you position the TCP at chessboard center initially,
    the more accurate the calculated offset will be.

    Args:
        context: RobotCalibrationContext containing all calibration state
        
    Returns:
        Next state to transition to
    """
    log_debug_message(
        context.logger_context, 
        f"CHESSBOARD FOUND at {context.chessboard_center_px}, calculating TCP offset..."
    )
    
    # Capture current TCP position (this is offset below chessboard center for visibility)
    current_position = context.calibration_robot_controller.get_current_position()

    if current_position:
        # Store the current TCP position
        # The actual offset calculation will be done in finalization when we have
        # the camera-to-robot transformation
        context.tcp_at_chessboard_start = current_position[:2]  # Store X, Y only

        log_debug_message(
            context.logger_context,
            f"✓ Captured TCP start position: X={current_position[0]:.2f}mm, Y={current_position[1]:.2f}mm"
        )

        # Log chessboard center if available
        if context.chessboard_center_px is not None:
            log_debug_message(
                context.logger_context,
                f"✓ Chessboard center detected at: X={context.chessboard_center_px[0]:.1f}px, Y={context.chessboard_center_px[1]:.1f}px"
            )
        else:
            log_debug_message(
                context.logger_context,
                "⚠ Chessboard center not yet available in context (will be set from calibration_vision)"
            )
    else:
        log_debug_message(
            context.logger_context,
            "⚠ Warning: Could not capture TCP position"
        )

    # Transition directly to looking for ArUco markers
    # The chessboard detection has already stored the necessary reference points
    return RobotCalibrationStates.LOOKING_FOR_ARUCO_MARKERS