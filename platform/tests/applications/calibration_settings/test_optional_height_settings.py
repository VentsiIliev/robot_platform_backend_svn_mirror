import unittest
from unittest.mock import MagicMock

from PyQt6.QtWidgets import QApplication

from src.applications.calibration.calibration_factory import CalibrationFactory
from src.applications.calibration.service.stub_calibration_service import StubCalibrationService
from src.applications.calibration_settings.calibration_settings_data import CalibrationSettingsData
from src.applications.calibration_settings.calibration_settings_factory import CalibrationSettingsFactory
from src.applications.calibration_settings.service.i_calibration_settings_service import ICalibrationSettingsService
from src.engine.robot.configuration import RobotCalibrationSettings
from src.engine.vision.calibration_vision_settings import CalibrationVisionSettings


def _settings():
    return CalibrationSettingsData(
        vision=CalibrationVisionSettings(), robot=RobotCalibrationSettings(),
    )


class _CalibrationWithoutHeight(StubCalibrationService):
    def load_calibration_settings(self):
        return _settings()


class OptionalHeightSettingsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_calibration_widget_loads_without_height_settings(self):
        view = CalibrationFactory(
            show_laser_tab=False, show_height_mapping_tab=False,
        ).build(_CalibrationWithoutHeight(), messaging=MagicMock())
        try:
            self.assertIsNotNone(view)
        finally:
            view._controller.stop()
            view.close()

    def test_settings_widget_hides_height_tabs_and_saves_remaining_settings(self):
        service = MagicMock(spec=ICalibrationSettingsService)
        service.load_settings.return_value = _settings()
        view = CalibrationSettingsFactory().build(service)
        try:
            self.assertFalse(view.settings_view._tabs.isTabVisible(2))
            self.assertFalse(view.settings_view._tabs.isTabVisible(3))
            self.assertTrue(view.settings_view._tabs.isTabVisible(0))
            view.save_requested.emit(view.settings_view.get_values())
            service.save_settings.assert_called_once()
            self.assertIsNone(service.save_settings.call_args.args[0].height)
        finally:
            view._controller.stop()
            view.close()
