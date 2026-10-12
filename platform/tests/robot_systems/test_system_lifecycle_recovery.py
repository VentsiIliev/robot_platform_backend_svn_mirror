"""Fault injection for construction rollback and resource ownership at shutdown."""
import unittest
from unittest.mock import MagicMock

from src.robot_systems.base_robot_system import BaseRobotSystem, ShutdownPendingError
from src.robot_systems.system_builder import SystemBuilder
from src.robot_systems.paint.paint_robot_system import PaintRobotSystem
from src.shared_contracts.declarations import ServiceSpec


class Resource:
    def __init__(self, name, events):
        self.name, self.events = name, events

    def close(self):
        self.events.append(self.name)


class MinimalSystem(BaseRobotSystem):
    def on_start(self):
        pass

    def on_stop(self):
        pass


class SystemLifecycleRecoveryTests(unittest.TestCase):
    def test_failed_builder_unwinds_completed_services_in_reverse_order(self):
        events = []
        first, second = Resource('first', events), Resource('second', events)
        def fail(ctx):
            raise ValueError('invalid third device')
        class System(MinimalSystem):
            services = [
                ServiceSpec('first', Resource, builder=lambda ctx: first),
                ServiceSpec('second', Resource, builder=lambda ctx: second),
                ServiceSpec('broken', Resource, builder=fail),
            ]
        with self.assertRaisesRegex(ValueError, 'invalid third device'):
            SystemBuilder().with_robot(MagicMock()).with_messaging_service(MagicMock()).build(System)
        self.assertEqual(events, ['second', 'first'])

    def test_start_failure_unwinds_runtime_and_unregistered_built_services(self):
        events = []
        first, second = Resource('first', events), Resource('second', events)
        class System(MinimalSystem):
            services = [ServiceSpec('first', Resource), ServiceSpec('second', Resource)]
            def on_start(self):
                self.register_managed_resource(first)
                self.register_managed_resource(Resource('runtime', events))
                raise ValueError('late startup failure')
            def on_stop(self):
                events.append('halt')
        system = System()
        with self.assertRaisesRegex(ValueError, 'late startup failure'):
            system.start({'first': first, 'second': second})
        self.assertEqual(events, ['halt', 'runtime', 'first', 'second'])
        self.assertFalse(system.is_running)
        system.stop()
        self.assertEqual(len(events), 4)

    def test_rollback_error_does_not_replace_original_start_error(self):
        events = []
        class System(MinimalSystem):
            def on_start(self):
                self.register_managed_resource(Resource('closed', events))
                raise ValueError('original')
            def on_stop(self):
                raise RuntimeError('stop also failed')
        system = System()
        with self.assertRaisesRegex(ValueError, 'original'):
            system.start({})
        self.assertEqual(events, ['closed'])
        self.assertFalse(system.is_running)

    def test_shutdown_deadline_preserves_resources_for_later_attempt(self):
        events = []
        class System(MinimalSystem):
            pending = True
            def on_start(self):
                self.register_managed_resource(Resource('closed', events))
            def on_stop(self):
                if self.pending:
                    raise ShutdownPendingError('worker still active')
        system = System()
        system.start({})
        with self.assertRaises(ShutdownPendingError):
            system.stop()
        self.assertEqual(events, [])
        self.assertTrue(system.is_running)
        system.pending = False
        system.stop()
        self.assertEqual(events, ['closed'])
        self.assertFalse(system.is_running)

    def test_paint_waits_for_process_before_disabling_and_closing_hardware(self):
        system = PaintRobotSystem()
        system._running = True
        events = []
        process = MagicMock()
        process.shutdown.side_effect = lambda: events.append('workers finished')
        robot = MagicMock(spec=["stop_motion", "disable_robot", "stop"])
        robot.stop_motion.side_effect = lambda: events.append('halt')
        robot.disable_robot.side_effect = lambda: events.append('disable')
        robot.side_effect = lambda: events.append('close')
        system._robot, system._main_process = robot, process
        system.register_managed_resource(robot)
        system.register_managed_resource(process)
        system.stop()
        self.assertEqual(events, ['workers finished', 'halt', 'disable', 'close'])
        process.stop.assert_not_called()

    def test_paint_attempts_disable_even_when_halt_raises(self):
        system = PaintRobotSystem()
        system._robot = MagicMock()
        system._robot.stop_motion.side_effect = OSError('halt unavailable')
        with self.assertRaisesRegex(OSError, 'halt unavailable'):
            system.on_stop()
        system._robot.disable_robot.assert_called_once()


    def test_startup_rollback_honors_delegated_resource_cleanup(self):
        events = []
        device = Resource('direct close', events)
        class System(MinimalSystem):
            services = [ServiceSpec('device', Resource)]
            def on_start(self):
                self.register_managed_resource(device, cleanup=lambda: events.append('owner close'))
                raise ValueError('late failure')
        with self.assertRaises(ValueError):
            System().start({'device': device})
        self.assertEqual(events, ['owner close'])

    def test_unregister_removes_custom_cleanup(self):
        events = []
        device = Resource('device', events)
        system = MinimalSystem()
        system.start({})
        system.register_managed_resource(device, cleanup=lambda: events.append('cleanup'))
        system.unregister_managed_resource(device)
        system.stop()
        self.assertEqual(events, [])
