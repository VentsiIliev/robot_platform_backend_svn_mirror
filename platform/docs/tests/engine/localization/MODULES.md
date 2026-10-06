# Module reference: `tests/engine/localization`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_localization_service.py](#test_localization_servicepy)

## `test_localization_service.py`

Source: [tests/engine/localization/test_localization_service.py](../../../../tests/engine/localization/test_localization_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `json`, `pathlib`, `src.engine.localization.dict_translator`, `src.engine.localization.localization_service`, `src.shared_contracts.events.localization_events`, `tempfile`, `unittest`, `unittest.mock`.

### `TestDictTranslator`

```python
class TestDictTranslator(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_translate_returns_none_on_miss(self)
```

```python
def test_is_empty_reflects_loaded_data(self)
```

### `TestLocalizationService`

```python
class TestLocalizationService(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_available_languages_discovers_json_catalogs(self)
```

```python
def test_set_language_installs_selected_translation(self)
```

```python
def test_set_language_falls_back_to_english_for_missing_key(self)
```

```python
def test_translate_uses_qt_translation_chain(self)
```

```python
def test_missing_language_falls_back_to_default_language(self)
```

```python
def test_publishes_language_changed_event(self)
```

```python
def test_persists_selected_language(self)
```

```python
def test_initializes_from_persisted_language(self)
```

```python
def test_merges_multiple_catalog_roots_with_later_root_override(self)
```
