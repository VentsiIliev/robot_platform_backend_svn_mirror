# Shared system declarations

This package defines the types used to describe systems before runtime instances exist. `system_specs.py` supplies metadata, settings/service specs, shell folders/application specs and role policy. Other modules describe movement groups, work areas, tools, dispense channels and targeting frames/points.

A robot system owns concrete values; `SystemBuilder` consumes them to validate and construct runtime services. `ApplicationSpec.factory(robot_system)` is a deferred construction hook, not a widget created at declaration time. `SettingsSpec` associates an enum key, serializer and relative storage key. `ServiceSpec` associates a service key, interface, required/optional policy and optional custom builder.

Stable IDs are persisted and consumed across processes/settings/screens. Changing an ID is a migration concern; changing a display label is presentation/localization work. Use enum values from shared engine or system-specific component IDs at injection/retrieval sites rather than inventing string keys.

The [module reference](MODULES.md) gives every declaration's exact fields/defaults, enum members, methods and exports. See [robot systems](../../robot_systems/README.md) for ownership and [bootstrap](../../bootstrap/README.md) for consumption.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
