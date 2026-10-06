# Module reference: `src/engine/hardware/weight/http`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [http_cell_transport.py](#http_cell_transportpy)
- [http_weight_cell_factory.py](#http_weight_cell_factorypy)

## `__init__.py`

Source: [src/engine/hardware/weight/http/__init__.py](../../../../../src/engine/hardware/weight/http/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `http_cell_transport.py`

Source: [src/engine/hardware/weight/http/http_cell_transport.py](../../../../../src/engine/hardware/weight/http/http_cell_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `requests`, `src.engine.hardware.weight.config`, `src.engine.hardware.weight.interfaces.i_cell_calibrator`, `src.engine.hardware.weight.interfaces.i_cell_transport`, `typing`.

### `HttpCellTransport`

```python
class HttpCellTransport(ICellTransport, ICellCalibrator):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: CellConfig)
```

```python
def connect(self) -> bool
```

```python
def disconnect(self) -> None
```

```python
@property
def is_connected(self) -> bool
```

```python
def read_weight(self) -> float
```

```python
def tare(self, cell_id: int) -> bool
```

```python
def get_config(self, cell_id: int) -> CalibrationConfig
```

```python
def update_offset(self, cell_id: int, offset: float) -> bool
```

```python
def update_scale(self, cell_id: int, scale: float) -> bool
```

```python
def update_config(self, cell_id: int, offset: float, scale: float) -> bool
```

## `http_weight_cell_factory.py`

Source: [src/engine/hardware/weight/http/http_weight_cell_factory.py](../../../../../src/engine/hardware/weight/http/http_weight_cell_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.core.i_messaging_service`, `src.engine.hardware.weight.http.http_cell_transport`, `src.engine.hardware.weight.interfaces.i_cell_calibrator`, `src.engine.hardware.weight.interfaces.i_cell_transport`, `src.engine.hardware.weight.weight_cell_service`, `src.robot_systems.glue.settings.cells`.

### `build_http_weight_cell_service`

```python
def build_http_weight_cell_service(cells_config: GlueCellsConfig, messaging: IMessagingService) -> WeightCellService
```
