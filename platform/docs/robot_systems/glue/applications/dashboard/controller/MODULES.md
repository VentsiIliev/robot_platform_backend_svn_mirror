# Module reference: `src/robot_systems/glue/applications/dashboard/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_dashboard_controller.py](#glue_dashboard_controllerpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/dashboard/controller/__init__.py](../../../../../../src/robot_systems/glue/applications/dashboard/controller/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_dashboard_controller.py`

Source: [src/robot_systems/glue/applications/dashboard/controller/glue_dashboard_controller.py](../../../../../../src/robot_systems/glue/applications/dashboard/controller/glue_dashboard_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `__future__`, `logging`, `src.applications.base.background_worker`, `src.applications.base.dashboard_camera_feed_mixin`, `src.applications.base.i_application_controller`, `src.applications.base.notification_presenter`, `src.engine.core.i_messaging_service`, `src.engine.system`, `src.robot_systems.glue.applications.dashboard`, `src.robot_systems.glue.applications.dashboard.model.glue_dashboard_model`, `src.robot_systems.glue.applications.dashboard.ui.glue_change_guide_wizard`, `src.robot_systems.glue.component_ids`, `src.shared_contracts.events.glue_overlay_events`, `src.shared_contracts.events.notification_events`, `src.shared_contracts.events.process_events`, `src.shared_contracts.events.robot_events`, `src.shared_contracts.events.vision_events`, `src.shared_contracts.events.weight_events`, `typing`.

### `_DashboardBridge`

```python
class _DashboardBridge(QObject):
```

Declared fields/defaults:

```python
weight_reading = pyqtSignal(int, float)
cell_state = pyqtSignal(int, str)
glue_type = pyqtSignal(int, str)
robot_state = pyqtSignal(str)
process_state = pyqtSignal(str, str, str)
system_state = pyqtSignal(str, str)
service_warning = pyqtSignal(str)
camera_image = pyqtSignal(object)
overlay_loaded = pyqtSignal(object)
```

### `GlueDashboardController`

```python
class GlueDashboardController(IApplicationController, BackgroundWorker, DashboardCameraFeedMixin):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: GlueDashboardModel, view: GlueDashboardView, broker: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
