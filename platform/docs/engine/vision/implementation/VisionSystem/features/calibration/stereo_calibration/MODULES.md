# Module reference: `src/engine/vision/implementation/VisionSystem/features/calibration/stereo_calibration`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [StereoCalibration.py](#stereocalibrationpy)
- [__init__.py](#__init__py)
- [get_images.py](#get_imagespy)

## `StereoCalibration.py`

Source: [src/engine/vision/implementation/VisionSystem/features/calibration/stereo_calibration/StereoCalibration.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/calibration/stereo_calibration/StereoCalibration.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `glob`, `logging`, `numpy`, `os`, `sys`.

Module declarations (expressions are shown without evaluating them):

```python
CHESSBOARD_SIZE = (17, 11)
SQUARE_SIZE = 15.0
left_images_path = '/home/plp/cobot-soft-v2.1.8/cobot-glue-dispencing-v2/cobot-soft-glue-dispencing-v2/VisionSystem/calibration/stereo_calibration/calibration_images/left/*.png'
right_images_path = '/home/plp/cobot-soft-v2.1.8/cobot-glue-dispencing-v2/cobot-soft-glue-dispencing-v2/VisionSystem/calibration/stereo_calibration/calibration_images/right/*.png'
output_dir = '/home/plp/cobot-soft-v2.1.8/cobot-glue-dispencing-v2/cobot-soft-glue-dispencing-v2/VisionSystem/calibration/stereo_calibration/output'
objp = np.zeros((CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3), np.float32)
objpoints = []
imgpoints_left = []
imgpoints_right = []
left_images = sorted(glob.glob(left_images_path))
right_images = sorted(glob.glob(right_images_path))
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
flags = 0
criteria_stereo = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-05)
baseline = np.linalg.norm(T)
test_left = cv2.imread(left_images[0])
test_right = cv2.imread(right_images[0])
rect_left = cv2.remap(test_left, map1_left, map2_left, interpolation=cv2.INTER_LINEAR)
rect_right = cv2.remap(test_right, map1_right, map2_right, interpolation=cv2.INTER_LINEAR)
grayL = cv2.cvtColor(rect_left, cv2.COLOR_BGR2GRAY)
grayR = cv2.cvtColor(rect_right, cv2.COLOR_BGR2GRAY)
stereo = cv2.StereoSGBM_create(minDisparity=0, numDisparities=128, blockSize=5, P1=8 * 3 * 5 ** 2, P2=32 * 3 * 5 ** 2, disp12MaxDiff=1, uniquenessRatio=10, speckleWindowSize=100, speckleRange=32)
disparity = stereo.compute(grayL, grayR).astype(np.float32) / 16.0
disp_vis = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
disp_vis = np.uint8(disp_vis)
points_3D = cv2.reprojectImageTo3D(disparity, Q)
mask_map = disparity > disparity.min()
output_points = points_3D[mask_map]
output_colors = rect_left[mask_map]
```

### `write_ply`

```python
def write_ply(filename, verts, colors)
```

Save point cloud to PLY file.

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/calibration/stereo_calibration/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/calibration/stereo_calibration/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `get_images.py`

Source: [src/engine/vision/implementation/VisionSystem/features/calibration/stereo_calibration/get_images.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/calibration/stereo_calibration/get_images.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `datetime`, `logging`, `numpy`, `os`, `requests`.

Module declarations (expressions are shown without evaluating them):

```python
LEFT_URL = 'http://192.168.222.225:5000/image/left'
RIGHT_URL = 'http://192.168.222.225:5000/image/right'
SAVE_DIR_LEFT = 'calibration_images/left'
SAVE_DIR_RIGHT = 'calibration_images/right'
img_counter = 0
```

### `get_image`

```python
def get_image(url)
```

Fetch image from a URL and decode it into OpenCV format.
