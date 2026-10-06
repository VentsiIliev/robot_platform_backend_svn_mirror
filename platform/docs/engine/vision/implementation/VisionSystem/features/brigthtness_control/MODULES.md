# Module reference: `src/engine/vision/implementation/VisionSystem/features/brigthtness_control`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [brightness_manager.py](#brightness_managerpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/brigthtness_control/__init__.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/brigthtness_control/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `brightness_manager.py`

Source: [src/engine/vision/implementation/VisionSystem/features/brigthtness_control/brightness_manager.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/brigthtness_control/brightness_manager.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `numpy`, `src.engine.vision.implementation.plvision.PLVision.PID.BrightnessController`.

### `BrightnessManager`

```python
class BrightnessManager:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, vision_system)
```

```python
def auto_brightness_control_off(self)
```

```python
def auto_brightness_control_on(self)
```

```python
def on_brighteness_toggle(self, mode)
```

```python
def get_area_by_threshold(self)
```

```python
def adjust_brightness(self)
```
