# Module reference: `src/engine/localization`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [dict_translator.py](#dict_translatorpy)
- [i_localization_service.py](#i_localization_servicepy)
- [localization_service.py](#localization_servicepy)

## `__init__.py`

Source: [src/engine/localization/__init__.py](../../../src/engine/localization/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `.i_localization_service`, `.localization_service`.

Package-level import/export surface:

```python
from .i_localization_service import ILocalizationService
from .localization_service import LocalizationService
```

Module declarations (expressions are shown without evaluating them):

```python
__all__ = ['ILocalizationService', 'LocalizationService']
```

## `dict_translator.py`

Source: [src/engine/localization/dict_translator.py](../../../src/engine/localization/dict_translator.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `typing`.

### `DictTranslator`

```python
class DictTranslator(QTranslator):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, translations: Dict[str, Dict[str, str]], parent=None)
```

```python
def isEmpty(self) -> bool
```

```python
def translate(self, context, source_text, disambiguation=None, n=-1)
```

## `i_localization_service.py`

Source: [src/engine/localization/i_localization_service.py](../../../src/engine/localization/i_localization_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `abc`, `typing`.

### `ILocalizationService`

```python
class ILocalizationService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def set_language(self, code: str) -> None
```

```python
@abstractmethod
def get_language(self) -> str
```

```python
@abstractmethod
def available_languages(self) -> List[Tuple[str, str]]
```

```python
@abstractmethod
def translate(self, context: str, source_text: str, fallback: str | None=None) -> str
```

```python
@abstractmethod
def sync_selector(self, selector) -> None
```

## `localization_service.py`

Source: [src/engine/localization/localization_service.py](../../../src/engine/localization/localization_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `__future__`, `json`, `logging`, `pathlib`, `re`, `src.engine.core.i_messaging_service`, `src.engine.localization.dict_translator`, `src.engine.localization.i_localization_service`, `src.shared_contracts.events.localization_events`, `typing`.

### `LocalizationService`

```python
class LocalizationService(ILocalizationService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, translations_dir: str | Iterable[str], messaging_service: IMessagingService | None=None, default_language: str='en', state_file: str | None=None) -> None
```

```python
def set_language(self, code: str) -> None
```

```python
def get_language(self) -> str
```

```python
def available_languages(self) -> List[Tuple[str, str]]
```

```python
def translate(self, context: str, source_text: str, fallback: str | None=None) -> str
```

```python
def sync_selector(self, selector) -> None
```
