import unittest
from dataclasses import replace
from threading import Event, get_ident
from unittest.mock import MagicMock
from time import monotonic

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


class CoordinatorRecoveryTests(unittest.TestCase):
    def test_transient_write_retries_without_new_process_event_and_dismisses_fault(self):
        config = OperatorLightsConfig(enabled=True)
        lights = MagicMock()
        lights.get_channel.side_effect = lambda name: name
        retried = Event()
        notifications = []
        def write(channels):
            if lights.set_active.call_count == 1:
                raise OSError("bus disconnected")
            self.assertEqual(channels, ("green",))
        lights.set_active.side_effect = write
        messaging = MagicMock()
        def publish(topic, event):
            notifications.append((topic, event))
            if topic.endswith("dismiss"):
                retried.set()
        messaging.publish.side_effect = publish
        coordinator = OperatorLightCoordinator(lights, config, messaging, "paint",
            lambda: ProcessState.RUNNING, retry_interval=0.01)
        coordinator.start()
        try:
            self.assertTrue(retried.wait(2))
            self.assertTrue(coordinator.is_healthy())
            self.assertIsNone(coordinator.last_error)
            self.assertEqual(lights.set_active.call_count, 2)
            self.assertEqual(len(notifications), 2)
        finally:
            coordinator.stop()
        lights.close.assert_called_once()

    def test_new_state_supersedes_retry_and_shutdown_keeps_transport_owned_by_writer(self):
        entered, release, closed = Event(), Event(), Event()
        lights = MagicMock()
        lights.get_channel.side_effect = lambda name: name
        def write(channels):
            entered.set()
            self.assertTrue(release.wait(2))
            raise OSError("blocked bus failed")
        lights.set_active.side_effect = write
        lights.close.side_effect = closed.set
        coordinator = OperatorLightCoordinator(lights, OperatorLightsConfig(enabled=True),
            MagicMock(), "paint", lambda: ProcessState.RUNNING, shutdown_timeout=0.01)
        coordinator.start()
        self.assertTrue(entered.wait(2))
        started = monotonic()
        try:
            with self.assertRaises(TimeoutError):
                coordinator.stop()
            self.assertLess(monotonic() - started, 0.5)
            lights.close.assert_not_called()
        finally:
            release.set()
            self.assertTrue(closed.wait(2))
            coordinator.stop()
        self.assertEqual(lights.set_active.call_count, 1)
        lights.close.assert_called_once()

    def test_latest_state_interrupts_retry_backoff(self):
        failed, recovered = Event(), Event()
        messaging, lights = MagicMock(), MagicMock()
        lights.get_channel.side_effect = lambda name: name
        def write(channels):
            if channels == ("green",):
                raise OSError("transient")
            self.assertEqual(channels, ("red",))
            recovered.set()
        lights.set_active.side_effect = write
        messaging.publish.side_effect = lambda *args: failed.set()
        coordinator = OperatorLightCoordinator(lights, OperatorLightsConfig(enabled=True),
            messaging, "paint", lambda: ProcessState.RUNNING, retry_interval=5)
        coordinator.start()
        try:
            self.assertTrue(failed.wait(2))
            callback = messaging.subscribe.call_args.args[1]
            callback(ProcessStateEvent("paint", ProcessState.ERROR, ProcessState.RUNNING))
            self.assertTrue(recovered.wait(1))
        finally:
            coordinator.stop()
