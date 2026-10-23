"""Simple PyQt6 app: camera feed + draw slot polygons + capture training images.

Run:
    python slot_capture_app.py                       # camera 0, slots.json, data/
    python slot_capture_app.py --camera 1 --config slots.json --data data
    python slot_capture_app.py --image frame.png     # no camera, still image

How to use
  1. Click "New slot", then click the corners of the slot interior on the video.
     Close the polygon by double-clicking, pressing Enter, or clicking the first point.
     Right-click / Backspace removes the last point, Esc cancels.
  2. Click a polygon (or pick it in the list) to select it; drag its corner handles to adjust.
  3. Put the slot in a known state and press "Capture EMPTY" (E) or "Capture OCCUPIED" (O).
     Tick "Apply to all slots" when every slot is in the same state in the frame.
     Vary lighting / part orientation between captures.
  4. Slots are autosaved to the config file; frames go to
        data/<slot_name>/empty/*.png   data/<slot_name>/occupied/*.png
     which is exactly what calibrate_slots.py reads.

Keep the camera resolution the same later in the detector, because the polygons are
stored in pixel coordinates of the frame.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

import cv2
import numpy as np
from PyQt6.QtCore import QPointF, QTimer, Qt, pyqtSignal
from PyQt6.QtGui import (
    QColor, QImage, QKeySequence, QPainter, QPen, QPixmap, QPolygonF, QShortcut,
)
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QHBoxLayout, QInputDialog, QLabel, QListWidget,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from slot_detector import DetectorConfig, SlotConfig

HANDLE_R = 7
CLOSE_DIST = 12
PALETTE = [(230, 120, 40), (60, 180, 75), (70, 130, 230), (200, 70, 200),
           (220, 190, 40), (60, 200, 200)]


def bgr_to_qimage(frame: np.ndarray) -> QImage:
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = rgb.shape
    return QImage(rgb.data, w, h, 3 * w, QImage.Format.Format_RGB888).copy()


# --------------------------------------------------------------------------- #
class Canvas(QWidget):
    """Video view with polygon drawing and vertex editing."""
    polygonFinished = pyqtSignal(list)       # list[(x, y)] in image pixels
    selectionChanged = pyqtSignal(int)
    geometryChanged = pyqtSignal()           # after a vertex drag ends

    def __init__(self, cfg: DetectorConfig):
        super().__init__()
        self.cfg = cfg
        self.pix: Optional[QPixmap] = None
        self.selected = -1
        self.drawing = False
        self.current: List[tuple] = []
        self._cursor: Optional[QPointF] = None
        self._drag: Optional[tuple] = None
        self.setMinimumSize(1280, 720)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    # coordinate mapping (aspect preserving)
    def _scale(self):
        if not self.pix:
            return 1.0, 0.0, 0.0
        s = min(self.width() / self.pix.width(), self.height() / self.pix.height())
        ox = (self.width() - self.pix.width() * s) / 2
        oy = (self.height() - self.pix.height() * s) / 2
        return s, ox, oy

    def to_widget(self, p) -> QPointF:
        s, ox, oy = self._scale()
        return QPointF(p[0] * s + ox, p[1] * s + oy)

    def to_image(self, pos: QPointF) -> tuple:
        s, ox, oy = self._scale()
        x = (pos.x() - ox) / s
        y = (pos.y() - oy) / s
        if self.pix:
            x = float(np.clip(x, 0, self.pix.width() - 1))
            y = float(np.clip(y, 0, self.pix.height() - 1))
        return (x, y)

    def set_frame(self, frame: np.ndarray):
        self.pix = QPixmap.fromImage(bgr_to_qimage(frame))
        self.update()

    # drawing mode
    def start_drawing(self):
        self.drawing = True
        self.current = []
        self.setFocus()
        self.update()

    def cancel_drawing(self):
        self.drawing = False
        self.current = []
        self.update()

    def finish_drawing(self):
        if len(self.current) >= 3:
            pts = list(self.current)
            self.drawing = False
            self.current = []
            self.polygonFinished.emit(pts)
        self.update()

    # painting
    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(30, 30, 30))
        if not self.pix:
            p.setPen(QColor(200, 200, 200))
            p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Waiting for camera...")
            return
        s, ox, oy = self._scale()
        p.drawPixmap(int(ox), int(oy), int(self.pix.width() * s), int(self.pix.height() * s), self.pix)

        for i, slot in enumerate(self.cfg.slots):
            r, g, b = PALETTE[i % len(PALETTE)]
            col = QColor(r, g, b)
            pts = [self.to_widget(v) for v in slot.polygon]
            sel = i == self.selected
            p.setPen(QPen(col, 3 if sel else 2))
            fill = QColor(r, g, b, 55 if sel else 30)
            p.setBrush(fill)
            p.drawPolygon(QPolygonF(pts))
            p.setBrush(Qt.BrushStyle.NoBrush)
            if sel:
                p.setBrush(col)
                for v in pts:
                    p.drawEllipse(v, HANDLE_R, HANDLE_R)
                p.setBrush(Qt.BrushStyle.NoBrush)
            if pts:
                p.setPen(QColor(255, 255, 255))
                p.drawText(int(pts[0].x()) + 4, int(pts[0].y()) - 6, slot.name)

        if self.drawing and self.current:
            p.setPen(QPen(QColor(255, 255, 0), 2))
            pts = [self.to_widget(v) for v in self.current]
            for a, c in zip(pts, pts[1:]):
                p.drawLine(a, c)
            if self._cursor is not None:
                p.setPen(QPen(QColor(255, 255, 0), 1, Qt.PenStyle.DashLine))
                p.drawLine(pts[-1], self._cursor)
            p.setPen(QPen(QColor(255, 255, 0), 2))
            p.setBrush(QColor(255, 255, 0))
            for v in pts:
                p.drawEllipse(v, 4, 4)

    # mouse
    def mousePressEvent(self, e):
        if not self.pix:
            return
        pos = e.position()
        if self.drawing:
            if e.button() == Qt.MouseButton.RightButton:
                if self.current:
                    self.current.pop()
                    self.update()
            elif e.button() == Qt.MouseButton.LeftButton:
                if len(self.current) >= 3:
                    first = self.to_widget(self.current[0])
                    if (first - pos).manhattanLength() <= CLOSE_DIST:
                        self.finish_drawing()
                        return
                self.current.append(self.to_image(pos))
                self.update()
            return

        if e.button() != Qt.MouseButton.LeftButton:
            return
        if 0 <= self.selected < len(self.cfg.slots):
            for vi, v in enumerate(self.cfg.slots[self.selected].polygon):
                if (self.to_widget(v) - pos).manhattanLength() <= HANDLE_R * 2:
                    self._drag = (self.selected, vi)
                    return
        ix, iy = self.to_image(pos)
        for i in reversed(range(len(self.cfg.slots))):
            poly = np.array(self.cfg.slots[i].polygon, np.float32)
            if cv2.pointPolygonTest(poly, (ix, iy), False) >= 0:
                self.selected = i
                self.selectionChanged.emit(i)
                self.update()
                return

    def mouseDoubleClickEvent(self, e):
        if self.drawing and e.button() == Qt.MouseButton.LeftButton:
            self.finish_drawing()

    def mouseMoveEvent(self, e):
        self._cursor = e.position()
        if self._drag is not None:
            si, vi = self._drag
            self.cfg.slots[si].polygon[vi] = self.to_image(e.position())
        if self._drag is not None or self.drawing:
            self.update()

    def mouseReleaseEvent(self, _):
        if self._drag is not None:
            self._drag = None
            self.geometryChanged.emit()

    def keyPressEvent(self, e):
        if self.drawing:
            if e.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                self.finish_drawing(); return
            if e.key() == Qt.Key.Key_Escape:
                self.cancel_drawing(); return
            if e.key() == Qt.Key.Key_Backspace and self.current:
                self.current.pop(); self.update(); return
        super().keyPressEvent(e)


# --------------------------------------------------------------------------- #
class MainWindow(QWidget):
    def __init__(self, config_path: str, data_dir: str,
                 camera: Optional[int] = None, image: Optional[str] = None,
                 width: Optional[int] = None, height: Optional[int] = None):
        super().__init__()
        self.setWindowTitle("Slot polygons + training capture")
        self.config_path = Path(config_path)
        self.data_dir = Path(data_dir)
        self.cfg = DetectorConfig.load(self.config_path) if self.config_path.exists() else DetectorConfig()
        self.frame: Optional[np.ndarray] = None
        self.cap: Optional[cv2.VideoCapture] = None
        self._still: Optional[np.ndarray] = None

        # ---- widgets
        self.canvas = Canvas(self.cfg)
        self.canvas.polygonFinished.connect(self._on_polygon)
        self.canvas.selectionChanged.connect(self._on_canvas_selected)
        self.canvas.geometryChanged.connect(self.save_config)

        self.list = QListWidget()
        self.list.currentRowChanged.connect(self._on_list_selected)

        btn_new = QPushButton("New slot (N)")
        btn_rename = QPushButton("Rename")
        btn_delete = QPushButton("Delete")
        btn_new.clicked.connect(self._new_slot)
        btn_rename.clicked.connect(self._rename)
        btn_delete.clicked.connect(self._delete)

        self.chk_all = QCheckBox("Apply capture to all slots")
        btn_empty = QPushButton("Capture EMPTY (E)")
        btn_occ = QPushButton("Capture OCCUPIED (O)")
        btn_empty.setStyleSheet("background:#2e7d32;color:white;padding:8px;")
        btn_occ.setStyleSheet("background:#c62828;color:white;padding:8px;")
        btn_empty.clicked.connect(lambda: self.capture("empty"))
        btn_occ.clicked.connect(lambda: self.capture("occupied"))
        btn_save = QPushButton("Save config")
        btn_save.clicked.connect(self.save_config)

        self.hint = QLabel()
        self.hint.setWordWrap(True)
        self.status = QLabel("")
        self.status.setWordWrap(True)

        side = QVBoxLayout()
        side.addWidget(QLabel("Slots"))
        side.addWidget(self.list, 1)
        row = QHBoxLayout()
        for b in (btn_new, btn_rename, btn_delete):
            row.addWidget(b)
        side.addLayout(row)
        side.addSpacing(8)
        side.addWidget(self.chk_all)
        side.addWidget(btn_empty)
        side.addWidget(btn_occ)
        side.addWidget(btn_save)
        side.addWidget(self.hint)
        side.addWidget(self.status)
        side_w = QWidget()
        side_w.setLayout(side)
        side_w.setFixedWidth(280)

        lay = QHBoxLayout(self)
        lay.addWidget(self.canvas, 1)
        lay.addWidget(side_w)

        for key, fn in (("E", lambda: self.capture("empty")),
                        ("O", lambda: self.capture("occupied")),
                        ("N", self._new_slot)):
            QShortcut(QKeySequence(key), self, activated=fn)

        # ---- source
        if image:
            self._still = cv2.imread(image)
            if self._still is None:
                raise SystemExit(f"Cannot read image {image}")
        else:
            self.cap = cv2.VideoCapture(camera if camera is not None else 0)
            if width:
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            if height:
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            if not self.cap.isOpened():
                self.status.setText("Could not open the camera. Check --camera index.")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(33)

        self._refresh_list()
        self._update_hint()

    # ---- frames ---------------------------------------------------------
    def _tick(self):
        if self._still is not None:
            self.on_frame(self._still.copy())
        elif self.cap is not None and self.cap.isOpened():
            ok, f = self.cap.read()
            if ok:
                self.on_frame(f)

    def on_frame(self, frame: np.ndarray):
        self.frame = frame
        self.canvas.set_frame(frame)

    # ---- slot management --------------------------------------------------
    def _selected_name(self) -> Optional[str]:
        i = self.canvas.selected
        return self.cfg.slots[i].name if 0 <= i < len(self.cfg.slots) else None

    def _unique_name(self, base: str) -> str:
        names = {s.name for s in self.cfg.slots}
        if base not in names:
            return base
        k = 2
        while f"{base}_{k}" in names:
            k += 1
        return f"{base}_{k}"

    def _new_slot(self):
        if self.frame is None:
            self.status.setText("No frame yet - wait for the camera.")
            return
        self.canvas.start_drawing()
        self._update_hint()

    def _on_polygon(self, pts):
        name = self._unique_name(f"slot_{len(self.cfg.slots) + 1}")
        self.cfg.slots.append(SlotConfig(name=name, polygon=[tuple(p) for p in pts]))
        self.canvas.selected = len(self.cfg.slots) - 1
        self.save_config()
        self._refresh_list()
        self._update_hint()

    def _rename(self):
        i = self.canvas.selected
        if not (0 <= i < len(self.cfg.slots)):
            return
        old = self.cfg.slots[i].name
        text, ok = QInputDialog.getText(self, "Rename slot", "Slot name:", text=old)
        text = text.strip().replace(" ", "_").replace("/", "_")
        if not ok or not text or text == old:
            return
        if text in {s.name for s in self.cfg.slots}:
            QMessageBox.warning(self, "Rename", "That name is already used.")
            return
        old_dir, new_dir = self.data_dir / old, self.data_dir / text
        if old_dir.exists() and not new_dir.exists():
            old_dir.rename(new_dir)
        self.cfg.slots[i].name = text
        self.save_config()
        self._refresh_list()

    def _delete(self):
        i = self.canvas.selected
        if not (0 <= i < len(self.cfg.slots)):
            return
        name = self.cfg.slots[i].name
        if QMessageBox.question(self, "Delete slot",
                                f"Delete '{name}'? Captured images are kept on disk.") \
                != QMessageBox.StandardButton.Yes:
            return
        del self.cfg.slots[i]
        self.canvas.selected = min(i, len(self.cfg.slots) - 1)
        self.save_config()
        self._refresh_list()
        self.canvas.update()

    def _on_canvas_selected(self, i):
        self.list.blockSignals(True)
        self.list.setCurrentRow(i)
        self.list.blockSignals(False)

    def _on_list_selected(self, row):
        self.canvas.selected = row
        self.canvas.update()

    def _count(self, slot: str, label: str) -> int:
        d = self.data_dir / slot / label
        return len(list(d.glob("*.png"))) if d.exists() else 0

    def _refresh_list(self):
        self.list.blockSignals(True)
        self.list.clear()
        for s in self.cfg.slots:
            self.list.addItem(f"{s.name}   [{self._count(s.name, 'empty')} empty / "
                              f"{self._count(s.name, 'occupied')} occ]")
        self.list.setCurrentRow(self.canvas.selected)
        self.list.blockSignals(False)

    def _update_hint(self):
        if self.canvas.drawing:
            self.hint.setText("Drawing: click corners. Double-click / Enter / click first "
                              "point = close. Right-click or Backspace = undo point. Esc = cancel.")
        else:
            self.hint.setText("Click a polygon to select it, drag its corner handles to adjust.")

    # ---- persistence ------------------------------------------------------
    def save_config(self):
        self.cfg.save(self.config_path)
        self.status.setText(f"Saved {self.config_path}")

    def capture(self, label: str):
        if self.frame is None:
            self.status.setText("No frame to capture.")
            return
        if not self.cfg.slots:
            self.status.setText("Draw at least one slot first.")
            return
        if self.chk_all.isChecked():
            names = [s.name for s in self.cfg.slots]
        else:
            n = self._selected_name()
            if n is None:
                self.status.setText("Select a slot (or tick 'Apply to all slots').")
                return
            names = [n]
        fname = f"{int(time.time() * 1000)}.png"
        saved = 0
        for n in names:
            d = self.data_dir / n / label
            d.mkdir(parents=True, exist_ok=True)
            if cv2.imwrite(str(d / fname), self.frame):    # raw frame, no overlay
                saved += 1
        self.status.setText(f"Saved {label} frame for {saved} slot(s).")
        self._refresh_list()

    def closeEvent(self, e):
        self.timer.stop()
        if self.cap is not None:
            self.cap.release()
        self.save_config()
        super().closeEvent(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--camera", type=int, default=0)
    ap.add_argument("--image", type=str, help="use a still image instead of a camera")
    ap.add_argument("--config", default="slots.json")
    ap.add_argument("--data", default="data")
    ap.add_argument("--width", type=int)
    ap.add_argument("--height", type=int)
    a = ap.parse_args()

    app = QApplication(sys.argv)
    w = MainWindow(a.config, a.data, camera=a.camera, image=a.image,
                   width=a.width, height=a.height)
    w.resize(1100, 680)
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
