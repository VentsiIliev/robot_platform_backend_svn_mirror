# Module reference: `src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/ui`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [demo_card_factory.py](#demo_card_factorypy)
- [demo_status_card.py](#demo_status_cardpy)

## `demo_card_factory.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/ui/demo_card_factory.py](../../../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/ui/demo_card_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `pl_gui.dashboard.config`, `src.robot_systems.ROBOT_SYSTEM_BLUEPRINT.applications.dashboard.ui.demo_status_card`.

### `DemoCardFactory`

```python
class DemoCardFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build_cards(self, card_configs: list[CardConfig]) -> list[tuple]
```

## `demo_status_card.py`

Source: [src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/ui/demo_status_card.py](../../../../../../src/robot_systems/ROBOT_SYSTEM_BLUEPRINT/applications/dashboard/ui/demo_status_card.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`.

### `DemoStatusCard`

```python
class DemoStatusCard(QWidget):
```

Minimal dashboard card compatible with DashboardWidget typed setters.

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, label: str, parent=None)
```

```python
def set_weight(self, grams: float) -> None
```

```python
def set_state(self, state: str) -> None
```

```python
def set_glue_type(self, glue_type: str) -> None
```
