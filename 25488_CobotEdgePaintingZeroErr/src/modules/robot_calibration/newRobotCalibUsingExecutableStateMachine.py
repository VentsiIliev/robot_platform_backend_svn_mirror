"""
Refactored Robot Calibration using ExecutableStateMachine

This module provides a refactored version of the robot calibration system
that uses the ExecutableStateMachine for better separation of concerns,
maintainability, and consistency with other system components.
"""

import time
import cv2
import numpy as np

from modules.utils.custom_logging import log_warning_message, log_info_message, log_debug_message, LoggerContext

from modules.robot_calibration import metrics
from modules.robot_calibration.CalibrationVision import CalibrationVision
from modules.robot_calibration.config_helpers import (
    RobotCalibrationEventsConfig, 
    RobotCalibrationConfig, 
    AdaptiveMovementConfig
)
from modules.robot_calibration.debug import DebugDraw
from modules.robot_calibration.logging import (
    get_log_timing_summary, 
    construct_calibration_completion_log_message
)
from modules.robot_calibration.robot_controller import CalibrationRobotController
from modules.robot_calibration.RobotCalibrationContext import RobotCalibrationContext

# Import all state handlers
from modules.robot_calibration.states.initializing import handle_initializing_state
from modules.robot_calibration.states.axis_mapping import handle_axis_mapping_state
from modules.robot_calibration.states.looking_for_chessboard_handler import handle_looking_for_chessboard_state
from modules.robot_calibration.states.chessboard_found_handler import handle_chessboard_found_state
from modules.robot_calibration.states.looking_for_aruco_markers_handler import handle_looking_for_aruco_markers_state
from modules.robot_calibration.states.all_aruco_found_handler import handle_all_aruco_found_state
from modules.robot_calibration.states.compute_offsets_handler import handle_compute_offsets_state
from modules.robot_calibration.states.remaining_handlers import (
    handle_align_robot_state,
    handle_iterate_alignment_state,
    handle_done_state,
    handle_error_state
)

# Import state machine components
from modules.robot_calibration.states.robot_calibration_states import (
    RobotCalibrationStates, 
    RobotCalibrationTransitionRules
)
from applications.glue_dispensing_application.glue_process.state_machine.ExecutableStateMachine import (
    ExecutableStateMachine,
    StateRegistry,
    State,
    ExecutableStateMachineBuilder
)
from modules.shared.MessageBroker import MessageBroker


ENABLE_LOGGING = True
robot_calibration_logger = None
if ENABLE_LOGGING:
    from modules.utils.custom_logging import setup_logger
    robot_calibration_logger = setup_logger("RefactoredRobotCalibration")


class RefactoredRobotCalibrationPipeline:
    """
    Refactored robot calibration pipeline using ExecutableStateMachine.
    
    This class provides the same functionality as the original pipeline
    but with better separation of concerns and maintainability.
    """

    def __init__(self, 
                 config: RobotCalibrationConfig,
                 adaptive_movement_config: AdaptiveMovementConfig = None,
                 events_config: RobotCalibrationEventsConfig = None):
        """
        Initialize the refactored calibration pipeline.
        
        Args:
            config: Main calibration configuration
            adaptive_movement_config: Movement adaptation settings
            events_config: Event broadcasting configuration
        """
        self.calibration_context = RobotCalibrationContext()
        self._setup_context(config, adaptive_movement_config, events_config)
        self.calibration_state_machine = self._create_state_machine()
        
        log_info_message(
            self.calibration_context.logger_context,
            f"RefactoredRobotCalibrationPipeline initialized with {len(config.required_ids)} markers"
        )

    def _setup_context(self, 
                      config: RobotCalibrationConfig,
                      adaptive_movement_config: AdaptiveMovementConfig,
                      events_config: RobotCalibrationEventsConfig):
        """Setup the calibration context with configuration data"""
        context = self.calibration_context
        
        # Basic configuration
        context.debug = config.debug
        context.step_by_step = config.step_by_step
        context.live_visualization = config.live_visualization
        context.system = config.vision_system
        context.required_ids = set(config.required_ids)
        context.Z_target = config.z_target

        # Camera configuration
        context.system.camera_settings.set_draw_contours(False)
        context.chessboard_size = (
            context.system.camera_settings.get_chessboard_width(),
            context.system.camera_settings.get_chessboard_height()
        )
        context.square_size_mm = context.system.camera_settings.get_square_size_mm()

        # Adaptive movement configuration
        if adaptive_movement_config:
            context.alignment_threshold_mm = adaptive_movement_config.target_error_mm

        # Event configuration
        if events_config:
            context.broker = events_config.broker
            context.BROADCAST_TOPIC = events_config.calibration_log_topic
            context.CALIBRATION_START_TOPIC = events_config.calibration_start_topic
            context.CALIBRATION_STOP_TOPIC = events_config.calibration_stop_topic
            context.CALIBRATION_IMAGE_TOPIC = events_config.calibration_image_topic
            context.broadcast_events = True
        else:
            context.broadcast_events = False

        # Logger context setup
        context.logger_context = LoggerContext(
            ENABLE_LOGGING, 
            robot_calibration_logger, 
            context.broadcast_events, 
            context.BROADCAST_TOPIC
        )

        # Initialize robot controller
        context.calibration_robot_controller = CalibrationRobotController(
            config.robot_service,
            adaptive_movement_config,
            context.logger_context
        )
        context.calibration_robot_controller.move_to_calibration_position()

        # Initialize supporting components
        context.debug_draw = DebugDraw()
        context.calibration_vision = CalibrationVision(
            context.system,
            context.chessboard_size,
            context.square_size_mm,
            context.required_ids,
            context.logger_context,
            context.debug_draw,
            context.debug
        )

        # Z-axis calculations
        context.Z_current = context.calibration_robot_controller.get_current_z_value()
        context.ppm_scale = context.Z_current / context.Z_target
        
        log_info_message(
            context.logger_context,
            f"Z_current: {context.Z_current}, Z_target: {context.Z_target}, ppm_scale: {context.ppm_scale}"
        )

    def _create_state_machine(self) -> ExecutableStateMachine:
        """Create and configure the executable state machine"""
        
        # Create state handlers map
        state_handlers_map = {
            RobotCalibrationStates.INITIALIZING: self._handle_initializing,
            RobotCalibrationStates.AXIS_MAPPING: self._handle_axis_mapping,
            RobotCalibrationStates.LOOKING_FOR_CHESSBOARD: self._handle_looking_for_chessboard,
            RobotCalibrationStates.CHESSBOARD_FOUND: self._handle_chessboard_found,
            RobotCalibrationStates.LOOKING_FOR_ARUCO_MARKERS: self._handle_looking_for_aruco_markers,
            RobotCalibrationStates.ALL_ARUCO_FOUND: self._handle_all_aruco_found,
            RobotCalibrationStates.COMPUTE_OFFSETS: self._handle_compute_offsets,
            RobotCalibrationStates.ALIGN_ROBOT: self._handle_align_robot,
            RobotCalibrationStates.ITERATE_ALIGNMENT: self._handle_iterate_alignment,
            RobotCalibrationStates.DONE: self._handle_done,
            RobotCalibrationStates.ERROR: self._handle_error,
        }

        # Create state registry
        registry = StateRegistry()
        for state_enum, handler in state_handlers_map.items():
            registry.register_state(State(
                state=state_enum,
                handler=handler,
                on_enter=lambda ctx, s=state_enum: self.calibration_context.start_state_timer(s.name),
                on_exit=lambda ctx, s=state_enum: self.calibration_context.end_state_timer()
            ))

        # Build the executable state machine
        transition_rules = RobotCalibrationTransitionRules.get_calibration_transition_rules()
        
        state_machine = (
            ExecutableStateMachineBuilder()
            .with_initial_state(RobotCalibrationStates.INITIALIZING)
            .with_transition_rules(transition_rules)
            .with_state_registry(registry)
            .with_context(self.calibration_context)
            .with_message_broker(self.calibration_context.broker or MessageBroker())
            .with_state_topic("ROBOT_CALIBRATION_STATE")
            .build()
        )

        # Store reference in context for state handlers to access
        self.calibration_context.state_machine = state_machine
        
        return state_machine

    # State handler wrapper methods
    def _handle_initializing(self, context):
        init_frame = context.system.getLatestFrame()
        result = handle_initializing_state(init_frame, context.logger_context)
        return result.next_state

    def _handle_axis_mapping(self, context):
        result = handle_axis_mapping_state(
            context.system, 
            context.calibration_vision, 
            context.calibration_robot_controller, 
            context.logger_context
        )
        context.image_to_robot_mapping = result.data
        time.sleep(1)
        return result.next_state

    def _handle_looking_for_chessboard(self, context):
        return handle_looking_for_chessboard_state(context)

    def _handle_chessboard_found(self, context):
        return handle_chessboard_found_state(context)

    def _handle_looking_for_aruco_markers(self, context):
        return handle_looking_for_aruco_markers_state(context)

    def _handle_all_aruco_found(self, context):
        return handle_all_aruco_found_state(context)

    def _handle_compute_offsets(self, context):
        return handle_compute_offsets_state(context)

    def _handle_align_robot(self, context):
        return handle_align_robot_state(context)

    def _handle_iterate_alignment(self, context):
        return handle_iterate_alignment_state(context)

    def _handle_done(self, context):
        next_state = handle_done_state(context)
        # If we're truly done (all markers processed), stop the state machine
        if next_state == RobotCalibrationStates.DONE and context.current_marker_id >= len(context.required_ids) - 1:
            self.calibration_state_machine.stop_execution()
        return next_state

    def _handle_error(self, context):
        next_state = handle_error_state(context)
        # Stop the state machine on error
        self.calibration_state_machine.stop_execution()
        return next_state

    def run(self):
        """
        Run the calibration process using the state machine.
        
        Returns:
            bool: True if calibration completed successfully, False if error occurred
        """
        try:
            log_debug_message(
                self.calibration_context.logger_context,
                "=== STARTING REFACTORED CALIBRATION RUN ===",
            )
            log_debug_message(
                self.calibration_context.logger_context,
                f"Required IDs: {self.calibration_context.required_ids}"
            )

            # Broadcast calibration start event
            if self.calibration_context.broadcast_events:
                self.calibration_context.broker.publish(
                    self.calibration_context.CALIBRATION_START_TOPIC, 
                    ""
                )

            # Start total calibration timer
            self.calibration_context.total_calibration_start_time = time.time()

            # Run the state machine
            self.calibration_state_machine.start_execution(delay=0.2)

            # Check final state
            final_state = self.calibration_state_machine.current_state
            success = final_state == RobotCalibrationStates.DONE

            if success:
                self._finalize_calibration()
            
            return success

        except Exception as e:
            log_debug_message(
                self.calibration_context.logger_context,
                f"ERROR in refactored calibration run: {e}"
            )
            import traceback
            traceback.print_exc()
            return False

    def _finalize_calibration(self):
        """Finalize the calibration by computing and saving the homography matrix"""
        context = self.calibration_context

        log_debug_message(context.logger_context, "--- Calibration Process Complete ---")

        # Sort by marker ID
        sorted_robot_items = sorted(context.robot_positions_for_calibration.items(), key=lambda x: x[0])
        sorted_camera_items = sorted(context.camera_points_for_homography.items(), key=lambda x: x[0])

        # Prepare corresponding points in sorted order
        robot_positions = [pos[:2] for _, pos in sorted_robot_items]
        camera_points = [pt for _, pt in sorted_camera_items]

        # Compute homography
        src_pts = np.array(camera_points, dtype=np.float32)
        dst_pts = np.array(robot_positions, dtype=np.float32)
        H_camera_center, status = cv2.findHomography(src_pts, dst_pts)

        # Test and validate
        average_error_camera_center, _ = metrics.test_calibration(
            H_camera_center, src_pts, dst_pts, context.logger_context, "transformation_to_camera_center"
        )

        # Save or warn based on error
        if average_error_camera_center <= 1:
            np.save(context.system.camera_to_robot_matrix_path, H_camera_center)
            log_info_message(
                context.logger_context, 
                f"Saved homography matrix to {context.system.camera_to_robot_matrix_path}"
            )
        else:
            log_warning_message(
                context.logger_context, 
                "High reprojection error — recalibration suggested"
            )

        # Camera-to-TCP offset calibration is now done via separate button
        # See: Camera to TCP Offset Calibration section in Robot Settings
        # self._compute_and_save_camera_tcp_offset(context, robot_positions)

        # End final state timer and log summary
        context.end_state_timer()
        total_calibration_time = time.time() - context.total_calibration_start_time

        # Log timing summary
        if context.state_timings:
            summary = get_log_timing_summary(context.state_timings)
            log_debug_message(context.logger_context, summary)

        # Structured final log
        completion_log = construct_calibration_completion_log_message(
            sorted_robot_items=sorted_robot_items,
            sorted_camera_items=sorted_camera_items,
            H_camera_center=H_camera_center,
            status=status,
            average_error_camera_center=average_error_camera_center,
            matrix_path=context.system.camera_to_robot_matrix_path,
            total_calibration_time=total_calibration_time
        )
        log_debug_message(context.logger_context, completion_log)

        # Broadcast calibration stop event
        if context.broadcast_events:
            context.broker.publish(context.CALIBRATION_STOP_TOPIC, "")

    def _compute_and_save_camera_tcp_offset(self, context, robot_positions):
        """
        Compute the camera-to-TCP offset based on the calibration data.

        The workflow accounts for the fact that TCP is positioned BELOW the chessboard center
        at the start (to keep the board fully visible):

        1. At start: TCP is below chessboard center (tcp_at_chessboard_start)
        2. Chessboard center detected in pixels (chessboard_center_px)
        3. During calibration: robot moves camera to markers (robot_positions)
        4. Calculate: Where would TCP be if it were AT the chessboard center
        5. Compare with camera center position to get offset

        Args:
            context: RobotCalibrationContext
            robot_positions: List of robot positions during calibration
        """
        try:
            log_debug_message(
                context.logger_context,
                "=== Camera-to-TCP Offset Calculation Starting ==="
            )
            log_debug_message(
                context.logger_context,
                f"Debug: tcp_at_chessboard_start = {context.tcp_at_chessboard_start}"
            )
            log_debug_message(
                context.logger_context,
                f"Debug: chessboard_center_px = {context.chessboard_center_px}"
            )
            log_debug_message(
                context.logger_context,
                f"Debug: robot_positions count = {len(robot_positions) if robot_positions else 0}"
            )

            if context.tcp_at_chessboard_start is None:
                log_warning_message(
                    context.logger_context,
                    "❌ Camera-to-TCP offset not computed: TCP position at chessboard start was not captured"
                )
                log_warning_message(
                    context.logger_context,
                    "💡 This happens when the TCP position wasn't captured in CHESSBOARD_FOUND state"
                )
                return

            if not robot_positions or len(robot_positions) < 2:
                log_warning_message(
                    context.logger_context,
                    "Camera-to-TCP offset not computed: Insufficient robot positions"
                )
                return

            if context.chessboard_center_px is None:
                log_warning_message(
                    context.logger_context,
                    "Camera-to-TCP offset not computed: Chessboard center pixels not available"
                )
                return

            # Calculate average robot position during marker detection
            # This is where the robot was when the CAMERA was viewing markers (camera at/near center)
            camera_at_markers_pos = np.mean(robot_positions, axis=0)

            # The camera-to-TCP offset is simply:
            # TCP position (when TCP was at center) - Camera position (when camera was at markers)
            # This measures the physical movement needed to go from TCP-at-center to camera-at-center
            offset_x = context.tcp_at_chessboard_start[0] - camera_at_markers_pos[0]
            offset_y = context.tcp_at_chessboard_start[1] - camera_at_markers_pos[1]

            context.camera_to_tcp_offset = [offset_x, offset_y]

            log_info_message(
                context.logger_context,
                f"✅ Camera-to-TCP offset computed from position difference:"
            )
            log_info_message(
                context.logger_context,
                f"  TCP at chessboard center: X={context.tcp_at_chessboard_start[0]:.2f}mm, "
                f"Y={context.tcp_at_chessboard_start[1]:.2f}mm"
            )
            log_info_message(
                context.logger_context,
                f"  Camera at markers (avg): X={camera_at_markers_pos[0]:.2f}mm, "
                f"Y={camera_at_markers_pos[1]:.2f}mm"
            )
            log_info_message(
                context.logger_context,
                f"  📐 Camera-to-TCP offset: X={offset_x:.2f}mm, Y={offset_y:.2f}mm"
            )
            log_info_message(
                context.logger_context,
                f"  💡 For best accuracy: Position TCP EXACTLY at chessboard center before calibration"
            )

            # Publish to message broker for UI to receive
            log_debug_message(
                context.logger_context,
                f"Attempting to publish camera-to-TCP offset. Broker available: {hasattr(context, 'broker') and context.broker is not None}"
            )

            # Try to get broker from context or create new one
            broker = None
            if hasattr(context, 'broker') and context.broker:
                broker = context.broker
                log_debug_message(context.logger_context, "Using context broker")
            else:
                # Try to create MessageBroker directly
                try:
                    from modules.shared.MessageBroker import MessageBroker
                    broker = MessageBroker()
                    log_debug_message(context.logger_context, "Created new MessageBroker instance")
                except Exception as broker_error:
                    log_warning_message(
                        context.logger_context,
                        f"Could not create MessageBroker: {broker_error}"
                    )

            if broker:
                from communication_layer.api.v1.topics import RobotTopics
                message = {
                    "success": True,
                    "source": "chessboard_calibration",
                    "tcp_offset": {
                        "x": offset_x / 1000.0,  # Convert to meters
                        "y": offset_y / 1000.0,
                        "z": 0.0
                    },
                    "camera_to_tcp_offset": {
                        "x_mm": offset_x,
                        "y_mm": offset_y
                    },
                    "tcp_at_chessboard": {
                        "x_mm": context.tcp_at_chessboard_start[0],
                        "y_mm": context.tcp_at_chessboard_start[1]
                    },
                    "camera_at_markers": {
                        "x_mm": camera_at_markers_pos[0],
                        "y_mm": camera_at_markers_pos[1]
                    }
                }

                log_info_message(
                    context.logger_context,
                    f"Publishing to topic: {RobotTopics.TCP_CALIBRATION_RESULT}"
                )
                log_info_message(
                    context.logger_context,
                    f"Message content: {message}"
                )

                broker.publish(RobotTopics.TCP_CALIBRATION_RESULT, message)

                log_info_message(
                    context.logger_context,
                    "Camera-to-TCP offset published to TCP_CALIBRATION_RESULT topic"
                )
            else:
                log_warning_message(
                    context.logger_context,
                    "Could not publish camera-to-TCP offset: No broker available"
                )

        except Exception as e:
            log_warning_message(
                context.logger_context,
                f"Failed to compute camera-to-TCP offset: {e}"
            )
            import traceback
            traceback.print_exc()

    def get_context(self) -> RobotCalibrationContext:
        """Get the calibration context for external access"""
        return self.calibration_context

    def get_state_machine(self) -> ExecutableStateMachine:
        """Get the state machine for external monitoring"""
        return self.calibration_state_machine