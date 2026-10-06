# Module reference: `src/robot_systems/glue/applications/dashboard/ui/factories`

[Package guide](README.md) · [Complete source index](../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [glue_card_factory.py](#glue_card_factorypy)

## `__init__.py`

Source: [src/robot_systems/glue/applications/dashboard/ui/factories/__init__.py](../../../../../../../src/robot_systems/glue/applications/dashboard/ui/factories/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `glue_card_factory.py`

Source: [src/robot_systems/glue/applications/dashboard/ui/factories/glue_card_factory.py](../../../../../../../src/robot_systems/glue/applications/dashboard/ui/factories/glue_card_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `pl_gui.dashboard.config`, `src.robot_systems.glue.applications.dashboard.model.glue_dashboard_model`, `src.robot_systems.glue.applications.dashboard.ui.widgets.GlueMeterCard`, `typing`.

### `GlueCardFactory`

```python
class GlueCardFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, model: GlueDashboardModel)
```

```python
def build_cards(self, cell_configs: List[CardConfig]) -> list
```
