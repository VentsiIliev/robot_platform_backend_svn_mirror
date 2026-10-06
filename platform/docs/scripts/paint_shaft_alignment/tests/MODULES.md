# Module reference: `scripts/paint_shaft_alignment/tests`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_alignment_reference.py](#test_alignment_referencepy)
- [test_coordinate_mapper.py](#test_coordinate_mapperpy)
- [test_detector.py](#test_detectorpy)
- [test_orientation.py](#test_orientationpy)
- [test_stabilizer.py](#test_stabilizerpy)

## `__init__.py`

Source: [scripts/paint_shaft_alignment/tests/__init__.py](../../../../scripts/paint_shaft_alignment/tests/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_alignment_reference.py`

Source: [scripts/paint_shaft_alignment/tests/test_alignment_reference.py](../../../../scripts/paint_shaft_alignment/tests/test_alignment_reference.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `scripts.paint_shaft_alignment.alignment_reference`, `unittest`.

### `AlignmentReferenceCaptureTests`

```python
class AlignmentReferenceCaptureTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_restores_a_persisted_reference_without_capturing(self)
```

```python
def test_thresholds_report_each_exceeded_absolute_limit(self)
```

```python
def test_collects_required_samples_and_reports_signed_misalignment(self)
```

```python
def test_start_replaces_previous_reference(self)
```

```python
def test_start_can_change_sample_count_for_next_capture(self)
```

## `test_coordinate_mapper.py`

Source: [scripts/paint_shaft_alignment/tests/test_coordinate_mapper.py](../../../../scripts/paint_shaft_alignment/tests/test_coordinate_mapper.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `scripts.paint_shaft_alignment.coordinate_mapper`, `scripts.paint_shaft_alignment.models`, `unittest`.

### `_FakeTransformer`

```python
class _FakeTransformer:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, available=True, error=None)
```

```python
def is_available(self)
```

```python
def transform(self, x, y)
```

### `_FakeTcpTransformer`

```python
class _FakeTcpTransformer:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def is_available(self)
```

```python
def transform_to_tcp(self, x, y)
```

### `MarkerCenterRobotMapperTests`

```python
class MarkerCenterRobotMapperTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_compensates_transform_for_capture_pose_translation(self)
```

```python
def test_updates_capture_pose_and_applies_rz_rotation(self)
```

```python
def test_unavailable_until_dynamic_capture_pose_is_set(self)
```

```python
def test_measures_marker_edges_after_transforming_all_corners(self)
```

```python
def test_tcp_adapter_uses_camera_to_tcp_conversion(self)
```

```python
def test_maps_detected_center_through_paint_transformer(self)
```

```python
def test_does_not_map_when_marker_is_missing(self)
```

```python
def test_reports_unavailable_calibration(self)
```

## `test_detector.py`

Source: [scripts/paint_shaft_alignment/tests/test_detector.py](../../../../scripts/paint_shaft_alignment/tests/test_detector.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `numpy`, `scripts.paint_shaft_alignment.detector`, `scripts.paint_shaft_alignment.models`, `scripts.paint_shaft_alignment.region`, `scripts.paint_shaft_alignment.tracker`, `unittest`.

### `_FakeVision`

```python
class _FakeVision:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, *, frame=None, corners=None, ids=None, error=None)
```

```python
def get_latest_frame(self)
```

```python
def detect_aruco_markers(self, image)
```

### `SelectableDetectionRegionProviderTests`

```python
class SelectableDetectionRegionProviderTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self) -> None
```

```python
def test_uses_centered_default_until_region_is_drawn(self) -> None
```

```python
def test_normalizes_reverse_drag_and_clips_to_frame(self) -> None
```

```python
def test_ignores_zero_area_selection_and_can_restore_default(self) -> None
```

### `ShaftMarkerDetectorTests`

```python
class ShaftMarkerDetectorTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self) -> None
```

```python
def test_reports_target_marker_geometry(self) -> None
```

```python
def test_selects_target_from_multiple_markers(self) -> None
```

```python
def test_rejects_marker_below_minimum_area(self) -> None
```

```python
def test_reports_missing_frame(self) -> None
```

```python
def test_reports_missing_target_and_visible_ids(self) -> None
```

```python
def test_rejects_duplicate_target_id(self) -> None
```

```python
def test_converts_detector_exception_to_failure(self) -> None
```

```python
def test_centered_region_crops_detection_and_restores_full_frame_coordinates(self) -> None
```

```python
def test_reports_clockwise_image_orientation(self) -> None
```

```python
def test_tracker_uses_detection_to_create_next_region(self) -> None
```

```python
def test_tracker_expands_then_falls_back_after_consecutive_misses(self) -> None
```

```python
def test_tracking_region_can_follow_marker_outside_narrow_base_region(self) -> None
```

```python
def test_acquisition_allows_short_gaps_between_confirming_detections(self) -> None
```

## `test_orientation.py`

Source: [scripts/paint_shaft_alignment/tests/test_orientation.py](../../../../scripts/paint_shaft_alignment/tests/test_orientation.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `cv2`, `numpy`, `scripts.paint_shaft_alignment.orientation`, `unittest`.

### `MarkerOrientationStrategyTests`

```python
class MarkerOrientationStrategyTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_corner_edge_averages_all_edges_to_reduce_single_corner_noise(self)
```

```python
def test_corner_edge_strategy_preserves_current_convention(self)
```

```python
def test_solve_pnp_recovers_camera_frame_yaw(self)
```

```python
def test_comparison_uses_same_corners_and_selected_primary(self)
```

## `test_stabilizer.py`

Source: [scripts/paint_shaft_alignment/tests/test_stabilizer.py](../../../../scripts/paint_shaft_alignment/tests/test_stabilizer.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `scripts.paint_shaft_alignment.models`, `scripts.paint_shaft_alignment.stabilizer`, `unittest`.

### `_marker`

```python
def _marker(x: float, y: float, orientation: float) -> DetectedMarker
```

### `MarkerSampleStabilizerTests`

```python
class MarkerSampleStabilizerTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_requires_window_and_reports_median_center(self)
```

```python
def test_rejects_large_position_spread(self)
```

```python
def test_circular_orientation_mean_handles_wrap(self)
```

```python
def test_consecutive_misses_clear_samples(self)
```
