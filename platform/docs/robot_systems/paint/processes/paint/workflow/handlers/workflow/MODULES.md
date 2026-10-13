# Module reference: `src/robot_systems/paint/processes/paint/workflow/handlers/workflow`

[Package guide](README.md). Generated from source ASTs; no runtime imports.

## `__init__.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/workflow/__init__.py).


## `capture_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/workflow/capture_handler.py).

- `handle_capture_workpiece`: See source for contract.

## `edge_cleanup_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/workflow/edge_cleanup_handler.py).

- `handle_edge_cleanup`: See source for contract.

## `execution_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/workflow/execution_handler.py).

- `handle_execute_paint`: See source for contract.

## `paint_contact_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/workflow/paint_contact_handler.py).

- `handle_paint_contact`: See source for contract.

## `pickup_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/workflow/pickup_handler.py).

- `handle_pickup`: See source for contract.
- `try_execute_ordered_pickup_and_paint_contact`: Legacy adapter; production uses the typed ordered-attempt result.
- `execute_ordered_pickup_and_paint_contact_result`: Execute pickup/staging and primary paint contact as one preplanned ordered chain.
- `build_ordered_second_pass_segments`: Build the guarded unwind, re-attach, and contact sequence for pass two.
- `_unmatched_second_pass_requested`: See source for contract.

## `plan_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/workflow/plan_handler.py).

- `handle_build_execution_plan`: See source for contract.
- `_path_executor_supports_motion_states`: See source for contract.

## `preparation_handler.py`

[Source](../../../../../../../../src/robot_systems/paint/processes/paint/workflow/handlers/workflow/preparation_handler.py).

- `handle_prepare_workpiece`: See source for contract.
- `_cycle_default_paint_settings`: See source for contract.
