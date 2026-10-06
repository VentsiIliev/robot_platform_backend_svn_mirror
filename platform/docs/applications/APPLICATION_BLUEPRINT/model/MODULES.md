# Module reference: `src/applications/APPLICATION_BLUEPRINT/model`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [my_model.py](#my_modelpy)

## `__init__.py`

Source: [src/applications/APPLICATION_BLUEPRINT/model/__init__.py](../../../../src/applications/APPLICATION_BLUEPRINT/model/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `my_model.py`

Source: [src/applications/APPLICATION_BLUEPRINT/model/my_model.py](../../../../src/applications/APPLICATION_BLUEPRINT/model/my_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.APPLICATION_BLUEPRINT.service.i_my_service`, `src.applications.base.i_application_model`, `typing`.

### `MyModel`

```python
class MyModel(IApplicationModel):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, service: IMyService)
```

```python
def load(self) -> str
```

```python
def save(self, value: str, **kwargs) -> None
```

```python
@property
def value(self) -> Optional[str]
```
