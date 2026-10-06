# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset`

[Package guide](README.md) · [Complete source index](../../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [data_augmentation.py](#data_augmentationpy)
- [pair_generator.py](#pair_generatorpy)
- [shape_factory.py](#shape_factorypy)
- [synthetic_dataset.py](#synthetic_datasetpy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/__init__.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/__init__.py).

Dataset Generation and Management Module Provides tools for synthetic contour generation, data augmentation, and training pair creation.

Imports (including optional/function-local imports; not a startup dependency list): `.data_augmentation`, `.pair_generator`, `.shape_factory`, `.synthetic_dataset`.

Package-level import/export surface:

```python
from .shape_factory import ShapeFactory
from .synthetic_dataset import SyntheticDataset, SyntheticContour
from .data_augmentation import ContourAugmenter
from .pair_generator import PairGenerator
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ShapeFactory', 'SyntheticDataset', 'SyntheticContour', 'ContourAugmenter', 'PairGenerator']
```

## `data_augmentation.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/data_augmentation.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/data_augmentation.py).

Data Augmentation Module Provides various augmentation techniques for contour data including rotation, noise addition, deformation, and simplification.

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `cv2`, `numpy`, `random`, `typing`.

### `BaseAugmentation`

```python
class BaseAugmentation(ABC):
```

Abstract base class for augmentation techniques

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

```python
@abstractmethod
def apply(self, contour: np.ndarray) -> np.ndarray
```

Apply augmentation to a contour Args: contour: Input contour Returns: Augmented contour

```python
@abstractmethod
def get_parameters(self) -> Dict[str, Any]
```

Get augmentation parameters

### `RotationAugmentation`

```python
class RotationAugmentation(BaseAugmentation):
```

Rotate contour by random or specified angle

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

```python
def apply(self, contour: np.ndarray) -> np.ndarray
```

Apply rotation to contour

```python
def get_parameters(self) -> Dict[str, Any]
```

### `NoiseAugmentation`

```python
class NoiseAugmentation(BaseAugmentation):
```

Add Gaussian noise to contour points

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

```python
def apply(self, contour: np.ndarray) -> np.ndarray
```

Apply noise to contour

```python
def get_parameters(self) -> Dict[str, Any]
```

### `DeformationAugmentation`

```python
class DeformationAugmentation(BaseAugmentation):
```

Apply random deformation to contour

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

```python
def apply(self, contour: np.ndarray) -> np.ndarray
```

Apply deformation to contour

```python
def get_parameters(self) -> Dict[str, Any]
```

### `SimplificationAugmentation`

```python
class SimplificationAugmentation(BaseAugmentation):
```

Simplify contour using Douglas-Peucker algorithm

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

```python
def apply(self, contour: np.ndarray) -> np.ndarray
```

Apply simplification to contour

```python
def get_parameters(self) -> Dict[str, Any]
```

### `ScaleAugmentation`

```python
class ScaleAugmentation(BaseAugmentation):
```

Scale contour by a random or specified factor

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

```python
def apply(self, contour: np.ndarray) -> np.ndarray
```

Apply scaling to contour

```python
def get_parameters(self) -> Dict[str, Any]
```

### `ElasticDeformationAugmentation`

```python
class ElasticDeformationAugmentation(BaseAugmentation):
```

Apply elastic deformation to contour

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

```python
def apply(self, contour: np.ndarray) -> np.ndarray
```

Apply elastic deformation

```python
def get_parameters(self) -> Dict[str, Any]
```

### `ContourAugmenter`

```python
class ContourAugmenter:
```

Main augmentation coordinator that applies multiple augmentations to contours with configurable pipelines.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, augmentation_config: Optional[Dict[str, Any]]=None)
```

Initialize contour augmenter Args: augmentation_config: Configuration for augmentations

```python
def augment_contour(self, contour: np.ndarray, augmentations: Optional[List[str]]=None) -> np.ndarray
```

Apply augmentations to a single contour Args: contour: Input contour augmentations: List of augmentation names to apply (None = all) Returns: Augmented contour

```python
def create_variants(self, contour: np.ndarray, n_variants: int=5, variant_types: Optional[List[str]]=None) -> List[np.ndarray]
```

Create multiple variants of a contour Args: contour: Base contour n_variants: Number of variants to create variant_types: Types of variants to create Returns: List of variant contours

```python
def get_augmentation_info(self) -> Dict[str, Any]
```

Get information about configured augmentations

### `create_rotation_variants`

```python
def create_rotation_variants(contour: np.ndarray, n_variants: int=6) -> List[np.ndarray]
```

Create rotation variants of a contour

### `create_noisy_variants`

```python
def create_noisy_variants(contour: np.ndarray, n_variants: int=4, noise_levels: Optional[List[float]]=None) -> List[np.ndarray]
```

Create noisy variants of a contour

## `pair_generator.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/pair_generator.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/pair_generator.py).

Pair Generator Module Provides functionality for generating balanced training pairs from contour datasets with configurable positive/negative pair strategies.

Imports (including optional/function-local imports; not a startup dependency list): `.shape_factory`, `.synthetic_dataset`, `itertools`, `logging`, `numpy`, `random`, `typing`.

### `PairGenerator`

```python
class PairGenerator:
```

Generates balanced positive and negative pairs from contour datasets for training shape similarity models.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, include_hard_negatives: bool=True, balance_strategy: str='downsample', max_pairs_per_object: Optional[int]=None, random_state: int=42)
```

```python
def generate_balanced_pairs(self, contours: List[SyntheticContour]) -> Tuple[List[Tuple], List[int]]
```

```python
def generate_hard_negative_pairs(self, contours: List[SyntheticContour], hard_negative_ratio: float=0.3) -> Tuple[List[Tuple], List[int]]
```

```python
def generate_stratified_pairs(self, contours: List[SyntheticContour], pairs_per_object: int=100) -> Tuple[List[Tuple], List[int]]
```

```python
def get_pair_statistics(self, pairs: List[Tuple], labels: List[int], contours: List[SyntheticContour]) -> Dict[str, Any]
```

## `shape_factory.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/shape_factory.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/shape_factory.py).

Shape Factory Module Provides a factory pattern for generating various geometric shapes with consistent interfaces and extensible architecture for adding new shapes.

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `cv2`, `enum`, `numpy`, `typing`.

### `ShapeType`

```python
class ShapeType(Enum):
```

Enumeration of available shape types

Declared fields/defaults:

```python
CIRCLE = 'circle'
ELLIPSE = 'ellipse'
RECTANGLE = 'rectangle'
SQUARE = 'square'
TRIANGLE = 'triangle'
DIAMOND = 'diamond'
HEXAGON = 'hexagon'
OCTAGON = 'octagon'
PENTAGON = 'pentagon'
OVAL = 'oval'
ROUNDED_RECT = 'rounded_rect'
ROUNDED_CORNER_RECT = 'rounded_corner_rect'
S_SHAPE = 's_shape'
C_SHAPE = 'c_shape'
T_SHAPE = 't_shape'
U_SHAPE = 'u_shape'
L_SHAPE = 'l_shape'
STAR = 'star'
CROSS = 'cross'
ARROW = 'arrow'
HEART = 'heart'
CRESCENT = 'crescent'
GEAR = 'gear'
DONUT = 'donut'
TRAPEZOID = 'trapezoid'
PARALLELOGRAM = 'parallelogram'
HOURGLASS = 'hourglass'
LIGHTNING = 'lightning'
```

### `BaseShapeGenerator`

```python
class BaseShapeGenerator(ABC):
```

Abstract base class for shape generators

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, shape_type: ShapeType)
```

```python
@abstractmethod
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate a contour for this shape Args: scale: Scale factor for the shape img_size: Size of the image canvas **kwargs: Additional shape-specific parameters Returns: OpenCV contour array

```python
@abstractmethod
def get_default_parameters(self) -> Dict[str, Any]
```

Get default parameters for this shape Returns: Dictionary of default parameters

```python
def validate_parameters(self, **kwargs) -> Dict[str, Any]
```

Validate and merge parameters with defaults Args: **kwargs: Parameters to validate Returns: Validated parameter dictionary

### `CircleGenerator`

```python
class CircleGenerator(BaseShapeGenerator):
```

Generator for circular shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate circle contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `EllipseGenerator`

```python
class EllipseGenerator(BaseShapeGenerator):
```

Generator for elliptical shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate ellipse contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `RectangleGenerator`

```python
class RectangleGenerator(BaseShapeGenerator):
```

Generator for rectangular shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate rectangle contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `PolygonGenerator`

```python
class PolygonGenerator(BaseShapeGenerator):
```

Generator for regular polygon shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, shape_type: ShapeType, n_sides: int)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate regular polygon contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `StarGenerator`

```python
class StarGenerator(BaseShapeGenerator):
```

Generator for star shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, n_points: int=5)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate star contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `HeartGenerator`

```python
class HeartGenerator(BaseShapeGenerator):
```

Generator for heart shapes using parametric equations

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate heart contour using parametric equations

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `OvalGenerator`

```python
class OvalGenerator(BaseShapeGenerator):
```

Generator for oval shapes (elongated ellipse)

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate oval contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `RoundedRectGenerator`

```python
class RoundedRectGenerator(BaseShapeGenerator):
```

Generator for rounded rectangle shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate rounded rectangle contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `RoundedCornerRectGenerator`

```python
class RoundedCornerRectGenerator(BaseShapeGenerator):
```

Generator for rectangle with rounded corners (less rounded than RoundedRect)

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate rounded corner rectangle contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `CrossGenerator`

```python
class CrossGenerator(BaseShapeGenerator):
```

Generator for cross/plus shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate cross contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `ArrowGenerator`

```python
class ArrowGenerator(BaseShapeGenerator):
```

Generator for arrow shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate arrow contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `TrapezoidGenerator`

```python
class TrapezoidGenerator(BaseShapeGenerator):
```

Generator for trapezoid shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate trapezoid contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `ParallelogramGenerator`

```python
class ParallelogramGenerator(BaseShapeGenerator):
```

Generator for parallelogram shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate parallelogram contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `CrescentGenerator`

```python
class CrescentGenerator(BaseShapeGenerator):
```

Generator for crescent moon shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate crescent contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `DonutGenerator`

```python
class DonutGenerator(BaseShapeGenerator):
```

Generator for donut/ring shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate donut contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `LetterShapeGenerator`

```python
class LetterShapeGenerator(BaseShapeGenerator):
```

Generator for letter-shaped contours (T, U, L, S, C)

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, shape_type: ShapeType)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate letter-shaped contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `GearGenerator`

```python
class GearGenerator(BaseShapeGenerator):
```

Generator for gear shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate gear contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `HourglassGenerator`

```python
class HourglassGenerator(BaseShapeGenerator):
```

Generator for hourglass shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate hourglass contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `LightningGenerator`

```python
class LightningGenerator(BaseShapeGenerator):
```

Generator for lightning bolt shapes

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def generate(self, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate lightning bolt contour

```python
def get_default_parameters(self) -> Dict[str, Any]
```

### `ShapeFactory`

```python
class ShapeFactory:
```

Factory class for creating shape generators and managing shape types

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def register_generator(cls, shape_type: ShapeType, generator_class: Type[BaseShapeGenerator])
```

Register a shape generator

```python
@classmethod
def create_generator(cls, shape_type: ShapeType) -> BaseShapeGenerator
```

Create a shape generator for the specified type

```python
@classmethod
def generate_shape(cls, shape_type: ShapeType, scale: float=1.0, img_size: Tuple[int, int]=(256, 256), **kwargs) -> np.ndarray
```

Generate a shape contour Args: shape_type: Type of shape to generate scale: Scale factor img_size: Image canvas size **kwargs: Shape-specific parameters Returns: OpenCV contour array

```python
@classmethod
def get_available_shapes(cls) -> List[ShapeType]
```

Get list of available shape types

```python
@classmethod
def get_shape_info(cls, shape_type: ShapeType) -> Dict[str, Any]
```

Get information about a shape type

```python
@classmethod
def get_hard_negative_pairs(cls) -> List[Tuple[ShapeType, ShapeType]]
```

Get pairs of similar-looking but different shapes for hard negative training

## `synthetic_dataset.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/synthetic_dataset.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/dataset/synthetic_dataset.py).

Synthetic Dataset Generation Module Provides comprehensive synthetic dataset generation for shape similarity training with configurable parameters and augmentation pipelines.

Imports (including optional/function-local imports; not a startup dependency list): `.data_augmentation`, `.shape_factory`, `cv2`, `dataclasses`, `numpy`, `pathlib`, `pickle`, `random`, `typing`.

### `SyntheticContour`

```python
@dataclass
class SyntheticContour:
```

Container for synthetic contour with metadata

Declared fields/defaults:

```python
contour: np.ndarray
object_id: str
shape_type: ShapeType
scale: float
variant_name: str
parameters: Dict[str, Any]
```

### `SyntheticDataset`

```python
class SyntheticDataset:
```

Generates synthetic datasets of contours with controlled variations for training shape similarity models.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, n_shapes: int=8, n_scales: int=3, n_variants: int=5, n_noisy: int=4, shape_types: Optional[List[ShapeType]]=None, img_size: Tuple[int, int]=(256, 256), scale_range: Tuple[float, float]=(0.5, 3.0), include_hard_negatives: bool=True)
```

Initialize synthetic dataset generator Args: n_shapes: Number of different shape types to use n_scales: Number of different scales per shape n_variants: Number of rotation variants per scale n_noisy: Number of noise variants per rotation shape_types: Specific shape types to use (None = auto-select) img_size: Size of image canvas scale_range: Min and max scale factors include_hard_negatives: Whether to ensure hard negative pairs are included

```python
def generate(self) -> List[SyntheticContour]
```

Generate the complete synthetic dataset Returns: List of synthetic contours with metadata

```python
def generate_shape_variants(self, shape_type: ShapeType, n_variants: int=10) -> List[SyntheticContour]
```

Generate multiple variants of a specific shape Args: shape_type: Type of shape to generate n_variants: Number of variants to create Returns: List of shape variants

```python
def get_dataset_statistics(self, contours: List[SyntheticContour]) -> Dict[str, Any]
```

Get statistics about the generated dataset

```python
def save_dataset(self, contours: List[SyntheticContour], filepath: str)
```

Save dataset to file

```python
@classmethod
def load_dataset(cls, filepath: str) -> Tuple['SyntheticDataset', List[SyntheticContour]]
```

Load dataset from file
