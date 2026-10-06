"""Hardware-free reproductions of the defects recorded in docs/CODE_ISSUES.md.

Uses short-lived fake processes, local objects and a daemon thread. No robot,
serial, network, GUI or persistent-settings operations are performed.
"""
from pathlib import Path
import sys
import threading

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.bootstrap.startup_config import _read_optional_float
from src.engine.core.message_broker import MessageBroker
from src.engine.hardware.communication.i_register_transport import IRegisterTransport
from src.engine.process.base_process import BaseProcess
from src.engine.process.process_sequence import ProcessSequence
from src.engine.robot.services.motion_service import MotionService
from src.engine.robot.drivers.ros2_robot import Ros2Robot
from src.engine.robot.enums.axis import Direction, RobotAxis
from src.engine.system.system_manager import SystemManager
from src.engine.system.system_state import SystemTopics
from src.shared_contracts.events.process_events import ProcessState


def main() -> None:
    class ReadOnly(IRegisterTransport):
        def read_register(self, address):
            return 0

    try:
        ReadOnly().write_register(0, 1)
    except RecursionError:
        print("F01 reproduced: inherited write methods recurse")
    else:
        raise AssertionError("F01 no longer reproduces")

    broker = MessageBroker()
    broker.clear_all()
    manager = SystemManager(broker)
    first = BaseProcess("A", broker, manager)
    second = BaseProcess("B", broker, manager)
    first.start()
    first.start()
    assert first.state == ProcessState.RUNNING and manager.active_process_id is None
    second.start()
    assert second.state == first.state == ProcessState.RUNNING
    print("F02 reproduced: repeated start permits two RUNNING processes")

    broker.clear_all()
    manager = SystemManager(broker)
    callback_entered = threading.Event()

    class Subscriber:
        def on_state(self, event):
            callback_entered.set()
            manager.release("A")

    subscriber = Subscriber()
    broker.subscribe(SystemTopics.STATE, subscriber.on_state)
    thread = threading.Thread(target=manager.acquire, args=("A",), daemon=True)
    thread.start()
    assert callback_entered.wait(1.0)
    thread.join(0.1)
    assert thread.is_alive()
    print("F03 reproduced: state callback deadlocks on manager lock")

    broker.clear_all()
    first = BaseProcess("first", broker)
    second = BaseProcess("second", broker)

    def before_next(completed, next_process):
        sequence.stop()
        return True

    sequence = ProcessSequence([first, second], broker, before_next)
    sequence.start()
    first.stop()
    assert second.state == ProcessState.RUNNING
    print("F04 reproduced: stop during advancement still starts next process")

    value = _read_optional_float({"startup_delay_s": float("nan")}, "startup_delay_s", minimum=0.0)
    assert value != value
    print("F05 reproduced: NaN startup delay passes validation")

    class ShortPoseRobot:
        def get_current_position(self):
            return [0.0, 0.0, 0.0]

    motion = MotionService(ShortPoseRobot(), object())
    assert motion._wait_for_position([0, 0, 0, 90, 90, 90], delay=0, timeout=0.1)
    print("F06 reproduced: missing orientation is accepted for a six-axis target")

    class EmptyJogClient:
        def start_jog(self, *args):
            return None

    robot = Ros2Robot.__new__(Ros2Robot)
    robot._client = EmptyJogClient()
    assert robot.start_jog(RobotAxis.X, Direction.PLUS, 1.0, 10.0, 10.0) == 0
    print("F07 reproduced: missing jog return code is normalized to success")
    broker.clear_all()


if __name__ == "__main__":
    main()
