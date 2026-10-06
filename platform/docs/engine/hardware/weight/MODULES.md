# Module reference: `src/engine/hardware/weight`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [config.py](#configpy)
- [weight_cell_service.py](#weight_cell_servicepy)

## `__init__.py`

Source: [src/engine/hardware/weight/__init__.py](../../../../src/engine/hardware/weight/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.weight.config`, `src.engine.hardware.weight.http.http_weight_cell_factory`, `src.engine.hardware.weight.weight_cell_service`, `src.shared_contracts.events.weight_events`.

Package-level import/export surface:

```python
from src.shared_contracts.events.weight_events import CellState, WeightReading
from src.engine.hardware.weight.config import CalibrationConfig, MeasurementConfig, CellConfig, CellsConfig, CellsConfigSerializer
from src.engine.hardware.weight.weight_cell_service import WeightCellService
from src.engine.hardware.weight.http.http_weight_cell_factory import build_http_weight_cell_service
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['CellState', 'WeightReading', 'CalibrationConfig', 'MeasurementConfig', 'CellConfig', 'CellsConfig', 'CellsConfigSerializer', 'WeightCellService', 'build_http_weight_cell_service']
```

## `config.py`

Source: [src/engine/hardware/weight/config.py](../../../../src/engine/hardware/weight/config.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `src.engine.repositories.interfaces.settings_serializer`, `typing`.

### `CalibrationConfig`

```python
@dataclass(frozen=True)
class CalibrationConfig:
```

Declared fields/defaults:

```python
zero_offset: float
scale_factor: float
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'CalibrationConfig'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `MeasurementConfig`

```python
@dataclass(frozen=True)
class MeasurementConfig:
```

Declared fields/defaults:

```python
sampling_rate: int
filter_cutoff: float
averaging_samples: int
min_weight_threshold: float
max_weight_threshold: float
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'MeasurementConfig'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `CellConfig`

```python
@dataclass(frozen=True)
class CellConfig:
```

Declared fields/defaults:

```python
id: int
type: str
url: str
capacity: float
fetch_timeout_seconds: float
data_fetch_interval_ms: int
calibration: CalibrationConfig
measurement: MeasurementConfig
motor_address: int = 0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'CellConfig'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `CellsConfig`

```python
@dataclass(frozen=True)
class CellsConfig:
```

Declared fields/defaults:

```python
cells: List[CellConfig]
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def get_cell_by_id(self, cell_id: int) -> Optional[CellConfig]
```

```python
def get_all_cell_ids(self) -> List[int]
```

```python
def get_cells_by_type(self, cell_type: str) -> List[CellConfig]
```

```python
@property
def cell_count(self) -> int
```

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> 'CellsConfig'
```

```python
def to_dict(self) -> Dict[str, Any]
```

### `CellsConfigSerializer`

```python
class CellsConfigSerializer(ISettingsSerializer['CellsConfig']):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> 'CellsConfig'
```

```python
def to_dict(self, settings: 'CellsConfig') -> Dict[str, Any]
```

```python
def from_dict(self, data: Dict[str, Any]) -> 'CellsConfig'
```

## `weight_cell_service.py`

Source: [src/engine/hardware/weight/weight_cell_service.py](../../../../src/engine/hardware/weight/weight_cell_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.core.i_messaging_service`, `src.engine.hardware.weight.config`, `src.engine.hardware.weight.interfaces.i_cell_calibrator`, `src.engine.hardware.weight.interfaces.i_cell_transport`, `src.engine.hardware.weight.interfaces.i_weight_cell_service`, `src.shared_contracts.events.weight_events`, `threading`, `time`, `typing`.

### `_CellContext`

```python
class _CellContext:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: CellConfig, transport: ICellTransport, calibrator: ICellCalibrator)
```

### `WeightCellService`

```python
class WeightCellService(IWeightCellService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, cells_config: CellsConfig, transport_factory: Callable[[CellConfig], ICellTransport], calibrator_factory: Callable[[CellConfig], ICellCalibrator], messaging: IMessagingService)
```

```python
def connect(self, cell_id: int) -> bool
```

```python
def disconnect(self, cell_id: int) -> None
```

```python
def connect_all(self) -> None
```

Non-blocking — each cell connects in its own daemon thread.

```python
def disconnect_all(self) -> None
```

```python
def read_weight(self, cell_id: int) -> Optional[WeightReading]
```

```python
def get_cell_state(self, cell_id: int) -> CellState
```

```python
def get_connected_cell_ids(self) -> List[int]
```

```python
def start_monitoring(self, cell_ids: List[int], interval_s: float=0.5) -> None
```

```python
def stop_monitoring(self) -> None
```

```python
def tare(self, cell_id: int) -> bool
```

```python
def get_calibration(self, cell_id: int) -> Optional[CalibrationConfig]
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
