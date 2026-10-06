# Module reference: `tests/engine/hardware/weight`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_weight_cell_service.py](#test_weight_cell_servicepy)
- [test_weight_config.py](#test_weight_configpy)

## `__init__.py`

Source: [tests/engine/hardware/weight/__init__.py](../../../../../tests/engine/hardware/weight/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_weight_cell_service.py`

Source: [tests/engine/hardware/weight/test_weight_cell_service.py](../../../../../tests/engine/hardware/weight/test_weight_cell_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.weight.config`, `src.engine.hardware.weight.weight_cell_service`, `src.shared_contracts.events.weight_events`, `threading`, `time`, `unittest`, `unittest.mock`.

### `_calib`

```python
def _calib()
```

### `_meas`

```python
def _meas()
```

### `_cell`

```python
def _cell(cid)
```

### `_cells`

```python
def _cells(*ids)
```

### `_make_transport`

```python
def _make_transport(connect_ok=True, weight=42.0)
```

### `_make_calibrator`

```python
def _make_calibrator(tare_ok=True, update_ok=True)
```

### `_make_service`

```python
def _make_service(cell_ids=(0,), connect_ok=True, weight=42.0)
```

### `TestWeightCellServiceInit`

```python
class TestWeightCellServiceInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_creates_context_per_cell(self)
```

```python
def test_initial_state_disconnected(self)
```

```python
def test_unknown_cell_returns_disconnected(self)
```

### `TestWeightCellServiceConnect`

```python
class TestWeightCellServiceConnect(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_connect_success(self)
```

```python
def test_connect_failure(self)
```

```python
def test_connect_unknown_cell_returns_false(self)
```

```python
def test_connect_publishes_connecting_then_connected(self)
```

```python
def test_connect_transport_exception_sets_error(self)
```

```python
def test_disconnect_sets_disconnected(self)
```

```python
def test_disconnect_unknown_cell_no_raise(self)
```

```python
def test_disconnect_all(self)
```

```python
def test_get_connected_cell_ids(self)
```

### `TestWeightCellServiceRead`

```python
class TestWeightCellServiceRead(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_read_weight_when_connected(self)
```

```python
def test_read_weight_when_disconnected_returns_none(self)
```

```python
def test_read_weight_unknown_cell_returns_none(self)
```

```python
def test_read_weight_publishes_reading_topic(self)
```

```python
def test_read_weight_transport_exception_sets_error(self)
```

### `TestWeightCellServiceCalibration`

```python
class TestWeightCellServiceCalibration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_tare_delegates_to_calibrator(self)
```

```python
def test_tare_unknown_cell_returns_false(self)
```

```python
def test_tare_exception_returns_false(self)
```

```python
def test_update_offset(self)
```

```python
def test_update_scale(self)
```

```python
def test_update_config(self)
```

```python
def test_update_config_unknown_cell_returns_false(self)
```

```python
def test_get_calibration(self)
```

```python
def test_get_calibration_unknown_returns_none(self)
```

### `TestWeightCellServiceMonitoring`

```python
class TestWeightCellServiceMonitoring(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_monitoring_spawns_thread(self)
```

```python
def test_start_monitoring_idempotent(self)
```

```python
def test_stop_monitoring_clears_flag(self)
```

```python
def test_monitoring_uses_cell_interval(self)
```

data_fetch_interval_ms=100 → thread sleeps 0.1s per iteration.

## `test_weight_config.py`

Source: [tests/engine/hardware/weight/test_weight_config.py](../../../../../tests/engine/hardware/weight/test_weight_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.hardware.weight.config`, `unittest`.

### `_calib`

```python
def _calib(offset=0.0, scale=1.0)
```

### `_meas`

```python
def _meas(sr=10, fc=1.0, avg=5, mn=0.0, mx=1000.0)
```

### `_cell`

```python
def _cell(cid=0, url='http://host/w0')
```

### `TestCalibrationConfig`

```python
class TestCalibrationConfig(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_defaults_from_empty_dict(self)
```

```python
def test_from_dict_values(self)
```

```python
def test_roundtrip(self)
```

```python
def test_frozen(self)
```

### `TestMeasurementConfig`

```python
class TestMeasurementConfig(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_defaults_from_empty_dict(self)
```

```python
def test_roundtrip(self)
```

### `TestCellConfig`

```python
class TestCellConfig(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_roundtrip(self)
```

```python
def test_from_dict_id_required(self)
```

```python
def test_fetch_timeout_default(self)
```

```python
def test_data_fetch_interval_default(self)
```

```python
def test_motor_address_default(self)
```

### `TestCellsConfig`

```python
class TestCellsConfig(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_cell_count(self)
```

```python
def test_get_cell_by_id_found(self)
```

```python
def test_get_cell_by_id_not_found(self)
```

```python
def test_get_all_cell_ids(self)
```

```python
def test_get_cells_by_type(self)
```

```python
def test_roundtrip(self)
```

```python
def test_empty(self)
```

### `TestCellsConfigSerializer`

```python
class TestCellsConfigSerializer(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_settings_type(self)
```

```python
def test_get_default_empty(self)
```

```python
def test_roundtrip(self)
```
