# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [my_dashboard_controller.py](#my_dashboard_controllerpy)

## `my_dashboard_controller.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/controller/my_dashboard_controller.py](../../../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/controller/my_dashboard_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.broker_subscription_mixin`, `src.applications.base.dashboard_camera_feed_mixin`, `src.applications.base.dashboard_process_state_mixin`, `src.applications.base.i_application_controller`, `src.engine.core.i_messaging_service`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard.model.my_dashboard_model`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard.view.my_dashboard_view`.

### `MyDashboardController`

```python
class MyDashboardController(IApplicationController, BrokerSubscriptionMixin, DashboardCameraFeedMixin, DashboardProcessStateMixin):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: MyDashboardModel, view: MyDashboardView, broker: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
