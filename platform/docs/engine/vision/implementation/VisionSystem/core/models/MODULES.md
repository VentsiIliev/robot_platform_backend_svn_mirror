# Module reference: `src/engine/vision/implementation/VisionSystem/core/models`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [contour.py](#contourpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/core/models/__init__.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/models/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.core.models.contour`.

Package-level import/export surface:

```python
from src.engine.vision.implementation.VisionSystem.core.models.contour import Contour
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `contour.py`

Source: [src/engine/vision/implementation/VisionSystem/core/models/contour.py](../../../../../../../src/engine/vision/implementation/VisionSystem/core/models/contour.py).

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`.

### `Contour`

```python
class Contour:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, contour_points)
```

```python
def get(self)
```

```python
def as_cv(self)
```

```python
def getArea(self)
```

```python
def getBbox(self)
```

```python
def getMinAreaRect(self)
```

```python
def getMoments(self)
```

```python
def getPerimeter(self)
```

```python
def getCentroid(self)
```

```python
def getConvexHull(self)
```

```python
def getOrientation(self)
```

```python
def match(self, other)
```

```python
def translate(self, dx, dy)
```

```python
def scale(self, factor)
```

```python
def rotate(self, angle_deg, pivot)
```

```python
def reflect_horizontal(self, pivot_x)
```

```python
def simplify(self, epsilon_factor=0.01)
```

```python
def getConvexityDefects(self)
```

```python
def shrink(self, offset_x, offset_y)
```

```python
def draw(self, frame, color=(0, 255, 0), thickness=2)
```
