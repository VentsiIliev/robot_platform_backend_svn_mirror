# Module reference: `src/applications/base/onboarding`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [onboarding_step.py](#onboarding_steppy)
- [onboarding_tour.py](#onboarding_tourpy)

## `__init__.py`

Source: [src/applications/base/onboarding/__init__.py](../../../../src/applications/base/onboarding/__init__.py).

Reusable, application-owned onboarding tours.

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.onboarding.onboarding_step`, `src.applications.base.onboarding.onboarding_tour`.

Package-level import/export surface:

```python
from src.applications.base.onboarding.onboarding_step import OnboardingStep
from src.applications.base.onboarding.onboarding_tour import OnboardingTour
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['OnboardingStep', 'OnboardingTour']
```

## `onboarding_step.py`

Source: [src/applications/base/onboarding/onboarding_step.py](../../../../src/applications/base/onboarding/onboarding_step.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`, `dataclasses`, `typing`.

### `OnboardingStep`

```python
@dataclass(frozen=True)
class OnboardingStep:
```

One translated-on-display step in an application onboarding tour.

Declared fields/defaults:

```python
target: Callable[[], QWidget | None]
title: str
body: str
hint: str = ''
spotlight: bool = True
```

## `onboarding_tour.py`

Source: [src/applications/base/onboarding/onboarding_tour.py](../../../../src/applications/base/onboarding/onboarding_tour.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `__future__`, `pl_gui.settings.settings_view.styles`, `src.applications.base.onboarding.onboarding_step`, `typing`.

### `_ProgressDots`

```python
class _ProgressDots(QWidget):
```

Compact visual progress indicator used by the tour card.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, parent: QWidget | None=None) -> None
```

```python
def set_progress(self, current: int, total: int, accessible_text: str) -> None
```

```python
def sizeHint(self) -> QSize
```

```python
def paintEvent(self, event) -> None
```

### `_TourOverlay`

```python
class _TourOverlay(QWidget):
```

Window-covering veil, spotlight and navigation card.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, host: QWidget, *, on_back: Callable[[], None], on_next: Callable[[], None], on_close: Callable[[], None]) -> None
```

```python
def show_step(self, *, target: QWidget, title: str, body: str, hint: str, spotlight: bool, index: int, total: int, labels: dict[str, str]) -> None
```

```python
def focus_next(self) -> None
```

```python
def paintEvent(self, event) -> None
```

```python
def keyPressEvent(self, event: QKeyEvent) -> None
```

### `OnboardingTour`

```python
class OnboardingTour(QObject):
```

Coordinates a reusable tour without knowing application internals.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, host_provider: Callable[[], QWidget | None], steps: Sequence[OnboardingStep], translator: Callable[[str], str], parent: QObject | None=None) -> None
```

```python
def start(self) -> None
```

```python
def stop(self) -> None
```

```python
def next(self) -> None
```

```python
def previous(self) -> None
```

```python
def eventFilter(self, watched: QObject, event: QEvent) -> bool
```
