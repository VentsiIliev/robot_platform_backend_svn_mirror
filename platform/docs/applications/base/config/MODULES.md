# Module reference: `src/applications/base/config`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [virtual_keyboard_config.py](#virtual_keyboard_configpy)

## `virtual_keyboard_config.py`

Source: [src/applications/base/config/virtual_keyboard_config.py](../../../../src/applications/base/config/virtual_keyboard_config.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `json`, `logging`, `pathlib`.

Module declarations (expressions are shown without evaluating them):

```python
ENABLE_CUSTOM_VIRTUAL_KEYBOARD = _load_custom_virtual_keyboard_enabled()
```

### `_load_custom_virtual_keyboard_enabled`

```python
def _load_custom_virtual_keyboard_enabled() -> bool
```
