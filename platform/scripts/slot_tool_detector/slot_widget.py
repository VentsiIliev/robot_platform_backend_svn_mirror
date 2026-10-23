"""PyQt6 widget: live slot-occupancy view with per-slot ROI editing.

Features
  * Drag polygon vertices of each slot ROI directly on the image
  * "Set empty reference" for the selected slot (or all)
  * "Save frame as empty / occupied" -> builds the dataset for calibrate_slots.py
  * Live state overlay (EMPTY / OCCUPIED / UNKNOWN) + score

Embed:
    w = SlotDetectorWidget(config_path="slots.json")
    w.set_frame(bgr_frame)          # push frames from your camera pipeline / ROS2 callback
    w.stateChanged.connect(lambda results: ...)

Standalone:
    python slot_widget.py --config slots.json --camera 0
    python slot_widget.py --config slots.json --image frame.png
"""
from __future__ import annotations

import argparse
import shlex
import sys
import time
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from PyQt6.QtCore import QPointF, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QImage, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QHBoxLayout, QLabel, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from slot_detector import (
    DetectorConfig, SlotConfig, SlotDetector, SlotResult, SlotState, STATE_COLORS,
)

HANDLE_R = 7


def bgr_to_qimage(frame: np.ndarray) -> QImage:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = rgb.shape
    return QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()


class FrameView(QWidget):
    """Draws the frame, polygons, state labels; handles vertex dragging."""
    polygonEdited = pyqtSignal(int)          # slot index

    def __init__(self, cfg: DetectorConfig):
        super().__init__()
        self.cfg = cfg
        self.pix: Optional[QPixmap] = None
        self.results: List[SlotResult] = []
        self.selected = 0
        self._drag: Optional[tuple] = None   # (slot_idx, vertex_idx)
        self.setMinimumSize(480, 320)
        self.setMouseTracking(True)

    # image <-> widget coordinate mapping (aspect-preserving)
    def _scale(self):
        if not self.pix:
            return 1.0, 0.0, 0.0
        s = min(self.width() / self.pix.width(), self.height() / self.pix.height())
        ox = (self.width() - self.pix.width() * s) / 2
        oy = (self.height() - self.pix.height() * s) / 2
        return s, ox, oy

    def to_widget(self, p):
        s, ox, oy = self._scale()
        return QPointF(p[0] * s + ox, p[1] * s + oy)

    def to_image(self, pos):
        s, ox, oy = self._scale()
        return ((pos.x() - ox) / s, (pos.y() - oy) / s)

    def set_frame(self, frame: np.ndarray, results: List[SlotResult]):
        self.pix = QPixmap.fromImage(bgr_to_qimage(frame))
        self.results = results
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        if self.pix:
            s, ox, oy = self._scale()
            p.drawPixmap(int(ox), int(oy), int(self.pix.width() * s), int(self.pix.height() * s), self.pix)
        by_name = {r.name: r for r in self.results}
        for i, slot in enumerate(self.cfg.slots):
            r = by_name.get(slot.name)
            b, g, rr = STATE_COLORS[r.state] if r else (200, 200, 200)
            col = QColor(rr, g, b)
            pen = QPen(col, 3 if i == self.selected else 2)
            p.setPen(pen)
            if slot.inspection_polygon is not None:
                outline = [self.to_widget(v) for v in slot.polygon]
                p.setPen(QPen(col, 1, Qt.PenStyle.DashLine))
                for a, c in zip(outline, outline[1:] + outline[:1]):
                    p.drawLine(a, c)
                p.setPen(pen)
            polygon = slot.inspection_polygon if slot.inspection_polygon is not None else slot.polygon
            pts = [self.to_widget(v) for v in polygon]
            for a, c in zip(pts, pts[1:] + pts[:1]):
                p.drawLine(a, c)
            if i == self.selected:
                p.setBrush(col)
                for v in pts:
                    p.drawEllipse(v, HANDLE_R, HANDLE_R)
                p.setBrush(Qt.BrushStyle.NoBrush)
            if r and pts:
                p.drawText(int(pts[0].x()), int(pts[0].y()) - 8,
                           f"{slot.name}: {r.state.value} ({r.score:.2f})")

    def mousePressEvent(self, e):
        if not self.cfg.slots:
            return
        slot = self.cfg.slots[self.selected]
        polygon = slot.inspection_polygon if slot.inspection_polygon is not None else slot.polygon
        for vi, v in enumerate(polygon):
            w = self.to_widget(v)
            if (w - e.position()).manhattanLength() <= HANDLE_R * 2:
                self._drag = (self.selected, vi)
                return

    def mouseMoveEvent(self, e):
        if self._drag is None or not self.pix:
            return
        si, vi = self._drag
        x, y = self.to_image(e.position())
        x = float(np.clip(x, 0, self.pix.width() - 1))
        y = float(np.clip(y, 0, self.pix.height() - 1))
        slot = self.cfg.slots[si]
        polygon = slot.inspection_polygon if slot.inspection_polygon is not None else slot.polygon
        polygon[vi] = (x, y)
        self.polygonEdited.emit(si)
        self.update()

    def mouseReleaseEvent(self, _):
        self._drag = None


class SlotDetectorWidget(QWidget):
    stateChanged = pyqtSignal(list)          # list[SlotResult]

    def __init__(self, config_path: str, data_dir: str = "data", parent=None):
        super().__init__(parent)
        self.config_path = Path(config_path)
        self.setWindowTitle(self.config_path.name)
        self.data_dir = Path(data_dir)
        self.cfg = DetectorConfig.load(self.config_path)
        self.det = SlotDetector(self.cfg)
        self.frame: Optional[np.ndarray] = None
        self._last_states = {}
        self._needs_retrain = False
        self._saved_for_retrain = False

        self.view = FrameView(self.cfg)
        self.view.polygonEdited.connect(self._on_polygon_edited)

        self.combo = QComboBox()
        self.combo.addItems([s.name for s in self.cfg.slots])
        self.combo.currentIndexChanged.connect(self._select)

        btn_ref = QPushButton("Set empty reference (selected)")
        btn_ref_all = QPushButton("Set empty reference (all)")
        btn_e = QPushButton("Save frame -> empty")
        btn_o = QPushButton("Save frame -> occupied")
        btn_save = QPushButton("Save config")
        btn_ref.clicked.connect(lambda: self._set_ref(False))
        btn_ref_all.clicked.connect(lambda: self._set_ref(True))
        btn_e.clicked.connect(lambda: self._save_frame("empty"))
        btn_o.clicked.connect(lambda: self._save_frame("occupied"))
        btn_save.clicked.connect(self._save_config)

        self.status = QLabel("No reference set - diff feature inactive until you set one.")
        row = QHBoxLayout()
        for w in (QLabel("Slot:"), self.combo, btn_ref, btn_ref_all, btn_e, btn_o, btn_save):
            row.addWidget(w)
        lay = QVBoxLayout(self)
        lay.addWidget(self.view, 1)
        lay.addLayout(row)
        lay.addWidget(self.status)

    # ---- public ---------------------------------------------------------
    def set_frame(self, frame: np.ndarray):
        self.frame = frame
        if self._needs_retrain:
            results = [SlotResult(s.name, 0.5, SlotState.UNKNOWN, SlotState.UNKNOWN,
                                  np.empty(0, np.float32)) for s in self.cfg.slots]
        else:
            results = self.det.update(frame)
        self.view.set_frame(frame, results)
        states = {r.name: r.state for r in results}
        if states != self._last_states:
            self._last_states = states
            self.stateChanged.emit(results)
        if self._needs_retrain:
            message = ("Config saved. Retrain the model, then restart the viewer." if self._saved_for_retrain
                       else "Inspection region changed. Save config and retrain before detection.")
            self.status.setText(message)
        else:
            self.status.setText("  |  ".join(f"{r.name}: {r.state.value} ({r.score:.2f})" for r in results))

    # ---- internals ------------------------------------------------------
    def _select(self, i):
        self.view.selected = max(0, i)
        self.view.update()

    def _on_polygon_edited(self, _index):
        self.det.invalidate_masks()
        self._needs_retrain = True
        self._saved_for_retrain = False
        if self.frame is not None:
            self.set_frame(self.frame)

    def _save_config(self):
        self.cfg.save(self.config_path)
        if self._needs_retrain:
            self._saved_for_retrain = True
            self.status.setText("Config saved. Retrain the model, then restart the viewer.")

    def _set_ref(self, all_slots: bool):
        if self.frame is None or self._needs_retrain:
            return
        names = None if all_slots else [self.cfg.slots[self.view.selected].name]
        self.det.set_reference(self.frame, names)
        self.det.reset_history()

    def _save_frame(self, label: str):
        if self.frame is None:
            return
        slot = self.cfg.slots[self.view.selected].name
        d = self.data_dir / slot / label
        d.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(d / f"{int(time.time() * 1000)}.png"), self.frame)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--data", default="data")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--camera", type=int)
    g.add_argument("--image", type=str)
    a = ap.parse_args()

    app = QApplication(sys.argv)
    try:
        w = SlotDetectorWidget(a.config, a.data)
    except (ValueError, OSError, cv2.error) as error:
        command = shlex.join([sys.executable, "calibrate_slots.py", "--config", a.config,
                              "--data", a.data, "--out", a.config, "--model", "forest", "--refit-all"])
        QMessageBox.critical(None, "Detector needs calibration",
                             f"{error}\n\nRetrain for the saved inspection regions, then reopen:\n\n{command}")
        return
    w.resize(1000, 650)
    w.show()

    if a.image:
        img = cv2.imread(a.image)
        timer = QTimer()
        timer.timeout.connect(lambda: w.set_frame(img))
    else:
        cap = cv2.VideoCapture(a.camera)
        timer = QTimer()
        def tick():
            ok, f = cap.read()
            if ok:
                w.set_frame(f)
        timer.timeout.connect(tick)
    timer.start(50)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
