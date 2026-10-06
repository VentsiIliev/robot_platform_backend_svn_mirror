# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/models`

[Package guide](README.md) · [Complete source index](../../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [base_model.py](#base_modelpy)
- [model_factory.py](#model_factorypy)
- [sgd_model.py](#sgd_modelpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/models/__init__.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/models/__init__.py).

Model Implementation Module Provides machine learning model implementations and factory for creating and managing different types of contour similarity classifiers.

Imports (including optional/function-local imports; not a startup dependency list): `.base_model`, `.model_factory`, `.sgd_model`.

Package-level import/export surface:

```python
from .base_model import BaseModel
from .sgd_model import SGDModel
from .model_factory import ModelFactory
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['BaseModel', 'SGDModel', 'ModelFactory']
```

## `base_model.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/models/base_model.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/models/base_model.py).

Abstract Base Model Interface Provides the abstract base class and interfaces for machine learning models used in shape similarity detection, ensuring consistent APIs and behavior.

Imports (including optional/function-local imports; not a startup dependency list): `...utils.metrics`, `..features.base_extractor`, `abc`, `datetime`, `joblib`, `numpy`, `pathlib`, `pickle`, `typing`.

### `PredictionResult`

```python
class PredictionResult:
```

Container for model prediction results

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, prediction: int, confidence: float, probabilities: Optional[np.ndarray]=None, features: Optional[np.ndarray]=None, metadata: Optional[Dict[str, Any]]=None)
```

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary representation

### `ModelMetrics`

```python
class ModelMetrics:
```

Container for model performance metrics

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, metrics: Dict[str, float])
```

```python
@property
def accuracy(self) -> float
```

```python
@property
def precision(self) -> float
```

```python
@property
def recall(self) -> float
```

```python
@property
def f1_score(self) -> float
```

```python
def get_metric(self, name: str, default: float=0.0) -> float
```

```python
def to_dict(self) -> Dict[str, float]
```

### `BaseModel`

```python
class BaseModel(ABC):
```

Abstract base class for all shape similarity models. Defines the interface that all models must implement for consistent training, prediction, and evaluation behavior.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

Initialize the model Args: config: Model configuration dictionary

```python
@abstractmethod
def fit(self, X: np.ndarray, y: np.ndarray) -> 'BaseModel'
```

Train the model on the provided data Args: X: Feature matrix of shape (n_samples, n_features) y: Labels of shape (n_samples,) Returns: Self for method chaining

```python
@abstractmethod
def predict(self, X: np.ndarray) -> np.ndarray
```

Make predictions on the provided data Args: X: Feature matrix of shape (n_samples, n_features) Returns: Predictions of shape (n_samples,)

```python
@abstractmethod
def predict_proba(self, X: np.ndarray) -> np.ndarray
```

Predict class probabilities Args: X: Feature matrix of shape (n_samples, n_features) Returns: Probabilities of shape (n_samples, n_classes)

```python
def predict_similarity(self, contour1: np.ndarray, contour2: np.ndarray, feature_extractor: 'BaseFeatureExtractor') -> PredictionResult
```

Predict similarity between two contours Args: contour1: First contour contour2: Second contour feature_extractor: Feature extractor to use Returns: PredictionResult object with prediction details

```python
def evaluate(self, X: np.ndarray, y: np.ndarray) -> ModelMetrics
```

Evaluate model performance on test data Args: X: Test feature matrix y: Test labels Returns: ModelMetrics object with performance metrics

```python
def get_feature_importance(self) -> Optional[np.ndarray]
```

Get feature importance scores if available Returns: Feature importance array or None if not available

```python
def get_model_info(self) -> Dict[str, Any]
```

Get information about the model Returns: Dictionary with model information

```python
def save_model(self, filepath: Union[str, Path]) -> None
```

Save the model to file Args: filepath: Path to save the model

```python
@classmethod
def load_model(cls, filepath: Union[str, Path]) -> 'BaseModel'
```

Load a model from file Args: filepath: Path to the saved model Returns: Loaded model instance

```python
def set_feature_names(self, feature_names: List[str]) -> None
```

Set the feature names for this model

```python
def get_training_history(self) -> Dict[str, Any]
```

Get training history if available

### `ModelCompatibilityChecker`

```python
class ModelCompatibilityChecker:
```

Utility class for checking model compatibility with features and data

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def check_feature_compatibility(model: BaseModel, feature_extractor: 'BaseFeatureExtractor') -> bool
```

Check if model is compatible with feature extractor Args: model: Model to check feature_extractor: Feature extractor to check against Returns: True if compatible

```python
@staticmethod
def check_data_compatibility(model: BaseModel, X: np.ndarray) -> bool
```

Check if model is compatible with input data Args: model: Model to check X: Input data to check Returns: True if compatible

```python
@staticmethod
def get_compatibility_report(model: BaseModel, feature_extractor: 'BaseFeatureExtractor') -> Dict[str, Any]
```

Get detailed compatibility report Args: model: Model to check feature_extractor: Feature extractor to check Returns: Compatibility report dictionary

## `model_factory.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/models/model_factory.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/models/model_factory.py).

Model Factory Provides factory pattern for creating and managing different types of machine learning models for shape similarity detection.

Imports (including optional/function-local imports; not a startup dependency list): `...config.model_configs`, `.base_model`, `.sgd_model`, `json`, `numpy`, `pathlib`, `time`, `typing`, `yaml`.

### `ModelFactory`

```python
class ModelFactory:
```

Factory for creating and managing model instances

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def register_model(cls, name: str, model_class: Type[BaseModel]) -> None
```

Register a model class Args: name: Name to register the model under model_class: Model class to register

```python
@classmethod
def create_model(cls, model_type: str, config: Optional[Dict[str, Any]]=None) -> BaseModel
```

Create a model instance Args: model_type: Type of model to create config: Model configuration Returns: Model instance Raises: ValueError: If model type is unknown

```python
@classmethod
def create_sgd_model(cls, config_name: str='default', **kwargs) -> SGDModel
```

Create SGD model with predefined configuration Args: config_name: Name of predefined configuration ('default', 'robust', 'fast') **kwargs: Additional configuration overrides Returns: SGD model instance

```python
@classmethod
def create_online_sgd_model(cls, config_name: str='fast', **kwargs) -> OnlineSGDModel
```

Create online SGD model optimized for incremental learning Args: config_name: Name of predefined configuration **kwargs: Additional configuration overrides Returns: Online SGD model instance

```python
@classmethod
def create_ensemble_model(cls, model_configs: List[Dict[str, Any]], ensemble_method: str='voting') -> 'EnsembleModel'
```

Create ensemble model from multiple base models Args: model_configs: List of model configurations ensemble_method: Method for ensemble ('voting', 'weighted', 'stacking') Returns: Ensemble model instance

```python
@classmethod
def list_available_models(cls) -> Dict[str, str]
```

List all available model types with descriptions Returns: Dictionary mapping model names to descriptions

```python
@classmethod
def get_model_info(cls, model_type: str) -> Dict[str, Any]
```

Get information about a model type Args: model_type: Type of model to get info for Returns: Model information dictionary

```python
@classmethod
def create_model_from_config_file(cls, config_path: str) -> BaseModel
```

Create model from configuration file Args: config_path: Path to configuration file (JSON or YAML) Returns: Model instance

### `EnsembleModel`

```python
class EnsembleModel(BaseModel):
```

Ensemble model that combines multiple base models

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, models: List[BaseModel], ensemble_method: str='voting', weights: Optional[List[float]]=None)
```

Initialize ensemble model Args: models: List of base models ensemble_method: Ensemble method ('voting', 'weighted', 'average') weights: Weights for weighted ensemble (optional)

```python
def fit(self, X: np.ndarray, y: np.ndarray) -> 'EnsembleModel'
```

Fit all models in the ensemble Args: X: Feature matrix y: Labels Returns: Self for method chaining

```python
def predict(self, X: np.ndarray) -> np.ndarray
```

Make ensemble predictions Args: X: Feature matrix Returns: Predictions

```python
def predict_proba(self, X: np.ndarray) -> np.ndarray
```

Predict class probabilities using ensemble Args: X: Feature matrix Returns: Probabilities

```python
def get_model_info(self) -> Dict[str, Any]
```

Get ensemble model information

```python
def get_feature_importance(self) -> Optional[np.ndarray]
```

Get averaged feature importance from all models Returns: Average feature importance or None

## `sgd_model.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/models/sgd_model.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/models/sgd_model.py).

SGD Model Implementation Provides SGD (Stochastic Gradient Descent) classifier implementation with calibrated probability outputs for shape similarity detection.

Imports (including optional/function-local imports; not a startup dependency list): `...config.model_configs`, `.base_model`, `numpy`, `sklearn.calibration`, `sklearn.linear_model`, `sklearn.preprocessing`, `time`, `traceback`, `typing`.

### `SGDModel`

```python
class SGDModel(BaseModel):
```

SGD classifier implementation with probability calibration for shape similarity detection.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

Initialize SGD model Args: config: Model configuration dictionary or SGDCalibratedConfig

```python
def fit(self, X: np.ndarray, y: np.ndarray) -> 'SGDModel'
```

Fit the SGD model with calibration Args: X: Feature matrix of shape (n_samples, n_features) y: Labels of shape (n_samples,) Returns: Self for method chaining

```python
def predict(self, X: np.ndarray) -> np.ndarray
```

Make predictions Args: X: Feature matrix of shape (n_samples, n_features) Returns: Predictions of shape (n_samples,)

```python
def predict_proba(self, X: np.ndarray) -> np.ndarray
```

Predict class probabilities Args: X: Feature matrix of shape (n_samples, n_features) Returns: Probabilities of shape (n_samples, 2)

```python
def score(self, X: np.ndarray, y: np.ndarray) -> float
```

Return the mean accuracy on the given test data and labels Args: X: Feature matrix of shape (n_samples, n_features) y: True labels of shape (n_samples,) Returns: Mean accuracy score

```python
def predict_with_confidence(self, X: np.ndarray, confidence_threshold: float=0.8) -> tuple
```

Make predictions with confidence filtering Args: X: Feature matrix confidence_threshold: Minimum confidence for predictions Returns: Tuple of (predictions, confidences, high_confidence_mask)

```python
def get_feature_importance(self) -> Optional[np.ndarray]
```

Get feature importance based on coefficient magnitudes Returns: Feature importance array or None

```python
def get_model_info(self) -> Dict[str, Any]
```

Get comprehensive model information

```python
def partial_fit(self, X: np.ndarray, y: np.ndarray, classes: Optional[List]=None)
```

Perform incremental learning on a batch of data Args: X: Feature matrix y: Labels classes: Array of possible classes (required for first call)

```python
def get_decision_function(self, X: np.ndarray) -> np.ndarray
```

Get decision function values Args: X: Feature matrix Returns: Decision function values

### `OnlineSGDModel`

```python
class OnlineSGDModel(SGDModel):
```

SGD model optimized for online/incremental learning without calibration for faster updates.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

Initialize online SGD model

```python
def fit(self, X: np.ndarray, y: np.ndarray) -> 'OnlineSGDModel'
```

Fit the online SGD model (without calibration) Args: X: Feature matrix of shape (n_samples, n_features) y: Labels of shape (n_samples,) Returns: Self for method chaining

```python
def predict_proba(self, X: np.ndarray) -> np.ndarray
```

Predict class probabilities (may not be well-calibrated) Args: X: Feature matrix of shape (n_samples, n_features) Returns: Probabilities of shape (n_samples, 2)

```python
def get_model_info(self) -> Dict[str, Any]
```

Get model information
