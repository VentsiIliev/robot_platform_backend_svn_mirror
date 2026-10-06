# Module reference: `src/engine/vision/implementation/plvision/PLVision/PID`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [BrightnessController.py](#brightnesscontrollerpy)
- [PIDController.py](#pidcontrollerpy)
- [__init__.py](#__init__py)

## `BrightnessController.py`

Source: [src/engine/vision/implementation/plvision/PLVision/PID/BrightnessController.py](../../../../../../../src/engine/vision/implementation/plvision/PLVision/PID/BrightnessController.py).

* File: PIDController.y_pixels * Author: IlV * Comments: * Revision history: * Date Author Description * ----------------------------------------------------------------- ** 100624 IlV Initial release * ----------------------------------------------------------------- *

Imports (including optional/function-local imports; not a startup dependency list): `..PID.PIDController`, `cv2`, `numpy`.

### `BrightnessController`

```python
class BrightnessController(PIDController):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, Kp, Ki, Kd, setPoint)
```

```python
def calculateBrightness(self, frame, roi_points=None)
```

Calculate the brightness of a frame, optionally within a specific region of interest. Args: frame (np.array): The frame to calculate the brightness of. roi_points (np.array, optional): Points defining the region of interest. If None, calculates brightness of entire frame. Returns: float: The brightness of the frame or region.

```python
def compute_with_antiwindup(self, currentValue)
```

Compute PID output with anti-windup (back-calculation method). Only accumulates integral when output is not saturated. Args: currentValue (float): The current value to be controlled. Returns: float: The clamped output of the PID controller.

```python
def adjustBrightness(self, frame, adjustment)
```

Adjust the brightness of a frame, optionally within a specific region of interest. Args: frame (np.array): The frame to adjust the brightness of. adjustment (float): The amount to adjust the brightness by. Returns: np.array: The frame with adjusted brightness.

## `PIDController.py`

Source: [src/engine/vision/implementation/plvision/PLVision/PID/PIDController.py](../../../../../../../src/engine/vision/implementation/plvision/PLVision/PID/PIDController.py).

* File: PIDController.y_pixels * Author: IlV * Comments: * Revision history: * Date Author Description * ----------------------------------------------------------------- ** 100624 IlV Initial release * ----------------------------------------------------------------- *

### `PIDController`

```python
class PIDController:
```

A simple PID controller. Attributes: Kp (float): Proportional gain. Ki (float): Integral gain. Kd (float): Derivative gain. target (float): Desired value. previousError (float): The error at the previous time step. integral (float): Accumulated error over time.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, Kp, Ki, Kd, target)
```

Initialize the PID controller.

```python
def compute(self, currentValue)
```

Compute the output of the PID controller. Args: currentValue (float): The current value to be controlled. Returns: float: The output of the PID controller.

## `__init__.py`

Source: [src/engine/vision/implementation/plvision/PLVision/PID/__init__.py](../../../../../../../src/engine/vision/implementation/plvision/PLVision/PID/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
