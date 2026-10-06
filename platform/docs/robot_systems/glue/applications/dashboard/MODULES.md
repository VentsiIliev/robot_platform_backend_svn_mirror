# Module reference: `src/robot_systems/glue/applications/dashboard`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [config.py](#configpy)
- [glue_dashboard.py](#glue_dashboardpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/dashboard/__init__.py](../../../../../src/robot_systems/glue/applications/dashboard/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.dashboard.config`, `src.robot_systems.glue.applications.dashboard.view.glue_dashboard_view`.

Package-level import/export surface:

```python
from src.robot_systems.glue.applications.dashboard.config import ACTION_BUTTONS, BUTTON_STATE_MAP, GLUE_CELLS, GlueCellTopics, MODE_TOGGLE_LABELS
from src.robot_systems.glue.applications.dashboard.view.glue_dashboard_view import GlueDashboardView
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `config.py`

Source: [src/robot_systems/glue/applications/dashboard/config.py](../../../../../src/robot_systems/glue/applications/dashboard/config.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `pl_gui.dashboard.config`, `src.shared_contracts.events.process_events`.

Module declarations (expressions are shown without evaluating them):

```python
GLUE_CELLS: list[CardConfig] = [CardConfig(card_id=1, label='Glue 1'), CardConfig(card_id=2, label='Glue 2'), CardConfig(card_id=3, label='Glue 3')]
ACTION_BUTTONS: list[ActionButtonConfig] = [ActionButtonConfig(action_id='reset_errors', label='Reset Errors', enabled=True, row=1, col=0), ActionButtonConfig(action_id='mode_toggle', label='Pick And Spray', row_span=1, col_span=2), ActionButtonConfig(action_id='clean', label='Clean')]
BUTTON_STATE_MAP: dict = {ProcessState.IDLE.value: {'start': True, 'stop': False, 'pause': False, 'pause_text': 'Pause', 'mode_toggle': True, 'clean': True, 'reset_errors': False}, ProcessState.RUNNING.value: {'start': False, 'stop': True, 'pause': True, 'pause_text': 'Pause', 'mode_toggle': False, 'clean': False, 'reset_errors': False}, ProcessState.PAUSED.value: {'start': False, 'stop': True, 'pause': True, 'pause_text': 'Resume', 'mode_toggle': False, 'clean': False, 'reset_errors': False}, ProcessState.STOPPED.value: {'start': True, 'stop': False, 'pause': False, 'pause_text': 'Pause', 'mode_toggle': True, 'clean': True, 'reset_errors': False}, ProcessState.ERROR.value: {'start': False, 'stop': True, 'pause': False, 'pause_text': 'Pause', 'mode_toggle': False, 'clean': False, 'reset_errors': True}, 'disconnected': {'start': False, 'stop': False, 'pause': False, 'pause_text': 'Pause', 'mode_toggle': True, 'clean': True, 'reset_errors': False}}
MODE_TOGGLE_LABELS = ('Pick And Spray', 'Spray Only')
```

### `GlueCellTopics`

```python
class GlueCellTopics:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def weight(cell_id: int) -> str
```

```python
@staticmethod
def state(cell_id: int) -> str
```

```python
@staticmethod
def glue_type(cell_id: int) -> str
```

### `GlueDashboardConfig`

```python
@dataclass
class GlueDashboardConfig(DashboardConfig):
```

Declared fields/defaults:

```python
default_cell_capacity_grams: float = 5000.0
show_placeholders: bool = False
```

## `glue_dashboard.py`

Source: [src/robot_systems/glue/applications/dashboard/glue_dashboard.py](../../../../../src/robot_systems/glue/applications/dashboard/glue_dashboard.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `pl_gui.dashboard.config`, `src.engine.core.i_messaging_service`, `src.engine.hardware.weight.interfaces.i_weight_cell_service`, `src.engine.repositories.interfaces.i_settings_service`, `src.robot_systems.glue.applications.dashboard`, `src.robot_systems.glue.applications.dashboard.controller.glue_dashboard_controller`, `src.robot_systems.glue.applications.dashboard.model.glue_dashboard_model`, `src.robot_systems.glue.applications.dashboard.service.glue_dashboard_service`, `src.robot_systems.glue.applications.dashboard.ui.factories.glue_card_factory`, `src.robot_systems.glue.applications.dashboard.view.glue_dashboard_view`, `src.robot_systems.glue.domain.glue_job_execution_service`, `src.robot_systems.glue.processes.glue_operation_coordinator`, `typing`.

### `GlueDashboard`

```python
class GlueDashboard:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def create(coordinator: GlueOperationCoordinator, settings_service: ISettingsService, messaging_service: IMessagingService, weight_service: Optional[IWeightCellService]=None, execution_service: GlueJobExecutionService | None=None, robot_service=None, preview_transformer=None, preview_transformer_getter=None) -> QWidget
```
