# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/__init__.py).

Core Business Logic Module Contains the main business logic for shape matching training including: - Dataset generation and management - Feature extraction - Model implementations - Training orchestration

Imports (including optional/function-local imports; not a startup dependency list): `.dataset`, `.features`, `.models`, `.training`.

Package-level import/export surface:

```python
from .dataset import ShapeFactory, SyntheticDataset
from .features import FeatureExtractorFactory
from .models import ModelFactory
from .training import TrainingPipeline
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ShapeFactory', 'SyntheticDataset', 'FeatureExtractorFactory', 'ModelFactory', 'TrainingPipeline']
```
