from src.engine.common_settings_ids import CommonSettingsID
from src.robot_systems.paint.component_ids import SettingsID as PaintSettingsID
from src.robot_systems.paint_tray_dry.component_ids import SettingsID


def build_operator_lights_service(ctx):
    """Select simulated outputs or the existing configured hardware transport."""
    from src.engine.hardware.communication.memory_register_transport import MemoryRegisterTransport
    from src.engine.hardware.communication.transport_registry import DEFAULT_TRANSPORT_REGISTRY
    from src.engine.hardware.operator_lights.operator_lights import OperatorLights

    from src.engine.hardware.operator_lights.config import LightChannel
    from src.engine.hardware.xinje import XinjeMA8X8YR

    config = ctx.settings.get(SettingsID.OPERATOR_LIGHTS)
    if config.transport == "memory":
        return OperatorLights(MemoryRegisterTransport(), config)

    peripherals = ctx.settings.get(PaintSettingsID.PERIPHERALS)
    binding = peripherals.get("operator_lights")
    if binding is None:
        return None
    if set(binding.outputs) != set(config.channels):
        raise ValueError("Operator light peripheral outputs must match configured channel names")
    channels = {
        name: LightChannel(
            address=XinjeMA8X8YR.resolve_output(address),
            on_value=binding.commands.get(f"{name}_on", binding.commands.get("on", 1)),
            off_value=binding.commands.get(f"{name}_off", binding.commands.get("off", 0)),
        )
        for name, address in binding.outputs.items()
    }
    modbus_config = ctx.settings.get(CommonSettingsID.MODBUS_CONFIG)
    transport = DEFAULT_TRANSPORT_REGISTRY.build_for_slave_id(modbus_config, binding.slave_id)
    return OperatorLights(transport, config, channels=channels)
