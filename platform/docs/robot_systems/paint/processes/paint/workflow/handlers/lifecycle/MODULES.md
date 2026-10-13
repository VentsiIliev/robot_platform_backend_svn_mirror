# Module reference: `src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle/__init__.py).


## `completed_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle/completed_handler.py).

- `handle_completed`: See source for contract.

## `error_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle/error_handler.py).

- `handle_error`: See source for contract.

## `finished_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle/finished_handler.py).

- `handle_finished`: Restore resources after an expected stop without marking work completed.

## `idle_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle/idle_handler.py).

- `handle_idle`: See source for contract.

## `pause_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle/pause_handler.py).

- `handle_paused`: See source for contract.

## `startup_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle/startup_handler.py).

- `handle_starting`: Choose the first production phase for this cycle.

## `stopped_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle/stopped_handler.py).

- `handle_stopped`: See source for contract.

## `terminal_common.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/lifecycle/terminal_common.py).

- `restore_cycle_resources`: See source for contract.
- `stop_machine`: See source for contract.
