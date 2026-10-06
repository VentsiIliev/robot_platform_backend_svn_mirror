# Code issues found during documentation audit

Audit date: 2026-10-06. Production code is unchanged. Severity below describes the possible impact of the demonstrated trigger, not evidence that it happened on a real machine. Reproductions used local objects/fakes, with no robot or hardware commands.

Run the seven deterministic checks from the repository root:

```bash
.venv/bin/python docs/_tools/reproduce_code_issues.py
```

This script asserts the current defects and prints `F01`–`F07`; it intentionally fails if their behavior has been fixed. It is an audit reproduction, not a regression test that should pass after remediation.

## Reproduced defects

### F01 — Register write defaults recurse (medium)

**Location:** [i_register_transport.py](../src/engine/hardware/communication/i_register_transport.py), `write_register()` / `write_registers()`.

**Trigger:** Implement the only abstract operation, `read_register()`, instantiate that valid subclass, and call `write_register(0, 1)` or a nonempty batch write.

**Evidence:** Single write calls batch write; batch write calls single write. Neither default terminates without a subclass override. The reproduction raises `RecursionError`.

**Impact:** A nominally valid transport cannot fail cleanly on unsupported writes. Current Modbus implementations override writes, so this is a base-contract defect rather than a demonstrated failure of those devices.

**Suggested fix/verification:** Make unsupported writes fail explicitly or require one primitive implementation; test read-only behavior plus single/batch fallback behavior without mutual recursion.

### F02 — Repeated start releases another active run's exclusivity (high)

**Location:** [base_process.py](../src/engine/process/base_process.py), `_transition()`; [system_manager.py](../src/engine/system/system_manager.py), `acquire()`.

**Trigger:** Start process A, then call `A.start()` again while it is `RUNNING`.

**Evidence:** `_transition(RUNNING)` acquires the manager before checking the transition table. Same-owner acquire succeeds, but `RUNNING → RUNNING` is rejected and releases A's ownership. A's state remains `RUNNING`. The reproduction then starts B successfully while A is still `RUNNING`.

**Impact:** Duplicate start requests can defeat the single-process gate and permit concurrent operations. The reproduction uses `BaseProcess`; it does not show which deployed UI can generate such a duplicate request.

**Suggested fix/verification:** Validate transitions before acquisition, or track ownership newly obtained by the attempted transition. Verify duplicate starts/resumes preserve ownership and block competing processes.

### F03 — Synchronous state delivery under non-reentrant locks deadlocks (high)

**Location:** [system_manager.py](../src/engine/system/system_manager.py), `acquire()` / `release()` / `_publish()`; [base_process.py](../src/engine/process/base_process.py), state transitions/publication; [message_broker.py](../src/engine/core/message_broker.py), synchronous `publish()`.

**Trigger:** A `SystemTopics.STATE` subscriber calls `manager.release("A")` during A's acquisition event.

**Evidence:** The callback runs synchronously while `acquire()` holds `threading.Lock`; `release()` tries to acquire the same lock. The reproduction confirms callback entry and that the acquisition thread never completes its short join. It uses a daemon thread so the audit process can exit.

**Impact:** A reentrant control callback can freeze acquisition/transition execution. `BaseProcess` also publishes while holding a non-reentrant lock, exposing the analogous risk if its own state subscriber calls a locking lifecycle method. The manager case is reproduced; the base-process case is source inspection, not a separate deployed-flow reproduction.

**Suggested fix/verification:** Publish ordered state notifications after releasing state locks, with an explicit policy for concurrent/reentrant transitions. Simply changing lock type needs careful event-order review. Verify callbacks can query/control state without deadlock and preserve event order.

### F04 — Stop during sequence advancement does not cancel the next start (high)

**Location:** [process_sequence.py](../src/engine/process/process_sequence.py), `_on_current_stopped()` / `stop()`.

**Trigger:** Call `sequence.stop()` during `before_next_start()` and then let that callback return `True`. This deterministically exercises the window also exposed to a concurrent stop.

**Evidence:** Advancement assigns/subscribes the next process before running the hook outside the lock. `stop()` targets that still-IDLE process and unsubscribes it; the pending callback subsequently calls `next_process.start()` without checking cancellation. The next process ends up `RUNNING` after the stop request.

**Impact:** A stop can be lost between phases; the started next process is also no longer observed by the sequence. This contradicts the class docstring's pending-advancement cancellation claim.

**Suggested fix/verification:** Track a run/cancellation generation and revalidate immediately before starting the next process; verify stop/pause/reset during hooks and concurrent completion cannot start a canceled phase.

### F05 — Startup numeric validation accepts non-finite values (low)

**Location:** [startup_config.py](../src/bootstrap/startup_config.py), `_read_optional_float()`.

**Trigger:** Supply `NaN` for a nonnegative startup delay/timeout. Python's JSON decoder accepts `NaN` by default; the helper checks only numeric type and comparison with the minimum.

**Evidence:** `NaN < minimum` is false, so the reproduction returns NaN rather than rejecting it. Positive infinity is accepted by the same logic.

**Impact:** Malformed configuration can reach time/sleep/timeout operations and produce errors or unusable startup behavior. This is not a problem with the checked-in finite config.

**Suggested fix/verification:** Require `math.isfinite(value)` in addition to the minimum and reject nonstandard JSON numeric constants as appropriate. Test NaN/infinity, booleans and valid boundary values.

### F06 — Completion wait succeeds without target orientation data (medium)

**Location:** [motion_service.py](../src/engine/robot/services/motion_service.py), `_wait_for_position()`.

**Trigger:** Wait for a six-coordinate target when a driver returns only XYZ matching its position.

**Evidence:** `orientation_delta` is initialized to zero and computed only if both poses have six values. The reproduction returns `[0, 0, 0]` for target `[0, 0, 0, 90, 90, 90]`; three samples satisfy the wait and it returns `True` despite having no orientation evidence.

**Impact:** Malformed/incomplete pose responses can falsely confirm a requested orientation. Normal drivers returning valid six-coordinate poses do not trigger this reproduction.

**Suggested fix/verification:** Require all requested coordinates and finite values before counting a stable sample. Test incomplete XYZ/orientation data, malformed values and wrapped-angle success. Preserve the intentional `move_ptp()` → driver `move_linear()` contract.

### F07 — Missing jog return code becomes success (medium)

**Location:** [ros2_robot.py](../src/engine/robot/drivers/ros2_robot.py), `start_jog()`, with the same fallback in `start_servo_jog()` and `start_joint_jog()`.

**Trigger:** A client returns `None` instead of an integer jog result code.

**Evidence:** `ret = client_call(...) or 0` normalizes missing/false responses to the success code. The fake-client reproduction confirms `start_jog()` returns zero for `None`. By comparison, this driver's PTP/linear methods reject non-integer and boolean response codes.

**Impact:** Invalid transport responses can appear to confirm jog acceptance and update higher-level jog/floor-supervision state. A valid client returning an integer code does not trigger this defect. No live malformed-response incident is claimed.

**Suggested fix/verification:** Apply consistent integer-result validation to jog methods, preserving valid zero/nonzero codes and rejecting `None`/booleans/malformed payloads. Test the three jog entry points with fake clients.

## Source-inspected issues and implementation limitations

These entries have concrete code evidence but have not been exercised against hardware or a full deployed user flow. Keep them separate from the reproduced defects above.

### I01 — Startup cleanup does not cover all post-build failures (medium)

[run_main.py](../src/bootstrap/run_main.py) stops the backend if `SystemBuilder.build()` fails. Its wider cleanup `finally` starts only around `qt_app.exec()`. Exceptions in intervening shell/localization/login/descriptor setup can leave a built system/backend without their normal `stop()` calls. Review ownership across the whole startup transaction and test an injected failure after system build. No entry-point change was made.

### I02 — Shared weight contracts import glue-specific settings (architecture)

[i_cell_calibrator.py](../src/engine/hardware/weight/interfaces/i_cell_calibrator.py), [i_weight_cell_service.py](../src/engine/hardware/weight/interfaces/i_weight_cell_service.py), and [http_weight_cell_factory.py](../src/engine/hardware/weight/http/http_weight_cell_factory.py) import `src.robot_systems.glue.settings.cells`. This reverses the intended engine/system dependency and impedes independently packaging/reusing the weight engine. Move shared DTO/config contracts to a neutral owning layer with migration/compatibility tests; runtime breakage is not claimed.

### I03 — Twin runtime is not attached by generic startup (integration limitation)

[TwinRobotSystem](../src/robot_systems/twin_robot/twin_robot_system.py) expects `set_twin_runtime()`. The current generic startup uses `build_configured_robot()` instead of `TwinBootstrapProvider.build_robot()` and does not attach a twin runtime. The package has a product entry, but is absent from the checked-in startup supported-system list. This may be intentional unfinished integration; the dashboard package should not be documented as ready for synchronized production merely because it exists.

### I04 — Welding dashboard process remains a simulation (implementation limitation)

[WeldingProcess](../src/robot_systems/welding/processes/welding_process.py) completes via a three-second timer, uses no required-service gate by default, and restarts a full timer on resume. It has no welding-motion/IO execution. This is documented current behavior, not a claim that simulation is an accidental bug.

### I05 — Hand-eye configuration persistence contract is not implemented (low)

[IHandEyeCalibrationService.save_config()](../src/applications/hand_eye_calibration/service/i_hand_eye_service.py) says it persists a configuration. [HandEyeCalibrationService.save_config()](../src/applications/hand_eye_calibration/service/hand_eye_service.py) only assigns `_config`. Config edits therefore have no persistence in that implementation. Reconcile the contract or add system-owned serialization and test restart persistence. Saved calibration results are separate from acquisition settings.

### I06 — Documentation viewer lacks path confinement and source/asset serving (tooling)

[serve_docs.py](../serve_docs.py), `DocsHandler.do_GET()`, joins a URL-derived path to the repository root without canonical-path containment validation. A crafted `..` URL can address Markdown outside the repository. The server binds localhost and only renders `.md`; this is a local file-exposure boundary issue, not a remotely reproduced exploit. Restrict allowed roots after resolving the requested path, and verify traversal rejection using dummy files.

The viewer also returns 404 for linked `.py`, `.json`, `.pdf` and image files; its custom heading slugging differs from GitHub Markdown for punctuation/code-formatted headings. Local editor/repository links work, but viewer support would need a separate tool change. Its docstring's `serve_docs.y_pixels` invocation is an additional typo; the executable is `serve_docs.py`. The embedded JavaScript string also produces a Python `SyntaxWarning` for `\s` at line 474; a raw string or properly escaped literal would preserve the regex without that warning.

## Verification snapshot

The existing runner discovered 3,336 tests: 3,312 passed, 23 skipped, no assertion failures, and one sandbox `PermissionError` on Unix-socket binding. The blocked test `tests.engine.remote_support.test_controller.RemoteSupportControllerTests.test_client_and_controller_exchange_status_over_unix_socket` passed when rerun with socket permission. The above seven defects reproduced separately despite the existing suite passing its executable checks.

All `src/` and `pl_gui/` Python files parsed successfully. Documentation checks validate relative file links and generated reference coverage. No live motion, serial, camera calibration, deployment or release operation was performed by the audit reproductions.
