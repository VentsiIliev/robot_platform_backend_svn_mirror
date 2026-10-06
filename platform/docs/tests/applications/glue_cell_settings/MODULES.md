# Module reference: `tests/applications/glue_cell_settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_glue_cell_mapper.py](#test_glue_cell_mapperpy)
- [test_glue_cell_settings_model.py](#test_glue_cell_settings_modelpy)
- [test_glue_cell_settings_service.py](#test_glue_cell_settings_servicepy)

## `__init__.py`

Source: [tests/applications/glue_cell_settings/__init__.py](../../../../tests/applications/glue_cell_settings/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_glue_cell_mapper.py`

Source: [tests/applications/glue_cell_settings/test_glue_cell_mapper.py](../../../../tests/applications/glue_cell_settings/test_glue_cell_mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.glue_cell_settings.model.mapper`, `src.engine.hardware.weight.config`, `unittest`.

### `_cell`

```python
def _cell()
```

### `TestGlueCellMapperToFlat`

```python
class TestGlueCellMapperToFlat(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_url(self)
```

```python
def test_type(self)
```

```python
def test_capacity(self)
```

```python
def test_fetch_timeout(self)
```

```python
def test_interval_ms(self)
```

```python
def test_motor_address(self)
```

```python
def test_zero_offset(self)
```

```python
def test_scale_factor(self)
```

```python
def test_sampling_rate(self)
```

```python
def test_filter_cutoff(self)
```

```python
def test_averaging(self)
```

```python
def test_min_threshold(self)
```

```python
def test_max_threshold(self)
```

### `TestGlueCellMapperFromFlat`

```python
class TestGlueCellMapperFromFlat(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_roundtrip_url(self)
```

```python
def test_roundtrip_type(self)
```

```python
def test_roundtrip_capacity(self)
```

```python
def test_roundtrip_timeout(self)
```

```python
def test_roundtrip_interval(self)
```

```python
def test_roundtrip_motor(self)
```

```python
def test_roundtrip_zero_offset(self)
```

```python
def test_roundtrip_scale_factor(self)
```

```python
def test_roundtrip_sampling_rate(self)
```

```python
def test_roundtrip_max_threshold(self)
```

```python
def test_partial_flat_uses_original_fallback(self)
```

## `test_glue_cell_settings_model.py`

Source: [tests/applications/glue_cell_settings/test_glue_cell_settings_model.py](../../../../tests/applications/glue_cell_settings/test_glue_cell_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.glue_cell_settings.model.glue_cell_settings_model`, `src.engine.hardware.weight.config`, `unittest`, `unittest.mock`.

### `_calib`

```python
def _calib(offset=0.0, scale=1.0)
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

### `_make_service`

```python
def _make_service(cell_ids=(0, 1))
```

### `TestGlueCellSettingsModelLoad`

```python
class TestGlueCellSettingsModelLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_service(self)
```

```python
def test_load_returns_cells_config(self)
```

```python
def test_load_caches_config(self)
```

### `TestGlueCellSettingsModelGetFlat`

```python
class TestGlueCellSettingsModelGetFlat(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_flat_returns_dict(self)
```

```python
def test_get_flat_unknown_cell_returns_none(self)
```

```python
def test_get_flat_lazy_loads(self)
```

### `TestGlueCellSettingsModelSave`

```python
class TestGlueCellSettingsModelSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_calls_save_cells(self)
```

```python
def test_save_pushes_calibration(self)
```

```python
def test_save_updates_cached_config(self)
```

```python
def test_save_unknown_cell_no_call_to_service(self)
```

```python
def test_save_does_not_affect_other_cells(self)
```

### `TestGlueCellSettingsModelTare`

```python
class TestGlueCellSettingsModelTare(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_tare_delegates_to_service(self)
```

```python
def test_tare_failure_propagates(self)
```

### `TestGlueCellSettingsModelGetCellIds`

```python
class TestGlueCellSettingsModelGetCellIds(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_cell_ids_lazy_loads(self)
```

## `test_glue_cell_settings_service.py`

Source: [tests/applications/glue_cell_settings/test_glue_cell_settings_service.py](../../../../tests/applications/glue_cell_settings/test_glue_cell_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.glue_cell_settings.service.glue_cell_settings_service`, `src.engine.hardware.weight.config`, `src.robot_systems.glue.component_ids`, `unittest`, `unittest.mock`.

### `_cells`

```python
def _cells()
```

### `_make_settings`

```python
def _make_settings(cells=None)
```

### `TestGlueCellSettingsServiceLoad`

```python
class TestGlueCellSettingsServiceLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_cells_calls_settings_get(self)
```

```python
def test_load_cells_returns_cells_config(self)
```

### `TestGlueCellSettingsServiceSave`

```python
class TestGlueCellSettingsServiceSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_calls_settings_save(self)
```

### `TestGlueCellSettingsServiceTare`

```python
class TestGlueCellSettingsServiceTare(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_tare_with_no_weight_service_returns_false(self)
```

```python
def test_tare_delegates_to_weight_service(self)
```

```python
def test_tare_propagates_false(self)
```

### `TestGlueCellSettingsServicePushCalibration`

```python
class TestGlueCellSettingsServicePushCalibration(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_push_with_no_weight_service_returns_false(self)
```

```python
def test_push_delegates_to_update_config(self)
```

```python
def test_push_propagates_false(self)
```

### `TestGlueCellSettingsServiceGetCellIds`

```python
class TestGlueCellSettingsServiceGetCellIds(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_cell_ids(self)
```

```python
def test_get_cell_ids_settings_exception_returns_empty(self)
```
