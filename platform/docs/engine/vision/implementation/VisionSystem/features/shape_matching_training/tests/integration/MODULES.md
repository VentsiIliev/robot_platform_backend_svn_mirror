# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/integration`

[Package guide](README.md) · [Complete source index](../../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_training_pipeline.py](#test_training_pipelinepy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/integration/__init__.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/integration/__init__.py).

Integration Tests Module This module contains integration tests that verify the interaction between different components of the shape matching training vision_service.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_training_pipeline.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/integration/test_training_pipeline.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/tests/integration/test_training_pipeline.py).

Integration tests for Training Pipeline

Imports (including optional/function-local imports; not a startup dependency list): `config.training_configs`, `core.dataset.data_augmentation`, `core.dataset.pair_generator`, `core.dataset.shape_factory`, `core.dataset.synthetic_dataset`, `core.features.base_extractor`, `core.features.geometric_features`, `core.features.moment_features`, `core.models.sgd_model`, `core.training.pipeline`, `json`, `numpy`, `pathlib`, `pytest`, `utils.io_utils`.

### `TestTrainingPipelineIntegration`

```python
@pytest.mark.integration
class TestTrainingPipelineIntegration:
```

Integration tests for the complete training pipeline.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_complete_pipeline_execution(self, temp_dir)
```

Test complete pipeline from dataset generation to model evaluation.

```python
def test_dataset_generation_integration(self)
```

Test dataset generation and pair creation integration.

```python
def test_feature_extraction_integration(self, synthetic_contours)
```

Test feature extraction integration with different extractors.

```python
def test_training_only_pipeline(self, training_pairs, composite_extractor)
```

Test training pipeline with provided data.

```python
@pytest.mark.slow
def test_pipeline_with_different_configurations(self, temp_dir)
```

Test pipeline with different training configurations.

```python
def test_quick_training_pipeline(self)
```

Test quick training pipeline convenience function.

```python
def test_pipeline_error_handling(self)
```

Test pipeline error handling and recovery.

```python
def test_pipeline_reproducibility(self)
```

Test that pipeline results are reproducible with same random state.

### `TestEndToEndWorkflow`

```python
@pytest.mark.integration
class TestEndToEndWorkflow:
```

End-to-end workflow integration tests.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_shape_generation_to_prediction_workflow(self)
```

Test complete workflow from shape generation to prediction.

```python
def test_data_augmentation_to_training_workflow(self)
```

Test workflow including data augmentation.

```python
def test_configuration_to_results_workflow(self, temp_dir)
```

Test workflow from configuration loading to results.

### `TestPipelinePerformance`

```python
@pytest.mark.integration
@pytest.mark.slow
class TestPipelinePerformance:
```

Integration tests for pipeline performance.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_pipeline_scalability(self, performance_tracker)
```

Test pipeline performance with larger datasets.

```python
def test_parallel_feature_extraction_performance(self, performance_tracker)
```

Test performance of parallel feature extraction.

### `TestPipelineErrorRecovery`

```python
@pytest.mark.integration
class TestPipelineErrorRecovery:
```

Test pipeline error handling and recovery.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_invalid_shape_type_recovery(self)
```

Test recovery from invalid shape types.

```python
def test_insufficient_data_handling(self)
```

Test handling of insufficient training data.
