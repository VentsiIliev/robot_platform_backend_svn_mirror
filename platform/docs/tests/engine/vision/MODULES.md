# Module reference: `tests/engine/vision`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_brightness_service.py](#test_brightness_servicepy)
- [test_calibration_vision_settings.py](#test_calibration_vision_settingspy)
- [test_camera_device_settings.py](#test_camera_device_settingspy)
- [test_camera_initialization.py](#test_camera_initializationpy)
- [test_camera_stream_publisher.py](#test_camera_stream_publisherpy)
- [test_capture_snapshot_service.py](#test_capture_snapshot_servicepy)
- [test_contour_matcher_alignment.py](#test_contour_matcher_alignmentpy)
- [test_frame_orientation.py](#test_frame_orientationpy)
- [test_geometric_matching_strategy.py](#test_geometric_matching_strategypy)
- [test_homography_transformer.py](#test_homography_transformerpy)
- [test_vision_service.py](#test_vision_servicepy)
- [test_vision_service_matching.py](#test_vision_service_matchingpy)
- [test_vision_system_stale_frame.py](#test_vision_system_stale_framepy)

## `__init__.py`

Source: [tests/engine/vision/__init__.py](../../../../tests/engine/vision/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_brightness_service.py`

Source: [tests/engine/vision/test_brightness_service.py](../../../../tests/engine/vision/test_brightness_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.vision.implementation.VisionSystem.services.brightness_service`, `unittest`.

### `_CameraSettings`

```python
class _CameraSettings:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def get_brightness_kp()
```

```python
@staticmethod
def get_brightness_ki()
```

```python
@staticmethod
def get_brightness_kd()
```

```python
@staticmethod
def get_target_brightness()
```

```python
@staticmethod
def get_brightness_area_points()
```

### `TestBrightnessService`

```python
class TestBrightnessService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_restores_last_adjustment_when_returning_to_work_area(self)
```

```python
def test_first_visit_to_new_area_starts_from_current_adjustment(self)
```

## `test_calibration_vision_settings.py`

Source: [tests/engine/vision/test_calibration_vision_settings.py](../../../../tests/engine/vision/test_calibration_vision_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.calibration_vision_settings`, `unittest`.

### `TestCalibrationVisionSettings`

```python
class TestCalibrationVisionSettings(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_legacy_data_defaults_to_global_mode(self)
```

```python
def test_profiles_and_explicit_area_assignments_round_trip(self)
```

```python
def test_invalid_mode_falls_back_to_global(self)
```

## `test_camera_device_settings.py`

Source: [tests/engine/vision/test_camera_device_settings.py](../../../../tests/engine/vision/test_camera_device_settings.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.camera_device_settings`, `unittest`.

### `TestCameraDevicesConfigSerializer`

```python
class TestCameraDevicesConfigSerializer(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self) -> None
```

```python
def test_round_trip_preserves_path_and_index_devices(self) -> None
```

```python
def test_missing_orientation_flags_use_identity_defaults(self) -> None
```

```python
def test_rotation_is_folded_to_a_canonical_value(self) -> None
```

```python
def test_rejects_rotation_that_is_not_a_multiple_of_ninety(self) -> None
```

```python
def test_rejects_non_integer_rotation(self) -> None
```

```python
def test_rejects_non_boolean_flip(self) -> None
```

```python
def test_rejects_empty_device_path(self) -> None
```

```python
def test_rejects_metadata_free_invalid_device_type(self) -> None
```

## `test_camera_initialization.py`

Source: [tests/engine/vision/test_camera_initialization.py](../../../../tests/engine/vision/test_camera_initialization.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.camera_initialization`, `unittest`, `unittest.mock`.

### `TestCameraInitializer`

```python
class TestCameraInitializer(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.engine.vision.implementation.VisionSystem.camera_initialization.Camera')
def test_passes_device_path_to_camera_backend(self, camera_cls) -> None
```

```python
@patch('src.engine.vision.implementation.VisionSystem.camera_initialization.Camera')
def test_strict_device_failure_does_not_scan_for_another_camera(self, camera_cls) -> None
```

### `TestVisionSystemConfiguredCamera`

```python
class TestVisionSystemConfiguredCamera(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.engine.vision.implementation.VisionSystem.VisionSystem.CameraInitializer')
def test_setup_uses_configured_device_and_resolution_strictly(self, initializer_cls) -> None
```

## `test_camera_stream_publisher.py`

Source: [tests/engine/vision/test_camera_stream_publisher.py](../../../../tests/engine/vision/test_camera_stream_publisher.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `src.engine.vision.camera_stream_publisher`, `src.engine.vision.implementation.VisionSystem.core.external_communication.system_state_management`, `src.shared_contracts.events.vision_events`, `threading`, `time`, `unittest`, `unittest.mock`.

### `CameraStreamPublisherTests`

```python
class CameraStreamPublisherTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@patch('src.engine.vision.camera_stream_publisher.cv2.VideoCapture')
def test_stop_cancels_retry_wait(self, video_capture) -> None
```

```python
@patch('src.engine.vision.camera_stream_publisher.cv2.VideoCapture')
def test_retries_initially_missing_camera_until_it_appears(self, video_capture) -> None
```

```python
@patch('src.engine.vision.camera_stream_publisher.cv2.VideoCapture')
def test_reopens_after_lost_frames(self, video_capture) -> None
```

```python
@patch('src.engine.vision.camera_stream_publisher.cv2.VideoCapture')
def test_live_flip_update_changes_published_auxiliary_frames(self, video_capture) -> None
```

```python
@patch('src.engine.vision.camera_stream_publisher.cv2.VideoCapture')
def test_live_rotation_update_changes_published_auxiliary_frames(self, video_capture) -> None
```

```python
def test_primary_vision_publishes_named_camera_topic(self) -> None
```

```python
@patch('src.engine.vision.camera_stream_publisher.cv2.VideoCapture')
def test_opens_once_and_publishes_named_camera_frames(self, video_capture) -> None
```

## `test_capture_snapshot_service.py`

Source: [tests/engine/vision/test_capture_snapshot_service.py](../../../../tests/engine/vision/test_capture_snapshot_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.capture_snapshot_service`, `src.engine.vision.i_vision_service`, `unittest`, `unittest.mock`.

### `TestCaptureSnapshotService`

```python
class TestCaptureSnapshotService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_capture_snapshot_collects_frame_contours_and_robot_pose(self)
```

```python
def test_capture_snapshot_records_the_validated_work_area(self)
```

```python
def test_capture_snapshot_without_services_returns_empty_snapshot(self)
```

```python
def test_capture_snapshot_tolerates_vision_failures(self)
```

```python
def test_capture_snapshot_blocks_stale_vision_frames_without_fallback(self)
```

```python
def test_capture_snapshot_tolerates_robot_pose_failure(self)
```

```python
def test_capture_snapshot_blocks_when_active_work_area_unknown(self)
```

```python
def test_capture_snapshot_blocks_when_active_work_area_validator_fails(self)
```

```python
def test_capture_snapshot_blocks_when_active_work_area_not_verified(self)
```

```python
def test_capture_snapshot_rejects_area_change_during_vision_processing(self)
```

## `test_contour_matcher_alignment.py`

Source: [tests/engine/vision/test_contour_matcher_alignment.py](../../../../tests/engine/vision/test_contour_matcher_alignment.py).

Imports (including optional/function-local imports; not a startup dependency list): `contextlib`, `cv2`, `io`, `numpy`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.contour_matcher`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.utils`, `unittest`.

### `_Workpiece`

```python
class _Workpiece:
```

Declared fields/defaults:

```python
workpieceId = 'saved'
sprayPattern = {'Contour': [], 'Fill': []}
pickupPoint = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, points)
```

```python
def get_main_contour(self)
```

```python
def get_spray_pattern_contours(self)
```

```python
def get_spray_pattern_fills(self)
```

### `TestContourMatcherAlignment`

```python
class TestContourMatcherAlignment(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_accepts_rigidly_aligned_workpiece(self)
```

```python
def test_rejects_same_silhouette_when_rigid_alignment_cannot_fit(self)
```

```python
def test_keeps_results_aligned_when_one_of_two_contours_is_rejected(self)
```

```python
def test_half_turn_aligns_asymmetric_contour(self)
```

```python
def test_aligns_reflected_contour_and_associated_geometry(self)
```

## `test_frame_orientation.py`

Source: [tests/engine/vision/test_frame_orientation.py](../../../../tests/engine/vision/test_frame_orientation.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`, `src.engine.vision.frame_orientation`, `unittest`.

### `TestNormalizeRotation`

```python
class TestNormalizeRotation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_folds_arbitrary_multiples_of_ninety(self) -> None
```

```python
def test_rejects_values_that_are_not_multiples_of_ninety(self) -> None
```

```python
def test_rejects_bool_and_non_integer(self) -> None
```

```python
def test_only_quarter_turns_transpose(self) -> None
```

### `TestApplyOrientation`

```python
class TestApplyOrientation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self) -> None
```

```python
def test_identity_returns_the_input_untouched(self) -> None
```

```python
def test_ninety_degrees_rotates_clockwise(self) -> None
```

```python
def test_two_hundred_seventy_degrees_rotates_counter_clockwise(self) -> None
```

```python
def test_rotation_is_applied_before_the_mirror(self) -> None
```

```python
def test_rotation_transposes_the_frame_shape(self) -> None
```

## `test_geometric_matching_strategy.py`

Source: [tests/engine/vision/test_geometric_matching_strategy.py](../../../../tests/engine/vision/test_geometric_matching_strategy.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.strategies.geometric_matching_strategy`, `unittest`.

### `_Workpiece`

```python
class _Workpiece:
```

Declared fields/defaults:

```python
workpieceId = 'saved'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, contour)
```

```python
def get_main_contour(self)
```

### `TestGeometricMatchingStrategy`

```python
class TestGeometricMatchingStrategy(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_accepts_translated_shape_at_same_camera_scale(self)
```

```python
def test_accepts_rotated_shape_with_uneven_point_spacing(self)
```

```python
def test_rejects_different_silhouette_at_similar_area(self)
```

```python
def test_rejects_shape_with_much_smaller_pixel_area(self)
```

```python
def test_accepts_small_camera_scale_variation(self)
```

```python
def test_rejects_scale_change_that_rigid_alignment_cannot_correct(self)
```

```python
def test_rejects_rounded_square_as_four_corner_square(self)
```

```python
def test_matches_mirror_and_reports_reflection(self)
```

```python
def test_accepts_half_turn_of_asymmetric_workpiece(self)
```

## `test_homography_transformer.py`

Source: [tests/engine/vision/test_homography_transformer.py](../../../../tests/engine/vision/test_homography_transformer.py).

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `pathlib`, `src.engine.vision.homography_transformer`, `tempfile`, `unittest`.

### `TestHomographyTransformer`

```python
class TestHomographyTransformer(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_inverse_transform_round_trips_point(self)
```

## `test_vision_service.py`

Source: [tests/engine/vision/test_vision_service.py](../../../../tests/engine/vision/test_vision_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`, `numpy`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.vision_service`, `sys`, `types`, `unittest`, `unittest.mock`.

### `_ServiceState`

```python
class _ServiceState(Enum):
```

Declared fields/defaults:

```python
IDLE = 'idle'
STARTED = 'started'
ERROR = 'error'
```

### `_make_camera_settings`

```python
def _make_camera_settings()
```

### `_make_vision_system`

```python
def _make_vision_system()
```

### `TestVisionServiceLifecycle`

```python
class TestVisionServiceLifecycle(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_start_starts_system_and_sets_running(self)
```

```python
def test_stop_stops_system_and_clears_running(self)
```

### `TestVisionServiceHealth`

```python
class TestVisionServiceHealth(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_not_healthy_when_not_running(self)
```

```python
def test_running_without_state_manager_uses_running_camera_and_fresh_frame(self)
```

```python
def test_running_without_fresh_frame_is_unhealthy(self)
```

```python
def test_intentionally_paused_processing_remains_healthy_without_fresh_frame(self)
```

```python
def test_pause_does_not_mask_a_closed_camera(self)
```

```python
def test_running_without_open_camera_is_unhealthy(self)
```

```python
def test_running_with_started_state_is_healthy(self)
```

```python
def test_running_with_error_state_is_unhealthy(self)
```

### `TestVisionServiceFramesAndContours`

```python
class TestVisionServiceFramesAndContours(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_latest_frame_prefers_corrected_frame(self)
```

```python
def test_get_latest_frame_falls_back_to_raw_frame(self)
```

```python
def test_get_latest_contours_returns_copy(self)
```

### `TestVisionSystemRun`

```python
class TestVisionSystemRun(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_configure_hardware_auto_exposure_uses_persisted_setting(self)
```

```python
def test_run_publishes_corrected_frame_when_contour_detection_is_off(self)
```

### `TestVisionServiceDelegation`

```python
class TestVisionServiceDelegation(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_save_work_area_converts_points_to_float32_array(self)
```

```python
def test_set_auto_exposure_updates_only_camera_hardware(self)
```

```python
def test_set_auto_exposure_without_camera_support_does_not_change_brightness(self)
```

```python
def test_set_active_work_area_publishes_region_even_on_invalid_area(self)
```

```python
def test_set_active_work_area_with_none_clears_threshold_region(self)
```

```python
def test_run_matching_returns_result_counts_and_unwrapped_contours(self)
```

## `test_vision_service_matching.py`

Source: [tests/engine/vision/test_vision_service_matching.py](../../../../tests/engine/vision/test_vision_service_matching.py).

Imports (including optional/function-local imports; not a startup dependency list): `contextlib`, `numpy`, `src.engine.vision.vision_service`, `sys`, `types`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service() -> VisionService
```

### `_wrapped`

```python
def _wrapped(value)
```

### `_patched_matcher`

```python
def _patched_matcher(return_value)
```

### `TestVisionServiceRunMatching`

```python
class TestVisionServiceRunMatching(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_four_tuple_with_expected_types(self)
```

```python
def test_empty_inputs_return_empty_result_shape(self)
```

```python
def test_all_unmatched_contours_increase_no_match_count(self)
```

```python
def test_matched_and_unmatched_are_unwrapped_from_contour_objects(self)
```

```python
def test_passes_workpieces_and_contours_to_matcher(self)
```

## `test_vision_system_stale_frame.py`

Source: [tests/engine/vision/test_vision_system_stale_frame.py](../../../../tests/engine/vision/test_vision_system_stale_frame.py).

Imports (including optional/function-local imports; not a startup dependency list): `collections`, `numpy`, `src.engine.vision.i_vision_service`, `src.engine.vision.implementation.VisionSystem.VisionSystem`, `src.engine.vision.implementation.VisionSystem.core.camera.frame_grabber`, `time`, `types`, `unittest`, `unittest.mock`.

### `TestVisionSystemStaleFrame`

```python
class TestVisionSystemStaleFrame(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_rotated_frame_dimensions_are_used_for_new_work_areas_and_rois(self)
```

```python
def test_frame_grabber_applies_updated_horizontal_flip_to_next_frame(self)
```

```python
def test_frame_grabber_applies_updated_rotation_to_next_frame(self)
```

```python
def test_frame_grabber_reports_transposition_for_quarter_turns(self)
```

```python
def test_frame_grabber_rejects_unsupported_rotation(self)
```

```python
def test_frame_grabber_pause_clears_frames_and_resume_keeps_camera_open(self)
```

```python
def test_compute_contours_for_latest_frame_blocks_when_no_fresh_snapshot(self)
```

```python
def test_compute_contours_recomputes_when_active_area_changes_on_same_frame_sequence(self)
```
