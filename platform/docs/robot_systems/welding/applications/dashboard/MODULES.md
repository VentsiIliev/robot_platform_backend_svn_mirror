# Module reference: `src/robot_systems/welding/applications/dashboard`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [config.py](#configpy)
- [dashboard_state.py](#dashboard_statepy)
- [welding_dashboard_factory.py](#welding_dashboard_factorypy)

## `__init__.py`

Source: [src/robot_systems/welding/applications/dashboard/__init__.py](../../../../../src/robot_systems/welding/applications/dashboard/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.welding.applications.dashboard.welding_dashboard_factory`.

Package-level import/export surface:

```python
from src.robot_systems.welding.applications.dashboard.welding_dashboard_factory import WeldingDashboardFactory
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['WeldingDashboardFactory']
```

## `config.py`

Source: [src/robot_systems/welding/applications/dashboard/config.py](../../../../../src/robot_systems/welding/applications/dashboard/config.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `pl_gui.dashboard.config`.

Module declarations (expressions are shown without evaluating them):

```python
WELDING_DASHBOARD_CARDS: list[CardConfig] = [CardConfig(card_id=1, label='Welding Process')]
WELDING_DASHBOARD_ACTIONS: list[ActionButtonConfig] = [ActionButtonConfig(action_id='reset_errors', label='Reset Errors', row=1, col=0)]
```

### `WeldingDashboardConfig`

```python
@dataclass
class WeldingDashboardConfig(DashboardConfig):
```

Declared fields/defaults:

```python
show_placeholders: bool = False
```

## `dashboard_state.py`

Source: [src/robot_systems/welding/applications/dashboard/dashboard_state.py](../../../../../src/robot_systems/welding/applications/dashboard/dashboard_state.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `DashboardState`

```python
@dataclass
class DashboardState:
```

Declared fields/defaults:

```python
process_state: str = 'idle'
mode_label: str = 'Welding Mode'
active_job_label: str = 'No active job'
status_lines: list[str] = field(default_factory=list)
can_start: bool = True
can_stop: bool = False
can_pause: bool = False
pause_label: str = 'Pause'
```

## `welding_dashboard_factory.py`

Source: [src/robot_systems/welding/applications/dashboard/welding_dashboard_factory.py](../../../../../src/robot_systems/welding/applications/dashboard/welding_dashboard_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.robot_systems.welding.applications.dashboard.config`, `src.robot_systems.welding.applications.dashboard.controller.welding_dashboard_controller`, `src.robot_systems.welding.applications.dashboard.model.welding_dashboard_model`, `src.robot_systems.welding.applications.dashboard.service.i_welding_dashboard_service`, `src.robot_systems.welding.applications.dashboard.ui.welding_card_factory`, `src.robot_systems.welding.applications.dashboard.view.welding_dashboard_view`.

### `WeldingDashboardFactory`

```python
class WeldingDashboardFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def build(self, service, messaging=None, jog_service=None)
```
