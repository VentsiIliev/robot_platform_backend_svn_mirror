# Module reference: `src/engine/vision/implementation/VisionSystem/core`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [data_loading.py](#data_loadingpy)
- [path_resolver.py](#path_resolverpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/core/__init__.py](../../../../../../src/engine/vision/implementation/VisionSystem/core/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `data_loading.py`

Source: [src/engine/vision/implementation/VisionSystem/core/data_loading.py](../../../../../../src/engine/vision/implementation/VisionSystem/core/data_loading.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `os`.

### `DataManager`

```python
class DataManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, storage_path)
```

```python
def build_storage_paths(self)
```

```python
def loadWorkAreaPoints(self)
```

```python
def loadCameraToRobotMatrix(self)
```

```python
def loadCameraCalibrationData(self)
```

```python
def loadPerspectiveMatrix(self)
```

```python
def saveWorkAreaPoints(self, data)
```

```python
def get_camera_matrix(self)
```

```python
def get_distortion_coefficients(self)
```

```python
def get_named_area_points(self, area_type: str)
```

## `path_resolver.py`

Source: [src/engine/vision/implementation/VisionSystem/core/path_resolver.py](../../../../../../src/engine/vision/implementation/VisionSystem/core/path_resolver.py).

Imports (including optional/function-local imports; not a startup dependency list): `pathlib`.

### `PathResolver`

```python
class PathResolver:
```

Centralized path resolution for the vision vision_service

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, base_path: Path | str | None=None)
```

```python
@property
def project_root(self) -> Path
```

Return the project root path

```python
@property
def src_root(self) -> Path
```

Return the src directory path

```python
@property
def vision_system_root(self) -> Path
```

Return the VisionSystem directory path

```python
@property
def core_root(self) -> Path
```

Return the core directory path

```python
@property
def settings_root(self) -> Path
```

Return the settings directory path

```python
@property
def config_file(self) -> Path
```

Return the config.json file path

```python
@property
def features_root(self) -> Path
```

Return the features directory path

```python
@property
def calibration_root(self) -> Path
```

Return the calibration directory path

```python
@property
def camera_calibration_root(self) -> Path
```

Return the camera calibration directory path

```python
@property
def storage_path(self) -> Path
```

Return the default storage path

```python
@property
def external_dependencies_root(self) -> Path
```

Return the external dependencies directory path

```python
def ensure_path_exists(self, path: Path) -> Path
```

Ensure the given path exists, create if not

```python
def resolve_relative_path(self, relative_path: str) -> Path
```

Resolve a relative path from project root

```python
def get_user_config_path(self, filename: str='camera_settings.json') -> Path
```

Get path for user configuration file in storage directory

### `get_path_resolver`

```python
def get_path_resolver(base_path: Path | str | None=None) -> PathResolver
```

Get or create the global path resolver instance

### `get_project_root`

```python
def get_project_root() -> Path
```

### `get_config_file_path`

```python
def get_config_file_path() -> Path
```

### `get_storage_path`

```python
def get_storage_path() -> Path
```

### `get_user_config_path`

```python
def get_user_config_path(filename: str='camera_settings.json') -> Path
```
