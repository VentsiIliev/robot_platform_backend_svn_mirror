import os
from types import SimpleNamespace

os.environ.setdefault("EROB_CONFIG_PACKAGE", "zeroerr")

from motion.execution import trajectory_executor as trajectory_executor_module
from motion.execution.trajectory_executor import TrajectoryExecutor


class _Logger:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(str(message))

    def error(self, message):
        self.messages.append(str(message))


def test_post_stop_goal_acceptance_waits_once_for_stable_drive_state(monkeypatch):
    clock = SimpleNamespace(now=0.0)

    def monotonic():
        return clock.now

    def sleep(duration):
        clock.now += float(duration)

    monkeypatch.setattr(trajectory_executor_module.time, "monotonic", monotonic)
    monkeypatch.setattr(trajectory_executor_module.time, "sleep", sleep)
    monkeypatch.setattr(
        trajectory_executor_module.config,
        "EXECUTOR_DRIVE_ENABLE_STABLE_BEFORE_TRAJECTORY_S",
        0.0,
        raising=False,
    )
    monkeypatch.setattr(
        trajectory_executor_module.config,
        "EXECUTOR_POST_CONTROLLED_STOP_GOAL_ACCEPTANCE_STABLE_S",
        0.10,
        raising=False,
    )
    monkeypatch.setattr(
        trajectory_executor_module.config,
        "EXECUTOR_DRIVE_ENABLE_WAIT_TIMEOUT_S",
        2.0,
        raising=False,
    )

    logger = _Logger()
    executor = TrajectoryExecutor.__new__(TrajectoryExecutor)
    executor._node = SimpleNamespace(
        is_drive_operation_enabled_for_motion=lambda: True,
        get_logger=lambda: logger,
    )
    executor._last_controlled_stop_succeeded_monotonic = 0.0

    assert executor._ensure_drive_enabled_before_trajectory()
    assert clock.now >= 0.10
    assert executor._last_controlled_stop_succeeded_monotonic is None

    clock.now = 0.0
    assert executor._ensure_drive_enabled_before_trajectory()
    assert clock.now == 0.0
    assert any("accepting next trajectory" in message for message in logger.messages)
