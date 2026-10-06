# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit`

[Package guide](README.md) · [Complete source index](../../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_config.py](#test_configpy)
- [test_feature_extractors.py](#test_feature_extractorspy)
- [test_models.py](#test_modelspy)
- [test_shape_factory.py](#test_shape_factorypy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/__init__.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/__init__.py).

Unit Tests Module This module contains unit tests for individual components of the shape matching training vision_service.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_config.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/test_config.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/test_config.py).

Unit tests for Configuration modules

Imports (including optional/function-local imports; not a startup dependency list): `config.base_config`, `config.model_configs`, `config.training_configs`, `copy`, `os`, `pathlib`, `pytest`, `tempfile`.

### `TestBaseConfig`

```python
@pytest.mark.unit
class TestBaseConfig:
```

Test cases for BaseConfig abstract class.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_config_validation_on_init(self)
```

Test that validation is called during initialization.

```python
def test_config_serialization(self)
```

Test config to_dict and from_dict methods.

```python
def test_config_merge(self)
```

Test configuration merging.

### `TestModelConfigs`

```python
@pytest.mark.unit
class TestModelConfigs:
```

Test cases for model configurations.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_sgd_classifier_config_creation(self)
```

Test SGD classifier configuration creation.

```python
def test_sgd_config_validation(self)
```

Test SGD configuration validation.

```python
def test_model_config_registry(self)
```

Test model configuration registry.

```python
def test_invalid_config_name(self)
```

Test behavior with invalid configuration name.

### `TestTrainingConfigs`

```python
@pytest.mark.unit
class TestTrainingConfigs:
```

Test cases for training configurations.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_default_training_config(self)
```

Test default training configuration.

```python
def test_fast_training_config(self)
```

Test fast training configuration.

```python
def test_training_config_registry(self)
```

Test training configuration registry.

```python
def test_config_validation_errors(self)
```

Test configuration validation errors.

```python
def test_config_file_operations(self, temp_dir)
```

Test saving and loading configurations.

```python
def test_config_environment_variables(self)
```

Test configuration with environment variables.

### `TestConfigEdgeCases`

```python
@pytest.mark.unit
class TestConfigEdgeCases:
```

Test edge cases and error conditions for configurations.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_config_with_none_values(self)
```

Test configuration behavior with None values.

```python
def test_config_with_extreme_values(self)
```

Test configuration with extreme values.

```python
def test_config_immutability_simulation(self)
```

Test configuration immutability patterns.

```python
def test_config_nested_validation(self)
```

Test validation of nested configuration objects.

## `test_feature_extractors.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/test_feature_extractors.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/test_feature_extractors.py).

Unit tests for Feature Extractor modules

Imports (including optional/function-local imports; not a startup dependency list): `core.dataset.data_augmentation`, `core.dataset.shape_factory`, `core.features.base_extractor`, `core.features.fourier_features`, `core.features.geometric_features`, `core.features.moment_features`, `numpy`, `pytest`, `unittest.mock`.

### `TestGeometricFeatureExtractor`

```python
@pytest.mark.unit
class TestGeometricFeatureExtractor:
```

Test cases for GeometricFeatureExtractor.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_extract_features_valid_contour(self, geometric_extractor, simple_contour, test_helpers)
```

Test feature extraction from valid contour.

```python
def test_feature_names(self, geometric_extractor)
```

Test that feature names are provided.

```python
def test_empty_contour(self, geometric_extractor)
```

Test behavior with empty contour.

```python
def test_invalid_contour(self, geometric_extractor)
```

Test behavior with invalid contour.

```python
def test_feature_consistency(self, geometric_extractor)
```

Test that features are consistent across multiple extractions.

```python
def test_scale_invariance_properties(self, geometric_extractor)
```

Test that scale-invariant features behave correctly.

### `TestHuMomentExtractor`

```python
@pytest.mark.unit
class TestHuMomentExtractor:
```

Test cases for HuMomentExtractor.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_extract_features_valid_contour(self, hu_moment_extractor, simple_contour, test_helpers)
```

Test Hu moment extraction from valid contour.

```python
def test_invariance_properties(self, hu_moment_extractor)
```

Test rotation and scale invariance of Hu moments.

```python
def test_log_transform_option(self)
```

Test Hu moments with log transform option.

### `TestCompositeFeatureExtractor`

```python
@pytest.mark.unit
class TestCompositeFeatureExtractor:
```

Test cases for CompositeFeatureExtractor.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_combine_extractors(self, simple_contour, test_helpers)
```

Test combining multiple feature extractors.

```python
def test_feature_names_combination(self)
```

Test that feature names are properly combined.

```python
def test_empty_extractor_list(self)
```

Test behavior with empty extractor list.

```python
def test_single_extractor(self, simple_contour)
```

Test with single extractor (should work like the individual extractor).

```python
def test_get_feature_count(self)
```

Test getting total feature count.

### `TestFeatureExtractorFactory`

```python
@pytest.mark.unit
class TestFeatureExtractorFactory:
```

Test cases for FeatureExtractorFactory.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_create_extractor_geometric(self)
```

Test creating geometric extractor through factory.

```python
def test_create_extractor_hu_moments(self)
```

Test creating Hu moments extractor through factory.

```python
def test_create_extractor_with_config(self)
```

Test creating extractor with configuration.

```python
def test_create_composite_extractor(self)
```

Test creating composite extractor through factory.

```python
def test_invalid_extractor_name(self)
```

Test behavior with invalid extractor name.

```python
def test_get_available_extractors(self)
```

Test getting list of available extractors.

### `TestFeatureExtractorPerformance`

```python
@pytest.mark.unit
@pytest.mark.slow
class TestFeatureExtractorPerformance:
```

Performance tests for feature extractors.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_geometric_extraction_performance(self, geometric_extractor, multiple_contours, performance_tracker)
```

Test geometric feature extraction performance.

```python
def test_composite_extraction_performance(self, composite_extractor, multiple_contours, performance_tracker)
```

Test composite feature extraction performance.

### `TestFeatureExtractorEdgeCases`

```python
@pytest.mark.unit
class TestFeatureExtractorEdgeCases:
```

Test edge cases and error conditions.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_very_small_contour(self, geometric_extractor)
```

Test with very small contour (few points).

```python
def test_contour_with_duplicate_points(self, geometric_extractor)
```

Test with contour containing duplicate points.

```python
def test_feature_extraction_with_noise(self)
```

Test feature extraction robustness to noise.

## `test_models.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/test_models.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/test_models.py).

Unit tests for Model modules

Imports (including optional/function-local imports; not a startup dependency list): `config.model_configs`, `copy`, `core.models.base_model`, `core.models.model_factory`, `core.models.sgd_model`, `numpy`, `pickle`, `pytest`, `queue`, `sklearn.exceptions`, `threading`, `unittest.mock`.

### `TestSGDModel`

```python
@pytest.mark.unit
class TestSGDModel:
```

Test cases for SGDModel.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_model_initialization(self)
```

Test SGD model initialization.

```python
def test_model_initialization_with_config(self)
```

Test SGD model initialization with configuration.

```python
def test_fit_and_predict(self, sgd_model, sample_features, sample_labels)
```

Test model fitting and prediction.

```python
def test_predict_proba(self, trained_model, sample_features)
```

Test probability prediction.

```python
def test_predict_with_confidence(self, trained_model, sample_features)
```

Test prediction with confidence scores.

```python
def test_predict_without_fitting(self, sgd_model, sample_features)
```

Test prediction on unfitted model.

```python
def test_feature_importance(self, trained_model)
```

Test getting feature importance.

```python
def test_model_info(self, trained_model)
```

Test getting model information.

```python
def test_set_feature_names(self, sgd_model)
```

Test setting feature names.

```python
def test_validate_input_shapes(self, trained_model, sample_features)
```

Test input shape validation.

```python
def test_empty_input(self, trained_model)
```

Test behavior with empty input.

```python
@pytest.mark.performance
def test_prediction_performance(self, trained_model, performance_tracker)
```

Test prediction performance.

### `TestModelFactory`

```python
@pytest.mark.unit
class TestModelFactory:
```

Test cases for ModelFactory.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_create_sgd_model(self)
```

Test creating SGD model through factory.

```python
def test_create_model_with_config_name(self)
```

Test creating model with configuration name.

```python
def test_create_model_with_config_object(self)
```

Test creating model with configuration object.

```python
def test_create_ensemble_model(self)
```

Test creating ensemble model.

```python
def test_invalid_model_type(self)
```

Test behavior with invalid model type.

```python
def test_get_available_models(self)
```

Test getting available model types.

### `TestBaseModel`

```python
@pytest.mark.unit
class TestBaseModel:
```

Test cases for BaseModel interface.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_abstract_methods(self)
```

Test that BaseModel is abstract.

```python
def test_prediction_result_structure(self)
```

Test PredictionResult dataclass.

### `TestModelCompatibility`

```python
@pytest.mark.unit
class TestModelCompatibility:
```

Test model compatibility and serialization.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_model_serialization(self, trained_model, temp_dir)
```

Test model saving and loading.

```python
def test_model_copy(self, trained_model)
```

Test model copying.

```python
@pytest.mark.slow
def test_concurrent_predictions(self, trained_model)
```

Test concurrent predictions (thread safety).

### `TestModelEdgeCases`

```python
@pytest.mark.unit
class TestModelEdgeCases:
```

Test edge cases and error conditions for models.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_fitting_with_invalid_data(self, sgd_model)
```

Test fitting with invalid data.

```python
def test_fitting_with_single_class(self, sgd_model)
```

Test fitting with only one class.

```python
def test_extreme_feature_values(self, sgd_model)
```

Test model behavior with extreme feature values.

```python
def test_nan_and_inf_handling(self, sgd_model)
```

Test model behavior with NaN and infinite values.

## `test_shape_factory.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/test_shape_factory.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/unit/test_shape_factory.py).

Unit tests for Shape Factory module

Imports (including optional/function-local imports; not a startup dependency list): `core.dataset.shape_factory`, `cv2`, `numpy`, `pytest`.

### `TestShapeFactory`

```python
@pytest.mark.unit
class TestShapeFactory:
```

Test cases for the ShapeFactory class.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_generate_circle(self)
```

Test circle generation.

```python
def test_generate_square(self)
```

Test square generation.

```python
def test_generate_triangle(self)
```

Test triangle generation.

```python
def test_different_scales(self)
```

Test shape generation with different scales.

```python
def test_different_image_sizes(self)
```

Test shape generation with different image sizes.

```python
def test_all_shape_types(self)
```

Test that all shape types can be generated.

```python
def test_invalid_scale(self)
```

Test behavior with invalid scale values.

```python
def test_get_hard_negative_pairs(self)
```

Test getting hard negative pairs.

```python
@pytest.mark.performance
def test_generation_performance(self, performance_tracker)
```

Test shape generation performance.

```python
def test_reproducibility(self)
```

Test that shape generation is deterministic with same parameters.

```python
def test_contour_properties(self)
```

Test that generated contours have expected properties.

```python
def test_edge_cases(self)
```

Test edge cases and boundary conditions.
