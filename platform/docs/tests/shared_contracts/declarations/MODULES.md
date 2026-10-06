# Module reference: `tests/shared_contracts/declarations`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [test_declaration_contracts.py](#test_declaration_contractspy)

## `test_declaration_contracts.py`

Source: [tests/shared_contracts/declarations/test_declaration_contracts.py](../../../../tests/shared_contracts/declarations/test_declaration_contracts.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.engine.robot.configuration`, `src.shared_contracts.declarations.dispensing`, `src.shared_contracts.declarations.movement`, `src.shared_contracts.declarations.system_specs`, `src.shared_contracts.declarations.targeting`, `src.shared_contracts.declarations.tooling`, `src.shared_contracts.declarations.work_areas`, `unittest`.

### `TestSystemSpecs`

```python
class TestSystemSpecs(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_folder_spec_defaults_translation_key_from_name(self)
```

```python
def test_application_spec_defaults_app_id_from_name(self)
```

```python
def test_role_policy_normalizes_values_to_strings(self)
```

```python
def test_role_policy_rejects_unknown_default_role(self)
```

```python
def test_role_policy_rejects_unknown_protected_role(self)
```

### `TestMovementDeclarations`

```python
class TestMovementDeclarations(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_movement_group_definition_defaults_label_from_id(self)
```

```python
def test_build_default_group_preserves_flags(self)
```

### `TestToolingDeclarations`

```python
class TestToolingDeclarations(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_tool_definition_round_trip_normalizes_values(self)
```

```python
def test_tool_slot_definition_accepts_slot_id_alias(self)
```

### `TestWorkAreaDeclarations`

```python
class TestWorkAreaDeclarations(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_work_area_key_helpers_are_stable(self)
```

```python
def test_work_area_observer_binding_preserves_payload(self)
```

### `TestDispensingDeclarations`

```python
class TestDispensingDeclarations(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_dispense_channel_round_trip_normalizes_values(self)
```

### `TestTargetingDeclarations`

```python
class TestTargetingDeclarations(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_remote_tcp_round_trip_defaults_display_name(self)
```

```python
def test_target_frame_round_trip_normalizes_values(self)
```
