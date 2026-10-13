# Pickup transfer planning

`transfer_planner.py` builds pickup and staging poses from prepared workpiece geometry and configuration. `build_required_plan()` reports missing or invalid geometry as `PaintPlanningError`; `build_plan()` retains its optional-result contract for callers such as preview preparation. Planning does not itself execute robot commands.

[Module reference](MODULES.md).
