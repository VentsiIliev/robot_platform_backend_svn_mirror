from __future__ import annotations

import logging
import math
from copy import deepcopy
from dataclasses import replace
import threading
from collections.abc import Callable, Sequence
from typing import Literal

from .interfaces import IToolService
from .interfaces.i_robot_service import IRobotService
from .interfaces.tool_operation_result import (
    ToolErrorCode, ToolOperationFailure, ToolOperationResult,
)
from .configuration.robot_settings import RobotSettings, MovementGroup
from .configuration.movement_group_settings import MovementGroupSettings
from .interfaces.i_tool_changer import IToolChanger
from .interfaces.i_motion_service import IMotionService
from .interfaces.tool_definition import ToolDefinition
from .tool_changer import ToolChangeStep, SlotConfig
from src.shared_contracts.declarations import ToolSlotDefinition


class ToolManager(IToolService):
    """Execute tool changes with typed outcomes and guarded runtime state.

    Expected validation and I/O failures become ToolOperationResult.error.
    Internal guards raise ToolOperationFailure so their codes survive the public
    result boundary. Legacy (ok, message) unpacking remains supported.
    """

    def __init__(
        self,
        motion_service: IMotionService,
        tool_changer:   IToolChanger,
        robot_config: RobotSettings,
        movement_groups: MovementGroupSettings,
        slot_definitions: list[ToolSlotDefinition] | None = None,
        tool_activator: IRobotService | None = None,
        operator_confirmation: Callable[[str], bool] | None = None,
        configuration_provider: (
            Callable[[], tuple[IToolChanger, RobotSettings, MovementGroupSettings]] | None
        ) = None,
        tool_change_group: str = "",
        tool_change_mover: Callable[[str, threading.Event, int, int], bool] | None = None,
    ) -> None:
        self._motion         = motion_service
        self._tool_changer   = tool_changer
        self._robot_config   = robot_config
        self._movement_groups = movement_groups
        self._slot_definitions = {
            int(slot.id): slot for slot in (slot_definitions or [])
        }
        self._current_gripper: int | None = None
        self._attached_slot_id: int | None = None
        self._tool_activator = tool_activator
        self._operator_confirmation = operator_confirmation
        self._recovery_required = False
        self._tool_change_group = str(tool_change_group or "").strip()
        self._tool_change_mover = tool_change_mover
        self._configuration_provider = configuration_provider
        self._lock           = threading.Lock()
        self._logger         = logging.getLogger(self.__class__.__name__)
        self._tools: dict[str, object] = {}

    @property
    def current_gripper(self) -> int | None:
        return self._current_gripper

    @property
    def current_tool(self) -> int | None:
        return self._current_gripper

    def pickup_tool(
        self, tool_id: int, max_retries: int = 3, *, cancelled: threading.Event | None = None,
    ) -> ToolOperationResult:
        return self.pickup_gripper(tool_id, max_retries, cancelled=cancelled)

    def drop_off_tool(
        self, tool_id: int, max_retries: int = 3, *, cancelled: threading.Event | None = None,
    ) -> ToolOperationResult:
        return self.drop_off_gripper(tool_id, max_retries, cancelled=cancelled)

    def add_tool(self, name: str, tool: object) -> None:
        self._tools[name] = tool

    def get_tool(self, name: str) -> object | None:
        return self._tools.get(name)

    def verify_gripper_change(self, target_gripper_id: int) -> bool:
        return self._current_gripper == target_gripper_id

    def _refresh_configuration(self) -> None:
        if self._configuration_provider is None:
            return
        try:
            changer, config, groups = self._configuration_provider()
        except Exception as exc:
            raise ToolOperationFailure(ToolErrorCode.CONFIGURATION_ERROR, str(exc),
                                       detail=type(exc).__name__) from exc
        # Occupancy is runtime state, not evidence supplied by saved settings.
        for tool in self._tool_changer.list_tools():
            old_id = self._tool_changer.get_slot_id_by_tool_id(tool.id)
            new_id = changer.get_slot_id_by_tool_id(tool.id)
            if old_id is not None and old_id == new_id:
                if self._tool_changer.is_slot_occupied(old_id):
                    changer.set_slot_not_available(new_id)
                else:
                    changer.set_slot_available(new_id)
        self._tool_changer, self._robot_config, self._movement_groups = changer, config, groups

    def pickup_gripper(
        self, gripper_id: int, max_retries: int = 3, *, cancelled: threading.Event | None = None,
    ) -> ToolOperationResult:
        """Run a saved pickup. Failed robot commands are never automatically replayed."""
        return self._change_tool(gripper_id, "pickup", cancelled)

    def drop_off_gripper(
        self, gripper_id: int, max_retries: int = 3, *, cancelled: threading.Event | None = None,
    ) -> ToolOperationResult:
        """Run a saved drop-off; max_retries is retained for caller compatibility."""
        return self._change_tool(gripper_id, "dropoff", cancelled)

    @property
    def recovery_required(self) -> bool:
        return self._recovery_required

    def confirm_attached_tool(self, tool_id: int | None) -> ToolOperationResult:
        """Reconcile after manual physical inspection, including after a failed operation.

        This is an operator acknowledgement, not a sensor check. None means the
        flange is empty. Runtime attachment/occupancy is deliberately not persisted.
        """
        if not self._lock.acquire(blocking=False):
            return ToolOperationResult.failure(ToolErrorCode.BUSY, "Another tool operation is running")
        try:
            self._refresh_configuration()
            slot_id = None
            if tool_id is not None:
                slot_id = self._tool_changer.get_slot_id_by_tool_id(tool_id)
                if slot_id is None:
                    return ToolOperationResult.failure(
                        ToolErrorCode.SLOT_NOT_FOUND,
                        f"No slot found for tool {tool_id}",
                    )
            self._require_ready_robot()
            if self._tool_activator is None:
                return ToolOperationResult.failure(
                    ToolErrorCode.ACTIVATION_UNAVAILABLE,
                    "Robot tool activation is not configured",
                )
            try:
                activated = self._tool_activator.set_active_tool(0 if tool_id is None else tool_id)
            except Exception as exc:
                raise ToolOperationFailure(ToolErrorCode.ACTIVATION_FAILED, str(exc),
                                           detail=type(exc).__name__) from exc
            if not activated:
                return ToolOperationResult.failure(
                    ToolErrorCode.ACTIVATION_FAILED,
                    "Failed to activate the confirmed tool",
                )
            self._robot_config.robot_tool = 0 if tool_id is None else int(tool_id)
            self._current_gripper = tool_id
            self._attached_slot_id = slot_id
            if slot_id is not None:
                self._tool_changer.set_slot_available(slot_id)
            self._recovery_required = False
            return ToolOperationResult()
        except ToolOperationFailure as exc:
            return ToolOperationResult(error=exc.error)
        except Exception as exc:
            self._logger.exception("Failed to confirm attached tool")
            return ToolOperationResult.failure(ToolErrorCode.UNEXPECTED_ERROR, str(exc), detail=type(exc).__name__)
        finally:
            self._lock.release()

    def _change_tool(self, tool_id: int, operation: Literal["pickup", "dropoff"],
                     cancelled: threading.Event | None) -> ToolOperationResult:
        if not self._lock.acquire(blocking=False):
            return ToolOperationResult.failure(ToolErrorCode.BUSY, "Another tool operation is running")
        started = False
        try:
            if self._recovery_required:
                return ToolOperationResult.failure(
                    ToolErrorCode.RECOVERY_REQUIRED,
                    "Inspect the tool and confirm its attachment state before continuing",
                )
            self._refresh_configuration()
            if not any(tool.id == tool_id for tool in self._tool_changer.list_tools()):
                return ToolOperationResult.failure(ToolErrorCode.TOOL_NOT_FOUND, f"Tool {tool_id} not found")
            slot_id = self._tool_changer.get_slot_id_by_tool_id(tool_id)
            if slot_id is None:
                return ToolOperationResult.failure(ToolErrorCode.SLOT_NOT_FOUND, f"No slot found for tool {tool_id}")
            if operation == "pickup" and self._current_gripper is not None:
                return ToolOperationResult.failure(
                    ToolErrorCode.TOOL_ALREADY_HELD,
                    f"Tool {self._current_gripper} is already held; drop it off first",
                )
            if operation == "dropoff":
                if self._current_gripper != tool_id:
                    return ToolOperationResult.failure(
                        ToolErrorCode.TOOL_NOT_HELD,
                        f"Tool {tool_id} is not currently held",
                    )
                if slot_id != self._attached_slot_id:
                    return ToolOperationResult.failure(
                        ToolErrorCode.SLOT_ASSIGNMENT_CHANGED,
                        "Held tool slot assignment changed; inspect and confirm its attachment state",
                    )
                if self._tool_changer.is_slot_occupied(slot_id):
                    return ToolOperationResult.failure(
                        ToolErrorCode.SLOT_OCCUPIED,
                        f"Slot {slot_id} is already occupied",
                    )
            slot: SlotConfig | None = getattr(self._tool_changer, "get_slot", lambda _: None)(slot_id)
            steps = list((slot.pickup_sequence if operation == "pickup" else slot.dropoff_sequence) if slot else [])
            if not steps:
                positions, group = self._get_positions_and_config(tool_id, operation.upper())
                if not positions or group is None:
                    return ToolOperationResult.failure(
                        ToolErrorCode.SEQUENCE_NOT_CONFIGURED,
                        f"No {operation} sequence or movement group configured for tool {tool_id}",
                    )
                try:
                    steps = [ToolChangeStep(pose=pose, velocity=group.velocity,
                                            acceleration=group.acceleration) for pose in positions]
                except (TypeError, ValueError) as exc:
                    raise ToolOperationFailure(ToolErrorCode.INVALID_SEQUENCE, str(exc),
                                               detail=type(exc).__name__) from exc
            steps = deepcopy(steps)
            # Physical operations must not contain the opposite attachment action.
            opposite = "detach" if operation == "pickup" else "attach"
            if any(step.kind == opposite for step in steps):
                return ToolOperationResult.failure(
                    ToolErrorCode.INVALID_SEQUENCE,
                    f"Invalid {operation} sequence: contains {opposite}",
                )
            steps = self._prepare_endpoint_moves(steps)
            self._validate_sequence(steps, tool_id)
            self._require_ready_robot()
            if steps[0].kind != "start_at_tool_changer":
                self._require_tool_change_position()
            if cancelled is not None and cancelled.is_set():
                return ToolOperationResult.failure(ToolErrorCode.CANCELLED, "Sequence stopped")
            started = True
            result = self._execute_taught_sequence(steps, tool_id, cancelled, slot_id)
            if not result.success:
                self._recovery_required = True
            if result.success:
                self._record_attachment(slot_id, tool_id, operation == "pickup")
            return result
        except ToolOperationFailure as exc:
            if started:
                self._recovery_required = True
            return ToolOperationResult(error=exc.error)
        except Exception as exc:
            if started:
                self._recovery_required = True
            self._logger.exception("Tool %s failed", operation)
            return ToolOperationResult.failure(ToolErrorCode.UNEXPECTED_ERROR, str(exc), detail=type(exc).__name__)
        finally:
            self._lock.release()

    def execute_sequence(self, slot_id: int, steps: Sequence[ToolChangeStep | dict[str, object]],
                         cancelled: threading.Event | None = None) -> ToolOperationResult:
        """Run an editor draft through the shared executor, without committing occupancy.

        Attach/detach steps select the TCP; they do not actuate a physical coupler.
        Cancellation is cooperative between blocking robot calls. The caller must
        also request stop_motion to interrupt a move already in progress.
        """
        if not self._lock.acquire(blocking=False):
            return ToolOperationResult.failure(ToolErrorCode.BUSY, "Another tool operation is running")
        try:
            if self._recovery_required:
                return ToolOperationResult.failure(
                    ToolErrorCode.RECOVERY_REQUIRED,
                    "Inspect the tool and confirm its attachment state before continuing",
                )
            self._refresh_configuration()
            slot: SlotConfig | None = getattr(self._tool_changer, "get_slot", lambda _: None)(slot_id)
            if slot is None:
                return ToolOperationResult.failure(ToolErrorCode.SLOT_NOT_FOUND, f"Slot {slot_id} not found")
            try:
                sequence = [ToolChangeStep.from_dict(step) if isinstance(step, dict) else deepcopy(step)
                            for step in steps]
            except (TypeError, ValueError, AttributeError) as exc:
                raise ToolOperationFailure(ToolErrorCode.INVALID_SEQUENCE, str(exc),
                                           detail=type(exc).__name__) from exc
            sequence = self._prepare_endpoint_moves(sequence)
            self._validate_sequence(sequence, slot.tool_id, allow_confirmation=False)
            self._require_ready_robot()
            if sequence[0].kind != "start_at_tool_changer":
                self._require_tool_change_position()
            result = self._execute_taught_sequence(sequence, slot.tool_id, cancelled)
            return ToolOperationResult(message="Sequence completed") if result.success else result
        except ToolOperationFailure as exc:
            return ToolOperationResult(error=exc.error)
        except Exception as exc:
            self._logger.exception("Failed to run taught tool sequence")
            return ToolOperationResult.failure(ToolErrorCode.UNEXPECTED_ERROR, str(exc), detail=type(exc).__name__)
        finally:
            self._lock.release()

    def get_tools(self) -> list[ToolDefinition]:
        with self._lock:
            self._refresh_configuration()
            return deepcopy(self._tool_changer.list_tools())

    def _prepare_endpoint_moves(self, steps: Sequence[ToolChangeStep]) -> list[ToolChangeStep]:
        """Resolve optional endpoint moves from live settings before any motion."""
        endpoint_kinds = {"start_at_tool_changer", "finish_at_tool_changer"}
        if not any(step.kind in endpoint_kinds for step in steps):
            return list(steps)
        if not any(step.kind not in endpoint_kinds for step in steps):
            raise ToolOperationFailure(ToolErrorCode.INVALID_SEQUENCE,
                                       "Capture positions before running the sequence")
        position = self._get_tool_change_position()
        if steps[0].kind == "start_at_tool_changer":
            self._read_tool_change_position()  # Verify feedback availability before the approach move.
        group = self._movement_groups.movement_groups[self._tool_change_group]
        result: list[ToolChangeStep] = []
        for index, step in enumerate(steps):
            if step.kind not in endpoint_kinds:
                result.append(step)
                continue
            if ((step.kind == "start_at_tool_changer" and index != 0)
                    or (step.kind == "finish_at_tool_changer" and index != len(steps) - 1)):
                raise ToolOperationFailure(ToolErrorCode.INVALID_SEQUENCE,
                                           "Tool-changer moves must be at sequence boundaries",
                                           step_number=index + 1)
            result.append(replace(step, pose=list(position), motion_type=group.motion_type,
                                  velocity=group.velocity, acceleration=group.acceleration,
                                  blend_radius=0.0))
        return result

    def _get_tool_change_position(self) -> list[float]:
        if not self._tool_change_group:
            raise ToolOperationFailure(ToolErrorCode.POSITION_NOT_CONFIGURED,
                                       "Tool-changer position is not configured or is invalid")
        group = self._movement_groups.movement_groups.get(self._tool_change_group)
        try:
            expected = group.parse_position() if group is not None else None
            if expected is None or len(expected) != 6:
                raise ValueError("Invalid staging pose")
            expected = [float(value) for value in expected]
            if not all(math.isfinite(value) for value in expected):
                raise ValueError("Non-finite staging pose")
        except Exception as exc:
            raise ToolOperationFailure(ToolErrorCode.POSITION_NOT_CONFIGURED,
                                       "Tool-changer position is not configured or is invalid", detail=str(exc)) from exc

        return expected

    def _require_tool_change_position(self) -> None:
        """Require fresh feedback within the capture guard's 10 mm / 5 deg tolerances."""
        if not self._tool_change_group:
            return
        expected = self._get_tool_change_position()
        pose = self._read_tool_change_position()

        for index in range(6):
            delta = (abs(pose[index] - expected[index]) if index < 3
                     else abs((pose[index] - expected[index] + 180.0) % 360.0 - 180.0))
            tolerance = 10.0 if index < 3 else 5.0
            if delta > tolerance:
                self._logger.warning(
                    "Tool-change position check failed: group=%s axis=%s delta=%.3f tolerance=%.3f",
                    self._tool_change_group, ("X", "Y", "Z", "RX", "RY", "RZ")[index], delta, tolerance,
                )
                raise ToolOperationFailure(
                    ToolErrorCode.NOT_AT_TOOL_CHANGER,
                    "Robot is not at the configured tool-changer position",
                )

    def _read_tool_change_position(self) -> list[float]:
        try:
            reader: Callable[[], list[float]] | None = getattr(
                self._tool_activator, "get_current_position_fresh", None)
            if not callable(reader):
                raise ValueError("Fresh pose reader is unavailable")
            pose = list(reader())
            if len(pose) != 6:
                raise ValueError("Invalid robot pose")
            pose = [float(value) for value in pose]
            if not all(math.isfinite(value) for value in pose):
                raise ValueError("Non-finite robot pose")
        except Exception as exc:
            raise ToolOperationFailure(ToolErrorCode.POSE_UNAVAILABLE,
                                       "Cannot verify robot pose at the tool changer", detail=str(exc)) from exc

        return pose

    def _require_ready_robot(self) -> None:
        robot = self._tool_activator
        if robot is None:
            return
        try:
            if hasattr(robot, "is_healthy") and not robot.is_healthy():
                raise ToolOperationFailure(ToolErrorCode.ROBOT_UNAVAILABLE, "Robot is unavailable")
            if hasattr(robot, "get_state"):
                state = str(robot.get_state() or "").strip().lower()
                if state in {"moving", "running", "executing", "busy", "error", "fault", "disconnected"}:
                    raise ToolOperationFailure(
                        ToolErrorCode.ROBOT_NOT_READY,
                        f"Robot must be stationary and ready (current state: {state})",
                    )
            if hasattr(robot, "get_current_velocity"):
                velocity = robot.get_current_velocity()
                if velocity is not None and (not math.isfinite(float(velocity)) or abs(float(velocity)) > 0.01):
                    raise ToolOperationFailure(
                        ToolErrorCode.ROBOT_NOT_READY,
                        "Robot must be stationary before tool setup",
                    )
        except ToolOperationFailure:
            raise
        except Exception as exc:
            raise ToolOperationFailure(ToolErrorCode.ROBOT_UNAVAILABLE, str(exc),
                                       detail=type(exc).__name__) from exc

    def _validate_sequence(self, steps: Sequence[ToolChangeStep], tool_id: int | None,
                           *, allow_confirmation: bool = True) -> None:
        if not steps:
            raise ToolOperationFailure(
                ToolErrorCode.INVALID_SEQUENCE,
                "Capture positions before running the sequence",
            )
        for step_number, step in enumerate(steps, start=1):
            if step.kind not in {"motion", "wait", "attach", "detach", "operator_confirm",
                                 "start_at_tool_changer", "finish_at_tool_changer"}:
                raise ToolOperationFailure(
                    ToolErrorCode.INVALID_SEQUENCE,
                    f"Unsupported tool-change step kind: {step.kind}",
                    step_number=step_number,
                )
            numbers = step.pose + [step.velocity, step.acceleration, step.blend_radius, step.wait_seconds]
            if not all(math.isfinite(value) for value in numbers):
                raise ToolOperationFailure(
                    ToolErrorCode.INVALID_SEQUENCE,
                    "Sequence contains non-finite values",
                    step_number=step_number,
                )
            allowed_motion_types = {"linear", "ptp"}
            if step.kind in {"start_at_tool_changer", "finish_at_tool_changer"} and self._tool_change_mover is not None:
                allowed_motion_types.add("fast_lin")
            is_motion = step.kind in {"motion", "start_at_tool_changer", "finish_at_tool_changer"}
            if is_motion and (len(step.pose) != 6 or step.motion_type not in allowed_motion_types
                              or step.velocity <= 0 or step.acceleration <= 0 or step.blend_radius < 0):
                raise ToolOperationFailure(
                    ToolErrorCode.INVALID_SEQUENCE,
                    "Invalid sequence motion settings",
                    step_number=step_number,
                )
            if step.kind == "wait" and step.wait_seconds < 0:
                raise ToolOperationFailure(
                    ToolErrorCode.INVALID_SEQUENCE,
                    "Invalid sequence wait duration",
                    step_number=step_number,
                )
            if step.kind == "operator_confirm" and (not allow_confirmation or not callable(self._operator_confirmation)):
                raise ToolOperationFailure(
                    ToolErrorCode.CONFIRMATION_REQUIRED,
                    "Operator confirmation required; no confirmation handler is configured",
                    step_number=step_number,
                )
            if step.kind == "attach" and tool_id is None:
                raise ToolOperationFailure(
                    ToolErrorCode.INVALID_SEQUENCE,
                    "Assign a tool to the slot before running an attach action",
                    step_number=step_number,
                )
            if step.kind in {"attach", "detach"} and self._tool_activator is None:
                raise ToolOperationFailure(
                    ToolErrorCode.ACTIVATION_UNAVAILABLE,
                    "Robot tool activation is not configured",
                    step_number=step_number,
                )


    def _record_attachment(self, slot_id: int, tool_id: int, attached: bool) -> None:
        if attached:
            self._tool_changer.set_slot_available(slot_id)
            self._current_gripper = tool_id
            self._attached_slot_id = slot_id
        else:
            self._tool_changer.set_slot_not_available(slot_id)
            self._current_gripper = None
            self._attached_slot_id = None

    def _execute_taught_sequence(self, steps: Sequence[ToolChangeStep], tool_id: int | None,
                                cancelled: threading.Event | None = None,
                                slot_id: int | None = None) -> ToolOperationResult:
        cancelled = cancelled if cancelled is not None else threading.Event()
        for index, step in enumerate(steps):
            step_number = index + 1
            if cancelled.is_set():
                return ToolOperationResult.failure(ToolErrorCode.CANCELLED, "Sequence stopped",
                                                   step_number=step_number)
            failure_code = ToolErrorCode.UNEXPECTED_ERROR
            try:
                if step.kind in {"motion", "start_at_tool_changer", "finish_at_tool_changer"}:
                    failure_code = ToolErrorCode.MOTION_FAILED
                    if step.kind in {"start_at_tool_changer", "finish_at_tool_changer"} and self._tool_change_mover is not None:
                        moved = self._tool_change_mover(self._tool_change_group, cancelled,
                                                        self._robot_config.robot_tool, self._robot_config.robot_user)
                    elif step.motion_type == "ptp":
                        moved = self._motion.move_ptp(
                            position=step.pose, tool=self._robot_config.robot_tool,
                            user=self._robot_config.robot_user, velocity=step.velocity,
                            acceleration=step.acceleration, wait_to_reach=True)
                    else:
                        moved = self._motion.move_linear(
                            position=step.pose, tool=self._robot_config.robot_tool,
                            user=self._robot_config.robot_user, velocity=step.velocity,
                            acceleration=step.acceleration, blendR=step.blend_radius, wait_to_reach=True)
                    if not moved:
                        return ToolOperationResult.failure(
                            ToolErrorCode.CANCELLED if cancelled.is_set() else ToolErrorCode.MOTION_FAILED,
                            "Sequence stopped" if cancelled.is_set() else f"Sequence step {step_number} failed",
                            step_number=step_number)
                    if step.kind in {"start_at_tool_changer", "finish_at_tool_changer"}:
                        if cancelled.is_set():
                            return ToolOperationResult.failure(ToolErrorCode.CANCELLED, "Sequence stopped",
                                                               step_number=step_number)
                        self._require_tool_change_position()
                elif step.kind == "wait":
                    if cancelled.wait(step.wait_seconds):
                        return ToolOperationResult.failure(ToolErrorCode.CANCELLED, "Sequence stopped",
                                                           step_number=step_number)
                elif step.kind == "operator_confirm":
                    handler = self._operator_confirmation
                    if handler is None:
                        return ToolOperationResult.failure(
                            ToolErrorCode.CONFIRMATION_REQUIRED,
                            "Operator confirmation required; no confirmation handler is configured",
                            step_number=step_number)
                    failure_code = ToolErrorCode.CONFIRMATION_FAILED
                    if not handler(step.label):
                        return ToolOperationResult.failure(
                            ToolErrorCode.CONFIRMATION_DECLINED,
                            f"Operator confirmation declined at step {step_number}", step_number=step_number)
                elif step.kind in {"attach", "detach"}:
                    activator = self._tool_activator
                    if activator is None:
                        return ToolOperationResult.failure(ToolErrorCode.ACTIVATION_UNAVAILABLE,
                                                           "Robot tool activation is not configured",
                                                           step_number=step_number)
                    active_tool = tool_id if step.kind == "attach" else 0
                    if active_tool is None:
                        return ToolOperationResult.failure(
                            ToolErrorCode.INVALID_SEQUENCE,
                            "Assign a tool to the slot before running an attach action", step_number=step_number)
                    failure_code = ToolErrorCode.ACTIVATION_FAILED
                    if not activator.set_active_tool(active_tool):
                        return ToolOperationResult.failure(ToolErrorCode.ACTIVATION_FAILED,
                                                           f"Failed to activate tool {active_tool}",
                                                           step_number=step_number)
                    self._robot_config.robot_tool = int(active_tool)
                    # Preserve completed attachment boundaries even if retreat later fails.
                    if slot_id is not None and tool_id is not None:
                        self._record_attachment(slot_id, tool_id, step.kind == "attach")
            except ToolOperationFailure as exc:
                return ToolOperationResult(error=replace(exc.error, step_number=step_number))
            except Exception as exc:
                self._logger.exception("Tool sequence failed at step %d", step_number)
                return ToolOperationResult.failure(failure_code, str(exc), step_number=step_number,
                                                   detail=type(exc).__name__)
        return (ToolOperationResult.failure(ToolErrorCode.CANCELLED, "Sequence stopped")
                if cancelled.is_set() else ToolOperationResult())

    def _get_positions_and_config(
        self, gripper_id: int, operation: str,
    ) -> tuple[list[list[float]] | None, MovementGroup | None]:
        """
        Resolves positions and motion config for a gripper operation.
        Prefers declared slot-to-movement-group bindings and falls back to the
        historical "SLOT {slot_id} {PICKUP|DROPOFF}" naming convention.
        """
        slot_id = self._tool_changer.get_slot_id_by_tool_id(gripper_id)
        if slot_id is None:
            self._logger.warning("No slot found for gripper_id=%d", gripper_id)
            return None, None

        group_name = self._resolve_group_name(slot_id, operation)
        if not group_name:
            self._logger.warning(
                "No declared %s movement group for slot_id=%d",
                operation.lower(),
                slot_id,
            )
            return None, None
        group = self._movement_groups.movement_groups.get(group_name)
        if group is None:
            self._logger.warning(
                "Movement group '%s' not found in robot config — available: %s",
                group_name, list(self._movement_groups.movement_groups.keys()),
            )
            return None, None

        try:
            positions = self._positions_from_group(group)
        except (TypeError, ValueError) as exc:
            raise ToolOperationFailure(ToolErrorCode.INVALID_SEQUENCE, str(exc),
                                       detail=type(exc).__name__) from exc
        if not positions:
            self._logger.warning("Movement group '%s' has no positions defined", group_name)
            return None, None

        return positions, group

    def _resolve_group_name(self, slot_id: int, operation: str) -> str:
        slot = self._slot_definitions.get(int(slot_id))
        if slot is not None:
            if operation == "PICKUP" and slot.pickup_movement_group_id:
                return slot.pickup_movement_group_id
            if operation == "DROPOFF" and slot.dropoff_movement_group_id:
                return slot.dropoff_movement_group_id
        return f"SLOT {slot_id} {operation}"

    def _positions_from_group(self, group: MovementGroup) -> list[list[float]]:
        """Returns list of positions from a MovementGroup (points take priority over position)."""
        if group.points:
            return group.parse_points()
        pos = group.parse_position()
        return [pos] if pos is not None else []
