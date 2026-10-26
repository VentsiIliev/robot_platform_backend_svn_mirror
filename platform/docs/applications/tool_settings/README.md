# `src/applications/tool_settings/` — Tool Settings

Manages the tool changer configuration: the set of available tools (`ToolDefinition`) and the physical slots (`SlotConfig`) that map slot positions to installed tools. Persists via `ISettingsService`.

The screen separates Tools, Slots, and guided TCP calibration into three tabs.
Tool and slot lists use touch-sized rows and action buttons. Slot assignment
changes are staged in the table until Save all changes; Discard restores the
last loaded assignments. The calibration tab has a tool selector and four
steps for reference capture, tool contacts, solving, and activation. Start over
resets the local progress display; capturing a new reference starts a fresh
calibration sample set in the service. Tool and slot dialogs use the shared
`KeyboardNumberField` for numeric inputs.

This is intended to be the shared tool-settings application for any robot system that adopts the common tool contract:
- `CommonSettingsID.TOOL_CHANGER_CONFIG`

In practice, robot systems should also declare:
- `CommonServiceID.TOOLS`
- `CommonSettingsID.ROBOT_CONFIG`

because the shared runtime `IToolService` is built separately through `SystemBuilder` and validates those contracts up front.

---

## MVC Structure

```
tool_settings/
├── service/
│   ├── i_tool_settings_service.py             ← IToolSettingsService (8 methods)
│   ├── stub_tool_settings_service.py          ← In-memory stub
│   └── tool_settings_application_service.py  ← Delegates to SettingsService
├── model/
│   └── tool_settings_model.py                 ← Thin delegation
├── view/
│   └── tool_settings_view.py                  ← Tools table + Slots table + edit forms
├── controller/
│   └── tool_settings_controller.py
└── tool_settings_factory.py
```

---

## `IToolSettingsService`

```python
class IToolSettingsService(ABC):
    # Tools
    def get_tools(self)                                   -> List[ToolDefinition]: ...
    def add_tool(self, tool_id: int, name: str)           -> Tuple[bool, str]: ...
    def update_tool(self, tool_id: int, name: str)        -> Tuple[bool, str]: ...
    def remove_tool(self, tool_id: int)                   -> Tuple[bool, str]: ...
    # Slots
    def get_slots(self)                                   -> List[SlotConfig]: ...
    def update_slot(self, slot_id: int, tool_id: int)     -> Tuple[bool, str]: ...
    def add_slot(self, slot_id: int, tool_id: int)        -> Tuple[bool, str]: ...
    def remove_slot(self, slot_id: int)                   -> Tuple[bool, str]: ...
```

`ToolDefinition` — `{tool_id: int, name: str, ...offsets}`
`SlotConfig` — `{slot_id: int, tool_id: int}` mapping a physical slot to an installed tool

---

## `ToolSettingsApplicationService`

Reads and writes the `TOOL_CHANGER_CONFIG` settings key via `ISettingsService`. All mutating operations:
1. Load current config
2. Apply the change
3. Persist via `settings_service.save(key, config)`

---

## Shared Wiring Pattern

```python
service = ToolSettingsApplicationService(
    robot_system._settings_service,
    robot_service=robot_system.get_optional_service(CommonServiceID.ROBOT),
    tool_service=robot_system.get_optional_service(CommonServiceID.TOOLS),
)
return WidgetApplication(widget_factory=lambda _ms: ToolSettingsFactory().build(service))
```

Use this app directly in any robot system that declares the common tool settings contract. `ApplicationSpec` is typically placed in the Service folder with icon `fa5s.tools`.

The application edits `CommonSettingsID.TOOL_CHANGER_CONFIG`. The runtime
`IToolService` is built separately by `SystemBuilder` through the shared
default builder in
[default_service_builders.py](../../../src/robot_systems/default_service_builders.py).

`ToolChangerSettings` and `ToolChangerSettingsSerializer` are now engine-level
types in
[tool_changer_settings.py](../../../src/engine/robot/configuration/tool_changer_settings.py),
not glue-specific settings classes.

The default tool catalog and default slot layout are robot-system declarations,
not engine defaults. A robot system should declare:
- `tools`
- `tool_slots`

and wire those into `ToolChangerSettingsSerializer(default_tools=..., default_slots=...)`
inside its `settings_specs`.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `localization/` | [localization](localization/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../SOURCE_INDEX.md).
<!-- source-navigation:end -->

## Shared sequence execution

Paint and glue inject the registered `IToolService` into the application service.
The sequence editor delegates its draft to `ToolManager.execute_sequence()`;
the application does not implement a second motion executor. Missing tool-service
wiring fails closed. Editing tools, calibration, and persistence remain the
application service's responsibility.

Draft runs preserve the editor contract: they execute the supplied steps without
saving them or committing attachment/slot occupancy. Attach/detach steps select
the active TCP; they do not actuate a physical coupler. A runtime process making
a complete tool change must call `IToolService.pickup_tool()` or
`drop_off_tool()` using the saved sequences instead.

The existing worker and stop path remain in use. Cancellation interrupts waits
and prevents subsequent steps. Stopping a move already in progress also requires
`stop_sequence_motion()`, which sends the robot stop request.

The shared executor returns `ToolOperationResult`, including a typed error code
and optional failing-step details. `ToolSettingsApplicationService` uses its
`success` and `message` fields and adapts them to the application's existing
`(ok, message)` contract; the view and model do not depend on engine result types.

## Optional Tool Changer endpoint moves

Each Pickup and Drop-off tab has independent **Start from Tool Changer** and
**Finish at Tool Changer** switches, both off by default. They are saved with the
sequence and apply to draft runs before saving as well. Start prepends a move to
the configured Tool Changer position; Finish appends that move after the taught
steps. Turning a switch off removes that generated move without changing any
captured positions. Reversing pickup into drop-off also reverses these endpoints.

Endpoint moves use the current movement group's position, speed, acceleration,
and motion type through the shared navigation service. They are symbolic saved
steps (`start_at_tool_changer` / `finish_at_tool_changer`), so changing the group
settings does not require recapturing the sequence. The table shows taught steps;
the switches control the generated moves around them.

With Start off, the existing staging-position check applies before execution.
With Start on, the manager checks configuration and feedback availability, makes
the approach move, then verifies arrival before executing any taught steps.
Finish also verifies arrival. Cancellation or a failed move prevents later steps.

The run buttons follow the selected tab: select **Drop-off**, enable its own start
and finish switches, then choose **Run drop-off**. The Pickup switches do not apply
to Drop-off. Running the inactive tab's sequence is disabled so visible settings
always match the sequence being executed.
