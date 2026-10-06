# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [conftest.py](#conftestpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/__init__.py).

Test Suite Module Comprehensive test suite for the shape matching training vision_service including unit tests, integration tests, and test fixtures.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `conftest.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/conftest.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/conftest.py).

pytest Configuration and Fixtures This module provides shared test fixtures and configuration for the entire test suite.

Imports (including optional/function-local imports; not a startup dependency list): `config.model_configs`, `config.training_configs`, `core.dataset.pair_generator`, `core.dataset.shape_factory`, `core.dataset.synthetic_dataset`, `core.features.base_extractor`, `core.features.geometric_features`, `core.features.moment_features`, `core.models.sgd_model`, `numpy`, `pathlib`, `pytest`, `shutil`, `sys`, `tempfile`, `time`, `typing`, `unittest.mock`.

### `temp_dir`

```python
def temp_dir() -> Generator[Path, None, None]
```

Create a temporary directory for test files.

### `simple_contour`

```python
def simple_contour() -> np.ndarray
```

Generate a simple square contour for testing.

### `circle_contour`

```python
def circle_contour() -> np.ndarray
```

Generate a circle contour for testing.

### `multiple_contours`

```python
def multiple_contours() -> List[np.ndarray]
```

Generate multiple different contours for testing.

### `synthetic_contours`

```python
def synthetic_contours() -> List[SyntheticContour]
```

Generate synthetic contours with metadata for testing.

### `training_pairs`

```python
def training_pairs() -> Tuple[List[Tuple[np.ndarray, np.ndarray]], List[int]]
```

Generate training pairs with labels for testing.

### `geometric_extractor`

```python
def geometric_extractor() -> GeometricFeatureExtractor
```

Create a geometric feature extractor for testing.

### `hu_moment_extractor`

```python
def hu_moment_extractor() -> HuMomentExtractor
```

Create a Hu moment extractor for testing.

### `composite_extractor`

```python
def composite_extractor() -> CompositeFeatureExtractor
```

Create a composite feature extractor for testing.

### `sgd_model`

```python
def sgd_model() -> SGDModel
```

Create an SGD model for testing.

### `trained_model`

```python
def trained_model(sgd_model, composite_extractor, training_pairs) -> SGDModel
```

Create a trained model for testing.

### `default_config`

```python
def default_config() -> DefaultTrainingConfig
```

Create a default training configuration for testing.

### `mock_model`

```python
def mock_model() -> Mock
```

Create a mock model for testing.

### `sample_features`

```python
def sample_features() -> np.ndarray
```

Generate sample feature matrix for testing.

### `sample_labels`

```python
def sample_labels() -> np.ndarray
```

Generate sample labels for testing.

### `small_dataset`

```python
def small_dataset() -> SyntheticDataset
```

Create a small synthetic dataset for testing.

### `pair_generator`

```python
def pair_generator() -> PairGenerator
```

Create a pair generator for testing.

### `pytest_configure`

```python
def pytest_configure(config)
```

Configure pytest markers.

### `TestHelpers`

```python
class TestHelpers:
```

Helper methods for testing.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def assert_contour_valid(contour: np.ndarray) -> None
```

Assert that a contour is valid.

```python
@staticmethod
def assert_features_valid(features: List[float]) -> None
```

Assert that extracted features are valid.

```python
@staticmethod
def assert_model_predictions_valid(predictions: np.ndarray) -> None
```

Assert that model predictions are valid.

### `test_helpers`

```python
def test_helpers() -> TestHelpers
```

Provide test helper methods.

### `performance_tracker`

```python
def performance_tracker()
```

Track performance metrics during tests.
