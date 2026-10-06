# Module reference: `src/applications/height_measuring/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [height_measuring_model.py](#height_measuring_modelpy)
- [mapper.py](#mapperpy)

## `__init__.py`

Source: [src/applications/height_measuring/model/__init__.py](../../../../src/applications/height_measuring/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `height_measuring_model.py`

Source: [src/applications/height_measuring/model/height_measuring_model.py](../../../../src/applications/height_measuring/model/height_measuring_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.applications.base.i_application_model`, `src.applications.height_measuring.service.i_height_measuring_app_service`, `src.engine.robot.height_measuring.settings`, `typing`.

### `HeightMeasuringModel`

```python
class HeightMeasuringModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IHeightMeasuringAppService)
```

```python
def load(self) -> HeightMeasuringModuleSettings
```

```python
def save(self, settings: HeightMeasuringModuleSettings=None, **kwargs) -> None
```

```python
def run_calibration(self) -> tuple[bool, str]
```

```python
def is_calibrated(self) -> bool
```

```python
def get_calibration_info(self) -> Optional[dict]
```

```python
def get_settings(self) -> HeightMeasuringModuleSettings
```

```python
def save_settings(self, settings: HeightMeasuringModuleSettings) -> tuple[bool, str]
```

```python
def get_latest_frame(self) -> Optional[np.ndarray]
```

```python
def reload_calibration(self) -> None
```

```python
def laser_on(self) -> tuple[bool, str]
```

```python
def laser_off(self) -> tuple[bool, str]
```

```python
def detect_once(self) -> LaserDetectionResult
```

```python
def cleanup(self) -> None
```

```python
def cancel_calibration(self) -> None
```

## `mapper.py`

Source: [src/applications/height_measuring/model/mapper.py](../../../../src/applications/height_measuring/model/mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `copy`, `src.engine.robot.height_measuring.settings`.

### `HeightMeasuringSettingsMapper`

```python
class HeightMeasuringSettingsMapper:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def to_flat_dict(s: HeightMeasuringModuleSettings) -> dict
```

```python
@staticmethod
def from_flat_dict(flat: dict, base: HeightMeasuringModuleSettings) -> HeightMeasuringModuleSettings
```
