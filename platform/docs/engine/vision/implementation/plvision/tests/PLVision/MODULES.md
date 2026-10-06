# Module reference: `src/engine/vision/implementation/plvision/tests/PLVision`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_Calibration.py](#test_calibrationpy)
- [test_Camera.py](#test_camerapy)
- [test_Contouring.py](#test_contouringpy)
- [test_ImageProcessing.py](#test_imageprocessingpy)
- [test_JsonHandler.py](#test_jsonhandlerpy)

## `__init__.py`

Source: [src/engine/vision/implementation/plvision/tests/PLVision/__init__.py](../../../../../../../src/engine/vision/implementation/plvision/tests/PLVision/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_Calibration.py`

Source: [src/engine/vision/implementation/plvision/tests/PLVision/test_Calibration.py](../../../../../../../src/engine/vision/implementation/plvision/tests/PLVision/test_Calibration.py).

* File: test_Calibration.y_pixels * Author: IlV * Comments: * Revision history: * Date Author Description * ----------------------------------------------------------------- ** 070524 IlV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `PLVision.Calibration`, `cv2`, `numpy`, `os`, `tempfile`, `unittest`.

### `TestCameraCalibrator`

```python
class TestCameraCalibrator(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(self)
```

```python
def setUp(self)
```

Set up the CameraCalibrator object for testing.

```python
def test_calculateObjp(self)
```

Test if the _calculateObjp method returns a numpy array of the correct shape.

```python
def test_findCorners(self)
```

Test if the findCorners method returns the correct types when given a grayscale image.

```python
def test_findCorners_wrong_chessboard_width(self)
```

Test if the findCorners method returns the correct types when given a grayscale image.

```python
def test_findCorners_wrong_chessboard_height(self)
```

Test if the findCorners method returns the correct types when given a grayscale image.

```python
def test_refineCorners(self)
```

Test if the refineCorners method returns a numpy array of the same shape as the input corners.

```python
def test_calculateMeanError(self)
```

Test if the calculateMeanError method returns a float when given valid input parameters.

```python
def test_saveCalibrationData(self)
```

Test if the saveCalibrationData method correctly creates a file in the specified directory.

## `test_Camera.py`

Source: [src/engine/vision/implementation/plvision/tests/PLVision/test_Camera.py](../../../../../../../src/engine/vision/implementation/plvision/tests/PLVision/test_Camera.py).

* File: test_Camera.y_pixels * Author: IlV * Comments: * Revision history: * Date Author Description * ----------------------------------------------------------------- ** 070524 IlV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `PLVision.Camera`, `unittest`.

### `TestCamera`

```python
class TestCamera(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

Set up the Camera object for testing.

```python
def test_init_resolution_1280x720(self)
```

Test if the Camera object is created with the correct resolution when no width and height are given.

```python
def test_setCameraIndex(self)
```

Test if the setCameraIndex method raises a ValueError when given a negative value.

```python
def test_setCameraIndexValidIndex(self)
```

Test if the setCameraIndex method raises a ValueError when given a negative value.

```python
def test_setWidth(self)
```

Test if the setWidth method raises a ValueError when given a negative value.

```python
def test_setHeight(self)
```

Test if the setHeight method raises a ValueError when given a negative value.

```python
def test_capture(self)
```

Test if the capture method works without raising an exception.

```python
def test_captureImage(self)
```

Test if the captureImage method returns an image of the correct size.

```python
def test_stop(self)
```

Test if the stop method works without raising an exception.

## `test_Contouring.py`

Source: [src/engine/vision/implementation/plvision/tests/PLVision/test_Contouring.py](../../../../../../../src/engine/vision/implementation/plvision/tests/PLVision/test_Contouring.py).

Imports (including optional/function-local imports; not a startup dependency list): `PLVision`, `cv2`, `numpy`, `unittest`.

### `TestContouring`

```python
class TestContouring(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_findContours(self)
```

```python
def test_rotateContour(self)
```

```python
def test_rotateContourAndChildren(self)
```

```python
def test_isContourWithinBbox(self)
```

## `test_ImageProcessing.py`

Source: [src/engine/vision/implementation/plvision/tests/PLVision/test_ImageProcessing.py](../../../../../../../src/engine/vision/implementation/plvision/tests/PLVision/test_ImageProcessing.py).

Imports (including optional/function-local imports; not a startup dependency list): `PLVision`, `cv2`, `numpy`, `unittest`.

### `TestImageProcessing`

```python
class TestImageProcessing(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

Set up a dummy image for testing.

```python
def test_applyAffineTransformation(self)
```

Test if the affineTransform function works without raising an exception.

```python
def test_undistortImage(self)
```

Test if the undistortImage function works without raising an exception.

```python
def test_cropImage(self)
```

Test if the cropImage function works without raising an exception.

```python
def test_grayscaleImage(self)
```

Test if the grayscaleImage function works without raising an exception and returns the correct shape.

```python
def test_zoom(self)
```

Test if the zoom function works without raising an exception.

```python
def test_cropImage_cropping(self)
```

Test if the cropImage function correctly crops the image.

```python
def test_cropImage_padding(self)
```

Test if the cropImage function correctly pads the image after cropping.

```python
def test_cropImage_negative_left_crop(self)
```

Test if the cropImage function correctly handles negative cropping values.

```python
def test_cropImage_negative_right_crop(self)
```

Test if the cropImage function correctly handles negative cropping values.

```python
def test_cropImage_negative_top_crop(self)
```

Test if the cropImage function correctly handles negative cropping values.

```python
def test_cropImage_negative_bottom_crop(self)
```

Test if the cropImage function correctly handles negative cropping values.

```python
def test_cropImage_all_negative(self)
```

Test if the cropImage function correctly handles negative cropping values.

```python
def test_zoom_zoomIn(self)
```

Test if the zoom function correctly zooms in the image.

```python
def test_zoom_zoomOut(self)
```

Test if the zoom function correctly zooms out the image.

## `test_JsonHandler.py`

Source: [src/engine/vision/implementation/plvision/tests/PLVision/test_JsonHandler.py](../../../../../../../src/engine/vision/implementation/plvision/tests/PLVision/test_JsonHandler.py).

* File: test_JsonHandler.y_pixels * Author: IlV * Comments: * Revision history: * Date Author Description * ----------------------------------------------------------------- ** 130524 IlV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `PLVision.JsonHandler`, `json`, `os`, `unittest`.

### `TestJsonHandler`

```python
class TestJsonHandler(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_read_json(self)
```

```python
def test_read_json_missing_file(self)
```

```python
def test_write_json(self)
```

```python
def test_write_json_creates_file(self)
```

```python
def test_update_json(self)
```

```python
def test_update_json_missing_file(self)
```
