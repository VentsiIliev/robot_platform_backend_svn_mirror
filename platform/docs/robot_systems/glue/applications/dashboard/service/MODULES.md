# Module reference: `src/robot_systems/glue/applications/dashboard/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_dashboard_service.py](#glue_dashboard_servicepy)
- [i_glue_dashboard_service.py](#i_glue_dashboard_servicepy)
- [stub_glue_dashboard_service.py](#stub_glue_dashboard_servicepy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/dashboard/service/__init__.py](../../../../../../src/robot_systems/glue/applications/dashboard/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_dashboard_service.py`

Source: [src/robot_systems/glue/applications/dashboard/service/glue_dashboard_service.py](../../../../../../src/robot_systems/glue/applications/dashboard/service/glue_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`, `src.engine.core.i_messaging_service`, `src.engine.hardware.weight.interfaces.i_weight_cell_service`, `src.engine.repositories.interfaces.i_settings_service`, `src.robot_systems.glue.applications.dashboard.service.i_glue_dashboard_service`, `src.robot_systems.glue.component_ids`, `src.robot_systems.glue.processes.glue_operation_coordinator`, `src.robot_systems.glue.processes.glue_operation_mode`, `src.robot_systems.glue.settings.cells`, `src.robot_systems.glue.settings.glue_types`, `src.shared_contracts.events.process_events`, `typing`.

### `GlueDashboardService`

```python
class GlueDashboardService(IGlueDashboardService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, runner: GlueOperationCoordinator, settings_service: ISettingsService, weight_service: Optional[IWeightCellService]=None, execution_service=None, messaging_service: IMessagingService | None=None, robot_service=None, preview_transformer=None, preview_transformer_getter=None)
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def pause(self) -> None
```

```python
def resume(self) -> None
```

```python
def reset_errors(self) -> None
```

```python
def clean(self) -> None
```

```python
def set_mode(self, mode: str) -> None
```

```python
def change_glue(self, cell_id: int, glue_type: str) -> None
```

```python
def get_cell_capacity(self, cell_id: int) -> float
```

```python
def get_cell_glue_type(self, cell_id: int) -> Optional[str]
```

```python
def get_all_glue_types(self) -> List[str]
```

```python
def get_initial_cell_state(self, cell_id: int) -> Optional[Dict]
```

```python
def get_cells_count(self) -> int
```

```python
def get_process_state(self) -> str
```

```python
def get_process_snapshot(self) -> Optional[Dict]
```

```python
def get_current_robot_image_position(self) -> Optional[tuple[float, float]]
```

```python
def get_cell_connection_state(self, cell_id: int) -> str
```

## `i_glue_dashboard_service.py`

Source: [src/robot_systems/glue/applications/dashboard/service/i_glue_dashboard_service.py](../../../../../../src/robot_systems/glue/applications/dashboard/service/i_glue_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IGlueDashboardService`

```python
class IGlueDashboardService(ABC):
```

Service interface for the glue dashboard. Commands delegate to GlueProcess — queries are answered by the service itself.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def start(self) -> None
```

```python
@abstractmethod
def stop(self) -> None
```

```python
@abstractmethod
def pause(self) -> None
```

```python
@abstractmethod
def resume(self) -> None
```

```python
@abstractmethod
def reset_errors(self) -> None
```

```python
@abstractmethod
def clean(self) -> None
```

```python
@abstractmethod
def set_mode(self, mode: str) -> None
```

```python
@abstractmethod
def change_glue(self, cell_id: int, glue_type: str) -> None
```

```python
@abstractmethod
def get_cell_capacity(self, cell_id: int) -> float
```

```python
@abstractmethod
def get_cell_glue_type(self, cell_id: int) -> Optional[str]
```

```python
@abstractmethod
def get_all_glue_types(self) -> List[str]
```

```python
@abstractmethod
def get_initial_cell_state(self, cell_id: int) -> Optional[Dict]
```

```python
@abstractmethod
def get_cells_count(self) -> int
```

```python
@abstractmethod
def get_cell_connection_state(self, cell_id: int) -> str
```

```python
@abstractmethod
def get_process_state(self) -> str
```

```python
@abstractmethod
def get_process_snapshot(self) -> Optional[Dict]
```

```python
@abstractmethod
def get_current_robot_image_position(self) -> Optional[tuple[float, float]]
```

## `stub_glue_dashboard_service.py`

Source: [src/robot_systems/glue/applications/dashboard/service/stub_glue_dashboard_service.py](../../../../../../src/robot_systems/glue/applications/dashboard/service/stub_glue_dashboard_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.applications.dashboard.service.i_glue_dashboard_service`, `typing`.

### `StubGlueDashboardService`

```python
class StubGlueDashboardService(IGlueDashboardService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def pause(self) -> None
```

```python
def clean(self) -> None
```

```python
def reset_errors(self) -> None
```

```python
def set_mode(self, mode: str) -> None
```

```python
def change_glue(self, cell_id: int, glue_type: str) -> None
```

```python
def get_cell_capacity(self, cell_id: int) -> float
```

```python
def get_cell_glue_type(self, cell_id: int) -> Optional[str]
```

```python
def get_all_glue_types(self) -> List[str]
```

```python
def get_initial_cell_state(self, cell_id: int) -> Optional[Dict]
```

```python
def get_cells_count(self) -> int
```

```python
def get_cell_connection_state(self, cell_id: int) -> str
```

```python
def get_process_state(self) -> str
```

```python
def resume(self) -> None
```
