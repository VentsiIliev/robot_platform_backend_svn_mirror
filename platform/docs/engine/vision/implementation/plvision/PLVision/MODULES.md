# Module reference: `src/engine/vision/implementation/plvision/PLVision`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [Aruco.py](#arucopy)
- [CNC.py](#cncpy)
- [Calibration.py](#calibrationpy)
- [Camera.py](#camerapy)
- [Contouring.py](#contouringpy)
- [Example.py](#examplepy)
- [FileSelector.py](#fileselectorpy)
- [HandTrackingModule.py](#handtrackingmodulepy)
- [ImageProcessing.py](#imageprocessingpy)
- [JsonHandler.py](#jsonhandlerpy)
- [__init__.py](#__init__py)
- [arucoModule.py](#arucomodulepy)

## `Aruco.py`

Source: [src/engine/vision/implementation/plvision/PLVision/Aruco.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/Aruco.py).

* File: arucoModule.y_pixels * Author: IlV * Comments: * Revision history: * Date Author Description * ----------------------------------------------------------------- ** 140524 IlV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `cv2`.

### `get_corners`

```python
def get_corners(image, arucoIds, maxAttempts=10)
```

## `CNC.py`

Source: [src/engine/vision/implementation/plvision/PLVision/CNC.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/CNC.py).

* File: CNC.y_pixels * Author: AtD * Comments: This file contains CNC functionality for CNC Software. * Revision history: * Date Author Description * ----------------------------------------------------------------- * 070524 AtD Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `PLVision.Contouring`, `cv2`, `linuxcnc`, `numpy`, `os`, `sys`, `threading`.

### `GenerateGCode`

```python
def GenerateGCode(contours, hierarchy, offset_x=0, offset_y=0)
```

### `PowerOnMachine`

```python
def PowerOnMachine()
```

### `PowerOffMachine`

```python
def PowerOffMachine()
```

### `HomeMachine`

```python
def HomeMachine()
```

### `run_program`

```python
def run_program(gcode_file)
```

### `headexecution`

```python
def headexecution()
```

### `RunGCode`

```python
def RunGCode()
```

### `StopGCode`

```python
def StopGCode()
```

### `ServiceMove`

```python
def ServiceMove()
```

### `MDIMode`

```python
def MDIMode()
```

### `MoveUp`

```python
def MoveUp()
```

### `MoveDown`

```python
def MoveDown()
```

### `MoveLeft`

```python
def MoveLeft()
```

### `MoveRight`

```python
def MoveRight()
```

### `MoveDiagonalUpLeft`

```python
def MoveDiagonalUpLeft()
```

### `MoveDiagonalUpRight`

```python
def MoveDiagonalUpRight()
```

### `MoveDiagonalDownLeft`

```python
def MoveDiagonalDownLeft()
```

### `MoveDiagonalDownRight`

```python
def MoveDiagonalDownRight()
```

### `StopMove`

```python
def StopMove()
```

### `Status`

```python
def Status()
```

## `Calibration.py`

Source: [src/engine/vision/implementation/plvision/PLVision/Calibration.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/Calibration.py).

* File: Calibration.y_pixels * Author: IlV * Comments: This file contains calibration functions for the camera. * Revision history: * Date Author Description * ----------------------------------------------------------------- * 070524 AtD/IlV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`, `os`.

### `CameraCalibrator`

```python
class CameraCalibrator:
```

A class for calibrating a camera using a chessboard pattern. Attributes: chessboardWidth (int): The number of inner corners per chessboard row. chessboardHeight (int): The number of inner corners per chessboard column. chessboardSquaresSize (float): The size of each chessboard square in real-world units. objp (np.ndarray): The object points in real-world space. objpoints (list): A list of object points in real-world space for all images. imgpoints (list): A list of corner points in the image space for all images. winZone (tuple): The size of the search window at each pyramid level for corner refinement. zeroZone (tuple): The size of the dead region in the middle of the search zone over which the summation in the formula below is not done. It is used to avoid possible singularities in the autocorrelation matrix. criteriaMaxIterations (int): The maximum number of iterations for corner refinement algorithm criteriaAccuracy (float): The accuracy desired for corner refinement algorithm

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, chessboardWidth, chessboardHeight, chessboardSquaresSize)
```

Initializes the CameraCalibrator with chessboard parameters. Parameters: chessboardWidth (int): Number of inner corners in chessboard rows. chessboardHeight (int): Number of inner corners in chessboard columns. chessboardSquaresSize (float): Size of each chessboard square.

```python
def findCorners(self, gray)
```

Finds the corners in a grayscale image of the chessboard. Parameters: gray (np.ndarray): A grayscale image of the chessboard. Returns: tuple: A tuple containing a boolean value indicating if corners were successfully found, and an array of detected corners in the image.

```python
def refineCorners(self, gray, corners)
```

Refines the detected corner locations in an image to sub-pixel accuracy. Parameters: gray (np.ndarray): A grayscale image of the chessboard. corners (np.ndarray): Initial coordinates of the detected corners in the image. Returns: np.ndarray: The refined corner locations in the image.

```python
def drawCorners(self, frame, corners2, ret)
```

Draws the chessboard corners detected in an image. Parameters: frame (np.ndarray): The image on which to draw the corners. corners2 (np.ndarray): The corner points. ret (bool): Indicates whether the chessboard corners were found.

```python
def appendCorners(self, corners2)
```

Appends the detected corners and corresponding object points for camera calibration. Parameters: corners2 (np.ndarray): The corner points in the image.

```python
def calculatePpm(self)
```

Calculates the pixels-per-metric ratio based on detected corners, considering both x and y distances between corners for a more accurate estimation. Returns: float: The average pixels-per-metric ratio for the detected squares.

```python
def calibrateCamera(self, image)
```

Performs camera calibration using the detected corners. Returns: tuple: The distortion coefficients, camera matrix, rotation vectors, and translation vectors determined during calibration.

```python
def calculateMeanError(self, dist, mtx, rvecs, tvecs)
```

Calculates the mean error of the reprojected points against the original detected corners. Parameters: dist (np.ndarray): The distortion coefficients. mtx (np.ndarray): The camera matrix. rvecs (list): List of rotation vectors. tvecs (list): List of translation vectors. Returns: float: The mean error across all calibration images.

```python
def saveCalibrationData(self, mtx, dist, ppm, path)
```

Saves the calibration data to a file. Parameters: mtx (np.ndarray): The camera matrix. dist (np.ndarray): The distortion coefficients. ppm (float): The pixels-per-metric ratio. path: (str) Path to the directory where the calibration data is saved

```python
def performCameraCalibration(self, image, path)
```

Perform camera calibration using the provided image. Parameters: path: (str) Path to the directory where the calibration data is saved image (np.ndarray): The input image for calibration. Returns: tuple: A tuple containing a boolean indicating if calibration was successful, the calibration data (distortion coefficients, camera matrix, rotation vectors, and translation vectors), the image and the coordinates of the detected corners.

## `Camera.py`

Source: [src/engine/vision/implementation/plvision/PLVision/Camera.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/Camera.py).

Camera wrapper with backend selection, device path/index support and explicit configuration for FOURCC, resolution and fps. Backwards compatible constructor: Camera(cameraIndex, width, height) New optional keyword params (use by name): - device: int or str (index or path). If provided it overrides cameraIndex. - backend: cv2 backend constant (e.g. cv2.CAP_V4L2) or name string ('V4L2','ANY') - fourcc: 4-char string like 'MJPG' to force pixel format - fps: desired capture fps (float) - open_timeout: seconds to keep trying to open the device - retries: number of retries when reading frames Public methods: - capture(grab_only=False): return frame (or None) - isOpened(), close(), get_properties(), set_resolution(), set_fps(), set_fourcc()

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `os`, `platform`, `sys`, `threading`, `time`.

### `Camera`

```python
class Camera:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, cameraIndex=0, width=1280, height=720, *, device=None, backend=None, fourcc=None, fps=None, open_timeout=5.0, retries=3, mjpg_preferred=True, verbose_ae=False)
```

```python
def isOpened(self)
```

```python
def get_properties(self)
```

```python
def set_resolution(self, width, height)
```

```python
def set_fps(self, fps)
```

```python
def set_fourcc(self, fourcc_str)
```

```python
def set_auto_exposure(self, enabled: bool)
```

Change AE mode reliably by restarting stream. Serialised with capture()/stream restarts via _io_lock so the restart never races the FrameGrabber thread. On failure the stream is restored before raising so the camera is never left released.

```python
def get_auto_exposure(self)
```

Return the current AUTO_EXPOSURE property value (or None).

```python
def set_exposure(self, exposure_value: float)
```

Set an absolute exposure value (driver-dependent units).

```python
def capture(self, grab_only=False, timeout=1.0)
```

```python
def close(self)
```

```python
def stopCapture(self)
```

```python
def stop_stream(self)
```

Stop the camera stream without destroying Camera object.

```python
def start_stream(self)
```

Restart camera stream with previous parameters. Retry if device is busy.

## `Contouring.py`

Source: [src/engine/vision/implementation/plvision/PLVision/Contouring.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/Contouring.py).

* File: Contouring.y_pixels * Author: AtD, IlV * Comments: * Revision history: * Date Author Description * ----------------------------------------------------------------- ** 070524 AtD/IlV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`.

### `calculateCentroid`

```python
def calculateCentroid(contour)
```

Calculates the centroid of a contour. Parameters: contour (np.ndarray): The contour for which to calculate the centroid. Returns: tuple: A tuple containing the (x, y) coordinates of the centroid.

### `scaleContourAndChildren`

```python
def scaleContourAndChildren(contours, hierarchy, ppm, mmToScale)
```

Scales contours and their children based on a given scaling factor. Parameters: contours (list): A list of contours. hierarchy (np.ndarray): Contour hierarchy as returned by cv2.findContours(). ppm (float): Pixels per millimeter scale factor. mmToScale (float): Millimeters to scale by. Note: This function modifies the input contours in place.

### `translateContourAndChildren`

```python
def translateContourAndChildren(contours, hierarchy, xOffset, yOffset, parentIndex=None)
```

Translates contours and their children by specified offsets. Parameters: contours (list): A list of contours. hierarchy (np.ndarray): Contour hierarchy as returned by cv2.findContours(). xOffset (int): Horizontal offset in pixels. yOffset (int): Vertical offset in pixels. parentIndex (int): Index of the parent contour. Defaults to None. Returns: list: A list of indices of translated child contours. Note: This function modifies the input contours in place.

### `drawContours`

```python
def drawContours(image, contours, contourColor, thickness)
```

Draws contours on an image. Parameters: image (np.ndarray): The input image. contours (list): A list of contours. contourColor (tuple): The color of the contours in BGR format. thickness (int): The thickness of the contour lines. Returns: np.ndarray: The image with contours drawn on it. Raises: ValueError: If thickness is not a positive integer.

### `findContours`

```python
def findContours(image, mode, method)
```

Finds contours in an image. Parameters: mode: method: image (np.ndarray): The input image. Returns: tuple: A tuple containing a list of contours and their hierarchy.

### `rotateContour`

```python
def rotateContour(contour, angle, pivot)
```

Rotates a single contour around a pivot point. Parameters: contour (np.ndarray): The contour to rotate. angle (float): The rotation angle in degrees. pivot (tuple): The pivot point (x, y) around which to rotate the contour. Returns: np.ndarray: The rotated contour.

### `rotateContourAndChildren`

```python
def rotateContourAndChildren(contours, hierarchy, angle)
```

Rotates contours and their children around their centroid by a given angle. Parameters: contours (list): A list of contours. hierarchy (np.ndarray): Contour hierarchy as returned by cv2.findContours(). angle (float): The rotation angle in degrees. Note: This function modifies the input contours in place.

### `isContourWithinBbox`

```python
def isContourWithinBbox(contour, bbox)
```

## `Example.py`

Source: [src/engine/vision/implementation/plvision/PLVision/Example.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/Example.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `FileSelector.py`

Source: [src/engine/vision/implementation/plvision/PLVision/FileSelector.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/FileSelector.py).

* File: FileSelector.y_pixels * Author: AtD * Comments: This file contains the main function of the project. * Revision history: * Date Author Description * ----------------------------------------------------------------- * 070524 AtD Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `glob`, `os`.

### `getFile`

```python
def getFile(fileCount, filePath, fileFormat, all=False)
```

## `HandTrackingModule.py`

Source: [src/engine/vision/implementation/plvision/PLVision/HandTrackingModule.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/HandTrackingModule.py).

* File: FileSelector.y_pixels * Author: ILV * Comments: This file contains the main function of the project. * Revision history: * Date Author Description * ----------------------------------------------------------------- * 070524 ILV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `enum`, `math`, `mediapipe`.

### `Modes`

```python
class Modes(Enum):
```

Declared fields/defaults:

```python
LIVE_STREAM = 'LIVE_STREAM'
IMAGE = 'IMAGE'
VIDEO = 'VIDEO'
```

### `HandDetector`

```python
class HandDetector:
```

A class to detect hands in a video frame using MediaPipe Hands. Attributes: mode (Modes): Whether to treat the input images as a batch of static and possibly unrelated images, or a stream of images where the hand presence and positioning is more predictable. Default is False. maxHands (int): Maximum number of hands to detect. Default is 2. detectionCon (float): Minimum confidence value ([0.0, 1.0]) for hand detection to be considered successful. Default is 1. trackCon (float): Minimum confidence value ([0.0, 1.0]) for the hand landmarks to be considered tracked successfully. Default is 0.5.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, mode=Modes.LIVE_STREAM, maxHands=1, detectionCon=1, trackCon=0.5)
```

```python
def findHands(self, image, draw=True)
```

Finds hands in an image. Args: image: The image in which to detect hands. draw (bool): Whether to draw the detection results on the image. Returns: The image with or without drawings.

```python
def findPosition(self, img, handNo=0, draw=True)
```

Finds the position of hand landmarks in an image. Args: img: The image from which to find the positions. handNo (int): The index of the hand to find positions for (in case of multiple hands detected). draw (bool): Whether to draw circles at each landmark position. Returns: A tuple containing a list of all landmark positions (with each position being a list of [id, x, y]) and a bounding box around the detected hand in the format (xmin, ymin, xmax, ymax).

```python
def fingersUp(self)
```

Определя дали пръстът е изправен (отворен) или сгънат (затворен). Връща: Списък с булеви стойности, където всяка стойност представлява отворен (1) или затворен (0) пръст: - Първият елемент отговаря на показалеца. - Вторият елемент отговаря на средния пръст. - Третият елемент отговаря на пръстът "халка". - Четвъртият елемент отговаря на малкия пръст. - Петият елемент отговаря на палеца.

```python
def isThumbOpen(self)
```

Determines if the thumb is open. Returns: True if the thumb is considered open, False otherwise.

```python
def isFingerOpen(self, finger_id)
```

Determines if a specified finger is open. Args: finger_id (int): The index of the finger to check. Returns: True if the finger is considered open, False otherwise.

```python
def calculateAngle(self, point1, point2, point3)
```

Calculates the angle between three points. Args: point1: The first point. point2: The second point, which acts as the vertex of the angle. point3: The third point. Returns: The angle in degrees between the three points.

```python
def findDistance(self, p1, p2, img, draw=True, r=15, t=3)
```

Finds the distance between two points on the hand. Args: p1, p2: The indices of the points to measure the distance between. img: The image on which the measurement is to be drawn. draw (bool): Whether to draw the measurement on the image. r (int): The radius of the circles to be drawn at points p1 and p2. t (int): The thickness of the line to be drawn between points p1 and p2. Returns: A tuple containing the distance between the points, the image, and the coordinates of the points.

## `ImageProcessing.py`

Source: [src/engine/vision/implementation/plvision/PLVision/ImageProcessing.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/ImageProcessing.py).

* File: ImageProcessing.y_pixels * Author: AtD * Comments: This file contains the main function of the project. * Revision history: * Date Author Description * ----------------------------------------------------------------- * 070524 AtD/IlV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`.

### `blurImage`

```python
def blurImage(image, kernelSize, sigmaX)
```

Blurs an image using a Gaussian filter. Parameters: image (np.ndarray): The image to be blurred. kernelSize (int): The size of the Gaussian kernel. Returns: np.ndarray: The blurred image.

### `threshImage`

```python
def threshImage(image, thresholdValue, maxValue, thresholdType)
```

Applies a fixed-level threshold to an image. Parameters: image (np.ndarray): The image to be thresholded. thresholdValue (float): The threshold value. maxValue (float): The maximum value to use with the THRESH_BINARY and THRESH_BINARY_INV threshold types. thresholdType (int): The thresholding type. Returns: np.ndarray: The thresholded image.

### `perspectiveTransform`

```python
def perspectiveTransform(image, srcPoints, dstPoints, calibration_file)
```

Applies a perspective transformation to an image. Parameters: image (np.ndarray): The image to be transformed. srcPoints (np.ndarray): The source points. dstPoints (np.ndarray): The destination points. calibration_file (str): The path to the calibration file. Returns: np.ndarray: The transformed image.

### `grayImage`

```python
def grayImage(image)
```

Converts an image to grayscale. Parameters: image (np.ndarray): The image to be converted to grayscale. Returns: np.ndarray: The grayscale image.

### `cannyImage`

```python
def cannyImage(image, threshold1, threshold2)
```

Applies the Canny edge detection algorithm to an image. Parameters: image (np.ndarray): The image to be processed. threshold1 (float): The first threshold for the hysteresis procedure. threshold2 (float): The second threshold for the hysteresis procedure. Returns: np.ndarray: The edge-detected image.

### `onesImage`

```python
def onesImage(rows, cols)
```

Creates an image filled with ones. Parameters: rows (int): The number of rows in the image. cols (int): The number of columns in the image. Returns: np.ndarray: The image filled with ones.

### `dilateImage`

```python
def dilateImage(image, kernel, iterations)
```

Dilates an image using a specific structuring element. Parameters: image (np.ndarray): The image to be dilated. kernel (np.ndarray): The structuring element. iterations (int): The number of iterations. Returns: np.ndarray: The dilated image.

### `erodeImage`

```python
def erodeImage(image, kernel, iterations)
```

Erodes an image using a specific structuring element. Parameters: image (np.ndarray): The image to be eroded. kernel (np.ndarray): The structuring element. iterations (int): The number of iterations. Returns: np.ndarray: The eroded image.

### `antiAliasImage`

```python
def antiAliasImage(image, iterations, kSize, sigmaX, sigmaColor, sigmaSpace)
```

Applies anti-aliasing to an image. Parameters: image (np.ndarray): The image to be anti-aliased. iterations (int): The number of iterations. Returns: np.ndarray: The anti-aliased image.

### `brightnessContrast`

```python
def brightnessContrast(image, brightness=0, contrast=0)
```

### `applyAffineTransformation`

```python
def applyAffineTransformation(image, xOffset, yOffset, rotationAngle, xScale, yScale)
```

### `undistortImage`

```python
def undistortImage(image, mtx, dist, imageWidth=1920, imageHeight=1080, crop=False, optimal_camera_matrix=None, roi=None)
```

Undistorts an image given the camera matrix and distortion coefficients. Parameters: imageHeight: imageWidth: crop: image (np.ndarray): The distorted image to be undistorted. mtx (np.ndarray): The camera matrix. dist (np.ndarray): The distortion coefficients. optimal_camera_matrix roi Returns: np.ndarray: The undistorted image. Raises: Exception: If either `mtx` or `dist` is None.

### `cropImage`

```python
def cropImage(image, leftCrop=0, rightCrop=0, topCrop=0, bottomCrop=0, pad=True)
```

Crops and then pads an image to maintain its original dimensions. Parameters: image (np.ndarray): The image to be cropped and padded. leftCrop (int): The number of pixels to crop from the left. rightCrop (int): The number of pixels to crop from the right. topCrop (int): The number of pixels to crop from the top. bottomCrop (int): The number of pixels to crop from the bottom. Returns: np.ndarray: The cropped and padded image. Notes: This function validates the crop values to ensure they are positive integers before performing the crop and pad operations.

### `grayscaleImage`

```python
def grayscaleImage(image)
```

Converts an image to grayscale. Parameters: image (np.ndarray): The image to be converted to grayscale. Returns: np.ndarray: The grayscale image.

### `zoom`

```python
def zoom(image, scaleFactor, xOffset=0, yOffset=0)
```

Zooms into or out of the center of the given image based on the scale factor. Parameters: image: numpy.ndarray Input image as a NumPy array. scaleFactor: float Scale factor for zooming. - Values greater than 1 zoom in. - Values less than 1 zoom out. xOffset: int, optional Horizontal offset from the center. yOffset: int, optional Vertical offset from the center. Returns: numpy.ndarray Zoomed image as a NumPy array.

## `JsonHandler.py`

Source: [src/engine/vision/implementation/plvision/PLVision/JsonHandler.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/JsonHandler.py).

* File: JsonHandler.y_pixels * Author: IlV * Comments: * Revision history: * Date Author Description * ----------------------------------------------------------------- ** 130524 IlV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `json`.

### `JsonHandler`

```python
class JsonHandler:
```

A class used to handle JSON file operations. Attributes ---------- file_path : str The path to the JSON file. encoder : json.JSONEncoder, optional The JSON encoder to use (default is json.JSONEncoder). Methods ------- read_json(): Reads and returns the data from the JSON file. write_json(data): Writes the given data to the JSON file. update_json(new_data): Updates the JSON file with the given new data.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, filePath, encoder=None)
```

Constructs all the necessary attributes for the JsonHandler object. Parameters ---------- filePath : str The path to the JSON file. encoder : json.JSONEncoder, optional The JSON encoder to use (default is json.JSONEncoder).

```python
def readJson(self)
```

Reads and returns the data from the JSON file. Returns ------- dict The data from the JSON file, or an empty dictionary if the file is empty.

```python
def writeJson(self, data)
```

Writes the given data to the JSON file. Parameters ---------- data : dict The data to write to the JSON file.

```python
def updateJson(self, newData)
```

Updates the JSON file with the given new data. Parameters ---------- newData : dict The new data to update the JSON file with.

## `__init__.py`

Source: [src/engine/vision/implementation/plvision/PLVision/__init__.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `arucoModule.py`

Source: [src/engine/vision/implementation/plvision/PLVision/arucoModule.py](../../../../../../src/engine/vision/implementation/plvision/PLVision/arucoModule.py).

* File: arucoModule.y_pixels * Author: IlV * Comments: * Revision history: * Date Author Description * ----------------------------------------------------------------- ** 140524 IlV Initial release * -----------------------------------------------------------------

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `enum`.

### `ArucoDictionary`

```python
class ArucoDictionary(Enum):
```

Enumeration for available ArUco dictionaries in OpenCV.

Declared fields/defaults:

```python
DICT_4X4_50 = cv2.aruco.DICT_4X4_50
DICT_4X4_100 = cv2.aruco.DICT_4X4_100
DICT_4X4_250 = cv2.aruco.DICT_4X4_250
DICT_4X4_1000 = cv2.aruco.DICT_4X4_1000
DICT_5X5_50 = cv2.aruco.DICT_5X5_50
DICT_5X5_100 = cv2.aruco.DICT_5X5_100
DICT_5X5_250 = cv2.aruco.DICT_5X5_250
DICT_5X5_1000 = cv2.aruco.DICT_5X5_1000
DICT_6X6_50 = cv2.aruco.DICT_6X6_50
DICT_6X6_100 = cv2.aruco.DICT_6X6_100
DICT_6X6_250 = cv2.aruco.DICT_6X6_250
DICT_6X6_1000 = cv2.aruco.DICT_6X6_1000
DICT_7X7_50 = cv2.aruco.DICT_7X7_50
DICT_7X7_100 = cv2.aruco.DICT_7X7_100
DICT_7X7_250 = cv2.aruco.DICT_7X7_250
DICT_7X7_1000 = cv2.aruco.DICT_7X7_1000
```

### `ArucoDetector`

```python
class ArucoDetector:
```

Detects ArUco markers in images using OpenCV 4.11+ ArucoDetector shared.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, arucoDict=ArucoDictionary.DICT_6X6_250)
```

```python
def detectAll(self, image)
```

Detects all ArUco markers in the given image.

```python
def detectAreaCorners(self, image, arucoIds, maxAttempts=10)
```

Detects four specified ArUco markers in the image and returns their corners.
