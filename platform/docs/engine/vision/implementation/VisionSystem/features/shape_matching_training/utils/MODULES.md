# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [io_utils.py](#io_utilspy)
- [metrics.py](#metricspy)
- [validation.py](#validationpy)
- [visualization.py](#visualizationpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/__init__.py).

Utility Functions Module Provides common utilities for I/O operations, visualization, metrics calculation, and data validation used throughout the shape matching training vision_service.

Imports (including optional/function-local imports; not a startup dependency list): `.io_utils`, `.metrics`, `.validation`, `.visualization`.

Package-level import/export surface:

```python
from .io_utils import load_model, save_model, load_dataset, save_dataset
from .visualization import plot_confusion_matrix, plot_feature_importance, plot_training_history
from .metrics import calculate_similarity_metrics, evaluate_model_performance
from .validation import validate_contour, validate_features, validate_config
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['load_model', 'save_model', 'load_dataset', 'save_dataset', 'plot_confusion_matrix', 'plot_feature_importance', 'plot_training_history', 'calculate_similarity_metrics', 'evaluate_model_performance', 'validate_contour', 'validate_features', 'validate_config']
```

## `io_utils.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/io_utils.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/io_utils.py).

I/O Utilities Module Provides utilities for loading and saving models, datasets, and configurations with comprehensive metadata management and versioning.

Imports (including optional/function-local imports; not a startup dependency list): `..core.features.base_extractor`, `datetime`, `joblib`, `json`, `os`, `pathlib`, `pickle`, `shutil`, `typing`.

### `ModelMetadata`

```python
class ModelMetadata:
```

Manages model metadata including feature extraction requirements, training information, and compatibility details.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model_name: str, accuracy: float, training_config: Optional[Dict]=None, feature_metadata: Optional[Dict]=None, dataset_info: Optional[Dict]=None)
```

```python
def to_dict(self) -> Dict[str, Any]
```

Convert metadata to dictionary for serialization

```python
@classmethod
def from_dict(cls, metadata_dict: Dict[str, Any]) -> 'ModelMetadata'
```

Create metadata from dictionary

### `save_model`

```python
def save_model(model: Any, model_name: str, accuracy: float, save_dir: Union[str, Path]='saved_models', training_config: Optional[Dict]=None, feature_metadata: Optional[Dict]=None, dataset_info: Optional[Dict]=None) -> Tuple[Path, Path]
```

Save trained model with comprehensive metadata in timestamped folder Args: model: Trained model object to save model_name: Name/type of the model accuracy: Model accuracy for filename save_dir: Directory to save models in training_config: Training configuration used feature_metadata: Feature extraction metadata dataset_info: Dataset generation information Returns: Tuple of (model_filepath, model_folder_path)

### `_save_model_summary`

```python
def _save_model_summary(summary_file: Path, metadata: ModelMetadata, filename: str, dataset_info: Optional[Dict]) -> None
```

Save a human-readable summary file

### `load_model`

```python
def load_model(filepath: Union[str, Path]) -> Any
```

Load a saved model from file Args: filepath: Path to the model file Returns: Loaded model object Raises: FileNotFoundError: If model file doesn't exist

### `list_saved_models`

```python
def list_saved_models(save_dir: Union[str, Path]='saved_models') -> List[Dict[str, Any]]
```

List all saved models with their metadata Args: save_dir: Directory containing saved models Returns: List of model information dictionaries

### `get_latest_model`

```python
def get_latest_model(save_dir: Union[str, Path]='saved_models') -> Path
```

Get the path to the most recently saved model Args: save_dir: Directory containing saved models Returns: Path to the latest model file Raises: FileNotFoundError: If no models are found

### `load_latest_model`

```python
def load_latest_model(save_dir: Union[str, Path]='saved_models') -> Any
```

Load the most recently saved model Args: save_dir: Directory containing saved models Returns: Loaded model object

### `get_model_metadata`

```python
def get_model_metadata(model_path: Union[str, Path]) -> Dict[str, Any]
```

Get metadata for a saved model Args: model_path: Path to model file Returns: Model metadata dictionary

### `cleanup_old_models`

```python
def cleanup_old_models(save_dir: Union[str, Path]='saved_models', keep_latest: int=5) -> int
```

Delete old models, keeping only the most recent ones Args: save_dir: Directory containing saved models keep_latest: Number of latest models to keep Returns: Number of models deleted

### `save_dataset`

```python
def save_dataset(dataset: Any, pairs: List, labels: List, save_dir: Union[str, Path]='saved_datasets', dataset_config: Optional[Dict]=None) -> Tuple[Path, Path]
```

Save dataset with metadata in timestamped folder Args: dataset: Original dataset object pairs: Training pairs labels: Corresponding labels save_dir: Directory to save datasets dataset_config: Dataset generation configuration Returns: Tuple of (dataset_filepath, dataset_folder_path)

### `load_dataset`

```python
def load_dataset(filepath: Union[str, Path]) -> Tuple[List, List]
```

Load saved dataset Args: filepath: Path to the dataset file Returns: Tuple of (pairs, labels)

### `predict_similarity`

```python
def predict_similarity(model, contour1, contour2)
```

Compatibility function for the old predict_similarity interface. Use trained model to predict similarity between two contours. Args: model: Trained model (should have predict and predict_proba methods) contour1: First contour (numpy array) contour2: Second contour (numpy array) Returns: Tuple of (result, confidence, features) where: - result: "SAME", "DIFFERENT", or "UNCERTAIN" - confidence: Confidence score (0-1) - features: Extracted features used for prediction

## `metrics.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/metrics.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/metrics.py).

Metrics Utilities Module Provides custom metrics and evaluation functions for shape similarity models, including performance analysis and statistical tests.

Imports (including optional/function-local imports; not a startup dependency list): `numpy`, `scipy.stats`, `sklearn.metrics`, `typing`.

### `calculate_similarity_metrics`

```python
def calculate_similarity_metrics(y_true: List[int], y_pred: List[int], y_proba: Optional[List[float]]=None) -> Dict[str, float]
```

Calculate comprehensive similarity metrics Args: y_true: True labels (0 for different, 1 for same) y_pred: Predicted labels y_proba: Predicted probabilities for positive class (optional) Returns: Dictionary of calculated metrics

### `evaluate_model_performance`

```python
def evaluate_model_performance(model: Any, X_test: np.ndarray, y_test: List[int], model_name: str='Model') -> Dict[str, Any]
```

Comprehensive model performance evaluation Args: model: Trained model with predict and predict_proba methods X_test: Test features y_test: Test labels model_name: Name of the model for reporting Returns: Dictionary with comprehensive evaluation results

### `calculate_confidence_metrics`

```python
def calculate_confidence_metrics(confidences: List[float], predictions: List[int], true_labels: List[int]) -> Dict[str, float]
```

Calculate metrics related to prediction confidence Args: confidences: List of confidence scores predictions: List of predicted labels true_labels: List of true labels Returns: Dictionary of confidence-related metrics

### `perform_statistical_tests`

```python
def perform_statistical_tests(results1: Dict[str, Any], results2: Dict[str, Any], alpha: float=0.05) -> Dict[str, Any]
```

Perform statistical significance tests between two models Args: results1: Results from first model results2: Results from second model alpha: Significance level for tests Returns: Dictionary with statistical test results

### `analyze_error_patterns`

```python
def analyze_error_patterns(y_true: List[int], y_pred: List[int], feature_matrix: np.ndarray, feature_names: List[str]) -> Dict[str, Any]
```

Analyze patterns in prediction errors Args: y_true: True labels y_pred: Predicted labels feature_matrix: Feature matrix used for predictions feature_names: Names of features Returns: Dictionary with error analysis results

### `calculate_feature_stability`

```python
def calculate_feature_stability(feature_matrices: List[np.ndarray], feature_names: List[str]) -> Dict[str, float]
```

Calculate stability of features across multiple runs or datasets Args: feature_matrices: List of feature matrices from different runs feature_names: Names of features Returns: Dictionary with stability metrics per feature

## `validation.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/validation.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/validation.py).

Validation Utilities Module Provides data validation functions for contours, features, configurations, and other inputs to ensure data quality and consistency.

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `numpy`, `pathlib`, `typing`.

### `ValidationError`

```python
class ValidationError(Exception):
```

Raised when validation fails

### `validate_contour`

```python
def validate_contour(contour: np.ndarray, min_points: int=3, max_points: Optional[int]=None, min_area: float=1.0, max_area: Optional[float]=None) -> bool
```

Validate that a contour meets basic requirements Args: contour: OpenCV contour array min_points: Minimum number of points required max_points: Maximum number of points allowed (optional) min_area: Minimum contour area required max_area: Maximum contour area allowed (optional) Returns: True if valid Raises: ValidationError: If validation fails

### `validate_features`

```python
def validate_features(features: Union[List, np.ndarray], expected_length: Optional[int]=None, allow_nan: bool=False, allow_inf: bool=False, feature_names: Optional[List[str]]=None) -> bool
```

Validate feature vector Args: features: Feature vector or list expected_length: Expected number of features allow_nan: Whether to allow NaN values allow_inf: Whether to allow infinite values feature_names: Names of features for detailed error messages Returns: True if valid Raises: ValidationError: If validation fails

### `validate_training_data`

```python
def validate_training_data(X: np.ndarray, y: np.ndarray, min_samples: int=10, check_balance: bool=True, balance_threshold: float=0.1) -> bool
```

Validate training data matrices Args: X: Feature matrix y: Label vector min_samples: Minimum number of samples required check_balance: Whether to check class balance balance_threshold: Maximum allowed imbalance ratio Returns: True if valid Raises: ValidationError: If validation fails

### `validate_model_predictions`

```python
def validate_model_predictions(predictions: np.ndarray, probabilities: Optional[np.ndarray]=None, expected_classes: Tuple[int, ...]=(0, 1)) -> bool
```

Validate model predictions and probabilities Args: predictions: Predicted class labels probabilities: Predicted probabilities (optional) expected_classes: Expected class labels Returns: True if valid Raises: ValidationError: If validation fails

### `validate_config`

```python
def validate_config(config_dict: Dict[str, Any], required_keys: List[str], optional_keys: Optional[List[str]]=None) -> bool
```

Validate configuration dictionary Args: config_dict: Configuration dictionary to validate required_keys: List of required keys optional_keys: List of optional keys (default: allow any) Returns: True if valid Raises: ValidationError: If validation fails

### `validate_file_path`

```python
def validate_file_path(filepath: Union[str, Path], must_exist: bool=True, must_be_file: bool=True, allowed_extensions: Optional[List[str]]=None) -> bool
```

Validate file path Args: filepath: Path to validate must_exist: Whether file must exist must_be_file: Whether path must be a file (not directory) allowed_extensions: List of allowed file extensions (e.g., ['.pkl', '.json']) Returns: True if valid Raises: ValidationError: If validation fails

### `validate_dataset_pairs`

```python
def validate_dataset_pairs(pairs: List[Tuple], labels: List[int], min_pairs: int=10) -> bool
```

Validate dataset pairs and labels Args: pairs: List of (contour1, contour2) tuples labels: List of corresponding labels min_pairs: Minimum number of pairs required Returns: True if valid Raises: ValidationError: If validation fails

### `validate_feature_matrix_consistency`

```python
def validate_feature_matrix_consistency(feature_matrices: List[np.ndarray], tolerance: float=1e-06) -> bool
```

Validate that feature matrices have consistent dimensions and reasonable values Args: feature_matrices: List of feature matrices to compare tolerance: Tolerance for numerical comparisons Returns: True if valid Raises: ValidationError: If validation fails

## `visualization.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/visualization.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/utils/visualization.py).

Visualization Utilities Module Provides plotting and visualization functions for model evaluation, training progress, and result analysis.

Imports (including optional/function-local imports; not a startup dependency list): `cv2`, `matplotlib.pyplot`, `numpy`, `pandas`, `seaborn`, `sklearn.metrics`, `typing`.

### `plot_confusion_matrix`

```python
def plot_confusion_matrix(y_true: List[int], y_pred: List[int], model_name: str='Model', normalize: bool=False, save_path: Optional[str]=None, show_plot: bool=True) -> plt.Figure
```

Create an enhanced confusion matrix visualization Args: y_true: True labels y_pred: Predicted labels model_name: Name of the model for title normalize: Whether to normalize the confusion matrix save_path: Optional path to save the plot show_plot: Whether to display the plot Returns: Matplotlib figure object

### `plot_feature_importance`

```python
def plot_feature_importance(feature_importances: np.ndarray, feature_names: List[str], model_name: str='Model', top_k: int=15, save_path: Optional[str]=None, show_plot: bool=True) -> plt.Figure
```

Plot feature importance ranking Args: feature_importances: Array of feature importance values feature_names: List of feature names model_name: Name of the model for title top_k: Number of top features to display save_path: Optional path to save the plot show_plot: Whether to display the plot Returns: Matplotlib figure object

### `plot_model_comparison`

```python
def plot_model_comparison(results: Dict[str, Dict[str, Any]], metric: str='accuracy', save_path: Optional[str]=None, show_plot: bool=True) -> plt.Figure
```

Create comparison plot of multiple models Args: results: Dictionary of model results with metrics metric: Metric to compare (e.g., 'accuracy', 'f1_score') save_path: Optional path to save the plot show_plot: Whether to display the plot Returns: Matplotlib figure object

### `plot_training_history`

```python
def plot_training_history(history: Dict[str, List[float]], save_path: Optional[str]=None, show_plot: bool=True) -> plt.Figure
```

Plot training history (loss, accuracy over epochs) Args: history: Dictionary with training history data save_path: Optional path to save the plot show_plot: Whether to display the plot Returns: Matplotlib figure object

### `plot_prediction_confidence_distribution`

```python
def plot_prediction_confidence_distribution(confidences: List[float], predictions: List[int], save_path: Optional[str]=None, show_plot: bool=True) -> plt.Figure
```

Plot distribution of prediction confidences Args: confidences: List of confidence scores predictions: List of predictions (0/1) save_path: Optional path to save the plot show_plot: Whether to display the plot Returns: Matplotlib figure object

### `create_classification_report_plot`

```python
def create_classification_report_plot(y_true: List[int], y_pred: List[int], model_name: str='Model', save_path: Optional[str]=None, show_plot: bool=True) -> plt.Figure
```

Create a visual classification report Args: y_true: True labels y_pred: Predicted labels model_name: Name of the model save_path: Optional path to save the plot show_plot: Whether to display the plot Returns: Matplotlib figure object

### `visualize_training_results`

```python
def visualize_training_results(results: Dict[str, Dict[str, Any]], save_dir: Optional[str]=None) -> Dict[str, plt.Figure]
```

Create comprehensive visualization of training results Args: results: Training results from all models save_dir: Optional directory to save plots Returns: Dictionary of created figure objects

### `create_shape_similarity_showcase`

```python
def create_shape_similarity_showcase(contour_pairs: List[Tuple], predictions: List[str], confidences: List[float], n_examples: int=6, save_path: Optional[str]=None, show_plot: bool=True) -> plt.Figure
```

Create a showcase of shape similarity predictions Args: contour_pairs: List of (contour1, contour2) tuples predictions: List of prediction strings ('SAME', 'DIFFERENT') confidences: List of confidence scores n_examples: Number of examples to show save_path: Optional path to save the plot show_plot: Whether to display the plot Returns: Matplotlib figure object
