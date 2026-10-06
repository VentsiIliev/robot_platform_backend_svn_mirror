# Module reference: `src/robot_systems/welding/applications/dashboard/controller`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [welding_dashboard_controller.py](#welding_dashboard_controllerpy)

## `welding_dashboard_controller.py`

Source: [src/robot_systems/welding/applications/dashboard/controller/welding_dashboard_controller.py](../../../../../../src/robot_systems/welding/applications/dashboard/controller/welding_dashboard_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.broker_subscription_mixin`, `src.applications.base.dashboard_camera_feed_mixin`, `src.applications.base.dashboard_process_state_mixin`, `src.applications.base.i_application_controller`, `src.engine.core.i_messaging_service`, `src.robot_systems.welding.applications.dashboard.model.welding_dashboard_model`, `src.robot_systems.welding.applications.dashboard.view.welding_dashboard_view`.

### `WeldingDashboardController`

```python
class WeldingDashboardController(IApplicationController, BrokerSubscriptionMixin, DashboardCameraFeedMixin, DashboardProcessStateMixin):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: WeldingDashboardModel, view: WeldingDashboardView, broker: IMessagingService)
```

```python
def load(self) -> None
```

```python
def stop(self) -> None
```
