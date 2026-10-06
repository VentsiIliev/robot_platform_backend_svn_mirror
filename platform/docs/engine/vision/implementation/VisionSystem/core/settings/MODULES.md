# Module reference: `src/engine/vision/implementation/VisionSystem/core/settings`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [BaseSettings.py](#basesettingspy)
- [CameraSettingKey.py](#camerasettingkeypy)
- [CameraSettings.py](#camerasettingspy)
- [__init__.py](#__init__py)
- [settings_manager.py](#settings_managerpy)

## `BaseSettings.py`

Source: [src/engine/vision/implementation/VisionSystem/core/settings/BaseSettings.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/settings/BaseSettings.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`.

### `Settings`

```python
class Settings:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def set_value(self, key, value)
```

Generic method to set a setting value by key.

```python
def get_value(self, key, default=None)
```

Generic method to get a setting value by key. Returns default if key not found.

```python
def remove_value(self, key)
```

Remove a specific setting by key.

```python
def get_all_settings(self)
```

Returns all the settings as a dictionary.

```python
def clear_all_settings(self)
```

Clears all settings.

```python
def save_settings(self, filepath)
```

Save the settings to a file.

```python
def load_settings(self, filepath)
```

Load settings from a file.

```python
def toDict(self)
```

## `CameraSettingKey.py`

Source: [src/engine/vision/implementation/VisionSystem/core/settings/CameraSettingKey.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/settings/CameraSettingKey.py).

Imports (including optional/function-local imports; not a startup dependency list): `enum`.

### `CameraSettingKey`

```python
class CameraSettingKey(Enum):
```

Declared fields/defaults:

```python
INDEX = 'Index'
WIDTH = 'Width'
HEIGHT = 'Height'
SKIP_FRAMES = 'Skip frames'
CAPTURE_POS_OFFSET = 'Capture position offset'
THRESHOLD = 'Threshold'
THRESHOLD_PICKUP_AREA = 'Threshold pickup area'
EPSILON = 'Epsilon'
MIN_CONTOUR_AREA = 'Min contour area'
MAX_CONTOUR_AREA = 'Max contour area'
CONTOUR_DETECTION = 'Contour detection'
DRAW_CONTOURS = 'Draw contours'
GAUSSIAN_BLUR = 'Gaussian blur'
BLUR_KERNEL_SIZE = 'Blur kernel size'
THRESHOLD_TYPE = 'Threshold type'
CONTOUR_SMOOTHING_MODE = 'Contour smoothing mode'
CONTOUR_SMOOTHING_STRENGTH = 'Contour smoothing strength'
DILATE_ENABLED = 'Dilate enabled'
DILATE_KERNEL_SIZE = 'Dilate kernel size'
DILATE_ITERATIONS = 'Dilate iterations'
ERODE_ENABLED = 'Erode enabled'
ERODE_KERNEL_SIZE = 'Erode kernel size'
ERODE_ITERATIONS = 'Erode iterations'
CHESSBOARD_WIDTH = 'Chessboard width'
CHESSBOARD_HEIGHT = 'Chessboard height'
SQUARE_SIZE_MM = 'Square size (mm)'
CALIBRATION_SKIP_FRAMES = 'Calibration skip frames'
HARDWARE_AUTO_EXPOSURE = 'Hardware auto exposure'
BRIGHTNESS_AUTO = 'Enable auto adjust'
BRIGHTNESS_KP = 'Kp'
BRIGHTNESS_KI = 'Ki'
BRIGHTNESS_KD = 'Kd'
TARGET_BRIGHTNESS = 'Target brightness'
BRIGHTNESS_AREA_P1 = 'Brightness area point 1'
BRIGHTNESS_AREA_P2 = 'Brightness area point 2'
BRIGHTNESS_AREA_P3 = 'Brightness area point 3'
BRIGHTNESS_AREA_P4 = 'Brightness area point 4'
ARUCO_ENABLED = 'Enable Aruco detection'
ARUCO_DICTIONARY = 'Dictionary'
ARUCO_FLIP_IMAGE = 'Flip image'
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def getAsLabel(self)
```

## `CameraSettings.py`

Source: [src/engine/vision/implementation/VisionSystem/core/settings/CameraSettings.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/settings/CameraSettings.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.engine.vision.implementation.VisionSystem.core.settings.BaseSettings`, `src.engine.vision.implementation.VisionSystem.core.settings.CameraSettingKey`.

### `CameraSettings`

```python
class CameraSettings(Settings):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, data: dict=None)
```

```python
def updateSettings(self, settings: dict)
```

Updates the camera settings based on the given dictionary. Handles both flat and nested JSON structures. Parameters ---------- settings : dict A dictionary containing the camera settings to be updated. Can be flat (direct key-value pairs) or nested (with sections). Returns ------- tuple (bool, str) - Success status and message

```python
def from_dict(self, data)
```

Load settings from nested JSON structure

```python
def to_dict(self)
```

Convert internal flat structure back to nested JSON format

```python
def set_camera_index(self, index)
```

Set the camera index.

```python
def get_camera_index(self)
```

Get the camera index.

```python
def get_camera_width(self)
```

Get the camera width.

```python
def get_camera_height(self)
```

Get the camera height.

```python
def set_resolution(self, width, height)
```

Set the camera resolution.

```python
def set_width(self, width)
```

Set the camera width.

```python
def set_height(self, height)
```

Set the camera height.

```python
def get_resolution(self)
```

Get the camera resolution.

```python
def get_skip_frames(self)
```

Get the number of frames to skip.

```python
def set_skip_frames(self, skipFrames)
```

Set the number of frames to skip.

```python
def set_capture_pos_offset(self, offset)
```

Set the capture position offset.

```python
def get_capture_pos_offset(self)
```

Get the capture position offset.

```python
def get_threshold(self)
```

Get the threshold value.

```python
def set_threshold(self, threshold)
```

Set the threshold value.

```python
def get_threshold_pickup_area(self)
```

Get the threshold pickup area value.

```python
def set_threshold_pickup_area(self, threshold)
```

```python
def get_epsilon(self)
```

Get the epsilon value.

```python
def set_epsilon(self, epsilon)
```

Set the epsilon value.

```python
def get_min_contour_area(self)
```

```python
def set_min_contour_area(self, minContourArea)
```

```python
def get_max_contour_area(self)
```

Get the maximum contour area.

```python
def set_max_contour_area(self, maxContourArea)
```

```python
def get_contour_detection(self)
```

Get the contour detection status.

```python
def set_contour_detection(self, contourDetection)
```

Set the contour detection status.

```python
def get_draw_contours(self)
```

Get the draw contours status.

```python
def set_draw_contours(self, drawContours)
```

Set the draw contours status.

```python
def get_gaussian_blur(self)
```

Get gaussian blur enabled status.

```python
def set_gaussian_blur(self, enabled)
```

Set gaussian blur enabled status.

```python
def get_blur_kernel_size(self)
```

Get blur kernel size.

```python
def set_blur_kernel_size(self, size)
```

Set blur kernel size.

```python
def get_threshold_type(self)
```

Get threshold type.

```python
def set_threshold_type(self, threshold_type)
```

Set threshold type.

```python
def get_contour_smoothing_mode(self)
```

```python
def set_contour_smoothing_mode(self, mode)
```

```python
def get_contour_smoothing_strength(self)
```

```python
def set_contour_smoothing_strength(self, strength)
```

```python
def get_dilate_enabled(self)
```

Get dilate enabled status.

```python
def set_dilate_enabled(self, enabled)
```

Set dilate enabled status.

```python
def get_dilate_kernel_size(self)
```

Get dilate kernel size.

```python
def set_dilate_kernel_size(self, size)
```

Set dilate kernel size.

```python
def get_dilate_iterations(self)
```

Get dilate iterations.

```python
def set_dilate_iterations(self, iterations)
```

Set dilate iterations.

```python
def get_erode_enabled(self)
```

Get erode enabled status.

```python
def set_erode_enabled(self, enabled)
```

Set erode enabled status.

```python
def get_erode_kernel_size(self)
```

Get erode kernel size.

```python
def set_erode_kernel_size(self, size)
```

Set erode kernel size.

```python
def get_erode_iterations(self)
```

Get erode iterations.

```python
def set_erode_iterations(self, iterations)
```

Set erode iterations.

```python
def get_chessboard_width(self)
```

Get chessboard width.

```python
def set_chessboard_width(self, width)
```

Set chessboard width.

```python
def get_chessboard_height(self)
```

Get chessboard height.

```python
def set_chessboard_height(self, height)
```

Set chessboard height.

```python
def get_square_size_mm(self)
```

Get square size in mm.

```python
def set_square_size_mm(self, size)
```

Set square size in mm.

```python
def get_calibration_skip_frames(self)
```

Get calibration skip frames.

```python
def set_calibration_skip_frames(self, frames)
```

Set calibration skip frames.

```python
def set_chessboard_config(self, width, height, square_size_mm)
```

Set complete chessboard configuration.

```python
def get_chessboard_config(self)
```

Get complete chessboard configuration.

```python
def get_hardware_auto_exposure(self)
```

Get camera-driver automatic exposure status.

```python
def set_hardware_auto_exposure(self, enabled)
```

Set camera-driver automatic exposure status.

```python
def get_brightness_auto(self)
```

Get auto brightness adjustment status.

```python
def set_brightness_auto(self, enabled)
```

Set auto brightness adjustment status.

```python
def get_brightness_kp(self)
```

Get brightness PID Kp value.

```python
def set_brightness_kp(self, kp)
```

Set brightness PID Kp value.

```python
def get_brightness_ki(self)
```

Get brightness PID Ki value.

```python
def set_brightness_ki(self, ki)
```

Set brightness PID Ki value.

```python
def get_brightness_kd(self)
```

Get brightness PID Kd value.

```python
def set_brightness_kd(self, kd)
```

Set brightness PID Kd value.

```python
def get_target_brightness(self)
```

Get target brightness value.

```python
def set_target_brightness(self, brightness)
```

Set target brightness value.

```python
def set_brightness_pid_config(self, kp, ki, kd, target)
```

Set complete brightness PID configuration.

```python
def get_brightness_pid_config(self)
```

Get complete brightness PID configuration.

```python
def get_brightness_area_p1(self)
```

Get brightness area point 1 [x, y].

```python
def set_brightness_area_p1(self, point)
```

Set brightness area point 1 [x, y].

```python
def get_brightness_area_p2(self)
```

Get brightness area point 2 [x, y].

```python
def set_brightness_area_p2(self, point)
```

Set brightness area point 2 [x, y].

```python
def get_brightness_area_p3(self)
```

Get brightness area point 3 [x, y].

```python
def set_brightness_area_p3(self, point)
```

Set brightness area point 3 [x, y].

```python
def get_brightness_area_p4(self)
```

Get brightness area point 4 [x, y].

```python
def set_brightness_area_p4(self, point)
```

Set brightness area point 4 [x, y].

```python
def get_brightness_area_points(self)
```

Get all brightness area points as a list of [x, y] coordinates.

```python
def set_brightness_area_points(self, points)
```

Set all brightness area points from a list of [x, y] coordinates.

```python
def get_aruco_enabled(self)
```

Get ArUco detection enabled status.

```python
def set_aruco_enabled(self, enabled)
```

Set ArUco detection enabled status.

```python
def get_aruco_dictionary(self)
```

Get ArUco dictionary.

```python
def set_aruco_dictionary(self, dictionary)
```

Set ArUco dictionary.

```python
def get_aruco_flip_image(self)
```

Get ArUco flip image status.

```python
def set_aruco_flip_image(self, flip)
```

Set ArUco flip image status.

```python
def set_aruco_config(self, enabled, dictionary, flip_image)
```

Set complete ArUco configuration.

```python
def get_aruco_config(self)
```

Get complete ArUco configuration.

```python
def display_settings(self)
```

Utility method to display all camera settings.

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/core/settings/__init__.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/settings/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `settings_manager.py`

Source: [src/engine/vision/implementation/VisionSystem/core/settings/settings_manager.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/settings/settings_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `logging`, `os`, `src.engine.vision.implementation.VisionSystem.core.settings.CameraSettingKey`, `tempfile`, `typing`.

Module declarations (expressions are shown without evaluating them):

```python
CONFIG_FILE_PATH = os.path.join(os.path.dirname(__file__), 'config.json')
```

### `SettingsManager`

```python
class SettingsManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config_file_path: str | None=None)
```

```python
def loadSettings(self)
```

```python
def saveSettings(self, settings: dict) -> None
```

```python
def updateSettings(self, camera_settings, settings: dict, brightness_controller=None, reinit_camera: Callable[[int, int], None] | None=None) -> tuple[bool, str]
```
