# Module reference: `src/applications/glue_cell_settings/service`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_cell_settings_service.py](#glue_cell_settings_servicepy)
- [i_glue_cell_settings_service.py](#i_glue_cell_settings_servicepy)
- [stub_glue_cell_settings.py](#stub_glue_cell_settingspy)

## `__init__.py`

Source: [src/applications/glue_cell_settings/service/__init__.py](../../../../src/applications/glue_cell_settings/service/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_cell_settings_service.py`

Source: [src/applications/glue_cell_settings/service/glue_cell_settings_service.py](../../../../src/applications/glue_cell_settings/service/glue_cell_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.glue_cell_settings.service.i_glue_cell_settings_service`, `src.engine.hardware.weight.config`, `src.engine.hardware.weight.interfaces.i_weight_cell_service`, `src.engine.repositories.interfaces.i_settings_service`, `typing`.

### `GlueCellSettingsService`

```python
class GlueCellSettingsService(IGlueCellSettingsService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_service: ISettingsService, settings_key: str, weight_service: Optional[IWeightCellService]=None)
```

```python
def load_cells(self) -> CellsConfig
```

```python
def save_cells(self, config: CellsConfig) -> None
```

```python
def tare(self, cell_id: int) -> bool
```

```python
def push_calibration(self, cell_id: int, offset: float, scale: float) -> bool
```

```python
def get_cell_ids(self) -> List[int]
```

## `i_glue_cell_settings_service.py`

Source: [src/applications/glue_cell_settings/service/i_glue_cell_settings_service.py](../../../../src/applications/glue_cell_settings/service/i_glue_cell_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.hardware.weight.config`, `typing`.

### `IGlueCellSettingsService`

```python
class IGlueCellSettingsService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def load_cells(self) -> CellsConfig
```

```python
@abstractmethod
def save_cells(self, config: CellsConfig) -> None
```

```python
@abstractmethod
def tare(self, cell_id: int) -> bool
```

```python
@abstractmethod
def get_cell_ids(self) -> List[int]
```

```python
@abstractmethod
def push_calibration(self, cell_id: int, offset: float, scale: float) -> bool
```

Push offset + scale to the physical hardware (ESP32 server).

## `stub_glue_cell_settings.py`

Source: [src/applications/glue_cell_settings/service/stub_glue_cell_settings.py](../../../../src/applications/glue_cell_settings/service/stub_glue_cell_settings.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
