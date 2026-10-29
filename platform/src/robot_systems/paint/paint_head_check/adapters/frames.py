"""Image-side ports confined to adapters; domain policies do not import NumPy."""

from collections.abc import Callable
from typing import Protocol

import numpy as np
from numpy.typing import NDArray

from src.robot_systems.paint.contracts.paint_head_check.results import HeadObservationResult


class IHeadFrameEvaluator(Protocol):
    def reset(self) -> None: ...

    def evaluate(
        self,
        image: NDArray[np.uint8],
        *,
        frame_sequence: int,
        frame_captured_at: float,
        frame_received_at: float,
    ) -> HeadObservationResult: ...


class ICameraFrameSubscriptions(Protocol):
    def subscribe(self, topic: str, callback: Callable[[object], None]) -> None: ...

    def unsubscribe(self, topic: str, callback: Callable[[object], None]) -> None: ...
