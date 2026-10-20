import logging

from PyQt6.QtCore import QCoreApplication, QObject, pyqtSignal
from src.applications.base.background_worker import BackgroundWorker
from src.applications.base.i_application_controller import IApplicationController
from src.applications.base.styled_message_box import show_warning, ask_yes_no
from src.applications.robot_settings.model.mapper import RobotCalibrationMapper, RobotSettingsMapper
from src.applications.robot_settings.model.robot_settings_model import RobotSettingsModel
from src.applications.robot_settings.view.robot_settings_view import RobotSettingsView
from src.engine.core.i_messaging_service import IMessagingService
from src.shared_contracts.declarations import MovementGroupType
from src.shared_contracts.events.robot_events import RobotTopics


class _MotionBridge(QObject):
    done = pyqtSignal(object, str)
    failed = pyqtSignal(str, str)


class _ConfigBridge(QObject):
    changed = pyqtSignal()


class RobotSettingsController(IApplicationController, BackgroundWorker):

    def __init__(self, model: RobotSettingsModel, view: RobotSettingsView,
                 messaging: IMessagingService):
        BackgroundWorker.__init__(self)
        self._model    = model
        self._view     = view
        self._logger   = logging.getLogger(self.__class__.__name__)
        self._messaging = messaging
        self._motion_bridge = _MotionBridge()
        self._motion_bridge.done.connect(self._on_motion_done)
        self._motion_bridge.failed.connect(self._on_motion_failed)
        self._config_bridge = _ConfigBridge()
        self._config_bridge.changed.connect(self._on_robot_config_changed)

        self._view.save_requested.connect(self._on_save)
        self._view.discard_requested.connect(self._on_discard)
        self._view.remove_group_requested.connect(self._on_remove_group)
        self._view.set_current_requested.connect(self._on_set_current)
        self._view.move_to_requested.connect(self._on_move_to)
        self._view.execute_requested.connect(self._on_execute)
        self._view.targeting_changed.connect(self._on_targeting_changed)
        self._view.collision_config_refresh_requested.connect(
            self._on_collision_config_refresh)
        self._view.collision_config_save_requested.connect(
            self._on_collision_config_save)
        self._view.collision_diagnostics_open_requested.connect(
            self._on_collision_diagnostics_open)
        self._rviz_busy = False
        self._stopped = False
        self._view.rviz_status_refresh_requested.connect(self._on_rviz_refresh)
        self._view.rviz_enabled_requested.connect(self._on_rviz_enabled)
        self._view.destroyed.connect(self.stop)
        if self._messaging is not None:
            self._messaging.subscribe(
                RobotTopics.ROBOT_CONFIG_CHANGED,
                self._on_robot_config_changed_raw,
            )



    def load(self) -> None:
        config, calibration, targeting_definitions = self._model.load()
        flat = {
            **RobotSettingsMapper.to_flat_dict(config),
            **RobotCalibrationMapper.to_flat_dict(calibration),
        }
        self._view.load_config(flat)
        self._view.load_targeting_definitions(targeting_definitions)

        self._view.load_movement_groups(
            self._model.get_expected_movement_groups(),
            definitions=self._model.get_movement_group_definitions(),
        )
        self._view.mark_saved()

    def _on_discard(self) -> None:
        self.load()

    def stop(self) -> None:
        if self._stopped:
            return
        self._stopped = True
        self._stop_threads()
        try:
            self._view.rviz_status_refresh_requested.disconnect(self._on_rviz_refresh)
            self._view.rviz_enabled_requested.disconnect(self._on_rviz_enabled)
            self._view.collision_config_refresh_requested.disconnect(
                self._on_collision_config_refresh)
            self._view.collision_config_save_requested.disconnect(
                self._on_collision_config_save)
            self._view.collision_diagnostics_open_requested.disconnect(
                self._on_collision_diagnostics_open)
        except (RuntimeError, TypeError):
            pass
        if self._messaging is not None:
            try:
                self._messaging.unsubscribe(
                    RobotTopics.ROBOT_CONFIG_CHANGED,
                    self._on_robot_config_changed_raw,
                )
            except (RuntimeError, TypeError):
                pass
        try:
            self._motion_bridge.done.disconnect(self._on_motion_done)
        except (RuntimeError, TypeError):
            pass
        try:
            self._motion_bridge.failed.disconnect(self._on_motion_failed)
        except (RuntimeError, TypeError):
            pass

    def _on_robot_config_changed_raw(self, _message=None) -> None:
        self._config_bridge.changed.emit()

    def _on_robot_config_changed(self) -> None:
        try:
            self._view.update_robot_config(self._model.reload_config())
            self._view.load_targeting_definitions(self._model.reload_targeting_definitions())
            self._view.mark_saved()
            self._logger.debug("Robot Settings UI refreshed after external config change")
        except Exception:
            self._logger.exception("Failed to refresh Robot Settings after external config change")

    def _on_save(self, _values: dict) -> None:
        try:
            flat            = self._view.get_values()
            movement_groups = self._view.get_movement_groups()
            targeting_definitions = self._view.get_targeting_definitions()
            self._logger.debug("Saving %d fields, %d movement groups", len(flat), len(movement_groups))
            self._model.save(flat, movement_groups, targeting_definitions)
            self._view.mark_saved()
            self._publish_targeting_changed(targeting_definitions)
            self._logger.info("Robot settings saved")
        except Exception:
            self._logger.exception("Failed to save robot settings")

    def _on_set_current(self, group_name: str) -> None:
        position = self._model.get_current_position()
        if position is None:
            show_warning(
                self._view,
                self._t("Set Current Position"),
                self._t("Could not read robot position.\nMake sure the robot is connected."),
            )
            return

        position_str = "[" + ", ".join(f"{v:.3f}" for v in position) + "]"
        widget = self._view.get_group_widget(group_name)
        if widget is None:
            return

        from src.applications.robot_settings.view.movement_groups_tab import MovementGroupType
        if widget._def.group_type == MovementGroupType.SINGLE_POSITION:
            widget.set_position(position_str)
            self._logger.info("Set position for '%s': %s", group_name, position_str)
        else:
            widget.add_point(position_str)
            self._logger.info("Added point to '%s': %s", group_name, position_str)

    def _on_remove_group(self, name: str) -> None:
        if not ask_yes_no(
            self._view,
            self._t("Remove Group"),
            self._t("Remove movement group '{name}'?\n\nThis cannot be undone until you save.").format(name=name),
        ):
            return
        self._view.remove_movement_group(name)
        self._logger.info("Removed movement group '%s'", name)

    def _on_move_to(self, group_name: str, point_str) -> None:
        self._auto_save()
        if point_str is None:
            widget = self._view.get_group_widget(group_name)
            if widget is not None and widget._def.group_type == MovementGroupType.MULTI_POSITION:
                show_warning(
                    self._view,
                    self._t("Move To"),
                    self._t("No point selected.\nSelect a point from the list first."),
                )
                return
            fn = lambda: self._model.move_to_group(group_name)
            label = f"{self._t('Move To')} — {group_name}"
        else:
            fn = lambda: self._model.move_to_point(group_name, point_str)
            label = self._t("Move To point in {group_name}").format(group_name=group_name)
        self._run_blocking(fn=fn, label=label)

    def _on_execute(self, group_name: str) -> None:
        self._auto_save()
        self._run_blocking(
            fn=lambda: self._model.execute_group(group_name),
            label=f"{self._t('Execute')} — {group_name}",
        )

    def _on_targeting_changed(self) -> None:
        try:
            targeting = self._view.get_targeting_definitions()
            self._model.save_targeting_definitions(targeting)
            self._publish_targeting_changed(targeting)
            self._logger.debug("Auto-saved targeting definitions")
        except Exception:
            self._logger.exception("Auto-save targeting definitions failed")

    def _on_collision_config_refresh(self) -> None:
        self._view.set_collision_config_busy(True)
        self._run_in_thread(
            fn=self._model.load_collision_monitor_config,
            on_done=self._on_collision_config_loaded,
            on_error=self._on_collision_config_error,
        )

    def _on_rviz_refresh(self) -> None:
        if self._rviz_busy or self._stopped:
            return
        self._rviz_busy = True
        self._view.set_rviz_busy(True)
        self._run_in_thread(self._model.get_rviz_status, self._on_rviz_result, self._on_rviz_error)

    def _on_rviz_enabled(self, enabled: bool) -> None:
        if self._rviz_busy or self._stopped:
            return
        self._rviz_busy = True
        self._view.set_rviz_busy(True)
        self._run_in_thread(lambda: self._model.set_rviz_enabled(enabled), self._on_rviz_result, self._on_rviz_error)

    def _on_rviz_result(self, result) -> None:
        if self._stopped:
            return
        if not isinstance(result, dict) or not isinstance(result.get("running"), bool):
            message = result.get("error", "invalid_response") if isinstance(result, dict) else "invalid_response"
            self._on_rviz_error(str(message))
            return
        self._rviz_busy = False
        error = result.get("error")
        self._view.set_rviz_state(result["running"], str(error) if error else None)

    def _on_rviz_error(self, message: str) -> None:
        if self._stopped:
            return
        self._rviz_busy = False
        self._view.set_rviz_state(None, message)

    def _on_collision_config_save(self, config: dict) -> None:
        self._view.set_collision_config_busy(True)
        self._run_in_thread(
            fn=lambda: self._model.save_collision_monitor_config(config),
            on_done=self._on_collision_config_saved,
            on_error=self._on_collision_config_error,
        )

    def _on_collision_diagnostics_open(self) -> None:
        self._view.set_collision_config_busy(True)
        self._run_in_thread(
            fn=self._model.open_collision_monitor_diagnostics,
            on_done=self._on_collision_diagnostics_opened,
            on_error=self._on_collision_config_error,
        )

    def _on_collision_diagnostics_opened(self, result) -> None:
        if not isinstance(result, dict) or not result.get("success"):
            self._on_collision_config_error(
                str(result.get("error", "PlotJuggler could not be opened"))
                if isinstance(result, dict) else "PlotJuggler could not be opened")
            return
        config = result.get("config")
        if isinstance(config, dict):
            self._view.load_collision_config(config)
        self._view.set_collision_config_status(
            self._t("PlotJuggler opened with live observer diagnostics"), True)

    def _on_collision_config_loaded(self, result) -> None:
        if not isinstance(result, dict) or not result.get("success"):
            self._on_collision_config_error(
                str(result.get("error", "Collision monitor is unavailable"))
                if isinstance(result, dict) else "Collision monitor is unavailable")
            return
        config = result.get("config")
        if not isinstance(config, dict):
            self._on_collision_config_error("Backend returned an invalid configuration")
            return
        self._view.load_collision_config(config)
        self._view.set_collision_config_busy(False)

    def _on_collision_config_saved(self, result) -> None:
        if not isinstance(result, dict) or not result.get("success"):
            self._on_collision_config_error(
                str(result.get("error", "Collision settings were not applied"))
                if isinstance(result, dict) else "Collision settings were not applied")
            return
        config = result.get("config")
        if isinstance(config, dict):
            self._view.load_collision_config(config)
        self._view.set_collision_config_status(
            self._t("Collision settings applied and confirmed"), True)

    def _on_collision_config_error(self, message: str) -> None:
        self._view.set_collision_config_status(
            self._t("Collision monitor unavailable: {message}").format(message=message),
            False,
        )

    def _auto_save(self) -> None:
        """Flush current movement groups to disk before any motion — NavigationService reads from settings."""
        try:
            self._model.save(
                self._view.get_values(),
                self._view.get_movement_groups(),
                self._view.get_targeting_definitions(),
            )
            self._view.mark_saved()
            self._publish_targeting_changed(self._view.get_targeting_definitions())
            self._logger.debug("Auto-saved before motion")
        except Exception:
            self._logger.exception("Auto-save before motion failed")

    def _publish_targeting_changed(self, targeting_definitions: dict | None) -> None:
        if self._messaging is None:
            return
        try:
            self._messaging.publish(
                RobotTopics.TARGETING_DEFINITIONS_CHANGED,
                targeting_definitions or {},
            )
        except Exception:
            self._logger.debug("Failed to publish targeting-definitions change event", exc_info=True)

    def _run_blocking(self, fn, label: str) -> None:
        self._run_in_thread(
            fn=fn,
            on_done=lambda result: self._on_motion_done(result, label),
            on_error=lambda message: self._on_motion_failed(message, label),
        )

    def _on_motion_done(self, result, label: str) -> None:
        ok, reason = result if isinstance(result, tuple) else (bool(result), "")
        if not ok:
            msg = reason or (
                self._t("Motion failed for '{label}'.\nCheck the robot is connected and the group has a position configured.").format(
                    label=label
                )
            )
            show_warning(self._view, self._t(label), msg)
        else:
            self._logger.info("%s completed successfully", label)

    def _on_motion_failed(self, error: str, label: str) -> None:
        self._logger.exception("%s raised an unexpected error: %s", label, error)
        show_warning(
            self._view,
            self._t(label),
            error or self._t("Unexpected error while running '{label}'.").format(label=label),
        )

    @staticmethod
    def _t(text: str) -> str:
        translated = QCoreApplication.translate("RobotSettings", text)
        return translated or text
