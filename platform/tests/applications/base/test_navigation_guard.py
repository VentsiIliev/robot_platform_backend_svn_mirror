import threading
import time
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from PyQt6.QtWidgets import QApplication

from src.applications.base.application_factory import finalize_application_build
from src.applications.base.background_worker import BackgroundWorker
from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.i_application_view import IApplicationView
from pl_gui.shell.AppShell import AppShell
from src.robot_systems.paint.applications.dashboard.service.paint_dashboard_service import PaintDashboardService
from src.shared_contracts.events.process_events import ProcessState


class _View(IApplicationView):
    def setup_ui(self):
        pass

    def clean_up(self):
        pass


class _Controller(IApplicationController, BackgroundWorker):
    def __init__(self):
        BackgroundWorker.__init__(self)
        self.process_active = False

    def load(self):
        pass

    def stop(self):
        self._stop_threads()

    def has_active_operations(self):
        return self.process_active


class NavigationGuardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def pump_until(self, predicate):
        deadline = time.monotonic() + 3
        while not predicate() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(.005)
        self.assertTrue(predicate())

    @patch('src.applications.base.i_application_view.show_warning')
    def test_factory_blocks_submitted_read_and_process_until_completion(self, warning):
        view = _View('test')
        controller = _Controller()
        finalize_application_build(logger=MagicMock(), factory_name='test', model=MagicMock(), view=view, controller=controller)
        release = threading.Event()
        entered = threading.Event()
        done = []
        def read():
            entered.set()
            release.wait(3)
            return 'read'
        controller._run_in_thread(read, done.append)
        try:
            self.assertFalse(view.can_close())
            self.assertTrue(entered.wait(1))
            self.assertFalse(view.can_close())
        finally:
            release.set()
        self.pump_until(lambda: not controller.has_running_workers())
        self.assertEqual(done, ['read'])
        self.assertTrue(view.can_close())
        controller.process_active = True
        self.assertFalse(view.can_close())
        controller.process_active = False
        self.assertTrue(view.can_close())
        view.clean_up()
        view.deleteLater()

    def test_failed_worker_without_error_callback_finishes(self):
        controller = _Controller()
        def fail():
            raise RuntimeError('read failed')
        controller._run_in_thread(fail, MagicMock())
        self.pump_until(lambda: not controller.has_running_workers())
        controller.stop()

    def test_paint_process_guard_covers_paused_and_stopping_without_io(self):
        process = SimpleNamespace(state=ProcessState.IDLE, is_stopping=False)
        service = PaintDashboardService(process=process)
        for state, stopping, expected in [
            (ProcessState.IDLE, False, False), (ProcessState.RUNNING, False, True),
            (ProcessState.PAUSED, False, True), (ProcessState.STOPPED, True, True),
            (ProcessState.ERROR, True, True), (ProcessState.STOPPED, False, False),
        ]:
            process.state, process.is_stopping = state, stopping
            self.assertEqual(service.is_process_active(), expected)

    @patch('src.applications.base.i_application_view.show_warning')
    def test_guard_warning_initial_render_and_language_switch(self, warning):
        import json
        from pathlib import Path
        from src.engine.localization.dict_translator import DictTranslator
        view = _View('test')
        view.set_navigation_guard(lambda: True)
        catalog_root = Path(__file__).resolve().parents[3] / 'src/applications/localization'
        for language in ('en', 'bg', 'en'):
            catalog = json.loads((catalog_root / (language + '.json')).read_text())
            translator = DictTranslator(catalog)
            self.app.installTranslator(translator)
            try:
                self.assertFalse(view.can_close())
                self.assertEqual(warning.call_args.args[1], catalog['ApplicationNavigation']['Operation Running'])
                self.assertEqual(warning.call_args.args[2], catalog['ApplicationNavigation']['An operation is running or stopping. Please stop it or wait for it to finish before leaving.'])
            finally:
                self.app.removeTranslator(translator)
        view.deleteLater()

    def test_switch_to_another_cached_app_respects_active_guard(self):
        widget = MagicMock()
        widget.can_close.return_value = False
        shell = SimpleNamespace(running_widgets={'busy': widget})
        self.assertFalse(AppShell.can_switch_to_app(shell, 'other'))
        self.assertTrue(AppShell.can_switch_to_app(shell, 'busy'))
        widget.can_close.return_value = True
        self.assertTrue(AppShell.can_switch_to_app(shell, 'other'))

    def test_window_close_veto_precedes_cleanup(self):
        shell = SimpleNamespace(running_widgets={'app': MagicMock()}, cleanup=MagicMock())
        shell.running_widgets['app'].can_close.return_value = False
        event = MagicMock()
        AppShell.closeEvent(shell, event)
        event.ignore.assert_called_once()
        shell.cleanup.assert_not_called()
