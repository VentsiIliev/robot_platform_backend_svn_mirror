# Module reference: `src/robot_systems/glue/applications/dashboard/model`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_dashboard_model.py](#glue_dashboard_modelpy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/dashboard/model/__init__.py](../../../../../../src/robot_systems/glue/applications/dashboard/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_dashboard_model.py`

Source: [src/robot_systems/glue/applications/dashboard/model/glue_dashboard_model.py](../../../../../../src/robot_systems/glue/applications/dashboard/model/glue_dashboard_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `logging`, `src.applications.base.i_application_model`, `src.robot_systems.glue.applications.dashboard.config`, `src.robot_systems.glue.applications.dashboard.service.i_glue_dashboard_service`, `typing`.

### `GlueDashboardModel`

```python
class GlueDashboardModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IGlueDashboardService, config: GlueDashboardConfig=None)
```

```python
def load(self) -> GlueDashboardConfig
```

Return the dashboard config — initial state is pulled per-cell by the controller.

```python
def save(self, *args, **kwargs) -> None
```

Not applicable — dashboard state is not persisted.

```python
@property
def config(self) -> GlueDashboardConfig
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
def get_process_snapshot(self) -> Optional[Dict]
```

```python
def get_current_robot_image_position(self)
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
