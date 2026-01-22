"""
State Machine-based Nesting Handler

This module provides a nesting handler that uses the state machine implementation
for full pause/resume/stop control, similar to the glue dispensing process.
"""

from typing import List, Optional, Dict, Any
from threading import Thread
import time

from modules.utils.custom_logging import setup_logger, LoggerContext, log_info_message
from modules.VisionSystem.heightMeasuring.LaserTracker import LaserTrackService
from core.services.robot_service.impl.base_robot_service import RobotService

from .models import GrippersConfig
from .services import PickupService, PlacementService, PlaneManagementService, GripperService
from .workflows import VisionWorkflow, RobotWorkflow, MeasurementWorkflow, PlacementWorkflow, NestingResult
from .measure_height import HeightMeasureContext
from .Plane import Plane
from .state_machine import PickAndPlaceStateMachine, PickAndPlaceContext, PickAndPlaceState


class StateMachineNestingHandler:
    """
    Nesting handler with state machine-based pause/resume/stop control.
    
    Provides the same interface as the original nesting handler but with
    full state machine control capabilities.
    """
    
    def __init__(self):
        self.state_machine: Optional[PickAndPlaceStateMachine] = None
        self.context: Optional[PickAndPlaceContext] = None
        self.execution_thread: Optional[Thread] = None
        self.is_running = False
        
        # Setup logging
        enable_logging = True
        self.logger = setup_logger("StateMachineNesting") if enable_logging else None
        self.logger_context = LoggerContext(enabled=enable_logging, logger=self.logger)
    
    def start_nesting(self, application, workpieces: List) -> NestingResult:
        """
        Start nesting operation using state machine.
        
        Args:
            application: Application instance with movement methods and services
            workpieces: List of workpiece templates to match against
            
        Returns:
            NestingResult with operation status and message
        """
        try:
            # Initialize the state machine and context
            success = self._initialize_state_machine(application, workpieces)
            if not success:
                return NestingResult(success=False, message="Failed to initialize state machine")
            
            # Start the state machine
            success = self.state_machine.start()
            if not success:
                return NestingResult(success=False, message="Failed to start state machine")
            
            # Start execution in a separate thread for non-blocking operation
            self.is_running = True
            self.execution_thread = Thread(target=self._run_execution_loop, daemon=True)
            self.execution_thread.start()
            
            log_info_message(self.logger_context, "State machine nesting operation started")
            
            # For compatibility, we could either:
            # 1. Return immediately (non-blocking) - good for UI control
            # 2. Wait for completion (blocking) - matches original behavior
            
            # Option 1: Non-blocking (recommended for UI control)
            return NestingResult(success=True, message="Nesting operation started successfully")
            
        except Exception as e:
            log_info_message(self.logger_context, f"Failed to start nesting: {str(e)}")
            return NestingResult(success=False, message=f"Failed to start nesting: {str(e)}")
    
    def wait_for_completion(self, timeout: Optional[float] = None) -> NestingResult:
        """
        Wait for the nesting operation to complete.
        
        Args:
            timeout: Optional timeout in seconds
            
        Returns:
            NestingResult with final operation status
        """
        if self.execution_thread:
            self.execution_thread.join(timeout)
            
        if self.state_machine and self.context:
            status = self.state_machine.get_operation_status()
            current_state = self.state_machine.get_current_state()
            
            if current_state == PickAndPlaceState.COMPLETED:
                return NestingResult(
                    success=True, 
                    message=f"Nesting completed successfully. Placed {status.get('workpieces_placed', 0)} workpieces."
                )
            elif current_state == PickAndPlaceState.ERROR:
                return NestingResult(
                    success=False,
                    message=f"Nesting failed: {status.get('last_error', 'Unknown error')}"
                )
            elif current_state == PickAndPlaceState.STOPPED:
                return NestingResult(
                    success=False,
                    message=f"Nesting stopped. Placed {status.get('workpieces_placed', 0)} workpieces."
                )
        
        return NestingResult(success=False, message="Operation status unknown")
    
    def _initialize_state_machine(self, application, workpieces: List) -> bool:
        """Initialize the state machine with all required services and context."""
        try:
            # Extract services from application
            vision_service = application.visionService
            robot_service = application.robotService
            
            # Create configuration
            grippers_config = GrippersConfig(
                gripper_x_offset=100.429,
                gripper_y_offset=1.991,
                double_gripper_z_offset=14,
                single_gripper_z_offset=19
            )
            
            # Initialize plane and tools
            plane = Plane()
            laser = robot_service.tool_manager.get_tool("laser")
            laser_tracking_service = LaserTrackService()
            
            # Setup services
            pickup_service = PickupService(grippers_config, 150.0)  # DESCENT_HEIGHT_OFFSET
            plane_service = PlaneManagementService(plane)
            placement_service = PlacementService(plane_service)
            gripper_service = GripperService(grippers_config)
            
            # Setup workflows
            vision_workflow = VisionWorkflow(vision_service, self.logger_context)
            robot_workflow = RobotWorkflow(robot_service, self.logger_context)
            
            height_measure_context = HeightMeasureContext(
                robot_service=robot_service,
                vision_service=vision_service,
                laser_tracking_service=laser_tracking_service,
                laser=laser
            )
            measurement_workflow = MeasurementWorkflow(height_measure_context, self.logger_context)
            
            placement_workflow = PlacementWorkflow(
                pickup_service, placement_service, gripper_service,
                measurement_workflow, grippers_config, self.logger_context
            )
            
            # Create context with all services
            self.context = PickAndPlaceContext(
                application=application,
                vision_service=vision_service,
                robot_service=robot_service,
                preselected_workpieces=workpieces,
                pickup_service=pickup_service,
                placement_service=placement_service,
                gripper_service=gripper_service,
                plane_service=plane_service,
                vision_workflow=vision_workflow,
                robot_workflow=robot_workflow,
                measurement_workflow=measurement_workflow,
                placement_workflow=placement_workflow,
                grippers_config=grippers_config,
                plane=plane,
                laser=laser,
                logger_context=self.logger_context
            )
            
            # Create and setup state machine
            self.state_machine = PickAndPlaceStateMachine()
            success = self.state_machine.setup_state_machine(self.context)
            
            return success
            
        except Exception as e:
            log_info_message(self.logger_context, f"Failed to initialize state machine: {str(e)}")
            return False
    
    def _run_execution_loop(self):
        """Run the state machine execution loop."""
        try:
            if self.state_machine:
                self.state_machine.start_execution_loop(delay=0.1)
        except Exception as e:
            log_info_message(self.logger_context, f"Execution loop error: {str(e)}")
        finally:
            self.is_running = False
    
    # ==================== Control Methods ====================
    
    def pause(self) -> bool:
        """Pause the nesting operation."""
        if self.state_machine:
            return self.state_machine.pause()
        return False
    
    def resume(self) -> bool:
        """Resume the nesting operation."""
        if self.state_machine:
            return self.state_machine.resume()
        return False
    
    def stop(self) -> bool:
        """Stop the nesting operation gracefully."""
        if self.state_machine:
            success = self.state_machine.stop()
            self._cleanup()
            return success
        return False
    
    def emergency_stop(self) -> bool:
        """Emergency stop the nesting operation."""
        if self.state_machine:
            success = self.state_machine.emergency_stop()
            self._cleanup()
            return success
        return False
    
    def get_current_state(self) -> Optional[PickAndPlaceState]:
        """Get the current state of the operation."""
        if self.state_machine:
            return self.state_machine.get_current_state()
        return None
    
    def get_operation_status(self) -> Dict:
        """Get detailed operation status."""
        if self.state_machine:
            return self.state_machine.get_operation_status()
        return {}
    
    def is_paused(self) -> bool:
        """Check if the operation is currently paused."""
        return self.get_current_state() == PickAndPlaceState.PAUSED
    
    def is_completed(self) -> bool:
        """Check if the operation is completed."""
        current_state = self.get_current_state()
        return current_state in [PickAndPlaceState.COMPLETED, PickAndPlaceState.ERROR, PickAndPlaceState.STOPPED]
    
    def _cleanup(self):
        """Clean up resources."""
        try:
            if self.state_machine:
                self.state_machine.stop_execution_loop()
            
            if self.execution_thread and self.execution_thread.is_alive():
                self.execution_thread.join(timeout=5.0)
            
            self.is_running = False
            
        except Exception as e:
            log_info_message(self.logger_context, f"Cleanup error: {str(e)}")


# ==================== Convenience Functions ====================

# For backward compatibility, provide the same interface as the original handler
def start_nesting(application, workpieces: List) -> NestingResult:
    """
    Start nesting operation with blocking behavior (for backward compatibility).
    
    Args:
        application: Application instance with movement methods and services
        workpieces: List of workpiece templates to match against
        
    Returns:
        NestingResult with operation status and message
    """
    handler = StateMachineNestingHandler()
    
    # Start the operation
    result = handler.start_nesting(application, workpieces)
    if not result.success:
        return result
    
    # Wait for completion (blocking behavior like original)
    return handler.wait_for_completion()


def start_nesting_non_blocking(application, workpieces: List) -> StateMachineNestingHandler:
    """
    Start nesting operation with non-blocking behavior (for UI control).
    
    Args:
        application: Application instance with movement methods and services
        workpieces: List of workpiece templates to match against
        
    Returns:
        StateMachineNestingHandler instance for control operations
    """
    handler = StateMachineNestingHandler()
    handler.start_nesting(application, workpieces)
    return handler