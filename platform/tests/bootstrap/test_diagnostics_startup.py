from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from src.engine.diagnostics.config import DiagnosticsConfig


class DiagnosticsStartupTests(unittest.TestCase):
    def test_service_drains_on_normal_exit_and_startup_exception(self):
        import src.bootstrap.run_main as main
        for error in (None, ValueError('application startup failed')):
            with self.subTest(error=error):
                config = SimpleNamespace(diagnostics=DiagnosticsConfig())
                service = Mock()
                service.status = {'state': 'recording'}
                order = Mock()
                order.attach_mock(service.start, 'start')
                order.attach_mock(service.close, 'close')
                with (patch.object(main, 'setup_logging'),
                      patch.object(main, 'load_startup_config', return_value=config),
                      patch.object(main, 'build_diagnostics_service', return_value=service) as factory,
                      patch.object(main, '_run_application', side_effect=error) as application):
                    order.attach_mock(application, 'application')
                    if error is None:
                        main.main()
                    else:
                        with self.assertRaises(ValueError) as raised:
                            main.main()
                        self.assertIs(raised.exception, error)
                factory.assert_called_once_with(config.diagnostics)
                application.assert_called_once_with(config, service)
                self.assertEqual([call[0] for call in order.mock_calls], ['start', 'application', 'close'])

    def test_unavailable_optional_service_does_not_block_application(self):
        import src.bootstrap.run_main as main
        service = Mock()
        service.start.return_value = False
        service.status = {'state': 'unavailable', 'last_error': 'disk unavailable'}
        with (patch.object(main, 'setup_logging'),
              patch.object(main, 'load_startup_config'),
              patch.object(main, 'build_diagnostics_service', return_value=service),
              patch.object(main, '_run_application') as application,
              self.assertLogs('main', level='WARNING') as logs):
            main.main()
        application.assert_called_once()
        service.close.assert_called_once()
        self.assertIn('disk unavailable', logs.output[0])
