from typing import Union
from applications.glue_dispensing_application.pick_and_place_process.nesting_entry import start_nesting as nesting_start
from applications.glue_dispensing_application.pick_and_place_process.workflows import NestingResult
from applications.glue_dispensing_application.pick_and_place_process.state_machine_nesting_handler import (
    StateMachineNestingHandler, start_nesting as state_machine_start_nesting,
    start_nesting_non_blocking
)


def start_nesting(application, workpieces, use_state_machine: bool = True) -> NestingResult:
    """
    Start nesting operation using either the layered architecture or state machine.
    
    Args:
        application: Application instance with movement methods and services
        workpieces: List of workpiece templates to match against
        use_state_machine: If True, uses state machine with pause/resume/stop control
        
    Returns:
        NestingResult with operation status and message
    """
    if use_state_machine:
        return state_machine_start_nesting(application, workpieces)
    else:
        # Use original layered architecture (blocking)
        return nesting_start(
            application=application,
            vision_service=application.visionService,
            robot_service=application.robotService,
            preselected_workpiece=workpieces
        )


def start_nesting_with_control(application, workpieces) -> StateMachineNestingHandler:
    """
    Start nesting operation with full pause/resume/stop control.
    
    This function returns a handler that allows you to control the nesting operation
    similar to how the glue dispensing process works.
    
    Args:
        application: Application instance with movement methods and services
        workpieces: List of workpiece templates to match against
        
    Returns:
        StateMachineNestingHandler for controlling the operation
        
    Example usage:
        handler = start_nesting_with_control(app, workpieces)
        
        # Control the operation
        handler.pause()      # Pause at current state
        handler.resume()     # Resume from pause
        handler.stop()       # Graceful stop with cleanup
        handler.emergency_stop()  # Emergency stop
        
        # Monitor status
        status = handler.get_operation_status()
        current_state = handler.get_current_state()
        
        # Wait for completion
        result = handler.wait_for_completion()
    """
    return start_nesting_non_blocking(application, workpieces)


# For backward compatibility, keep the old function name
def start_nesting_legacy(application, workpieces) -> NestingResult:
    """
    Legacy function - start nesting operation using the original layered architecture.
    
    This is the non-state-machine version for backward compatibility.
    """
    return nesting_start(
        application=application,
        vision_service=application.visionService,
        robot_service=application.robotService,
        preselected_workpiece=workpieces
    )
