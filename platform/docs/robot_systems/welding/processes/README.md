# Welding processes

`WeldingProcess` currently simulates work with a three-second daemon timer. Start schedules completion, stop/pause/reset cancels the timer, and resume schedules a new full-duration timer. Requirements default to none. It does not execute welding motion or IO.

A system-owned robot-calibration wrapper file remains in this directory, while current `WeldingRobotSystem.on_start()` imports the shared engine `RobotCalibrationProcess`. Do not infer the runtime import path from the presence of a legacy wrapper. See the owning system and module reference for actual wiring.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
