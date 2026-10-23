from __future__ import annotations

from src.applications.base.i_application_model import IApplicationModel
from src.robot_systems.paint.applications.dashboard.dashboard_state import DashboardState
from src.robot_systems.paint.applications.dashboard.service.i_paint_dashboard_service import (
    ContourTransformDebugResult,
    IPaintDashboardService,
    DashboardCommandResult,
)


class PaintDashboardModel(IApplicationModel):
    def __init__(self, service: IPaintDashboardService):
        self._service = service

    def is_process_active(self) -> bool:
        """Include running, paused and stopping work without starting hardware I/O."""
        return self._service.is_process_active()

    def load(self) -> DashboardState:
        return self._service.load_state()

    def save(self, _data) -> None:
        return None

    def start(self, action_context: dict | None = None) -> DashboardState:
        if action_context:
            self._service.start(action_context)
        else:
            self._service.start()
        return self.load()

    def begin_start_request(self) -> dict:
        try:
            token = self._service.begin_start_request()
            return token if isinstance(token, dict) else {}
        except Exception:
            return {}

    def record_start_outcome(self, context: dict, outcome: str, stage: str, details: dict) -> None:
        try:
            self._service.record_start_outcome(context, outcome, stage, details)
        except Exception:
            pass

    def stop_process(self) -> DashboardState:
        self._service.stop()
        return self.load()

    def resume_vision_for_dashboard_exit(self) -> None:
        resume = getattr(self._service, "resume_vision_for_dashboard_exit", None)
        if callable(resume):
            resume()

    def toggle_pause(self) -> DashboardState:
        state = self.load()
        if state.process_state == "paused":
            self._service.resume()
        else:
            self._service.pause()
        return self.load()

    def reset_errors(self) -> DashboardState:
        self._service.reset_errors()
        return self.load()

    def acknowledge_collision(self) -> tuple[bool, str]:
        return self._service.acknowledge_collision()

    def collision_acknowledgement_required(self) -> bool:
        return self._service.collision_acknowledgement_required()

    def collision_detected(self) -> bool:
        return self._service.collision_detected()

    def retry_unmatched_workpiece(self) -> bool:
        return self._service.retry_unmatched_workpiece()

    def get_unmatched_paint_settings(self) -> dict:
        return self._service.get_unmatched_paint_settings()

    def save_unmatched_paint_settings(
        self,
        settings: dict | float,
        acceleration_percent: float | None = None,
        offset_mm: float | None = None,
    ):
        return self._service.save_unmatched_paint_settings(
            settings,
            acceleration_percent,
            offset_mm,
        )

    def relieve_cable(self):
        return self._service.relieve_cable()

    def get_acceleration_scale(self) -> float:
        return self._service.get_acceleration_scale()

    def save_acceleration_scale(self, scale_percent: float):
        return self._service.save_acceleration_scale(scale_percent)

    def is_paint_head_available(self) -> bool:
        return self._service.is_paint_head_available()

    def adjust_paint_head(self, direction: str, units: int):
        return self._service.adjust_paint_head(direction, units)

    def get_auxiliary_states(self) -> dict[str, bool]:
        return self._service.get_auxiliary_states()

    def set_auxiliary_enabled(self, device_id: str, enabled: bool):
        return self._service.set_auxiliary_enabled(device_id, enabled)

    def get_drying_mode(self) -> str:
        return self._service.get_drying_mode()

    def is_dry_run_mode_enabled(self) -> bool:
        return self._service.is_dry_run_mode_enabled() is True

    def set_drying_mode(self, mode: str):
        return self._service.set_drying_mode(mode)

    def get_production_start_guard_state(self, mode: str) -> dict[str, object]:
        return self._service.get_production_start_guard_state(mode)

    def prepare_production_start(self, mode: str, action_context: dict | None = None):
        if action_context:
            return self._service.prepare_production_start(mode, action_context)
        return self._service.prepare_production_start(mode)

    def get_plate_layout_state(self) -> dict[str, object]:
        return self._service.get_plate_layout_state()

    def confirm_empty_tray(self) -> DashboardCommandResult:
        return self._service.confirm_empty_tray()

    def clear_plate_layout(self):
        return self._service.clear_plate_layout()

    def remove_plate_placement(self, placement_id: int):
        return self._service.remove_plate_placement(placement_id)

    def capture_latest_contour_transform_debug(self) -> ContourTransformDebugResult:
        return self._service.capture_latest_contour_transform_debug()
