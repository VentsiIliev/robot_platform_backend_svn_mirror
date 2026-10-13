# Operator-paced paint adjustment

`session.py` owns adjustment phases, validated step commands, snapshots, and the path cursor. `incremental_painting.py` executes measured sections and moves to the inspection pose between commands. Only an explicit Finish continues to dropoff; cancellation and failure retain their typed outcomes.

This is a workflow around painting rather than another general-purpose workpiece operation. It uses the same painting operation and shared execution control as a normal cycle.

[Module reference](MODULES.md).

`settings_serializer.py` persists adjustment steps alongside the adjustment session and section executor.
