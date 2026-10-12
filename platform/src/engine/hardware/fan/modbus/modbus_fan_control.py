from __future__ import annotations

import logging
from src.engine.diagnostics.events import observe

_logger = logging.getLogger(__name__)

from src.engine.hardware.communication.i_register_transport import IRegisterTransport
from src.engine.core.i_health_checkable import IHealthCheckable
from src.engine.hardware.fan.interfaces.i_fan_control import IFanControl
from src.engine.hardware.xinje import XinjeMA8X8YR


class ModbusFanControl(IFanControl, IHealthCheckable):
    """Binary fan control through a configured register/coil transport."""

    def __init__(
        self,
        transport: IRegisterTransport,
        register: int | str = "Y0",
        on_value: int = 1,
        off_value: int = 0,
        diagnostic_name: str = "fan",
    ) -> None:
        self._diagnostic_name = diagnostic_name
        self._transport = transport
        self._register = XinjeMA8X8YR.resolve_output(register)
        self._on_value = int(on_value)
        self._off_value = int(off_value)
        self._last_operation_ok = False

    def turn_on(self) -> None:
        self._write(self._on_value)

    def turn_off(self) -> None:
        self._write(self._off_value)

    def read_state(self) -> bool:
        try:
            value = self._transport.read_register(self._register)
        except Exception:
            self._last_operation_ok = False
            raise
        self._last_operation_ok = True
        return int(value) == self._on_value

    def is_healthy(self) -> bool:
        return self._last_operation_ok

    def _write(self, value: int) -> None:
        name = self._diagnostic_name
        try:
            self._transport.write_register(self._register, value)
        except Exception:
            self._last_operation_ok = False
            observe(_logger, "fan.write_failed", level=logging.ERROR,
                    metrics={f"{name}.command_failures": 1},
                    output=(name, None), component=name, register=self._register)
            raise
        self._last_operation_ok = True
        state = value == self._on_value
        observe(_logger, "fan.output_written",
                metrics={f"{name}.commands.{'on' if state else 'off'}": 1},
                output=(name, state), component=name, register=self._register)
