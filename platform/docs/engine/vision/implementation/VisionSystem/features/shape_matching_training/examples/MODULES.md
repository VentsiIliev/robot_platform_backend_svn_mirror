# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/examples`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [basic_usage.py](#basic_usagepy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/examples/__init__.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/examples/__init__.py).

Examples Module This package contains practical examples and tutorials demonstrating how to use the shape matching training module effectively.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `basic_usage.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/examples/basic_usage.py](../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/examples/basic_usage.py).

Basic Usage Example This example demonstrates the most common use cases for the shape matching training module, including dataset generation, model training, and evaluation.

Imports (including optional/function-local imports; not a startup dependency list): `..`, `..core.dataset.shape_factory`, `..core.features`, `..core.features.moment_features`, `..core.models`, `..core.training.pipeline`, `..utils`, `matplotlib.pyplot`, `numpy`, `pathlib`, `random`, `sklearn.model_selection`, `sys`, `traceback`.

### `example_1_quick_start`

```python
def example_1_quick_start()
```

Example 1: Quick start with minimal configuration This is the fastest way to get started. The quick_training_pipeline function handles all the setup and provides reasonable defaults.

### `example_2_custom_configuration`

```python
def example_2_custom_configuration()
```

Example 2: Custom configuration and full pipeline This example shows how to create a custom training configuration and run the complete training pipeline.

### `example_3_step_by_step`

```python
def example_3_step_by_step()
```

Example 3: Step-by-step manual process This example shows how to use individual components to build a custom training workflow step by step.

### `example_4_feature_analysis`

```python
def example_4_feature_analysis()
```

Example 4: Feature analysis and comparison This example demonstrates how to analyze different feature types and their effectiveness for shape matching.

### `example_5_visualization`

```python
def example_5_visualization()
```

Example 5: Visualization and analysis This example shows how to create visualizations for model analysis and debugging.

### `main`

```python
def main()
```

Run all examples in sequence
