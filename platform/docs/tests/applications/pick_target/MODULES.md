# Module reference: `tests/applications/pick_target`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_pick_target_application_service.py](#test_pick_target_application_servicepy)

## `test_pick_target_application_service.py`

Source: [tests/applications/pick_target/test_pick_target_application_service.py](../../../../tests/applications/pick_target/test_pick_target_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.pick_target.service.pick_target_application_service`, `types`, `unittest`, `unittest.mock`.

### `TestPickTargetApplicationService`

```python
class TestPickTargetApplicationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_move_uses_live_robot_config_after_settings_object_is_replaced(self)
```

```python
def test_transform_point_uses_live_resolver_getter(self)
```

```python
def test_set_target_uses_current_resolver_registry(self)
```

```python
def test_transform_point_uses_active_frame_name_getter(self)
```

```python
def test_jog_reference_uses_active_frame_mapper(self)
```

```python
def test_move_to_calibration_position_routes_to_active_capture_group(self)
```
