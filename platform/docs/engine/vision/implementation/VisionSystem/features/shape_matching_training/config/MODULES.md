# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/config`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [base_config.py](#base_configpy)
- [model_configs.py](#model_configspy)
- [training_configs.py](#training_configspy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/config/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/config/__init__.py).

Configuration Management Module Provides configuration classes and utilities for the shape matching training vision_service. Supports hierarchical configuration, validation, and environment-specific settings.

Imports (including optional/function-local imports; not a startup dependency list): `.base_config`, `.model_configs`, `.training_configs`.

Package-level import/export surface:

```python
from .base_config import BaseConfig
from .model_configs import ModelConfigRegistry
from .training_configs import DefaultTrainingConfig, RobustTrainingConfig, FastTrainingConfig
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['BaseConfig', 'ModelConfigRegistry', 'DefaultTrainingConfig', 'RobustTrainingConfig', 'FastTrainingConfig']
```

## `base_config.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/config/base_config.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/config/base_config.py).

Base Configuration Classes Provides abstract base classes and utilities for configuration management with validation, inheritance, and serialization capabilities.

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `dataclasses`, `json`, `pathlib`, `typing`, `yaml`.

Module declarations (expressions are shown without evaluating them):

```python
T = TypeVar('T', bound='BaseConfig')
```

### `ConfigValidationError`

```python
class ConfigValidationError(Exception):
```

Raised when configuration validation fails

### `BaseConfig`

```python
@dataclass
class BaseConfig(ABC):
```

Abstract base class for all configuration objects. Provides common functionality for validation, serialization, and configuration inheritance.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def validate(self) -> None
```

Validate configuration parameters. Raises: ConfigValidationError: If validation fails

```python
def to_dict(self) -> Dict[str, Any]
```

Convert configuration to dictionary

```python
def to_json(self, filepath: Optional[Path]=None) -> str
```

Convert configuration to JSON string or save to file. Args: filepath: Optional path to save JSON file Returns: JSON string representation

```python
def to_yaml(self, filepath: Optional[Path]=None) -> str
```

Convert configuration to YAML string or save to file. Args: filepath: Optional path to save YAML file Returns: YAML string representation Raises: ImportError: If PyYAML is not installed

```python
@classmethod
def from_dict(cls: Type[T], config_dict: Dict[str, Any]) -> T
```

Create configuration from dictionary. Args: config_dict: Configuration parameters as dictionary Returns: Configuration instance

```python
@classmethod
def from_json(cls: Type[T], json_str_or_path: str) -> T
```

Create configuration from JSON string or file. Args: json_str_or_path: JSON string or path to JSON file Returns: Configuration instance

```python
@classmethod
def from_yaml(cls: Type[T], yaml_str_or_path: str) -> T
```

Create configuration from YAML string or file. Args: yaml_str_or_path: YAML string or path to YAML file Returns: Configuration instance Raises: ImportError: If PyYAML is not installed

```python
def merge(self: T, other: T) -> T
```

Merge this configuration with another configuration. Other configuration takes precedence for conflicting values. Args: other: Configuration to merge with Returns: New merged configuration instance

### `validate_positive_number`

```python
def validate_positive_number(value: float, name: str) -> None
```

Validate that a value is a positive number. Args: value: Value to validate name: Parameter name for error messages Raises: ConfigValidationError: If validation fails

### `validate_probability`

```python
def validate_probability(value: float, name: str) -> None
```

Validate that a value is a valid probability (0-1). Args: value: Value to validate name: Parameter name for error messages Raises: ConfigValidationError: If validation fails

### `validate_positive_integer`

```python
def validate_positive_integer(value: int, name: str) -> None
```

Validate that a value is a positive integer. Args: value: Value to validate name: Parameter name for error messages Raises: ConfigValidationError: If validation fails

### `validate_choice`

```python
def validate_choice(value: Any, choices: list, name: str) -> None
```

Validate that a value is one of the allowed choices. Args: value: Value to validate choices: List of allowed choices name: Parameter name for error messages Raises: ConfigValidationError: If validation fails

## `model_configs.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/config/model_configs.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/config/model_configs.py).

Model Configuration Classes Provides configuration classes for different machine learning models with comprehensive parameter validation and documentation.

Imports (including optional/function-local imports; not a startup dependency list): `.base_config`, `dataclasses`, `typing`.

### `SGDClassifierConfig`

```python
@dataclass
class SGDClassifierConfig(BaseConfig):
```

Configuration for SGDClassifier (Stochastic Gradient Descent Classifier) SGD is an online learning algorithm that updates model parameters for each training sample, making it suitable for large datasets and online/incremental learning scenarios.

Declared fields/defaults:

```python
loss: str = 'log_loss'
penalty: Optional[str] = 'l2'
alpha: float = 0.0001
l1_ratio: float = 0.15
fit_intercept: bool = True
max_iter: int = 1000
tol: Optional[float] = 0.001
shuffle: bool = True
verbose: int = 0
epsilon: float = 0.1
learning_rate: str = 'optimal'
eta0: float = 0.01
power_t: float = 0.5
early_stopping: bool = False
validation_fraction: float = 0.1
n_iter_no_change: int = 5
class_weight: Optional[Union[Dict, str]] = None
warm_start: bool = False
average: Union[bool, int] = False
random_state: Optional[int] = 42
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate SGD classifier configuration parameters

### `CalibratedClassifierConfig`

```python
@dataclass
class CalibratedClassifierConfig(BaseConfig):
```

Configuration for CalibratedClassifierCV (Probability Calibration) Calibration improves the reliability of predicted probabilities by mapping the classifier's output to better-calibrated probability estimates.

Declared fields/defaults:

```python
method: str = 'sigmoid'
cv: Union[int, str, None] = 3
n_jobs: Optional[int] = None
ensemble: bool = True
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate calibration configuration parameters

### `SGDCalibratedConfig`

```python
@dataclass
class SGDCalibratedConfig(BaseConfig):
```

Complete configuration for SGD Online (Calibrated) model combining SGDClassifier with CalibratedClassifierCV

Declared fields/defaults:

```python
sgd_config: SGDClassifierConfig = None
calibration_config: CalibratedClassifierConfig = None
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate the combined configuration

```python
def get_model_info(self) -> Dict[str, Any]
```

Get human-readable information about the configured model Returns: Model configuration summary

### `ModelConfigRegistry`

```python
class ModelConfigRegistry:
```

Registry for predefined model configurations. Provides easy access to common model configuration presets for different use cases and performance requirements.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def get_default_sgd_calibrated() -> SGDCalibratedConfig
```

Get the default configuration used in the original training script Returns: Default SGD calibrated configuration

```python
@staticmethod
def get_robust_sgd_calibrated() -> SGDCalibratedConfig
```

Get a more robust configuration for noisy data Returns: Robust SGD calibrated configuration

```python
@staticmethod
def get_fast_sgd_calibrated() -> SGDCalibratedConfig
```

Get a configuration optimized for speed Returns: Fast training SGD calibrated configuration

```python
@classmethod
def list_available_configs(cls) -> Dict[str, str]
```

List all available predefined configurations Returns: Dictionary mapping config names to descriptions

```python
@classmethod
def get_config(cls, config_name: str) -> SGDCalibratedConfig
```

Get a predefined configuration by name Args: config_name: Name of the configuration to retrieve Returns: Requested configuration Raises: ValueError: If configuration name is not found

## `training_configs.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/config/training_configs.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/config/training_configs.py).

Training Configuration Classes Provides configuration classes for training pipeline parameters, dataset generation settings, and evaluation criteria.

Imports (including optional/function-local imports; not a startup dependency list): `.base_config`, `.model_configs`, `dataclasses`, `pathlib`, `typing`.

### `DatasetConfig`

```python
@dataclass
class DatasetConfig(BaseConfig):
```

Configuration for synthetic dataset generation

Declared fields/defaults:

```python
n_shapes: int = 8
n_scales: int = 3
n_variants: int = 5
n_noisy: int = 4
included_shapes: Optional[List[str]] = None
include_hard_negatives: bool = True
img_size: tuple = (256, 256)
noise_level: float = 0.2
deform_strength: float = 0.01
epsilon_ratio: float = 0.01
min_scale: float = 0.5
max_scale: float = 3.0
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate dataset configuration parameters

### `FeatureConfig`

```python
@dataclass
class FeatureConfig(BaseConfig):
```

Configuration for feature extraction

Declared fields/defaults:

```python
n_fourier_descriptors: int = 4
n_curvature_bins: int = 16
use_parallel_processing: bool = True
max_workers: Optional[int] = None
feature_types: List[str] = field(default_factory=lambda: ['hu_moments', 'fourier', 'geometric', 'curvature'])
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate feature extraction configuration

### `TrainingConfig`

```python
@dataclass
class TrainingConfig(BaseConfig):
```

Configuration for training process

Declared fields/defaults:

```python
test_size: float = 0.3
validation_size: float = 0.1
random_state: int = 42
batch_size: int = 1000
enable_visualizations: bool = True
save_intermediate_results: bool = True
model_configs: List[str] = field(default_factory=lambda: ['default', 'robust'])
min_accuracy_threshold: float = 0.95
confidence_threshold: float = 0.8
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate training configuration

### `IOConfig`

```python
@dataclass
class IOConfig(BaseConfig):
```

Configuration for input/output operations

Declared fields/defaults:

```python
models_dir: Path = field(default_factory=lambda: Path('saved_models'))
datasets_dir: Path = field(default_factory=lambda: Path('saved_datasets'))
results_dir: Path = field(default_factory=lambda: Path('results'))
timestamp_format: str = '%Y%m%d_%H%M%S'
model_name_template: str = '{model_type}_acc{accuracy:.3f}'
save_model_metadata: bool = True
save_training_history: bool = True
compress_datasets: bool = False
max_saved_models: int = 10
auto_cleanup: bool = True
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate I/O configuration

### `DefaultTrainingConfig`

```python
@dataclass
class DefaultTrainingConfig(BaseConfig):
```

Complete default configuration for training pipeline

Declared fields/defaults:

```python
dataset: DatasetConfig = field(default_factory=DatasetConfig)
features: FeatureConfig = field(default_factory=FeatureConfig)
training: TrainingConfig = field(default_factory=TrainingConfig)
io: IOConfig = field(default_factory=IOConfig)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate all configuration components

### `RobustTrainingConfig`

```python
@dataclass
class RobustTrainingConfig(BaseConfig):
```

Configuration optimized for robust training with noisy data

Declared fields/defaults:

```python
dataset: DatasetConfig = field(default_factory=lambda: DatasetConfig(n_shapes=15, n_scales=6, n_variants=8, n_noisy=6, noise_level=0.5, include_hard_negatives=True))
features: FeatureConfig = field(default_factory=lambda: FeatureConfig(n_fourier_descriptors=6, n_curvature_bins=20, use_parallel_processing=True))
training: TrainingConfig = field(default_factory=lambda: TrainingConfig(test_size=0.2, validation_size=0.1, model_configs=['robust'], min_accuracy_threshold=0.92, batch_size=500))
io: IOConfig = field(default_factory=IOConfig)
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate robust configuration components

### `FastTrainingConfig`

```python
@dataclass
class FastTrainingConfig(BaseConfig):
```

Configuration optimized for fast training and prototyping

Declared fields/defaults:

```python
dataset: DatasetConfig = field(default_factory=lambda: DatasetConfig(n_shapes=6, n_scales=3, n_variants=3, n_noisy=2, img_size=(128, 128)))
features: FeatureConfig = field(default_factory=lambda: FeatureConfig(n_fourier_descriptors=3, n_curvature_bins=12, use_parallel_processing=True))
training: TrainingConfig = field(default_factory=lambda: TrainingConfig(test_size=0.3, model_configs=['fast'], enable_visualizations=False, batch_size=2000))
io: IOConfig = field(default_factory=lambda: IOConfig(save_training_history=False, max_saved_models=3))
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def validate(self) -> None
```

Validate fast configuration components

### `TrainingConfigRegistry`

```python
class TrainingConfigRegistry:
```

Registry for predefined training configurations

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@staticmethod
def get_default() -> DefaultTrainingConfig
```

Get default training configuration

```python
@staticmethod
def get_robust() -> RobustTrainingConfig
```

Get robust training configuration

```python
@staticmethod
def get_fast() -> FastTrainingConfig
```

Get fast training configuration

```python
@classmethod
def list_available_configs(cls) -> Dict[str, str]
```

List available training configurations

```python
@classmethod
def get_config(cls, config_name: str) -> BaseConfig
```

Get a training configuration by name
