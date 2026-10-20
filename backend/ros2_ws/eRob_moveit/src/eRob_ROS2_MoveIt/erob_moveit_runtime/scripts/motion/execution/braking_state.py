"""Immutable measured braking state and joint-state acceleration estimation."""
from dataclasses import dataclass
import math
import time


@dataclass(frozen=True)
class BrakingState:
    names: tuple
    position: tuple
    velocity: tuple
    acceleration: tuple
    received_at: float
    stamp_s: float


class BrakingStateTracker:
    """Called under RobotStateStore's lock; no ROS calls in the sampling path."""
    def __init__(self):
        self.previous = None
        self.state = None

    def observe(self, message, now=None):
        now = time.monotonic() if now is None else now
        names = tuple(getattr(message, 'name', ()) or ())
        position = tuple(getattr(message, 'position', ()) or ())
        velocity = tuple(getattr(message, 'velocity', ()) or ())
        stamp = getattr(getattr(message, 'header', None), 'stamp', None)
        stamp_s = float(stamp.sec) + float(stamp.nanosec)*1e-9 if stamp is not None else 0.0
        previous = self.previous
        self.state = None
        if (len(names) != 6 or len(set(names)) != 6 or len(position) != 6 or len(velocity) != 6
                or not all(math.isfinite(x) for x in position + velocity)):
            self.previous = None
            return
        self.previous = (names, position, velocity, now, stamp_s, (0.0,)*6)
        if previous is None or previous[0] != names:
            return
        dt = stamp_s - previous[4] if stamp_s > 0 and previous[4] > 0 else now - previous[3]
        if not 0.0001 <= dt <= 0.1:
            return
        alpha = 1.0 - math.exp(-2.0 * math.pi * 10.0 * dt)
        acceleration = tuple(old + alpha*((v-prev)/dt-old)
                             for v, prev, old in zip(velocity, previous[2], previous[5]))
        self.previous = (names, position, velocity, now, stamp_s, acceleration)
        self.state = BrakingState(names, position, velocity, acceleration, now, stamp_s)
