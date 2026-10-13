from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from PyQt6.QtWidgets import QWidget


@dataclass(frozen=True)
class OnboardingStep:
    """One translated-on-display step in an application onboarding tour."""

    target: Callable[[], QWidget | None]
    title: str
    body: str
    hint: str = ""
    spotlight: bool = True
