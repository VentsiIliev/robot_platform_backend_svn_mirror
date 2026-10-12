# Module reference: `src/engine/geometry`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [planar.py](#planarpy)
- [contour_to_dxf.py](#contour_to_dxfpy)
- [rectangle_scale_calibration.py](#rectangle_scale_calibrationpy)

## `contour_to_dxf.py`

Source: [contour_to_dxf.py](../../../src/engine/geometry/contour_to_dxf.py).

```python
def write_contour_dxf(path, contour, mm_per_pixel=None) -> Path
```

Exports a validated image-space contour as a closed DXF polyline. See
[capture and calibration workflow](contour_to_dxf.md).

## `rectangle_scale_calibration.py`

Source: [rectangle_scale_calibration.py](../../../src/engine/geometry/rectangle_scale_calibration.py).

```python
def calibrate_rectangle_scale(measured_size_mm, reference_size_mm) -> RectangleScaleCalibration
```

Fits one scale factor to short/long reference sides. The immutable result
provides measured/reference dimensions, correction, corrected dimensions,
and residuals in mm and percent.

## `planar.py`

Source: [src/engine/geometry/planar.py](../../../src/engine/geometry/planar.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `math`.

### `rotate_xy`

```python
def rotate_xy(x: float, y: float, angle_degrees: float) -> tuple[float, float]
```

### `rotate_xy_about`

```python
def rotate_xy_about(point_xy: tuple[float, float], angle_degrees: float, pivot_xy: tuple[float, float]) -> tuple[float, float]
```

### `unwrap_degrees`

```python
def unwrap_degrees(previous: float, current: float) -> float
```

### `normalize_degrees`

```python
def normalize_degrees(angle: float) -> float
```

### `nearest_axis_equivalent_degrees`

```python
def nearest_axis_equivalent_degrees(reference: float, axis_angle: float) -> float
```

Return the 180-degree-equivalent axis angle nearest to reference.

### `axis_equivalent_shift_degrees`

```python
def axis_equivalent_shift_degrees(reference: float, current: float) -> float
```

Return the constant 180-degree shift that puts current nearest reference.
