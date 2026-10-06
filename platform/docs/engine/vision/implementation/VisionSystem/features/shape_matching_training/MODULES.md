# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [run_tests.py](#run_testspy)
- [train_production_model.py](#train_production_modelpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/__init__.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/__init__.py).

Shape Matching Training Module A comprehensive machine learning vision_service for contour similarity detection and matching. This module provides tools for synthetic data generation, feature extraction, model training, and real-time shape matching applications.

Imports (including optional/function-local imports; not a startup dependency list): `.config.training_configs`, `.core.models.model_factory`, `.core.training.pipeline`, `.utils.io_utils`.

Package-level import/export surface:

```python
from .core.training.pipeline import TrainingPipeline
from .core.models.model_factory import ModelFactory
from .config.training_configs import DefaultTrainingConfig
from .utils.io_utils import load_model, save_model
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['TrainingPipeline', 'ModelFactory', 'DefaultTrainingConfig', 'load_model', 'save_model']
```

## `run_tests.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/run_tests.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/run_tests.py).

Test Runner for Shape Matching Training Module This script provides a convenient interface for running different types of tests with various options and configurations.

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `pathlib`, `subprocess`, `sys`.

### `run_pytest`

```python
def run_pytest(test_type='all', verbose=True, coverage=False, parallel=False, markers=None)
```

Run pytest with specified options Args: test_type: Type of tests to run ('unit', 'integration', 'all') verbose: Enable verbose output coverage: Enable coverage reporting parallel: Enable parallel test execution markers: Additional pytest markers to apply

### `run_quick_tests`

```python
def run_quick_tests()
```

Run quick tests (unit tests, excluding slow markers)

### `run_full_tests`

```python
def run_full_tests()
```

Run full test suite including integration and performance tests

### `run_performance_tests`

```python
def run_performance_tests()
```

Run only performance tests

### `check_dependencies`

```python
def check_dependencies()
```

Check that required testing dependencies are installed

### `main`

```python
def main()
```

Main test runner interface

## `train_production_model.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/train_production_model.py](../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/train_production_model.py).

Production Model Training Script This script trains a production-ready shape matching model using robust configuration and saves it for deployment.

Imports (including optional/function-local imports; not a startup dependency list): `datetime`, `json`, `pathlib`, `src.engine.vision.implementation.VisionSystem.features.shape_matching_training.config.training_configs`, `src.engine.vision.implementation.VisionSystem.features.shape_matching_training.core.training.pipeline`, `sys`, `traceback`.

### `train_production_model`

```python
def train_production_model()
```

Train a production-ready shape matching model
