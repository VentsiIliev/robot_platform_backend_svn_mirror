"""Reusable animated progress indicators for application views."""

from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PyQt6.QtWidgets import QWidget

from pl_gui.settings.settings_view.styles import (
    BORDER,
    PRIMARY,
    PRIMARY_DARK,
    PRIMARY_HOVER,
    SECONDARY_BG,
    TEXT_COLOR,
    TEXT_ON_PRIMARY,
)


def _color(value: str, alpha: float = 1.0) -> QColor:
    result = QColor(value)
    result.setAlpha(max(0, min(255, round(alpha * 255))))
    return result


@dataclass
class _Particle:
    x: float
    y: float
    vx: float
    vy: float
    radius: float
    growth: float
    age: float
    lifetime: float
    alpha: float
    shade: int


class FluidProgress(QWidget):
    """Base for determinate and indeterminate fluid progress indicators."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress = 0.0
        self.speed = 0.0
        self.waiting = False
        self.running = False
        self.particles: list[_Particle] = []
        self.phase = 0.0
        self._last_tick = time.monotonic()
        self._emission = 0.0
        self.setMinimumWidth(240)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    def set_progress(self, percent: float, speed_mb_s: float = 0.0) -> None:
        self.progress = max(0.0, min(100.0, float(percent)))
        self.speed = max(0.0, float(speed_mb_s))
        self.update()

    def set_waiting(self, waiting: bool) -> None:
        self.waiting = bool(waiting)
        self.update()

    def set_running(self, running: bool) -> None:
        self.running = bool(running)
        self.update()

    def reset(self) -> None:
        self.progress = 0.0
        self.speed = 0.0
        self.waiting = False
        self.running = False
        self.particles.clear()
        self.update()

    def _tick(self) -> None:
        now = time.monotonic()
        elapsed = min(0.05, now - self._last_tick)
        self._last_tick = now
        self.phase += elapsed
        for particle in self.particles:
            particle.age += elapsed
            particle.x += (
                particle.vx
                + math.sin(particle.y * 0.05 + self.phase * 1.4 + particle.shade * 2) * 14
            ) * elapsed
            particle.y += (
                particle.vy
                + math.cos(particle.x * 0.04 + self.phase * 1.1 + particle.shade) * 8
            ) * elapsed
            particle.radius += particle.growth * elapsed
        self.particles = [particle for particle in self.particles if particle.age < particle.lifetime]
        if self.running and self.progress < 100:
            self._emission += elapsed * 32 * (0.9 if self.waiting else 0.35 + self.speed / 8)
            while self._emission >= 1:
                self._emission -= 1
                self._emit_particle()
        self.update()

    def _add_particle(self, x, y, vx, vy, radius, growth, lifetime, alpha) -> None:
        self.particles.append(
            _Particle(
                x, y, vx, vy, radius, growth, 0, lifetime, alpha, random.randrange(3)
            )
        )
        if len(self.particles) > 260:
            self.particles.pop(0)

    def _paint_particles(self, painter: QPainter) -> None:
        shades = (PRIMARY_HOVER, PRIMARY_DARK, PRIMARY)
        for particle in self.particles:
            opacity = particle.alpha * (1 - particle.age / particle.lifetime) * min(1, particle.age * 4)
            gradient = QRadialGradient(QPointF(particle.x, particle.y), max(1, particle.radius))
            gradient.setColorAt(0, _color(shades[particle.shade], opacity))
            gradient.setColorAt(1, _color(shades[particle.shade], 0))
            painter.setBrush(gradient)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(particle.x, particle.y), particle.radius, particle.radius)

    def _blobs(self, painter, x0, x1, y0, y1, count, radius, alpha) -> None:
        for index in range(count):
            position = (index / count + self.phase * 0.025 * (1 if index % 2 else -1) + 10) % 1
            x = x0 + (x1 - x0) * position
            y = y0 + (y1 - y0) * (0.5 + math.sin(self.phase * 0.8 + index * 2.1) * 0.32)
            gradient = QRadialGradient(QPointF(x, y), radius)
            gradient.setColorAt(0, _color(PRIMARY_HOVER if index % 2 else PRIMARY, alpha))
            gradient.setColorAt(1, _color(PRIMARY, 0))
            painter.fillRect(QRectF(x - radius, y - radius, radius * 2, radius * 2), gradient)

    def _range(self) -> tuple[float, float]:
        if self.waiting and self.running:
            head = (self.phase * 0.4) % 1.35
            return max(0, head - 0.35), head
        return 0.0, self.progress / 100

    def _emit_particle(self) -> None:
        pass


class InkBar(FluidProgress):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(84)

    def _emit_particle(self) -> None:
        _, high = self._range()
        if high >= 1:
            return
        self._add_particle(
            high * self.width() + random.uniform(-2, 2),
            random.uniform(17, 67),
            random.uniform(18, 60),
            random.uniform(-14, 14),
            random.uniform(10, 22),
            9,
            random.uniform(1.2, 2.4),
            0.38,
        )

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, height = self.width(), self.height()
        bounds = QRectF(0.5, 0.5, width - 1, height - 1)
        clip = QPainterPath()
        clip.addRoundedRect(bounds, height / 2, height / 2)
        painter.fillPath(clip, _color(SECONDARY_BG))
        painter.save()
        painter.setClipPath(clip)
        low, high = self._range()
        x0, x1 = low * width, high * width
        if x1 > 0 and x0 < width:
            def wave(y, factor):
                return math.sin(y * 0.16 + self.phase * 3 * factor) * 5 + math.sin(
                    y * 0.07 - self.phase * 1.9 * factor
                ) * 3

            path = QPainterPath()
            path.moveTo(-30 if x0 <= 0 else x0 + wave(0, 1), 0)
            for y in range(4, height + 1, 4):
                path.lineTo(-30 if x0 <= 0 else x0 + wave(y, 1), y)
            for y in range(height, -1, -4):
                path.lineTo(width + 30 if x1 >= width else x1 + wave(y, 2), y)
            path.closeSubpath()
            gradient = QLinearGradient(max(0, x0), 0, min(width, x1) + 1, 0)
            gradient.setColorAt(0, _color(PRIMARY_DARK))
            gradient.setColorAt(0.7, _color(PRIMARY))
            gradient.setColorAt(1, _color(PRIMARY_HOVER))
            painter.fillPath(path, gradient)
            painter.save()
            painter.setClipPath(path)
            self._blobs(painter, max(0, x0), min(width, x1), 0, height, 6, height * 0.95, 0.35)
            painter.restore()
        self._paint_particles(painter)
        painter.restore()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(_color(BORDER), 1))
        painter.drawPath(clip)


class Vessel(FluidProgress):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(300)

    def _level(self) -> float:
        if self.waiting and self.running:
            return 0.5 + 0.1 * math.sin(self.phase * 1.2)
        return self.progress / 100

    def _emit_particle(self) -> None:
        level = self._level()
        if not 0 < level < 1:
            return
        self._add_particle(
            self.width() / 2 + random.uniform(-90, 90),
            self.height() / 2 + 112 - level * 224,
            random.uniform(-8, 8),
            random.uniform(-46, -22),
            random.uniform(8, 15),
            7,
            random.uniform(1.4, 2.6),
            0.4,
        )

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center_x, center_y, radius = self.width() / 2, self.height() / 2, 112
        bottom = center_y + radius
        level = self._level()
        top = bottom - level * 2 * radius
        circle = QPainterPath()
        circle.addEllipse(QPointF(center_x, center_y), radius, radius)
        painter.save()
        painter.setClipPath(circle)
        painter.fillPath(circle, _color(SECONDARY_BG))

        def surface(factor, phase, amplitude):
            path = QPainterPath()
            path.moveTo(center_x - radius, bottom + 2)
            for index in range(57):
                x = center_x - radius + index * 4
                y = top + math.sin(x * 0.045 + self.phase * 2 * factor + phase) * amplitude
                y += math.sin(x * 0.1 - self.phase * 1.4 * factor) * amplitude * 0.4
                path.lineTo(x, y)
            path.lineTo(center_x + radius, bottom + 2)
            path.closeSubpath()
            return path

        liquid = None
        if level > 0:
            amplitude = 0 if level >= 1 else 7
            painter.fillPath(surface(1.3, 1.7, amplitude * 0.9), _color(PRIMARY_HOVER, 0.55))
            liquid = surface(1, 0, amplitude)
            gradient = QLinearGradient(0, top, 0, bottom)
            gradient.setColorAt(0, _color(PRIMARY))
            gradient.setColorAt(1, _color(PRIMARY_DARK))
            painter.fillPath(liquid, gradient)
            painter.save()
            painter.setClipPath(liquid)
            self._blobs(painter, center_x - radius, center_x + radius, top, bottom, 5, radius * 0.8, 0.3)
            painter.restore()
        self._paint_particles(painter)
        label = "…" if self.waiting and self.running else f"{int(self.progress)}%"
        painter.setFont(QFont("Ubuntu", 34, QFont.Weight.Bold))
        label_bounds = QRectF(center_x - radius, center_y - 38, radius * 2, 76)
        painter.setPen(_color(TEXT_COLOR))
        painter.drawText(label_bounds, Qt.AlignmentFlag.AlignCenter, label)
        if liquid is not None:
            painter.save()
            painter.setClipPath(liquid)
            painter.setPen(_color(TEXT_ON_PRIMARY))
            painter.drawText(label_bounds, Qt.AlignmentFlag.AlignCenter, label)
            painter.restore()
        painter.restore()
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(_color(BORDER), 2))
        painter.drawPath(circle)


class PlumeLine(FluidProgress):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(96)

    def _emit_particle(self) -> None:
        _, high = self._range()
        if high >= 1:
            return
        width = self.width()
        self._add_particle(
            max(4, min(width - 4, high * width)) + random.uniform(-1, 1),
            self.height() / 2 + random.uniform(-2, 2),
            random.uniform(-46, -8),
            random.uniform(-26, 26),
            random.uniform(6, 14),
            14,
            random.uniform(1.4, 2.8),
            0.32,
        )

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        width, y = self.width(), self.height() / 2
        low, high = self._range()
        x0, x1 = low * width, max(0, min(width, high * width))
        self._paint_particles(painter)
        track = QPainterPath()
        track.addRoundedRect(QRectF(0, y - 4, width, 8), 4, 4)
        painter.fillPath(track, _color(SECONDARY_BG))
        if x1 > x0:
            gradient = QLinearGradient(x0, 0, x1 + 1, 0)
            gradient.setColorAt(0, _color(PRIMARY_DARK))
            gradient.setColorAt(0.75, _color(PRIMARY))
            gradient.setColorAt(1, _color(PRIMARY_HOVER))
            painter.save()
            painter.setClipPath(track)
            painter.fillRect(QRectF(x0, y - 4, x1 - x0, 8), gradient)
            painter.restore()
        if 0 < high <= 1 and self.running:
            head = max(4, min(width - 4, x1))
            glow = QRadialGradient(QPointF(head, y), 26)
            glow.setColorAt(0, _color(PRIMARY_HOVER, 0.55))
            glow.setColorAt(1, _color(PRIMARY_HOVER, 0))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(glow)
            painter.drawEllipse(QPointF(head, y), 26, 26)
            painter.setBrush(_color(TEXT_ON_PRIMARY))
            painter.drawEllipse(QPointF(head, y), 4.5, 4.5)


_STYLES = {
    "ink": InkBar,
    "plume": PlumeLine,
    "vessel": Vessel,
}


def create_fluid_progress(style: str = "plume", parent=None) -> FluidProgress:
    """Create a progress widget; callers can switch style without changing wiring."""
    try:
        widget_class = _STYLES[style]
    except KeyError as exc:
        raise ValueError(f"Unknown fluid progress style: {style}") from exc
    return widget_class(parent)
