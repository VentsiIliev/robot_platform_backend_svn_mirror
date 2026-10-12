from __future__ import annotations

from src.engine.hardware.communication.modbus.modbus import ModbusConfig
from src.engine.hardware.vacuum_pump.interfaces.i_vacuum_pump_controller import IVacuumPumpController
from src.engine.hardware.vacuum_pump.models.vacuum_pump_config import VacuumPumpConfig
from src.engine.hardware.vacuum_pump.vacuum_pump_controller import VacuumPumpController


def build_modbus_vacuum_pump_controller(
    modbus_config: ModbusConfig,
    vacuum_config: VacuumPumpConfig | None = None,
    profile_name: str = "default",
) -> IVacuumPumpController:
    from src.engine.hardware.communication.transport_registry import DEFAULT_TRANSPORT_REGISTRY
    config = vacuum_config or VacuumPumpConfig()
    if hasattr(modbus_config, "get_slave"):
        if modbus_config.get_slave(profile_name).transport_type == "modbus_bitwise_fc16":
            _validate_bitwise_config(config)
        transport = DEFAULT_TRANSPORT_REGISTRY.build_for_slave(modbus_config, profile_name)
    else:
        from src.engine.hardware.vacuum_pump.modbus.modbus_vacuum_pump_transport import (
            ModbusVacuumPumpTransport,
        )
        transport = ModbusVacuumPumpTransport(
            port=modbus_config.port,
            slave_address=modbus_config.slave_address,
            baudrate=modbus_config.baudrate,
            bytesize=modbus_config.bytesize,
            stopbits=modbus_config.stopbits,
            parity=modbus_config.parity,
            timeout=modbus_config.timeout,
        )
    return VacuumPumpController(
        transport=transport,
        config=config,
    )


def _validate_bitwise_config(config: VacuumPumpConfig) -> None:
    """Reject legacy word masks before constructing a bit-addressed controller."""
    from src.engine.hardware.xinje import XinjeMA8X8YR

    pump_bit = XinjeMA8X8YR.resolve_output(config.pump_register)
    registers = {"pump_register": pump_bit}
    values = {"on_value": config.on_value, "off_value": config.off_value}
    if config.blow_off_register is not None:
        blow_off_bit = XinjeMA8X8YR.resolve_output(config.blow_off_register)
        registers["blow_off_register"] = blow_off_bit
        values.update(blow_off_on_value=config.blow_off_on_value,
                      blow_off_off_value=config.blow_off_off_value)
        if pump_bit == blow_off_bit:
            raise ValueError("Bitwise vacuum pump and blow-off must use distinct bit indices")
    for name, address in registers.items():
        if not 0 <= address <= 15:
            raise ValueError(f"Bitwise vacuum pump {name} must be a bit index in 0..15")
    for name, value in values.items():
        if not isinstance(value, int) or value not in (0, 1):
            raise ValueError(f"Bitwise vacuum pump {name} must be 0 or 1, not a word mask ({value!r})")
