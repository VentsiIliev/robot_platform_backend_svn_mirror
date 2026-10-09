# Module reference: `packaging`

[Package guide](README.md) · [Complete source index](../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [paint_entrypoint.py](#paint_entrypointpy)
- [platform_entrypoint.py](#platform_entrypointpy)

## `paint_entrypoint.py`

Source: [packaging/platform/paint_entrypoint.py](../../packaging/platform/paint_entrypoint.py).

Standalone paint entry point with external data and update exclusion.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `os`, `pathlib`, `src.applications.software_update.service.stub_software_update_service`, `src.applications.software_update.software_update_factory`, `src.bootstrap.run_main`, `src.bootstrap.startup_config`, `src.engine.localization.localization_service`, `src.engine.updates.config`, `src.engine.updates.files`, `sys`, `tempfile`.

### `main`

```python
def main()
```

### `self_test`

```python
def self_test()
```

Verify frozen imports, startup resources and Qt without touching hardware.

## `platform_entrypoint.py`

Source: [packaging/platform/platform_entrypoint.py](../../packaging/platform/platform_entrypoint.py).

Standalone entry point bound to one robot-system/profile release target.

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtGui`, `PyQt6.QtWidgets`, `json`, `os`, `pathlib`, `src.applications.login.view.login_view`, `src.applications.software_update.service.stub_software_update_service`, `src.applications.software_update.software_update_factory`, `src.bootstrap.run_main`, `src.bootstrap.startup_config`, `src.bootstrap.startup_error`, `src.engine.localization.localization_service`, `src.engine.updates.config`, `src.engine.updates.factory_defaults`, `src.engine.updates.files`, `sys`, `tempfile`, `time`.

### `main`

```python
def main()
```

### `self_test`

```python
def self_test()
```

Verify frozen imports, startup resources and Qt without touching hardware.
