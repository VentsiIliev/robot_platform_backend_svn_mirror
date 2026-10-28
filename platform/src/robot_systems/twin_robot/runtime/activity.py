"""Transport-neutral execution state, independent of account/Qt implementations."""
from enum import Enum


class TwinRuntimeActivity(str, Enum):
    IDLE = "idle"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    UNKNOWN = "unknown"
