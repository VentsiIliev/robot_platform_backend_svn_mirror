# Module reference: `src/engine/hardware/weight/interfaces`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_cell_calibrator.py](#i_cell_calibratorpy)
- [i_cell_transport.py](#i_cell_transportpy)
- [i_weight_cell_service.py](#i_weight_cell_servicepy)

## `__init__.py`

Source: [src/engine/hardware/weight/interfaces/__init__.py](../../../../../src/engine/hardware/weight/interfaces/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.weight.interfaces.i_cell_calibrator`, `src.engine.hardware.weight.interfaces.i_cell_transport`, `src.engine.hardware.weight.interfaces.i_weight_cell_service`.

Package-level import/export surface:

```python
from src.engine.hardware.weight.interfaces.i_cell_transport import ICellTransport
from src.engine.hardware.weight.interfaces.i_cell_calibrator import ICellCalibrator
from src.engine.hardware.weight.interfaces.i_weight_cell_service import IWeightCellService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ICellTransport', 'ICellCalibrator', 'IWeightCellService']
```

## `i_cell_calibrator.py`

Source: [src/engine/hardware/weight/interfaces/i_cell_calibrator.py](../../../../../src/engine/hardware/weight/interfaces/i_cell_calibrator.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.robot_systems.glue.settings.cells`.

### `ICellCalibrator`

```python
class ICellCalibrator(ABC):
```

Responsible for calibration operations on a single cell. Decoupled from transport — calibration is a separate concern.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def tare(self, cell_id: int) -> bool
```

```python
@abstractmethod
def get_config(self, cell_id: int) -> CalibrationConfig
```

```python
@abstractmethod
def update_offset(self, cell_id: int, offset: float) -> bool
```

```python
@abstractmethod
def update_scale(self, cell_id: int, scale: float) -> bool
```

```python
@abstractmethod
def update_config(self, cell_id: int, offset: float, scale: float) -> bool
```

## `i_cell_transport.py`

Source: [src/engine/hardware/weight/interfaces/i_cell_transport.py](../../../../../src/engine/hardware/weight/interfaces/i_cell_transport.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`.

### `ICellTransport`

```python
class ICellTransport(ABC):
```

Responsible for raw communication with a single cell. Knows nothing about calibration or business logic.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def connect(self) -> bool
```

```python
@abstractmethod
def disconnect(self) -> None
```

```python
@property
@abstractmethod
def is_connected(self) -> bool
```

```python
@abstractmethod
def read_weight(self) -> float
```

## `i_weight_cell_service.py`

Source: [src/engine/hardware/weight/interfaces/i_weight_cell_service.py](../../../../../src/engine/hardware/weight/interfaces/i_weight_cell_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `src.engine.core.i_health_checkable`, `src.robot_systems.glue.settings.cells`, `src.shared_contracts.events.weight_events`, `typing`.

### `IWeightCellService`

```python
class IWeightCellService(IHealthCheckable, ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def connect(self, cell_id: int) -> bool
```

```python
@abstractmethod
def disconnect(self, cell_id: int) -> None
```

```python
@abstractmethod
def connect_all(self) -> None
```

```python
@abstractmethod
def disconnect_all(self) -> None
```

```python
@abstractmethod
def read_weight(self, cell_id: int) -> Optional[WeightReading]
```

```python
@abstractmethod
def get_cell_state(self, cell_id: int) -> CellState
```

```python
@abstractmethod
def get_connected_cell_ids(self) -> List[int]
```

```python
@abstractmethod
def start_monitoring(self, cell_ids: List[int], interval_s: float=0.5) -> None
```

```python
@abstractmethod
def stop_monitoring(self) -> None
```

```python
@abstractmethod
def tare(self, cell_id: int) -> bool
```

```python
@abstractmethod
def get_calibration(self, cell_id: int) -> Optional[CalibrationConfig]
```

```python
@abstractmethod
def update_offset(self, cell_id: int, offset: float) -> bool
```

```python
@abstractmethod
def update_scale(self, cell_id: int, scale: float) -> bool
```

```python
@abstractmethod
def update_config(self, cell_id: int, offset: float, scale: float) -> bool
```

```python
def is_healthy(self) -> bool
```

Healthy = at least one cell is connected.
