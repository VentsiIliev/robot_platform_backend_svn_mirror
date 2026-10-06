# Module reference: `src/applications/shaft_alignment/tests`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_shaft_alignment_model.py](#test_shaft_alignment_modelpy)
- [test_shaft_alignment_settings.py](#test_shaft_alignment_settingspy)

## `__init__.py`

Source: [src/applications/shaft_alignment/tests/__init__.py](../../../../src/applications/shaft_alignment/tests/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_shaft_alignment_model.py`

Source: [src/applications/shaft_alignment/tests/test_shaft_alignment_model.py](../../../../src/applications/shaft_alignment/tests/test_shaft_alignment_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.shaft_alignment.model.shaft_alignment_model`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.service.stub_shaft_alignment_service`, `time`, `unittest`.

### `ShaftAlignmentModelTests`

```python
class ShaftAlignmentModelTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_check_alignment_fails_safe_without_reference_and_returns_boolean(self)
```

```python
def test_delegates_lifecycle_reference_and_thresholds(self)
```

```python
def test_completed_reference_updates_in_memory_settings(self)
```

## `test_shaft_alignment_settings.py`

Source: [src/applications/shaft_alignment/tests/test_shaft_alignment_settings.py](../../../../src/applications/shaft_alignment/tests/test_shaft_alignment_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `collections`, `json`, `pathlib`, `src.applications.shaft_alignment.service.i_shaft_alignment_service`, `src.applications.shaft_alignment.service.paint_vision_shaft_alignment_service`, `src.applications.shaft_alignment.settings`, `tempfile`, `threading`, `unittest`.

### `ShaftAlignmentSettingsTests`

```python
class ShaftAlignmentSettingsTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_round_trip_preserves_all_settings(self)
```

```python
def test_runtime_state_updates_memory_and_json_atomically(self)
```

```python
def test_point_of_interest_uses_aligned_marker_image_axes(self)
```

```python
def test_alignment_check_uses_configured_median_sample_batch(self)
```
