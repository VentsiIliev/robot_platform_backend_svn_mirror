# Module reference: `tests/engine/robot/path_preparation`

[Package guide](README.md) · [Complete source index](../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_default_workpiece_path_preparation_service.py](#test_default_workpiece_path_preparation_servicepy)

## `test_default_workpiece_path_preparation_service.py`

Source: [tests/engine/robot/path_preparation/test_default_workpiece_path_preparation_service.py](../../../../../tests/engine/robot/path_preparation/test_default_workpiece_path_preparation_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.robot.path_preparation.default_workpiece_path_preparation_service`, `src.engine.robot.path_preparation.geometry`, `types`, `unittest`, `unittest.mock`.

### `_Schema`

```python
class _Schema:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def get_defaults()
```

### `_SegmentConfig`

```python
class _SegmentConfig:
```

Declared fields/defaults:

```python
schema = _Schema()
```

### `TestSavedPaintSelectionContourCut`

```python
class TestSavedPaintSelectionContourCut(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_moves_cut_to_first_point_of_segment_crossing_canonical_seam(self)
```

```python
def test_moves_cut_to_first_point_of_non_wrapping_selection_without_reversing(self)
```

### `_make_service`

```python
def _make_service(**kwargs)
```

### `TestDefaultWorkpiecePathPreparationService`

```python
class TestDefaultWorkpiecePathPreparationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_submit_debug_plot_allows_plot_function_label_keyword(self)
```

```python
def test_build_execution_plan_paint_job_includes_pickup_and_target_metadata(self)
```

```python
def test_transform_to_robot_uses_dynamic_calibration_frame_name_getter(self)
```

```python
def test_build_execution_plan_resolves_pickup_xy_with_normalized_axis_rz(self)
```

```python
def test_build_execution_plan_applies_pickup_axis_alignment_sign_before_resolving_xy(self)
```

```python
def test_build_execution_plan_uses_transformed_path_when_no_contour_processor_is_configured(self)
```

```python
def test_build_execution_plan_uses_injected_contour_processor_output(self)
```

```python
def test_build_execution_plan_paint_job_prefers_segment_offset_over_workpiece_offset(self)
```

```python
def test_build_execution_plan_workpiece_layer_uses_min_rect_pickup_rz(self)
```

```python
def test_workpiece_layer_with_saved_selection_uses_directed_segment_pickup_rz(self)
```

```python
def test_build_execution_plan_accepts_nested_workpiece_contour_payload(self)
```

```python
def test_build_execution_plan_accepts_numpy_nested_workpiece_contour_payload(self)
```

```python
def test_pickup_target_defaults_to_execution_target_when_not_configured(self)
```

```python
def test_transform_single_pixel_to_robot_uses_transformer_when_no_resolver(self)
```

```python
def test_transform_single_pixel_to_robot_uses_live_transformer_getter(self)
```

```python
def test_transform_single_pixel_to_robot_uses_resolver_and_compensation(self)
```

```python
def test_transform_single_pixel_to_robot_uses_live_resolver_getter(self)
```

```python
def test_transform_single_pixel_to_robot_falls_back_to_raw_pixels_without_transformer(self)
```

```python
def test_transform_to_robot_path_tangent_uses_compensation_and_computed_rz(self)
```

```python
def test_transform_to_robot_with_resolver_uses_seeded_z_values(self)
```

```python
def test_transform_to_robot_homography_residual_mode_skips_geometry_ppm(self)
```

```python
def test_parse_pickup_point_accepts_string_sequence_and_mapping(self)
```

```python
def test_parse_pickup_point_rejects_invalid_shapes(self)
```

```python
def test_extract_pickup_pixel_prefers_explicit_pickup_point(self)
```

```python
def test_extract_pickup_pixel_falls_back_to_contour_centroid(self)
```

```python
def test_extract_pickup_pixel_accepts_nested_contour_payload(self)
```

```python
def test_extract_pickup_pixel_falls_back_to_mean_when_contour_area_is_zero(self)
```

```python
def test_extract_pickup_pixel_returns_none_without_pickup_point_or_contour(self)
```

```python
def test_stable_paint_segment_pickup_rz_prefers_straight_low_rotation_segment(self)
```

```python
def test_initial_paint_segment_pickup_rz_uses_first_directed_run(self)
```

```python
def test_initial_paint_segment_pickup_rz_preserves_reverse_direction(self)
```

```python
def test_min_rect_long_axis_pickup_rz_ignores_contour_direction(self)
```

```python
def test_min_rect_long_axis_pickup_rz_uses_long_side(self)
```
