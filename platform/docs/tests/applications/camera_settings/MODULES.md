# Module reference: `tests/applications/camera_settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_camera_devices_controller.py](#test_camera_devices_controllerpy)
- [test_camera_settings_model.py](#test_camera_settings_modelpy)
- [test_camera_settings_schema.py](#test_camera_settings_schemapy)
- [test_camera_settings_service.py](#test_camera_settings_servicepy)

## `__init__.py`

Source: [tests/applications/camera_settings/__init__.py](../../../../tests/applications/camera_settings/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_camera_devices_controller.py`

Source: [tests/applications/camera_settings/test_camera_devices_controller.py](../../../../tests/applications/camera_settings/test_camera_devices_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `pl_gui.utils.utils_widgets.SwitchButton`, `src.applications.camera_settings.controller.camera_devices_controller`, `src.applications.camera_settings.service.i_camera_settings_service`, `src.applications.camera_settings.view.camera_devices_widget`, `src.engine.core.message_broker`, `src.shared_contracts.events.vision_events`, `unittest`, `unittest.mock`.

### `CameraDevicesControllerTests`

```python
class CameraDevicesControllerTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls) -> None
```

```python
def test_subscribes_only_while_camera_tab_is_visible(self) -> None
```

```python
def test_orientation_controls_are_loaded_and_saved_for_each_role(self) -> None
```

```python
def test_recalibration_hint_is_shown_only_for_transposing_rotation(self) -> None
```

```python
def test_rotation_change_also_refreshes_the_recalibration_hint(self) -> None
```

```python
def test_device_controls_rotate_each_camera_in_ninety_degree_steps(self) -> None
```

## `test_camera_settings_model.py`

Source: [tests/applications/camera_settings/test_camera_settings_model.py](../../../../tests/applications/camera_settings/test_camera_settings_model.py).

Tests for src/applications/camera_settings/model/camera_settings_model.y_pixels

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.camera_settings.camera_settings_data`, `src.applications.camera_settings.model.camera_settings_model`, `src.applications.camera_settings.service.i_camera_settings_service`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service(settings=None)
```

### `TestCameraSettingsModelLoad`

```python
class TestCameraSettingsModelLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_service(self)
```

```python
def test_load_returns_camera_settings_data(self)
```

```python
def test_load_caches_settings(self)
```

### `TestCameraSettingsModelSave`

```python
class TestCameraSettingsModelSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_delegates_to_service(self)
```

```python
def test_save_updates_cached_settings(self)
```

### `TestCameraSettingsModelCurrentSettings`

```python
class TestCameraSettingsModelCurrentSettings(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_initial_current_settings_is_default(self)
```

```python
def test_current_settings_reflects_loaded_data(self)
```

### `TestCameraSettingsModelWorkArea`

```python
class TestCameraSettingsModelWorkArea(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_work_area_converts_normalized_to_pixel(self)
```

```python
def test_save_work_area_strips_area_suffix(self)
```

```python
def test_get_work_area_returns_empty_on_failure(self)
```

```python
def test_get_work_area_converts_pixel_to_normalized(self)
```

## `test_camera_settings_schema.py`

Source: [tests/applications/camera_settings/test_camera_settings_schema.py](../../../../tests/applications/camera_settings/test_camera_settings_schema.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.camera_settings.view`, `unittest`.

### `TestCameraSettingsSchema`

```python
class TestCameraSettingsSchema(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_camera_settings_does_not_expose_calibration_group(self)
```

## `test_camera_settings_service.py`

Source: [tests/applications/camera_settings/test_camera_settings_service.py](../../../../tests/applications/camera_settings/test_camera_settings_service.py).

Tests for camera_settings service layer. Covers: - StubCameraSettingsService — interface compliance + in-memory behaviour - CameraSettingsApplicationService — delegation to settings_service and vision_service

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `src.applications.camera_settings.camera_settings_data`, `src.applications.camera_settings.service.camera_settings_application_service`, `src.applications.camera_settings.service.i_camera_settings_service`, `src.applications.camera_settings.service.stub_camera_settings_service`, `src.engine.vision.camera_device_settings`, `unittest`, `unittest.mock`.

### `_SettingsKey`

```python
class _SettingsKey(str, Enum):
```

Declared fields/defaults:

```python
CAMERAS = 'cameras'
```

### `_make_settings_service`

```python
def _make_settings_service(data: dict=None)
```

### `_make_vision_service`

```python
def _make_vision_service()
```

### `_make_work_area_service`

```python
def _make_work_area_service()
```

### `_make_app_service`

```python
def _make_app_service(data=None, vision=None, work_area_service=None)
```

### `TestStubCameraSettingsService`

```python
class TestStubCameraSettingsService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_load_settings_returns_data(self)
```

```python
def test_save_settings_updates_stored_data(self)
```

```python
def test_set_raw_mode_does_not_change_saved_settings(self)
```

```python
def test_update_settings_returns_true_tuple(self)
```

```python
def test_save_work_area_returns_true_tuple(self)
```

```python
def test_get_work_area_returns_tuple(self)
```

### `TestCameraSettingsApplicationServiceLoad`

```python
class TestCameraSettingsApplicationServiceLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_settings_service_get(self)
```

```python
def test_load_returns_camera_settings_data(self)
```

```python
def test_load_parses_index_from_raw(self)
```

```python
def test_load_parses_hardware_auto_exposure(self)
```

### `TestCameraSettingsApplicationServiceSave`

```python
class TestCameraSettingsApplicationServiceSave(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_applies_changed_hardware_auto_exposure(self)
```

```python
def test_save_does_not_reapply_unchanged_hardware_auto_exposure(self)
```

```python
def test_save_calls_settings_service_save(self)
```

```python
def test_save_calls_vision_update_settings(self)
```

```python
def test_save_preserves_existing_calibration_section(self)
```

### `TestCameraSettingsApplicationServiceUpdateSettings`

```python
class TestCameraSettingsApplicationServiceUpdateSettings(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_update_delegates_to_vision(self)
```

```python
def test_update_passes_through_failure(self)
```

### `TestCameraSettingsApplicationServiceVisionOptional`

```python
class TestCameraSettingsApplicationServiceVisionOptional(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_settings_requires_vision_service(self)
```

### `TestCameraSettingsApplicationServiceWorkArea`

```python
class TestCameraSettingsApplicationServiceWorkArea(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_work_area_delegates_to_work_area_service(self)
```

```python
def test_get_work_area_delegates_to_work_area_service(self)
```

```python
def test_set_raw_mode_delegates_to_vision(self)
```

```python
def test_save_work_area_fails_without_work_area_service(self)
```

```python
def test_get_work_area_fails_without_work_area_service(self)
```

### `TestCameraSettingsApplicationServiceDevices`

```python
class TestCameraSettingsApplicationServiceDevices(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_camera_devices_includes_missing_configured_devices(self)
```

```python
def test_save_camera_devices_preserves_role_metadata(self)
```

```python
def test_save_applies_orientation_to_running_camera_owners(self)
```

```python
def test_save_falls_back_to_persisted_orientation_for_unlisted_roles(self)
```

```python
def test_save_rejects_unsupported_rotation(self)
```
