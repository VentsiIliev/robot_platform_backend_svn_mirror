# Module reference: `tests/applications/calibration_settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_calibration_settings_service.py](#test_calibration_settings_servicepy)
- [test_coordinate_calibration_mapper.py](#test_coordinate_calibration_mapperpy)
- [test_optional_height_settings.py](#test_optional_height_settingspy)

## `__init__.py`

Source: [tests/applications/calibration_settings/__init__.py](../../../../tests/applications/calibration_settings/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_calibration_settings_service.py`

Source: [tests/applications/calibration_settings/test_calibration_settings_service.py](../../../../tests/applications/calibration_settings/test_calibration_settings_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.calibration_settings.calibration_settings_data`, `src.applications.calibration_settings.mapper`, `src.applications.calibration_settings.service.calibration_settings_application_service`, `src.engine.common_settings_ids`, `src.engine.repositories.settings_service`, `src.engine.robot.configuration`, `src.engine.vision.calibration_vision_settings`, `src.engine.vision.camera_settings_serializer`, `types`, `unittest`, `unittest.mock`.

### `_make_settings_service`

```python
def _make_settings_service()
```

### `TestCalibrationSettingsApplicationService`

```python
class TestCalibrationSettingsApplicationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_edit_and_save_without_height_repository(self)
```

```python
def test_load_requests_all_calibration_setting_groups(self)
```

```python
def test_save_persists_all_calibration_setting_groups(self)
```

```python
def test_save_pushes_merged_calibration_settings_to_live_vision_runtime(self)
```

```python
def test_workobject_solve_computes_rz_from_center_to_x_point(self)
```

```python
def test_workobject_solve_computes_full_orientation_for_tilted_surface(self)
```

```python
def test_workobject_capture_refuses_nonzero_workobject_user(self)
```

```python
def test_workobject_solve_rejects_y_point_on_negative_y_side(self)
```

```python
def test_workobject_solve_rejects_non_perpendicular_axes(self)
```

```python
def test_workobject_capture_uses_base_tcp_pose(self)
```

```python
def test_workobject_capture_allows_calibrated_nonzero_tool_with_user_zero(self)
```

```python
def test_workobject_capture_rejects_tool_change_after_center(self)
```

```python
def test_workobject_save_updates_runtime_robot_settings_and_active_workobject(self)
```

## `test_coordinate_calibration_mapper.py`

Source: [tests/applications/calibration_settings/test_coordinate_calibration_mapper.py](../../../../tests/applications/calibration_settings/test_coordinate_calibration_mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.calibration_settings.calibration_settings_data`, `src.applications.calibration_settings.mapper`, `src.engine.vision.calibration_vision_settings`, `unittest`, `unittest.mock`.

### `TestCoordinateCalibrationMapper`

```python
class TestCoordinateCalibrationMapper(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_ui_fields_round_trip_profiles_and_assignments(self)
```

```python
def test_invalid_profile_json_is_rejected(self)
```

## `test_optional_height_settings.py`

Source: [tests/applications/calibration_settings/test_optional_height_settings.py](../../../../tests/applications/calibration_settings/test_optional_height_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.calibration.calibration_factory`, `src.applications.calibration.service.stub_calibration_service`, `src.applications.calibration_settings.calibration_settings_data`, `src.applications.calibration_settings.calibration_settings_factory`, `src.applications.calibration_settings.service.i_calibration_settings_service`, `src.engine.robot.configuration`, `src.engine.vision.calibration_vision_settings`, `unittest`, `unittest.mock`.

### `_settings`

```python
def _settings()
```

### `_CalibrationWithoutHeight`

```python
class _CalibrationWithoutHeight(StubCalibrationService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def load_calibration_settings(self)
```

### `OptionalHeightSettingsTests`

```python
class OptionalHeightSettingsTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_calibration_widget_loads_without_height_settings(self)
```

```python
def test_settings_widget_hides_height_tabs_and_saves_remaining_settings(self)
```
