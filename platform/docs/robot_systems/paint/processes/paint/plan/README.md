# Paint planning

Planning converts selected workpiece geometry/configuration into raw execution inputs and paint-specific robot paths. `PaintWorkpiecePreparationService` combines injected matching hooks, live defaults and a targeting transformer. Enabled/available matching failure returns an unknown-workpiece result; only disabled/unavailable matching permits captured-contour fallback.

`PaintPickupTransferPlanner` creates pickup/transfer poses. `paint_contact_motion/` constructs source contact plans and projects continuous motion. Contour interpolation helpers prepare source geometry and diagnostic output. These plans feed the execution facade and business machine; plan construction does not itself prove completion of a robot command.

Shared pixel/robot conversion and `WorkpieceExecutionPlan` ownership remain in the engine path-preparation package. Exact defaults, result fields and parameters are in the references below.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `paint_contact_motion/` | [paint_contact_motion](paint_contact_motion/README.md) |

[Complete source index](../../../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
