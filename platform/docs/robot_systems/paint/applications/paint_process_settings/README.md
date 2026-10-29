# `src/robot_systems/paint/applications/paint_process_settings`

This page follows the source directory. The reference below records its modules and contracts; follow child guides for nested implementations.

[Parent guide](../README.md).

## Paint-head check settings

The head-check group exposes the enable switch (factory default off), frequency
policy, N-cycle interval, inspection timeout and individual PRESENT, MISSING,
MISALIGNED, UNKNOWN, failure and timeout responses. It also exposes whether
report-only UNKNOWN observations wait for confirmation. The factory policy is
every cycle, with a one-second window. See the
[integration guide](../../paint_head_check/README.md) for exact defaults, response
semantics, mode exclusions and required taught inspection pose.

`head_check_fields.py` and `view/head_check_choices.py` map typed configuration and
registered policy descriptions to localized settings choices. Persistence is the
`head_check` object within the process settings; settings do not store a fallback
inspection pose. A timeout response cannot be RETRY. The retired
`check_after_final_dropoff` key is accepted when reading old files but discarded;
it is neither exposed nor written back.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `controller/` | [controller](controller/README.md) |
| `model/` | [model](model/README.md) |
| `service/` | [service](service/README.md) |
| `view/` | [view](view/README.md) |

[Complete source index](../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
