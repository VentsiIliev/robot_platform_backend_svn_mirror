# Module reference: `src/engine/robot/path_preparation/pixel_to_mm`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [context.py](#contextpy)
- [geometry_ppm_anchor_strategy.py](#geometry_ppm_anchor_strategypy)
- [homography_only_preview_strategy.py](#homography_only_preview_strategypy)
- [homography_residual_strategy.py](#homography_residual_strategypy)

## `__init__.py`

Source: [src/engine/robot/path_preparation/pixel_to_mm/__init__.py](../../../../../src/engine/robot/path_preparation/pixel_to_mm/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.path_preparation.pixel_to_mm.context`, `src.engine.robot.path_preparation.pixel_to_mm.geometry_ppm_anchor_strategy`, `src.engine.robot.path_preparation.pixel_to_mm.homography_only_preview_strategy`, `src.engine.robot.path_preparation.pixel_to_mm.homography_residual_strategy`.

Package-level import/export surface:

```python
from src.engine.robot.path_preparation.pixel_to_mm.context import GeometryScaleCache, PixelToMmContext
from src.engine.robot.path_preparation.pixel_to_mm.geometry_ppm_anchor_strategy import GeometryPpmAnchorStrategy
from src.engine.robot.path_preparation.pixel_to_mm.homography_residual_strategy import HomographyResidualStrategy
from src.engine.robot.path_preparation.pixel_to_mm.homography_only_preview_strategy import HomographyOnlyPreviewStrategy
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['GeometryScaleCache', 'GeometryPpmAnchorStrategy', 'HomographyOnlyPreviewStrategy', 'HomographyResidualStrategy', 'PixelToMmContext']
```

## `context.py`

Source: [src/engine/robot/path_preparation/pixel_to_mm/context.py](../../../../../src/engine/robot/path_preparation/pixel_to_mm/context.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `dataclasses`, `logging`.

### `GeometryScaleCache`

```python
@dataclass
class GeometryScaleCache:
```

Mutable cache for calibration geometry scale artifacts.

Declared fields/defaults:

```python
entry: tuple[str, float] | None = None
```

### `PixelToMmContext`

```python
@dataclass(frozen=True)
class PixelToMmContext:
```

Shared inputs for pixel-to-mm conversion strategies.

Declared fields/defaults:

```python
base_z: float
rz_offset: float
rx: float
ry: float
target_point_name: str
calibration_frame_name: str
mode_name: str
logger: Logger
geometry_scale_cache: GeometryScaleCache
```

## `geometry_ppm_anchor_strategy.py`

Source: [src/engine/robot/path_preparation/pixel_to_mm/geometry_ppm_anchor_strategy.py](../../../../../src/engine/robot/path_preparation/pixel_to_mm/geometry_ppm_anchor_strategy.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `json`, `numpy`, `src.engine.robot.calibration.robot_calibration.calibration_report`, `src.engine.robot.path_preparation.pixel_to_mm.context`, `src.engine.robot.targeting`.

### `GeometryPpmAnchorStrategy`

```python
class GeometryPpmAnchorStrategy:
```

Convert pixels using one resolver anchor plus geometry PPM offsets.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def convert(self, compensated_pts_px: np.ndarray, *, resolver, context: PixelToMmContext) -> tuple[list, list[tuple[float, float]]] | None
```

## `homography_only_preview_strategy.py`

Source: [src/engine/robot/path_preparation/pixel_to_mm/homography_only_preview_strategy.py](../../../../../src/engine/robot/path_preparation/pixel_to_mm/homography_only_preview_strategy.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `logging`, `numpy`, `src.engine.robot.path_preparation`, `typing`.

### `HomographyOnlyPreviewStrategy`

```python
class HomographyOnlyPreviewStrategy:
```

Build a homography-only path for pixel-to-mm debug comparisons.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def convert(self, pts_px: np.ndarray, settings: dict, *, segment_config, z_min: float, base_position: list[float] | None, transformer, resolver, pixel_height_compensation_fn: Callable[[float], tuple[float, float]] | None, logger: Logger) -> list
```

### `_safe_float`

```python
def _safe_float(value, default: float) -> float
```

### `_base_orientation_xy`

```python
def _base_orientation_xy(base_position: list[float] | None) -> tuple[float, float]
```

## `homography_residual_strategy.py`

Source: [src/engine/robot/path_preparation/pixel_to_mm/homography_residual_strategy.py](../../../../../src/engine/robot/path_preparation/pixel_to_mm/homography_residual_strategy.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `numpy`, `src.engine.robot.path_preparation.pixel_to_mm.context`, `src.engine.robot.targeting`.

### `HomographyResidualStrategy`

```python
class HomographyResidualStrategy:
```

Resolve every pixel point through the calibrated resolver model.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def convert(self, compensated_pts_px: np.ndarray, *, resolver, context: PixelToMmContext) -> tuple[list, list[tuple[float, float]]]
```
