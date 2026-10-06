# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/training`

[Package guide](README.md) · [Complete source index](../../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [evaluator.py](#evaluatorpy)
- [pipeline.py](#pipelinepy)
- [trainer.py](#trainerpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/training/__init__.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/training/__init__.py).

Training Pipeline Module Provides training orchestration, model evaluation, and end-to-end pipeline management for shape matching model development.

Imports (including optional/function-local imports; not a startup dependency list): `.evaluator`, `.pipeline`, `.trainer`.

Package-level import/export surface:

```python
from .trainer import ModelTrainer
from .evaluator import ModelEvaluator
from .pipeline import TrainingPipeline
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ModelTrainer', 'ModelEvaluator', 'TrainingPipeline']
```

## `evaluator.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/training/evaluator.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/training/evaluator.py).

Model Evaluator Module Provides comprehensive evaluation capabilities for trained models including performance metrics, statistical tests, and comparative analysis.

Imports (including optional/function-local imports; not a startup dependency list): `...utils.metrics`, `...utils.visualization`, `..models.base_model`, `json`, `numpy`, `pathlib`, `pickle`, `sklearn.metrics`, `sklearn.model_selection`, `typing`.

### `ModelEvaluator`

```python
class ModelEvaluator:
```

Comprehensive model evaluation with statistical analysis and visualization

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, save_visualizations: bool=True, output_dir: Optional[str]=None)
```

Initialize model evaluator Args: save_visualizations: Whether to save visualization plots output_dir: Directory to save outputs (optional)

```python
def evaluate_single_model(self, model: BaseModel, X_test: np.ndarray, y_test: np.ndarray, model_name: str='Model') -> Dict[str, Any]
```

Comprehensive evaluation of a single model Args: model: Trained model to evaluate X_test: Test features y_test: Test labels model_name: Name for the model Returns: Comprehensive evaluation results

```python
def cross_validate_model(self, model: BaseModel, X: np.ndarray, y: np.ndarray, cv_folds: int=5, scoring: List[str]=None) -> Dict[str, Any]
```

Perform cross-validation evaluation Args: model: Model to evaluate (will be cloned for each fold) X: Features y: Labels cv_folds: Number of CV folds scoring: List of scoring metrics Returns: Cross-validation results

```python
def compare_models(self, model_results: Dict[str, Dict[str, Any]], comparison_metrics: List[str]=None) -> Dict[str, Any]
```

Compare multiple model evaluation results Args: model_results: Dictionary of model evaluation results comparison_metrics: Metrics to compare (default: main metrics) Returns: Comparison analysis results

```python
def evaluate_model_robustness(self, model: BaseModel, X_test: np.ndarray, y_test: np.ndarray, noise_levels: List[float]=None) -> Dict[str, Any]
```

Evaluate model robustness to input noise Args: model: Trained model X_test: Clean test data y_test: Test labels noise_levels: Levels of Gaussian noise to test Returns: Robustness evaluation results

```python
def generate_evaluation_report(self, evaluation_results: Union[Dict[str, Any], List[Dict[str, Any]]], report_title: str='Model Evaluation Report') -> str
```

Generate a comprehensive evaluation report Args: evaluation_results: Single or multiple evaluation results report_title: Title for the report Returns: Formatted report string

```python
def export_results(self, results: Dict[str, Any], filepath: str)
```

Export evaluation results to file

## `pipeline.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/training/pipeline.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/training/pipeline.py).

Training Pipeline Module Provides end-to-end training pipeline orchestration for shape similarity models, integrating data generation, feature extraction, model training, and evaluation.

Imports (including optional/function-local imports; not a startup dependency list): `...config.training_configs`, `...utils.io_utils`, `...utils.visualization`, `..dataset.data_augmentation`, `..dataset.pair_generator`, `..dataset.shape_factory`, `..dataset.synthetic_dataset`, `..features.base_extractor`, `..models.model_factory`, `.evaluator`, `.trainer`, `json`, `numpy`, `pathlib`, `time`, `typing`.

### `TrainingPipeline`

```python
class TrainingPipeline:
```

End-to-end training pipeline for shape similarity models

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Union[str, Dict[str, Any]]]=None)
```

Initialize training pipeline Args: config: Training configuration (name, dict, or config object)

```python
def run_complete_pipeline(self, save_models: bool=True, save_datasets: bool=True) -> Dict[str, Any]
```

Run the complete training pipeline from data generation to model evaluation Args: save_models: Whether to save trained models save_datasets: Whether to save generated datasets Returns: Complete pipeline results

```python
def run_training_only(self, contour_pairs: List[Tuple], labels: List[int], feature_extractor: Optional[CompositeFeatureExtractor]=None) -> Dict[str, Any]
```

Run training pipeline with provided data Args: contour_pairs: Pre-generated contour pairs labels: Corresponding labels feature_extractor: Optional feature extractor (will create default if None) Returns: Training results

```python
def get_pipeline_config_template(self) -> Dict[str, Any]
```

Get a template for pipeline configuration

```python
def save_pipeline_config(self, filepath: str)
```

Save current pipeline configuration

```python
@classmethod
def from_config_file(cls, config_path: str) -> 'TrainingPipeline'
```

Create pipeline from configuration file

### `quick_training_pipeline`

```python
def quick_training_pipeline(n_shapes: int=6, enable_viz: bool=True) -> Dict[str, Any]
```

Run a quick training pipeline with minimal configuration Args: n_shapes: Number of shape types to use enable_viz: Whether to generate visualizations Returns: Training results

### `production_training_pipeline`

```python
def production_training_pipeline(config_path: Optional[str]=None) -> Dict[str, Any]
```

Run a production-ready training pipeline with comprehensive evaluation Args: config_path: Path to configuration file (optional) Returns: Training results

## `trainer.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/training/trainer.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/training/trainer.py).

Model Trainer Module Provides the core training functionality for shape similarity models with comprehensive logging, monitoring, and evaluation capabilities.

Imports (including optional/function-local imports; not a startup dependency list): `...config.training_configs`, `...utils.metrics`, `...utils.validation`, `..features.base_extractor`, `..models.base_model`, `..models.model_factory`, `concurrent.futures`, `functools`, `multiprocessing`, `numpy`, `sklearn.model_selection`, `time`, `typing`.

### `TrainingProgress`

```python
class TrainingProgress:
```

Container for tracking training progress

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def start(self)
```

Mark training start

```python
def update_stage(self, stage: str, progress: float=None, **info)
```

Update current training stage

```python
def add_warning(self, warning: str)
```

Add a warning message

```python
def add_error(self, error: str)
```

Add an error message

```python
def get_elapsed_time(self) -> float
```

Get elapsed training time

```python
def to_dict(self) -> Dict[str, Any]
```

Convert to dictionary

### `ModelTrainer`

```python
class ModelTrainer:
```

Core trainer class for shape similarity models

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, feature_extractor: BaseFeatureExtractor, config: Optional[Union[Dict[str, Any], TrainingConfig]]=None)
```

Initialize model trainer Args: feature_extractor: Feature extractor to use config: Training configuration

```python
def train_model(self, model_config: Dict[str, Any], contour_pairs: List[Tuple], labels: List[int], validation_split: Optional[float]=None) -> Dict[str, Any]
```

Train a single model Args: model_config: Model configuration dictionary contour_pairs: List of (contour1, contour2) tuples labels: Corresponding labels validation_split: Validation set size (optional) Returns: Training results dictionary

```python
def train_multiple_models(self, model_configs: List[Dict[str, Any]], contour_pairs: List[Tuple], labels: List[int]) -> Dict[str, Dict[str, Any]]
```

Train multiple models and compare results Args: model_configs: List of model configurations contour_pairs: Training data labels: Training labels Returns: Dictionary of results for each model

```python
def get_training_summary(self, results: Dict[str, Any]) -> str
```

Generate human-readable training summary
