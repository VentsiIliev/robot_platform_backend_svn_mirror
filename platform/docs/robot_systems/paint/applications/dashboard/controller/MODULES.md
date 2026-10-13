# Module reference: `src/robot_systems/paint/applications/dashboard/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_dashboard_controller.py](#paint_dashboard_controllerpy)

## `paint_dashboard_controller.py`

Source: [src/robot_systems/paint/applications/dashboard/controller/paint_dashboard_controller.py](../../../../../../src/robot_systems/paint/applications/dashboard/controller/paint_dashboard_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `functools`, `src.applications.base.broker_subscription_mixin`, `src.applications.base.dashboard_camera_feed_mixin`, `src.applications.base.dashboard_process_state_mixin`, `src.applications.base.i_application_controller`, `src.engine.core.i_messaging_service`, `src.robot_systems.paint.applications.dashboard.dashboard_state`, `src.robot_systems.paint.applications.dashboard.model.paint_dashboard_model`, `src.robot_systems.paint.applications.dashboard.view.paint_dashboard_view`, `src.robot_systems.paint.contracts.events.dashboard_events`, `src.shared_contracts.events.robot_events`, `src.shared_contracts.events.shell_events`, `src.shared_contracts.events.vision_events`, `threading`.

### `_Worker`

```python
class _Worker(QObject):
```

Declared fields/defaults:

```python
finished = pyqtSignal(object)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, fn)
```

```python
def run(self) -> None
```

### `_DashboardNoticeBridge`

```python
class _DashboardNoticeBridge(QObject):
```

Declared fields/defaults:

```python
info_ready = pyqtSignal(str, str)
warning_ready = pyqtSignal(str, str)
unknown_workpiece_ready = pyqtSignal(str, str)
```

### `PaintDashboardController`

```python
class PaintDashboardController(IApplicationController, BrokerSubscriptionMixin, DashboardCameraFeedMixin, DashboardProcessStateMixin):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: PaintDashboardModel, view: PaintDashboardView, broker: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
