import unittest
from dataclasses import replace
from threading import Event, get_ident

from src.engine.hardware.communication.memory_register_transport import MemoryRegisterTransport
from src.engine.hardware.operator_lights.config import OperatorLightsConfig, OperatorLightsConfigSerializer
from src.engine.hardware.operator_lights.operator_lights import OperatorLights
from src.robot_systems.paint_tray_dry.operator_light_coordinator import OperatorLightCoordinator
from src.shared_contracts.events.process_events import ProcessState, ProcessStateEvent


class Messaging:
    def subscribe(self, topic, callback):
        self.callback = callback

    def unsubscribe(self, topic, callback):
        self.callback = None


class ObservedLights(OperatorLights):
    def __init__(self, config):
        super().__init__(MemoryRegisterTransport(), config)
        self.applied = Event()
        self.writer_thread = None

    def set_active(self, channels):
        super().set_active(channels)
        self.writer_thread = get_ident()
        self.applied.set()


class CoordinatorTests(unittest.TestCase):
    def test_custom_colors_initial_snapshot_events_and_shutdown(self):
        config = OperatorLightsConfig(
            enabled=True, channels=("blue", "white"), state_mapping={
                "idle": (), "running": ("blue",), "paused": ("white",),
                "stopped": (), "error": ("blue", "white"),
            },
        )
        lights = ObservedLights(config)
        messaging = Messaging()
        coordinator = OperatorLightCoordinator(lights, config, messaging, "paint",
                                               lambda: ProcessState.RUNNING)
        coordinator.start()
        try:
            self.assertTrue(lights.applied.wait(2))
            self.assertEqual(lights.get_state(), {"blue": True, "white": False})
            self.assertNotEqual(lights.writer_thread, get_ident())
            lights.applied.clear()
            messaging.callback(ProcessStateEvent("paint", ProcessState.ERROR, ProcessState.RUNNING))
            self.assertTrue(lights.applied.wait(2))
            self.assertEqual(lights.get_state(), {"blue": True, "white": True})
        finally:
            coordinator.stop()
            lights.close()
        self.assertIsNone(messaging.callback)
        self.assertFalse(any(lights.get_state().values()))

    def test_unknown_missing_states_and_unknown_channels_rejected(self):
        config = OperatorLightsConfig()
        lights = ObservedLights(config)
        for mapping in ({"unknown": ()}, {"running": ("green",)}):
            with self.assertRaises(ValueError):
                OperatorLightCoordinator(lights, replace(config, state_mapping=mapping),
                                         Messaging(), "paint", lambda: ProcessState.IDLE)
        with self.assertRaises(ValueError):
            replace(config, state_mapping={"running": ("purple",)})

    def test_channel_objects_and_custom_mapping_roundtrip(self):
        config = OperatorLightsConfig(enabled=True)
        lights = ObservedLights(config)
        lights.set_active([lights.get_channel("green")])
        self.assertTrue(lights.get_state()["green"])
        with self.assertRaises(ValueError):
            lights.get_channel("purple")
        serializer = OperatorLightsConfigSerializer()
        self.assertEqual(serializer.from_dict(serializer.to_dict(config)), config)

    def test_subscription_event_takes_precedence_over_initial_snapshot(self):
        config = OperatorLightsConfig(enabled=True)
        lights = ObservedLights(config)
        messaging = Messaging()

        def snapshot():
            messaging.callback(ProcessStateEvent("paint", ProcessState.ERROR, ProcessState.IDLE))
            return ProcessState.IDLE

        coordinator = OperatorLightCoordinator(lights, config, messaging, "paint", snapshot)
        coordinator.start()
        try:
            self.assertTrue(lights.applied.wait(2))
            self.assertTrue(lights.get_state()["red"])
        finally:
            coordinator.stop()
            lights.close()
