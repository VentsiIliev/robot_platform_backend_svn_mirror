# Module reference: `src/engine/vision/implementation/VisionSystem/features/contour_matching/settings`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [ContourMatchingSettings.py](#contourmatchingsettingspy)
- [__init__.py](#__init__py)
- [contour_matching_settings.py](#contour_matching_settingspy)
- [contour_matching_settings_data.py](#contour_matching_settings_datapy)
- [contour_matching_settings_serializer.py](#contour_matching_settings_serializerpy)
- [setting_key.py](#setting_keypy)

## `ContourMatchingSettings.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/ContourMatchingSettings.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/ContourMatchingSettings.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ContourMatchingSettings']
```

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_data`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_serializer`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.setting_key`.

Package-level import/export surface:

```python
from src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_data import ContourMatchingSettingsData
from src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_serializer import ContourMatchingSettingsSerializer
from src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings import ContourMatchingSettings
from src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.setting_key import ContourMatchingSettingKey
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ContourMatchingSettingsData', 'ContourMatchingSettingsSerializer', 'ContourMatchingSettings', 'ContourMatchingSettingKey']
```

## `contour_matching_settings.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/contour_matching_settings.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/contour_matching_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `pathlib`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_data`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_serializer`, `typing`.

### `ContourMatchingSettings`

```python
class ContourMatchingSettings:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, settings_file_path: Optional[Path]=None)
```

```python
def get_similarity_threshold(self) -> float
```

```python
def get_refinement_threshold(self) -> float
```

```python
def get_debug_similarity(self) -> bool
```

```python
def get_debug_calculate_differences(self) -> bool
```

```python
def get_debug_align_contours(self) -> bool
```

```python
def get_use_comparison_model(self) -> bool
```

```python
def set_similarity_threshold(self, value: float) -> None
```

```python
def set_refinement_threshold(self, value: float) -> None
```

```python
def set_debug_similarity(self, value: bool) -> None
```

```python
def set_debug_calculate_differences(self, value: bool) -> None
```

```python
def set_debug_align_contours(self, value: bool) -> None
```

```python
def set_use_comparison_model(self, value: bool) -> None
```

```python
def to_dict(self) -> dict
```

```python
def from_dict(self, data: dict) -> None
```

```python
def save_to_file(self, file_path: Optional[Path]=None) -> None
```

```python
def load_from_file(self, file_path: Optional[Path]=None) -> None
```

```python
def update_settings(self, settings: dict) -> Tuple[bool, str]
```

```python
def updateSettings(self, settings: dict) -> Tuple[bool, str]
```

## `contour_matching_settings_data.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/contour_matching_settings_data.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/contour_matching_settings_data.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`.

### `ContourMatchingSettingsData`

```python
@dataclass
class ContourMatchingSettingsData:
```

Declared fields/defaults:

```python
similarity_threshold: float = 80.0
refinement_threshold: float = 0.1
debug_similarity: bool = False
debug_calculate_differences: bool = False
debug_align_contours: bool = False
use_comparison_model: bool = False
```

## `contour_matching_settings_serializer.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/contour_matching_settings_serializer.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/contour_matching_settings_serializer.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.repositories.interfaces.settings_serializer`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.contour_matching_settings_data`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.settings.setting_key`.

### `ContourMatchingSettingsSerializer`

```python
class ContourMatchingSettingsSerializer(ISettingsSerializer[ContourMatchingSettingsData]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> ContourMatchingSettingsData
```

```python
def to_dict(self, settings: ContourMatchingSettingsData) -> dict
```

```python
def from_dict(self, data: dict) -> ContourMatchingSettingsData
```

## `setting_key.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/setting_key.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/settings/setting_key.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `ContourMatchingSettingKey`

```python
class ContourMatchingSettingKey(Enum):
```

Declared fields/defaults:

```python
SIMILARITY_THRESHOLD = 'SIMILARITY_THRESHOLD'
REFINEMENT_THRESHOLD = 'REFINEMENT_THRESHOLD'
DEBUG_SIMILARITY = 'DEBUG_SIMILARITY'
DEBUG_CALCULATE_DIFFERENCES = 'DEBUG_CALCULATE_DIFFERENCES'
DEBUG_ALIGN_CONTOURS = 'DEBUG_ALIGN_CONTOURS'
USE_COMPARISON_MODEL = 'USE_COMPARISON_MODEL'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def getAsLabel(self) -> str
```
