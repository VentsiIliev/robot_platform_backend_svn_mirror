# Module reference: `src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/strategies`

[Package guide](README.md) · [Complete source index](../../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [geometric_matching_strategy.py](#geometric_matching_strategypy)
- [matching_strategy_interface.py](#matching_strategy_interfacepy)
- [ml_matching_strategy.py](#ml_matching_strategypy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/strategies/__init__.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/strategies/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `geometric_matching_strategy.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/strategies/geometric_matching_strategy.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/strategies/geometric_matching_strategy.py).

Geometric matching for contours captured by the same camera.

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `logging`, `numpy`, `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.alignment.difference_calculator`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.best_match_result`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.normalized_mask_overlap`, `typing`.

### `GeometricMatchingStrategy`

```python
class GeometricMatchingStrategy:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, similarity_threshold: float=0.8, debug: bool=False, debug_differences: bool=False)
```

```python
def find_best_match(self, workpieces: list[Any], contour: Contour) -> BestMatchResult
```

### `_structural_vertex_count`

```python
def _structural_vertex_count(contour: np.ndarray) -> int
```

## `matching_strategy_interface.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/strategies/matching_strategy_interface.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/strategies/matching_strategy_interface.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.best_match_result`, `typing`.

### `MatchingStrategy`

```python
class MatchingStrategy(Protocol):
```

Interface for contour-workpiece matching strategies.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def find_best_match(self, workpieces: list[Any], contour: Contour) -> 'BestMatchResult'
```

## `ml_matching_strategy.py`

Source: [src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/strategies/ml_matching_strategy.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/contour_matching/matching/strategies/ml_matching_strategy.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.vision.implementation.VisionSystem.core.models.contour`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.alignment.difference_calculator`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching.best_match_result`, `src.engine.vision.implementation.VisionSystem.features.contour_matching.matching_config`, `src.engine.vision.implementation.VisionSystem.features.shape_matching_training.utils.io_utils`, `typing`.

### `MLMatchingStrategy`

```python
class MLMatchingStrategy:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: Any)
```

```python
def find_best_match(self, workpieces: list[Any], contour: Contour) -> BestMatchResult
```
