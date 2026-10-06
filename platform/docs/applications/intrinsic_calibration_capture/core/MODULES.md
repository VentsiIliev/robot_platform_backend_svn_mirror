# Module reference: `src/applications/intrinsic_calibration_capture/core`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [acquisition.py](#acquisitionpy)
- [data.py](#datapy)
- [vision_helpers.py](#vision_helperspy)

## `__init__.py`

Source: [src/applications/intrinsic_calibration_capture/core/__init__.py](../../../../src/applications/intrinsic_calibration_capture/core/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `acquisition.py`

Source: [src/applications/intrinsic_calibration_capture/core/acquisition.py](../../../../src/applications/intrinsic_calibration_capture/core/acquisition.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.intrinsic_capture.runner`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['capture_charuco_sweep_dataset', 'capture_intrinsic_dataset', 'estimate_local_xy_jacobian', 'move_board_center_near_region']
```

## `data.py`

Source: [src/applications/intrinsic_calibration_capture/core/data.py](../../../../src/applications/intrinsic_calibration_capture/core/data.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.intrinsic_capture.types`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['BoardDetection', 'BoardType', 'CaptureSample', 'FeasibleRegion', 'ImageInfo', 'LocalJacobian2D', 'TargetRegion', 'TiltAxis']
```

## `vision_helpers.py`

Source: [src/applications/intrinsic_calibration_capture/core/vision_helpers.py](../../../../src/applications/intrinsic_calibration_capture/core/vision_helpers.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.calibration.intrinsic_capture.vision_helpers`.

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['compute_feasible_region', 'detect_board', 'detect_charuco_board', 'detect_chessboard', 'make_grid_regions']
```
