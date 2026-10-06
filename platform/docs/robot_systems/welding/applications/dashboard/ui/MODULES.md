# Module reference: `src/robot_systems/welding/applications/dashboard/ui`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [welding_card_factory.py](#welding_card_factorypy)
- [welding_status_card.py](#welding_status_cardpy)

## `welding_card_factory.py`

Source: [src/robot_systems/welding/applications/dashboard/ui/welding_card_factory.py](../../../../../../src/robot_systems/welding/applications/dashboard/ui/welding_card_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `__future__`, `pl_gui.dashboard.config`, `src.robot_systems.welding.applications.dashboard.ui.welding_status_card`.

### `WeldingCardFactory`

```python
class WeldingCardFactory:
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def build_cards(self, card_configs: list[CardConfig]) -> list[tuple]
```

## `welding_status_card.py`

Source: [src/robot_systems/welding/applications/dashboard/ui/welding_status_card.py](../../../../../../src/robot_systems/welding/applications/dashboard/ui/welding_status_card.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `__future__`.

### `WeldingStatusCard`

```python
class WeldingStatusCard(QWidget):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, label: str, parent=None)
```

```python
def set_state(self, state: str) -> None
```
