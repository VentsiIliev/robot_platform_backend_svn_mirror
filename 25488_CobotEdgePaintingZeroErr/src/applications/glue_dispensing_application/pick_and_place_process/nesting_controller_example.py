"""
Example: How to use the state machine-based nesting controller for UI integration

This module shows how to integrate the pick and place state machine
with a UI or control system, providing the same pause/resume/stop control
as the glue dispensing process.
"""

from typing import Optional
from threading import Event
import time

from .handlers.nesting_handler import start_nesting_with_control
from .state_machine import PickAndPlaceState
from .state_machine_nesting_handler import StateMachineNestingHandler


class NestingController:
    """
    Example controller showing how to integrate pick and place state machine
    with a UI or control system.
    """
    
    def __init__(self):
        self.handler: Optional[StateMachineNestingHandler] = None
        self.operation_complete = Event()
        self.monitoring_active = False
    
    def start_nesting_operation(self, application, workpieces) -> bool:
        """
        Start a new nesting operation.
        
        Args:
            application: Application instance
            workpieces: List of workpieces to nest
            
        Returns:
            True if started successfully, False otherwise
        """
        try:
            # Start nesting with control
            self.handler = start_nesting_with_control(application, workpieces)
            
            # Start monitoring in background
            self.monitoring_active = True
            self._start_monitoring()
            
            return True
            
        except Exception as e:
            print(f"Failed to start nesting operation: {e}")
            return False
    
    def pause_operation(self) -> bool:
        """Pause the current operation."""
        if self.handler:
            return self.handler.pause()
        return False
    
    def resume_operation(self) -> bool:
        """Resume the paused operation."""
        if self.handler:
            return self.handler.resume()
        return False
    
    def stop_operation(self) -> bool:
        """Stop the current operation gracefully."""
        if self.handler:
            success = self.handler.stop()
            self.monitoring_active = False
            return success
        return False
    
    def emergency_stop(self) -> bool:
        """Emergency stop the operation."""
        if self.handler:
            success = self.handler.emergency_stop()
            self.monitoring_active = False
            return success
        return False
    
    def get_current_state(self) -> Optional[str]:
        """Get the current state as a string."""
        if self.handler:
            state = self.handler.get_current_state()
            return state.name if state else None
        return None
    
    def get_operation_progress(self) -> dict:
        """Get detailed operation progress."""
        if self.handler:
            return self.handler.get_operation_status()
        return {}
    
    def is_operation_active(self) -> bool:
        """Check if an operation is currently active."""
        if self.handler:
            state = self.handler.get_current_state()
            return state not in [
                PickAndPlaceState.IDLE,
                PickAndPlaceState.COMPLETED,
                PickAndPlaceState.ERROR,
                PickAndPlaceState.STOPPED,
                None
            ]
        return False
    
    def is_paused(self) -> bool:
        """Check if the operation is paused."""
        if self.handler:
            return self.handler.is_paused()
        return False
    
    def is_completed(self) -> bool:
        """Check if the operation is completed."""
        if self.handler:
            return self.handler.is_completed()
        return False
    
    def wait_for_completion(self, timeout: Optional[float] = None):
        """Wait for the operation to complete."""
        if self.handler:
            return self.handler.wait_for_completion(timeout)
        return None
    
    def _start_monitoring(self):
        """Start monitoring the operation status (would typically update UI)."""
        # In a real implementation, this might update a UI progress bar,
        # status display, etc. Here's a simple example:
        
        import threading
        
        def monitor():
            while self.monitoring_active and self.handler:
                status = self.handler.get_operation_status()
                state = self.handler.get_current_state()
                
                # Example: Print status updates (in real app, this would update UI)
                print(f"State: {state.name if state else 'Unknown'}")
                print(f"Workpieces placed: {status.get('workpieces_placed', 0)}")
                print(f"Paused: {status.get('paused', False)}")
                print("---")
                
                # Check if operation is complete
                if self.handler.is_completed():
                    self.operation_complete.set()
                    self.monitoring_active = False
                    break
                
                time.sleep(1.0)  # Update every second
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()


# ==================== Usage Example ====================

def example_usage():
    """
    Example of how to use the nesting controller in a UI application.
    """
    
    # This would be called from your UI code
    controller = NestingController()
    
    # Start operation
    # success = controller.start_nesting_operation(application, workpieces)
    
    # UI Button handlers:
    def on_pause_clicked():
        controller.pause_operation()
        print("Operation paused")
    
    def on_resume_clicked():
        controller.resume_operation()
        print("Operation resumed")
    
    def on_stop_clicked():
        controller.stop_operation()
        print("Operation stopped")
    
    def on_emergency_stop_clicked():
        controller.emergency_stop()
        print("Emergency stop executed")
    
    # Status updates (called periodically from UI timer):
    def update_ui_status():
        state = controller.get_current_state()
        progress = controller.get_operation_progress()
        
        # Update UI elements
        # status_label.text = f"State: {state}"
        # progress_bar.value = progress.get('workpieces_placed', 0)
        # pause_button.enabled = controller.is_operation_active()
        # resume_button.enabled = controller.is_paused()
        
        print(f"UI Update - State: {state}, Progress: {progress}")
    
    print("Nesting controller example setup complete")


if __name__ == "__main__":
    example_usage()