# Module reference: `src/applications/shaft_alignment/settings`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [shaft_alignment_settings.py](#shaft_alignment_settingspy)
- [shaft_alignment_settings_serializer.py](#shaft_alignment_settings_serializerpy)

## `__init__.py`

Source: [src/applications/shaft_alignment/settings/__init__.py](../../../../src/applications/shaft_alignment/settings/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.shaft_alignment.settings.shaft_alignment_settings`, `src.applications.shaft_alignment.settings.shaft_alignment_settings_serializer`.

Package-level import/export surface:

```python
from src.applications.shaft_alignment.settings.shaft_alignment_settings import ShaftAlignmentSettings
from src.applications.shaft_alignment.settings.shaft_alignment_settings_serializer import ShaftAlignmentSettingsSerializer
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ShaftAlignmentSettings', 'ShaftAlignmentSettingsSerializer']
```

## `shaft_alignment_settings.py`

Source: [src/applications/shaft_alignment/settings/shaft_alignment_settings.py](../../../../src/applications/shaft_alignment/settings/shaft_alignment_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`.

### `ShaftAlignmentSettings`

```python
@dataclass(frozen=True)
class ShaftAlignmentSettings:
```

Declared fields/defaults:

```python
marker_id: int = 2
marker_size_mm: float = 11.0
point_of_interest_x_offset_mm: float = 2.12
point_of_interest_y_offset_mm: float = 11.44
minimum_area_px2: float = 0.0
active_work_area: str = 'vertical_shaft_alignment'
raw_mode: bool = False
orientation_strategy: str = 'compare'
orientation_primary_strategy: str = 'corner_edge'
calibration_pose: tuple[float, ...] = (-29.075, 217.269, 200.076, -179.99, 0.0, 0.0)
capture_pose: tuple[float, ...] = (257.75, 215.7, 400.1, -179.2, 0.0, 0.0)
base_region_width_px: int = 100
base_region_height_px: int = 700
tracking_region_padding_px: int = 50
tracking_region_minimum_width_px: int = 160
tracking_region_minimum_height_px: int = 160
tracking_recovery_expansion_px: int = 50
marker_misses_before_region_fallback: int = 10
detections_before_tracking: int = 1
acquisition_misses_before_reset: int = 3
tracking_position_filter_alpha: float = 0.5
tracking_prediction_gain: float = 0.5
tracking_maximum_center_jump_px: float = 100.0
tracking_maximum_area_ratio_change: float = 3.0
stability_required_samples: int = 5
stability_maximum_center_spread_px: float = 5.0
stability_maximum_orientation_spread_deg: float = 3.0
stability_misses_before_reset: int = 3
reference_capture_samples: int = 30
alignment_check_samples: int = 10
misalignment_dx_threshold_mm: float = 1.0
misalignment_dy_threshold_mm: float = 1.0
misalignment_drz_threshold_deg: float = 1.0
misalignment_dw_threshold_mm: float = 0.5
misalignment_dh_threshold_mm: float = 0.5
detection_interval_s: float = 0.1
reference_tcp_x_mm: float | None = None
reference_tcp_y_mm: float | None = None
reference_orientation_deg: float | None = None
reference_marker_width_mm: float | None = None
reference_marker_height_mm: float | None = None
reference_marker_corners_normalized: tuple[tuple[float, float], ...] | None = None
reference_point_of_interest_normalized: tuple[float, float] | None = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def to_dict(self) -> dict
```

```python
@classmethod
def from_dict(cls, data: dict) -> 'ShaftAlignmentSettings'
```

```python
def validate(self) -> None
```

## `shaft_alignment_settings_serializer.py`

Source: [src/applications/shaft_alignment/settings/shaft_alignment_settings_serializer.py](../../../../src/applications/shaft_alignment/settings/shaft_alignment_settings_serializer.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.shaft_alignment.settings.shaft_alignment_settings`, `src.engine.repositories.interfaces.settings_serializer`.

### `ShaftAlignmentSettingsSerializer`

```python
class ShaftAlignmentSettingsSerializer(ISettingsSerializer[ShaftAlignmentSettings]):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@property
def settings_type(self) -> str
```

```python
def get_default(self) -> ShaftAlignmentSettings
```

```python
def to_dict(self, settings: ShaftAlignmentSettings) -> dict
```

```python
def from_dict(self, data: dict) -> ShaftAlignmentSettings
```
