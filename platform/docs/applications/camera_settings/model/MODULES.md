# Module reference: `src/applications/camera_settings/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [camera_settings_model.py](#camera_settings_modelpy)

## `camera_settings_model.py`

Source: [src/applications/camera_settings/model/camera_settings_model.py](../../../../src/applications/camera_settings/model/camera_settings_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.i_application_model`, `src.applications.camera_settings.camera_settings_data`, `src.applications.camera_settings.service.i_camera_settings_service`.

### `CameraSettingsModel`

```python
class CameraSettingsModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: ICameraSettingsService)
```

```python
def load(self) -> CameraSettingsData
```

```python
def save(self, settings: CameraSettingsData) -> None
```

```python
def set_raw_mode(self, enabled: bool) -> None
```

```python
def load_camera_devices(self)
```

```python
def save_camera_devices(self, assignments: dict[str, str], orientation: dict[str, CameraOrientation]) -> None
```

```python
def save_work_area(self, area_type: str, normalized_points) -> tuple
```

```python
def get_work_area(self, area_type: str) -> list
```

```python
@property
def current_settings(self) -> CameraSettingsData
```
