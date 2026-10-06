# Module reference: `src/robot_systems/paint_tray_dry`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [bootstrap_provider.py](#bootstrap_providerpy)
- [paint_robot_system.py](#paint_robot_systempy)
- [paint_system_config.py](#paint_system_configpy)

## `__init__.py`

Source: [src/robot_systems/paint_tray_dry/__init__.py](../../../src/robot_systems/paint_tray_dry/__init__.py).

Tray-dryer paint robot system entry point.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `bootstrap_provider.py`

Source: [src/robot_systems/paint_tray_dry/bootstrap_provider.py](../../../src/robot_systems/paint_tray_dry/bootstrap_provider.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.paint.bootstrap_provider`, `src.robot_systems.paint.paint_robot_system`, `src.robot_systems.paint_tray_dry`, `src.robot_systems.paint_tray_dry.paint_robot_system`, `src.robot_systems.robot_system_bootstrap_provider`.

### `create_bootstrap_provider`

```python
def create_bootstrap_provider() -> RobotSystemBootstrapProvider
```

## `paint_robot_system.py`

Source: [src/robot_systems/paint_tray_dry/paint_robot_system.py](../../../src/robot_systems/paint_tray_dry/paint_robot_system.py).

Imports (including optional/function-local imports; not a startup dependency list): `dataclasses`, `os`, `src.robot_systems.paint.component_ids`, `src.robot_systems.paint.paint_robot_system`, `src.robot_systems.paint.processes.paint.paint_process_config_serializer`.

### `TrayDryerPaintRobotSystem`

```python
class TrayDryerPaintRobotSystem(PaintRobotSystem):
```

Paint system variant with storage isolated for the tray dryer.

Declared fields/defaults:

```python
ui_config = replace(PaintRobotSystem.ui_config, show_drying_mode_control=False)
allowed_dropoff_strategies = ('plate_layout',)
settings_specs = [replace(spec, serializer=PaintProcessConfigSerializer(replace(spec.serializer.get_default(), dropoff=replace(spec.serializer.get_default().dropoff, strategy='plate_layout')))) if spec.name == SettingsID.PAINT_PROCESS_CONFIG else spec for spec in PaintRobotSystem.settings_specs]
metadata = replace(PaintRobotSystem.metadata, name='PaintSystemTrayDryer', settings_root=os.path.join('storage', 'settings'), translations_root=os.path.join('storage', 'translations'))
```

## `paint_system_config.py`

Source: [src/robot_systems/paint_tray_dry/paint_system_config.py](../../../src/robot_systems/paint_tray_dry/paint_system_config.py).

Optional overrides for this paint robot system. Shared defaults live in src.robot_systems.paint.paint_system_config. Declare only values that should differ for this system, using the same names. Unspecified values inherit the shared defaults. Overrides apply to this system only; they never modify the shared module or another paint system. These are source-controlled application/diagnostic switches, not machine settings. Examples (uncomment to override): SHOW_DASHBOARD_CAMERA_PREVIEW = True PAINT_ADJUSTMENT_APP = False BYPASS_CONTOUR_PREPARATION = False Intentionally empty: current behavior is preserved until an override is added.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
