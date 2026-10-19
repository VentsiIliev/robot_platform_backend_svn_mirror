from __future__ import annotations

import logging
from typing import Callable
from src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller import IVacuumPumpController
from src.robot_systems.paint.timing import timed_step

_logger = logging.getLogger(__name__)


class PaintVacuumControl:
    """Apply paint pickup/release policy to the platform vacuum controller."""

    def __init__(
        self,
        pump: IVacuumPumpController | None,
        *,
        enabled_provider: Callable[[], bool],
        dry_run_provider: Callable[[], bool] | None = None,
    ) -> None:
        self._pump = pump
        self._enabled_provider = enabled_provider
        self._dry_run_provider = dry_run_provider or (lambda: False)

    @timed_step(_logger, "vacuum_on")
    def turn_vacuum_on(self, *, required: bool = False) -> tuple[bool, str]:
        """Enable the vacuum pump before pickup if one is configured."""
        if self._dry_run_provider():
            _logger.info("[DRY_RUN] Vacuum pump ON skipped")
            return True, ""
        if not self._enabled_provider():
            if required:
                _logger.error("[PICKUP] Vacuum pump is required but disabled; refusing to start motion")
                return False, "Servo-contact pickup requires the vacuum pump to be enabled"
            _logger.info("[PICKUP] Vacuum pump ON skipped: disabled by configuration")
            return True, ""
        if self._pump is None:
            if required:
                _logger.error("[PICKUP] Vacuum pump is required but unavailable; refusing to start motion")
                return False, "Servo-contact pickup requires an available vacuum pump"
            _logger.info("[PICKUP] Vacuum pump ON skipped: pump not configured")
            return True, ""
        _logger.info("[PICKUP] Turning vacuum pump ON before pickup")
        try:
            enabled = bool(self._pump.turn_on())
        except Exception:
            _logger.exception("[PICKUP] Vacuum pump ON command failed; refusing to start motion")
            return False, "Vacuum pump ON command failed; pickup motion was not started"
        if enabled:
            return True, ""
        return False, "Vacuum pump failed to turn on; pickup motion was not started"

    @timed_step(_logger, "vacuum_off")
    def turn_vacuum_off(self, *, wait_for_blow_off: bool = True) -> tuple[bool, str]:
        """Disable the vacuum pump after staging if one is configured."""
        if self._dry_run_provider():
            _logger.info("[DRY_RUN] Vacuum pump OFF skipped")
            return True, ""
        if not self._enabled_provider():
            _logger.info("[PICKUP] Vacuum pump OFF skipped: disabled by configuration")
            return True, ""
        if self._pump is None:
            _logger.info("[PICKUP] Vacuum pump OFF skipped: pump not configured")
            return True, ""
        _logger.info("[PICKUP] Turning vacuum pump OFF after staged pivot move")
        turn_off = (
            self._pump.turn_off
            if wait_for_blow_off
            else self._pump.turn_off_nonblocking
        )
        if turn_off():
            return True, ""
        return False, "Pickup succeeded, but vacuum pump OFF failed after pivot stage"
