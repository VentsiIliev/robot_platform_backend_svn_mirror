# Module reference: `src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features`

[Package guide](README.md) · [Complete source index](../../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [base_extractor.py](#base_extractorpy)
- [fourier_features.py](#fourier_featurespy)
- [geometric_features.py](#geometric_featurespy)
- [moment_features.py](#moment_featurespy)

## `__init__.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/__init__.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/__init__.py).

Feature Extraction Module Provides modular feature extraction capabilities for contour analysis. Includes geometric features, moment invariants, and Fourier descriptors.

Imports (including optional/function-local imports; not a startup dependency list): `.base_extractor`, `.fourier_features`, `.geometric_features`, `.moment_features`.

Package-level import/export surface:

```python
from .base_extractor import BaseFeatureExtractor, FeatureExtractorFactory
from .geometric_features import GeometricFeatureExtractor
from .moment_features import MomentFeatureExtractor
from .fourier_features import FourierFeatureExtractor
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['BaseFeatureExtractor', 'FeatureExtractorFactory', 'GeometricFeatureExtractor', 'MomentFeatureExtractor', 'FourierFeatureExtractor']
```

## `base_extractor.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/base_extractor.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/base_extractor.py).

Abstract Base Feature Extractor Provides the abstract base class and factory for feature extraction, establishing a consistent interface for all feature extraction methods.

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `concurrent.futures`, `multiprocessing`, `numpy`, `typing`.

### `BaseFeatureExtractor`

```python
class BaseFeatureExtractor(ABC):
```

Abstract base class for feature extractors. All feature extractors must implement the extract_features method and provide metadata about the features they generate.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Optional[Dict[str, Any]]=None)
```

Initialize feature extractor with configuration Args: config: Optional configuration dictionary

```python
@abstractmethod
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract features from a single contour Args: contour: OpenCV contour array Returns: List of extracted feature values

```python
@abstractmethod
def get_feature_names(self) -> List[str]
```

Get names of the features extracted by this extractor Returns: List of feature names in the same order as extract_features output

```python
@abstractmethod
def get_feature_count(self) -> int
```

Get the number of features extracted by this extractor Returns: Number of features

```python
def get_metadata(self) -> Dict[str, Any]
```

Get metadata about this feature extractor Returns: Dictionary with extractor metadata

```python
def get_version(self) -> str
```

Get version string for this extractor Returns: Version string

```python
def extract_features_parallel(self, contours: List[np.ndarray]) -> List[List[float]]
```

Extract features from multiple contours in parallel Args: contours: List of contours Returns: List of feature vectors

### `CompositeFeatureExtractor`

```python
class CompositeFeatureExtractor(BaseFeatureExtractor):
```

Composite feature extractor that combines multiple extractors

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, extractors: List[BaseFeatureExtractor])
```

Initialize with list of extractors Args: extractors: List of feature extractors to combine

```python
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract features using all extractors

```python
def get_feature_names(self) -> List[str]
```

Get all feature names from all extractors

```python
def get_feature_count(self) -> int
```

Get total feature count from all extractors

```python
def get_metadata(self) -> Dict[str, Any]
```

Get metadata including all sub-extractors

### `FeatureExtractorFactory`

```python
class FeatureExtractorFactory:
```

Factory for creating and managing feature extractors

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def register_extractor(cls, name: str, extractor_class: Type[BaseFeatureExtractor]) -> None
```

Register a feature extractor class Args: name: Name to register the extractor under extractor_class: Feature extractor class

```python
@classmethod
def create_extractor(cls, name: str, config: Optional[Dict[str, Any]]=None) -> BaseFeatureExtractor
```

Create a feature extractor by name Args: name: Name of the extractor to create config: Optional configuration dictionary Returns: Initialized feature extractor Raises: ValueError: If extractor name is not registered

```python
@classmethod
def create_composite_extractor(cls, extractor_configs: List[Dict[str, Any]]) -> CompositeFeatureExtractor
```

Create a composite extractor from a list of configurations Args: extractor_configs: List of extractor configurations, each containing 'name' and optional 'config' Returns: Composite feature extractor

```python
@classmethod
def list_available_extractors(cls) -> List[str]
```

List all registered extractor names Returns: List of registered extractor names

```python
@classmethod
def get_extractor_info(cls, name: str) -> Dict[str, Any]
```

Get information about a registered extractor Args: name: Name of the extractor Returns: Dictionary with extractor information

### `compute_features_for_pair`

```python
def compute_features_for_pair(contour_pair: tuple, extractor: BaseFeatureExtractor) -> List[float]
```

Compute features for a pair of contours (difference features) Args: contour_pair: Tuple of (contour1, contour2) extractor: Feature extractor to use Returns: List of difference features

### `compute_features_parallel`

```python
def compute_features_parallel(contour_pairs: List[tuple], extractor: BaseFeatureExtractor, max_workers: Optional[int]=None) -> List[List[float]]
```

Compute features for multiple contour pairs in parallel Args: contour_pairs: List of (contour1, contour2) tuples extractor: Feature extractor to use max_workers: Maximum number of worker processes Returns: List of feature vectors for each pair

### `get_feature_extraction_metadata`

```python
def get_feature_extraction_metadata(extractor: BaseFeatureExtractor) -> Dict[str, Any]
```

Get comprehensive metadata about feature extraction process Args: extractor: Feature extractor instance Returns: Dictionary with feature extraction metadata

## `fourier_features.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/fourier_features.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/fourier_features.py).

Fourier-Based Feature Extractor Extracts Fourier descriptors and frequency domain features from contours, providing rotation and translation invariant shape descriptors.

Imports (including optional/function-local imports; not a startup dependency list): `.base_extractor`, `cv2`, `numpy`, `typing`.

### `FourierFeatureExtractor`

```python
class FourierFeatureExtractor(BaseFeatureExtractor):
```

Extracts Fourier descriptors from contours using FFT analysis of the contour boundary representation.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Dict[str, Any]=None, **kwargs)
```

Initialize Fourier feature extractor Args: config: Configuration dictionary with parameters: - n_descriptors: Number of Fourier descriptors to extract (default: 4) - normalize: Whether to normalize descriptors (default: True) - use_magnitude_only: Use only magnitude, ignore phase (default: True) **kwargs: Alternative way to pass configuration parameters directly

```python
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract Fourier descriptors from contour Args: contour: OpenCV contour array Returns: List of Fourier descriptor features

```python
def get_feature_names(self) -> List[str]
```

Get names of Fourier descriptor features

```python
def get_feature_count(self) -> int
```

Get number of Fourier descriptor features

### `CurvatureFeatureExtractor`

```python
class CurvatureFeatureExtractor(BaseFeatureExtractor):
```

Extracts curvature-based features from contours including curvature histograms and curvature statistics.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Dict[str, Any]=None)
```

Initialize curvature feature extractor Args: config: Configuration dictionary with parameters: - n_bins: Number of bins for curvature histogram (default: 16) - window_size: Window size for curvature calculation (default: 5) - normalize_histogram: Whether to normalize histogram (default: True)

```python
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract curvature-based features from contour Args: contour: OpenCV contour array Returns: List of curvature features (histogram + statistics)

```python
def get_feature_names(self) -> List[str]
```

Get names of curvature features

```python
def get_feature_count(self) -> int
```

Get number of curvature features

### `SpectralFeatureExtractor`

```python
class SpectralFeatureExtractor(BaseFeatureExtractor):
```

Extracts spectral features from contour using power spectrum analysis

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Dict[str, Any]=None)
```

Initialize spectral feature extractor Args: config: Configuration dictionary with parameters: - n_frequencies: Number of frequency components (default: 8) - use_log_power: Whether to use log power spectrum (default: True)

```python
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract spectral features from contour Args: contour: OpenCV contour array Returns: List of spectral features

```python
def get_feature_names(self) -> List[str]
```

Get names of spectral features

```python
def get_feature_count(self) -> int
```

Get number of spectral features

## `geometric_features.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/geometric_features.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/geometric_features.py).

Geometric Feature Extractor Extracts geometric properties from contours including area ratios, perimeter features, and shape descriptors.

Imports (including optional/function-local imports; not a startup dependency list): `.base_extractor`, `cv2`, `numpy`, `typing`.

### `GeometricFeatureExtractor`

```python
class GeometricFeatureExtractor(BaseFeatureExtractor):
```

Extracts geometric features from contours including: - Aspect ratio - Extent - Solidity - Convexity ratio - Equivalent diameter - Perimeter - Compactness - Eccentricity - Major/minor axis lengths

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Dict[str, Any]=None, **kwargs)
```

Initialize geometric feature extractor Args: config: Configuration dictionary (currently unused) **kwargs: Alternative way to pass configuration parameters directly

```python
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract geometric features from contour Args: contour: OpenCV contour array Returns: List of 9 geometric features

```python
def get_feature_names(self) -> List[str]
```

Get names of geometric features

```python
def get_feature_count(self) -> int
```

Get number of geometric features

### `AreaFeatureExtractor`

```python
class AreaFeatureExtractor(BaseFeatureExtractor):
```

Specialized extractor for area-based features including scale-sensitive area differences and scale band categorization

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Dict[str, Any]=None)
```

Initialize area feature extractor Args: config: Configuration with optional 'n_bands' parameter

```python
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract area-based features from contour Args: contour: OpenCV contour array Returns: List of area features

```python
def get_feature_names(self) -> List[str]
```

Get names of area features

```python
def get_feature_count(self) -> int
```

Get number of area features

```python
def scale_band_categorical(self, area1: float, area2: float) -> float
```

Classify areas into discrete bands and return categorical difference Args: area1: Area of first contour area2: Area of second contour Returns: Categorical difference between scale bands (0-1)

## `moment_features.py`

Source: [src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/moment_features.py](../../../../../../../../../src/engine/vision/implementation/VisionSystem/features/shape_matching_training/core/features/moment_features.py).

Moment-Based Feature Extractor Extracts moment invariants and other moment-based features from contours, providing scale, rotation, and translation invariant shape descriptors.

Imports (including optional/function-local imports; not a startup dependency list): `.base_extractor`, `cv2`, `numpy`, `typing`.

### `MomentFeatureExtractor`

```python
class MomentFeatureExtractor(BaseFeatureExtractor):
```

Extracts moment-based features including: - Hu moments (7 invariant moments) - Central moments - Normalized central moments

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Dict[str, Any]=None, **kwargs)
```

Initialize moment feature extractor Args: config: Configuration dictionary with optional parameters: - use_log_hu: Whether to use log-transformed Hu moments (default: True) - include_central_moments: Whether to include central moments (default: False) **kwargs: Alternative way to pass configuration parameters directly

```python
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract moment-based features from contour Args: contour: OpenCV contour array Returns: List of moment features (7 Hu moments + optional central moments)

```python
def get_feature_names(self) -> List[str]
```

Get names of moment features

```python
def get_feature_count(self) -> int
```

Get number of moment features

### `HuMomentExtractor`

```python
class HuMomentExtractor(BaseFeatureExtractor):
```

Simplified extractor that only extracts the 7 Hu moments

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Dict[str, Any]=None, **kwargs)
```

Initialize Hu moment extractor Args: config: Configuration dictionary with optional parameters: - use_log_transform: Whether to apply log transform (default: True) **kwargs: Alternative way to pass configuration parameters directly

```python
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract the 7 Hu moments from contour Args: contour: OpenCV contour array Returns: List of 7 Hu moment features

```python
def get_feature_names(self) -> List[str]
```

Get names of Hu moment features

```python
def get_feature_count(self) -> int
```

Get number of Hu moment features

### `ZernikeMomentExtractor`

```python
class ZernikeMomentExtractor(BaseFeatureExtractor):
```

Extractor for Zernike moments (orthogonal moments) Provides rotation invariant shape descriptors

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, config: Dict[str, Any]=None)
```

Initialize Zernike moment extractor Args: config: Configuration dictionary with parameters: - max_order: Maximum order of Zernike moments (default: 8) - radius: Radius for Zernike calculation (default: auto)

```python
def extract_features(self, contour: np.ndarray) -> List[float]
```

Extract Zernike moments from contour Args: contour: OpenCV contour array Returns: List of Zernike moment features

```python
def get_feature_names(self) -> List[str]
```

Get names of Zernike moment features

```python
def get_feature_count(self) -> int
```

Get number of Zernike moment features
