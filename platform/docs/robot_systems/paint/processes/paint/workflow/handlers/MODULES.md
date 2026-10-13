# Module reference: `src/robot_systems/paint/processes/paint/workflow/handlers`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)

## `__init__.py`

Source: [src/robot_systems/paint/processes/paint/workflow/handlers/__init__.py](../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.dropoff_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.post_return_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.prepare_dropoff_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.completed_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.error_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.idle_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.pause_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.startup_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.stopped_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.calibration_wait_camera_settle_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_capture_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_execute_pickup_release_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_move_to_calibration_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_move_to_magazine_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_prepare_pickup_release_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_wait_camera_settle_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.capture_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.edge_cleanup_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.execution_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.paint_contact_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.pickup_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.plan_handler`, `src.robot_systems.paint.processes.paint.workflow.handlers.workflow.preparation_handler`.

Package-level import/export surface:

```python
from src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.calibration_wait_camera_settle_handler import handle_calibration_wait_camera_settle
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.capture_handler import handle_capture_workpiece
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.completed_handler import handle_completed
from src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.dropoff_handler import handle_dropoff
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.edge_cleanup_handler import handle_edge_cleanup
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.error_handler import handle_error
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.execution_handler import handle_execute_paint
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.idle_handler import handle_idle
from src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_capture_handler import handle_magazine_capture
from src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_execute_pickup_release_handler import handle_magazine_execute_pickup_release
from src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_move_to_calibration_handler import handle_magazine_move_to_calibration
from src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_move_to_magazine_handler import handle_magazine_move_to_magazine
from src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_prepare_pickup_release_handler import handle_magazine_prepare_pickup_release
from src.robot_systems.paint.processes.paint.workflow.handlers.magazine_load.magazine_wait_camera_settle_handler import handle_magazine_wait_camera_settle
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.paint_contact_handler import handle_paint_contact
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.pause_handler import handle_paused
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.pickup_handler import handle_pickup
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.plan_handler import handle_build_execution_plan
from src.robot_systems.paint.processes.paint.workflow.handlers.workflow.preparation_handler import handle_prepare_workpiece
from src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.prepare_dropoff_handler import handle_prepare_dropoff
from src.robot_systems.paint.processes.paint.workflow.handlers.dropoff.post_return_handler import handle_post_return
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.startup_handler import handle_starting
from src.robot_systems.paint.processes.paint.workflow.handlers.lifecycle.stopped_handler import handle_stopped
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['handle_build_execution_plan', 'handle_calibration_wait_camera_settle', 'handle_capture_workpiece', 'handle_completed', 'handle_dropoff', 'handle_edge_cleanup', 'handle_error', 'handle_execute_paint', 'handle_idle', 'handle_magazine_capture', 'handle_magazine_execute_pickup_release', 'handle_magazine_move_to_calibration', 'handle_magazine_move_to_magazine', 'handle_magazine_prepare_pickup_release', 'handle_magazine_wait_camera_settle', 'handle_paint_contact', 'handle_paused', 'handle_pickup', 'handle_post_return', 'handle_prepare_dropoff', 'handle_prepare_workpiece', 'handle_starting', 'handle_stopped']
```
