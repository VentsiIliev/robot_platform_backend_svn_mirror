"""
Playful animations for the PyQt6 Material Design AnimationManager.

Adds springy, bouncy motion on top of the existing manager:
overshoot pop-in/out, squish-and-jelly button feedback, hover grow,
shake (for errors), pulse, hop, and staggered list entrances.

Usage:
    from playful_animations import PlayfulAnimationManager, make_playful, stagger_in

    make_playful(button)                       # hover grow + squish + jelly release
    PlayfulAnimationManager(panel).pop_in()    # springy entrance
    PlayfulAnimationManager(field).shake()     # "nope!" wiggle
    stagger_in(icons)                          # icons slide up one after another

Note: geometry/pos animations fight with layouts. They work best on
floating or manually positioned widgets (like the floating folder icons).
"""

import math
import sys
from typing import Callable, Iterable, List, Optional

from PyQt6.QtCore import (
    QAnimationGroup, QEasingCurve, QEvent, QObject, QParallelAnimationGroup,
    QPoint, QPropertyAnimation, QRect, QSequentialAnimationGroup, QSize, Qt,
    QTimer,
)
from PyQt6.QtWidgets import (
    QApplication, QGraphicsOpacityEffect, QLabel, QPushButton, QWidget,
)

from pl_gui.shell.ui.material.animation import AnimationManager


# --------------------------------------------------------------------------
# Timing & easing
# --------------------------------------------------------------------------
class PlayfulTiming:
    PRESS = 90
    HOVER = 220
    POP = 380
    SLIDE = 380
    SHAKE = 420
    PULSE = 520
    HOP = 700
    STAGGER = 45


class PlayfulEasing:
    """Curves with personality. Overshoot > 1.7 (the Qt default) = bouncier."""

    @staticmethod
    def overshoot(amount: float = 2.2, kind=QEasingCurve.Type.OutBack) -> QEasingCurve:
        curve = QEasingCurve(kind)
        curve.setOvershoot(amount)
        return curve

    @staticmethod
    def elastic(amplitude: float = 1.0, period: float = 0.4) -> QEasingCurve:
        curve = QEasingCurve(QEasingCurve.Type.OutElastic)
        curve.setAmplitude(amplitude)
        curve.setPeriod(period)
        return curve

    BOUNCE = QEasingCurve.Type.OutBounce


# --------------------------------------------------------------------------
# Geometry helpers
# --------------------------------------------------------------------------
def scaled_rect(rect: QRect, sx: float, sy: Optional[float] = None) -> QRect:
    """Scale a rect around its own center (sy defaults to sx)."""
    sy = sx if sy is None else sy
    w = max(1, int(rect.width() * sx))
    h = max(1, int(rect.height() * sy))
    return QRect(
        rect.x() + (rect.width() - w) // 2,
        rect.y() + (rect.height() - h) // 2,
        w, h,
    )


# --------------------------------------------------------------------------
# Manager
# --------------------------------------------------------------------------
class PlayfulAnimationManager(AnimationManager):
    """AnimationManager + springy, character-filled motion."""

    # Geometry-based button motions that must never run at the same time.
    _MOTION_IDS = ("hover", "press", "rest", "jelly", "pulse")

    def __init__(self, target_widget: QWidget, parent: Optional[QObject] = None):
        super().__init__(target_widget, parent)
        # The "true" size/position to settle back to. Captured once, so we
        # never have to guess it (the base class assumes a 0.95 scale).
        self._rest_rect: Optional[QRect] = None
        self._opacity_effect: Optional[QGraphicsOpacityEffect] = None

    # ---- internals -------------------------------------------------------
    def _build(self, obj: QObject, prop: bytes, duration: int, curve) -> QPropertyAnimation:
        anim = QPropertyAnimation(self)
        anim.setTargetObject(obj)
        anim.setPropertyName(prop)
        anim.setDuration(duration)
        anim.setEasingCurve(QEasingCurve(curve))
        return anim

    def _opacity_anim(self, start: float, end: float, duration: int,
                      curve=QEasingCurve.Type.OutCubic) -> QPropertyAnimation:
        """Opacity that works for windows AND child widgets.

        windowOpacity only affects top-level windows, so child widgets get a
        QGraphicsOpacityEffect instead.
        """
        if self.target.isWindow():
            obj, prop = self.target, b"windowOpacity"
            self.target.setWindowOpacity(start)
        else:
            if self._opacity_effect is None:
                self._opacity_effect = QGraphicsOpacityEffect(self.target)
                self.target.setGraphicsEffect(self._opacity_effect)
            obj, prop = self._opacity_effect, b"opacity"
            self._opacity_effect.setOpacity(start)
        anim = self._build(obj, prop, duration, curve)
        anim.setStartValue(start)
        anim.setEndValue(end)
        return anim

    def _cancel(self, *ids: str) -> None:
        for anim_id in ids:
            for store in (self.animations, self.animation_groups):
                anim = store.pop(anim_id, None)
                if anim is not None:
                    anim.stop()
                    anim.deleteLater()
            self._active_animations.discard(anim_id)

    def _cancel_motion(self) -> None:
        self._cancel(*self._MOTION_IDS)

    def _run(self, anim, anim_id: str,
             callback: Optional[Callable] = None,
             on_finish: Optional[Callable] = None) -> None:
        self._cancel(anim_id)
        store = self.animation_groups if isinstance(anim, QAnimationGroup) else self.animations
        store[anim_id] = anim
        anim.finished.connect(lambda: self._on_animation_finished(anim_id))
        if on_finish:
            anim.finished.connect(on_finish)
        if callback:
            anim.finished.connect(callback)
        self._active_animations.add(anim_id)
        anim.start()

    def _rest(self) -> QRect:
        if self._rest_rect is None:
            self._rest_rect = QRect(self.target.geometry())
        return self._rest_rect

    def _clear_rest(self) -> None:
        self._rest_rect = None

    def refresh_rest_rect(self) -> None:
        """Call after you move/resize the widget yourself."""
        self._rest_rect = None

    # ---- entrances & exits ----------------------------------------------
    def pop_in(self, center_pos: Optional[QPoint] = None, from_scale: float = 0.6,
               duration: int = PlayfulTiming.POP, overshoot: float = 2.2,
               callback: Optional[Callable] = None) -> QParallelAnimationGroup:
        """Springy entrance: grows past its size, then settles."""
        self._cancel("pop_in", "pop_out")
        final = QRect(self.target.geometry())
        if center_pos is not None:
            final.moveCenter(center_pos)
        start = scaled_rect(final, from_scale)

        geo = self._build(self.target, b"geometry", duration,
                          PlayfulEasing.overshoot(overshoot))
        geo.setStartValue(start)
        geo.setEndValue(final)
        fade = self._opacity_anim(0.0, 1.0, int(duration * 0.5))

        group = QParallelAnimationGroup(self)
        group.addAnimation(geo)
        group.addAnimation(fade)

        self.target.setGeometry(start)
        self.target.show()
        self.target.raise_()
        self._run(group, "pop_in", callback)
        return group

    def pop_out(self, to_scale: float = 0.4, duration: int = 280,
                callback: Optional[Callable] = None) -> QParallelAnimationGroup:
        """Anticipation exit: pulls back slightly, then shrinks away."""
        self._cancel("pop_in", "pop_out")
        start = QRect(self.target.geometry())

        geo = self._build(self.target, b"geometry", duration,
                          PlayfulEasing.overshoot(2.0, QEasingCurve.Type.InBack))
        geo.setStartValue(start)
        geo.setEndValue(scaled_rect(start, to_scale))
        fade = self._opacity_anim(1.0, 0.0, duration, QEasingCurve.Type.InCubic)

        group = QParallelAnimationGroup(self)
        group.addAnimation(geo)
        group.addAnimation(fade)

        def restore():
            self.target.hide()
            self.target.setGeometry(start)  # ready for the next pop_in
            self._opacity_anim(1.0, 1.0, 0)  # reset opacity to fully visible

        self._run(group, "pop_out", callback, on_finish=restore)
        return group

    def slide_up_in(self, offset: int = 28, duration: int = PlayfulTiming.SLIDE,
                    callback: Optional[Callable] = None) -> QParallelAnimationGroup:
        """Rises into place with a little overshoot while fading in."""
        self._cancel("slide_up")
        end = self.target.pos()
        start = end + QPoint(0, offset)

        move = self._build(self.target, b"pos", duration, PlayfulEasing.overshoot(2.4))
        move.setStartValue(start)
        move.setEndValue(end)
        fade = self._opacity_anim(0.0, 1.0, int(duration * 0.6))

        group = QParallelAnimationGroup(self)
        group.addAnimation(move)
        group.addAnimation(fade)

        self.target.move(start)
        self.target.show()
        self.target.raise_()
        self._run(group, "slide_up", callback)
        return group

    # ---- button feedback -------------------------------------------------
    def hover_enter(self, scale: float = 1.08) -> None:
        self._cancel_motion()
        anim = self._build(self.target, b"geometry", PlayfulTiming.HOVER,
                           PlayfulEasing.overshoot(2.5))
        anim.setStartValue(self.target.geometry())
        anim.setEndValue(scaled_rect(self._rest(), scale))
        self._run(anim, "hover")

    def hover_leave(self) -> None:
        self.return_to_rest()

    def squish_press(self, scale: float = 0.9) -> None:
        self._cancel_motion()
        anim = self._build(self.target, b"geometry", PlayfulTiming.PRESS,
                           QEasingCurve.Type.OutQuad)
        anim.setStartValue(self.target.geometry())
        anim.setEndValue(scaled_rect(self._rest(), scale))
        self._run(anim, "press")

    def return_to_rest(self, duration: int = 260) -> None:
        if self._rest_rect is None:
            return
        self._cancel_motion()
        anim = self._build(self.target, b"geometry", duration,
                           PlayfulEasing.overshoot(2.0))
        anim.setStartValue(self.target.geometry())
        anim.setEndValue(self._rest_rect)
        self._run(anim, "rest", on_finish=self._clear_rest)

    def jelly(self) -> QSequentialAnimationGroup:
        """Wobbly squash-and-stretch that settles back to normal size."""
        self._cancel_motion()
        rest = self._rest()
        steps = [
            (scaled_rect(rest, 1.14, 0.88), 90, QEasingCurve.Type.OutQuad),
            (scaled_rect(rest, 0.94, 1.08), 110, QEasingCurve.Type.InOutQuad),
            (scaled_rect(rest, 1.04, 0.97), 110, QEasingCurve.Type.InOutQuad),
            (rest, 200, PlayfulEasing.elastic()),
        ]
        seq = QSequentialAnimationGroup(self)
        prev = QRect(self.target.geometry())
        for rect, dur, curve in steps:
            anim = self._build(self.target, b"geometry", dur, curve)
            anim.setStartValue(prev)
            anim.setEndValue(rect)
            seq.addAnimation(anim)
            prev = rect
        self._run(seq, "jelly", on_finish=self._clear_rest)
        return seq

    # ---- attention grabbers ---------------------------------------------
    def pulse(self, scale: float = 1.1, beats: int = 2,
              duration: int = PlayfulTiming.PULSE) -> QPropertyAnimation:
        """Heartbeat: grows and shrinks `beats` times."""
        self._cancel_motion()
        rest = self._rest()
        anim = self._build(self.target, b"geometry", duration,
                           QEasingCurve.Type.InOutSine)
        anim.setKeyValueAt(0.0, rest)
        anim.setKeyValueAt(0.5, scaled_rect(rest, scale))
        anim.setKeyValueAt(1.0, rest)
        anim.setLoopCount(beats)
        self._run(anim, "pulse", on_finish=self._clear_rest)
        return anim

    def shake(self, distance: int = 10, shakes: int = 4,
              duration: int = PlayfulTiming.SHAKE) -> QPropertyAnimation:
        """Horizontal 'nope' wiggle that fades out. Great for errors."""
        self._cancel("shake")
        home = self.target.pos()
        anim = self._build(self.target, b"pos", duration, QEasingCurve.Type.Linear)
        anim.setKeyValueAt(0.0, home)
        for i in range(shakes):
            t = (i + 1) / (shakes + 1)
            amp = distance * (1 - i / shakes)
            dx = amp if i % 2 == 0 else -amp
            anim.setKeyValueAt(t, QPoint(int(home.x() + dx), home.y()))
        anim.setKeyValueAt(1.0, home)
        self._run(anim, "shake")
        return anim

    def hop(self, height: int = 22, bounces: int = 2,
            duration: int = PlayfulTiming.HOP) -> QPropertyAnimation:
        """Bouncing-ball hops that lose energy each time."""
        self._cancel("hop")
        home = self.target.pos()
        anim = self._build(self.target, b"pos", duration, QEasingCurve.Type.Linear)
        samples = 32
        for i in range(samples + 1):
            t = i / samples
            lift = height * abs(math.sin(math.pi * bounces * t)) * (1 - t)
            anim.setKeyValueAt(t, QPoint(home.x(), int(home.y() - lift)))
        anim.setKeyValueAt(1.0, home)
        self._run(anim, "hop")
        return anim


# --------------------------------------------------------------------------
# Drop-in helpers
# --------------------------------------------------------------------------
class _PlayfulFilter(QObject):
    """Event filter that wires hover / press / release to the manager."""

    def __init__(self, widget: QWidget, manager: PlayfulAnimationManager):
        super().__init__(widget)
        self._widget = widget
        self._manager = manager

    def eventFilter(self, obj, event) -> bool:
        kind = event.type()
        if kind == QEvent.Type.Enter:
            self._manager.hover_enter()
        elif kind == QEvent.Type.Leave:
            self._manager.hover_leave()
        elif (kind == QEvent.Type.MouseButtonPress
              and event.button() == Qt.MouseButton.LeftButton):
            self._manager.squish_press()
        elif (kind == QEvent.Type.MouseButtonRelease
              and event.button() == Qt.MouseButton.LeftButton):
            if self._widget.rect().contains(event.position().toPoint()):
                self._manager.jelly()
            else:
                self._manager.return_to_rest()
        return False  # never swallow events


def make_playful(widget: QWidget) -> PlayfulAnimationManager:
    """One-liner: hover grow, squish on press, jelly on release."""
    manager = PlayfulAnimationManager(widget, parent=widget)
    widget.installEventFilter(_PlayfulFilter(widget, manager))
    return manager


def stagger_in(widgets: Iterable[QWidget], delay_ms: int = PlayfulTiming.STAGGER,
               offset: int = 28, duration: int = PlayfulTiming.SLIDE
               ) -> List[PlayfulAnimationManager]:
    """Widgets rise into place one after another (great for folder contents)."""
    managers = []
    for i, widget in enumerate(widgets):
        widget.hide()
        manager = PlayfulAnimationManager(widget, parent=widget)
        QTimer.singleShot(
            i * delay_ms,
            lambda m=manager: m.slide_up_in(offset=offset, duration=duration),
        )
        managers.append(manager)
    return managers


# --------------------------------------------------------------------------
# Demo
# --------------------------------------------------------------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)

    win = QWidget()
    win.resize(560, 340)
    win.setWindowTitle("Playful animations")
    win.setStyleSheet("""
        QWidget { background: #FFF8F0; }
        QPushButton { background: #6750A4; color: white; border: none;
                      border-radius: 18px; font-size: 14px; font-weight: 600; }
        QLabel { background: #FFD8E4; color: #31111D; border-radius: 40px;
                 font-size: 34px; }
    """)

    mascot = QLabel("◕‿◕", win)
    mascot.setAlignment(Qt.AlignmentFlag.AlignCenter)
    mascot.setGeometry(220, 70, 120, 120)
    mascot_anim = PlayfulAnimationManager(mascot, parent=mascot)

    actions = [
        ("Pop", mascot_anim.pop_in),
        ("Hop", mascot_anim.hop),
        ("Shake", mascot_anim.shake),
        ("Pulse", mascot_anim.pulse),
        ("Jelly", mascot_anim.jelly),
    ]
    buttons = []
    for i, (label, action) in enumerate(actions):
        btn = QPushButton(label, win)
        btn.setGeometry(30 + i * 104, 250, 92, 40)
        btn.clicked.connect(lambda _=False, a=action: a())
        make_playful(btn)
        buttons.append(btn)

    win.show()
    mascot_anim.pop_in()
    stagger_in(buttons)
    sys.exit(app.exec())