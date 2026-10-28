from contextlib import contextmanager
import threading
import unittest
from unittest.mock import MagicMock, patch

from src.engine.auth.access_change_guard import SystemAccessChangeGuard
from src.engine.auth.account_service import AccountService
from src.engine.system.system_manager import SystemManager
from src.robot_systems.twin_robot.runtime.activity import TwinRuntimeActivity
from src.robot_systems.twin_robot.twin_robot_system import TwinRobotSystem
from src.shared_contracts.accounts.commands import ChangePassword
from src.shared_contracts.authorization.errors import AccountRuntimeInUseError, ErrorCode, ServiceUnavailableError
from src.shared_contracts.authorization.results import Success
import tests.engine.auth.test_account_service as fixtures


class _Runtime:
    def __init__(self):
        self.activity = TwinRuntimeActivity.IDLE
        self.reserved = False
        self.allow_reservation = True
        self._lock = threading.RLock()

    def get_activity(self):
        return self.activity

    @contextmanager
    def hold_idle(self):
        with self._lock:
            idle = self.activity == TwinRuntimeActivity.IDLE and self.allow_reservation
            self.reserved = idle
            try:
                yield idle
            finally:
                self.reserved = False

    def try_start(self):
        if not self._lock.acquire(blocking=False):
            return False
        try:
            self.activity = TwinRuntimeActivity.RUNNING
            return True
        finally:
            self._lock.release()


class TwinAccountActivityTests(unittest.TestCase):
    def setUp(self):
        self.fixture = fixtures.AccountServiceTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.system = TwinRobotSystem()
        self.system._system_manager = SystemManager(MagicMock())
        self.runtime = _Runtime()
        self.system.set_twin_runtime(self.runtime)
        extension = self.system.account_access_extensions()
        self.guard = SystemAccessChangeGuard(self.fixture.session, self.system.system_manager,
                                            extension.activity_check, extension.idle_reservation)
        self.accounts = AccountService(self.fixture.store, self.fixture.session, self.fixture.policy,
                                       self.fixture.credentials, activity_guard=self.guard)

    def change(self):
        return self.accounts.change_password(ChangePassword(self.fixture.admin.summary.account_id, 1,
                                                           "replacement", "initial-secret"))

    def test_idle_commit_holds_external_lease_and_rejects_a_concurrent_motion_start(self):
        original = self.fixture.credentials.hash_password
        attempted = []
        def hash_password(password):
            self.assertTrue(self.runtime.reserved)
            worker = threading.Thread(target=lambda: attempted.append(self.runtime.try_start()))
            worker.start()
            worker.join(1)
            self.assertFalse(worker.is_alive())
            return original(password)
        with patch.object(self.fixture.credentials, "hash_password", side_effect=hash_password):
            self.assertIsInstance(self.change(), Success)
        self.assertTrue(attempted)
        self.assertTrue(all(value is False for value in attempted))
        self.assertFalse(self.runtime.reserved)
        self.assertIsNone(self.system.system_manager.active_process_id)
        self.assertTrue(self.runtime.try_start())

    def test_active_states_reject_changes_without_stopping_or_editing(self):
        for state in (TwinRuntimeActivity.STARTING, TwinRuntimeActivity.RUNNING,
                      TwinRuntimeActivity.PAUSED, TwinRuntimeActivity.STOPPING):
            with self.subTest(state=state):
                self.runtime.activity = state
                self.assertEqual(self.change().error.code, ErrorCode.BUSY)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)

    def test_unknown_or_legacy_activity_never_becomes_idle(self):
        for value in (TwinRuntimeActivity.UNKNOWN, "idle", None):
            self.runtime.activity = value
            with self.assertRaises(ServiceUnavailableError):
                self.change()
        self.system._twin_runtime = object()  # legacy adapter with no contract
        with self.assertRaises(ServiceUnavailableError):
            self.change()

    def test_busy_reservation_closes_the_query_to_commit_race(self):
        self.runtime.allow_reservation = False
        self.assertEqual(self.change().error.code, ErrorCode.BUSY)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)

    def test_adapter_replacement_cannot_bypass_an_active_access_reservation(self):
        self.assertTrue(self.system.system_manager.acquire("account_change"))
        with self.assertRaises(AccountRuntimeInUseError):
            self.system.set_twin_runtime(None)
        self.assertIs(self.system._twin_runtime, self.runtime)

    def test_running_runtime_cannot_be_detached_to_bypass_idle(self):
        self.runtime.activity = TwinRuntimeActivity.RUNNING
        with self.assertRaises(AccountRuntimeInUseError):
            self.system.set_twin_runtime(None)
        self.assertIs(self.system._twin_runtime, self.runtime)

    def test_operation_conflict_rolls_back_without_being_translated_by_the_lease(self):
        original = self.fixture.credentials.hash_password
        def switch_session(password):
            self.fixture.login(self.fixture.manufacturer)
            return original(password)
        with patch.object(self.fixture.credentials, "hash_password", side_effect=switch_session):
            self.assertEqual(self.change().error.code, ErrorCode.CONFLICT)
        self.assertEqual(self.fixture.get(self.fixture.admin), self.fixture.admin)
        self.assertFalse(self.runtime.reserved)
