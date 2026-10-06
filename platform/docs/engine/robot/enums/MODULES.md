# Module reference: `src/engine/robot/enums`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [axis.py](#axispy)

## `__init__.py`

Source: [src/engine/robot/enums/__init__.py](../../../../src/engine/robot/enums/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `axis.py`

Source: [src/engine/robot/enums/axis.py](../../../../src/engine/robot/enums/axis.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `enum`, `typing`.

### `RobotAxis`

```python
class RobotAxis(Enum):
```

Declared fields/defaults:

```python
X = 1
Y = 2
Z = 3
RX = 4
RY = 5
RZ = 6
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def get_by_string(cls, axis_str: str)
```

Convert string to RobotAxis enum instance

### `Direction`

```python
class Direction(Enum):
```

Enum representing movement directions along an axis.

Declared fields/defaults:

```python
MINUS = -1
PLUS = 1
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def get_by_string(name: str)
```

### `ImageAxis`

```python
class ImageAxis(Enum):
```

Declared fields/defaults:

```python
X = auto()
Y = auto()
```

### `AxisMapping`

```python
@dataclass
class AxisMapping:
```

Declared fields/defaults:

```python
image_axis: ImageAxis
direction: Direction
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def apply(self, dx_img: float, dy_img: float) -> float
```

### `ImageToRobotMapping`

```python
@dataclass
class ImageToRobotMapping:
```

Declared fields/defaults:

```python
robot_x: AxisMapping
robot_y: AxisMapping
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def map(self, camera_x: float, camera_y: float) -> Tuple[float, float]
```

Map image offsets to robot coordinate offsets based on this mapping. Args: camera_x (float): Offset along image X axis relative to center (mm). camera_y (float): Offset along image Y axis relative to center (mm). Returns: Tuple[float, float]: (robot_x_offset, robot_y_offset) in mm
