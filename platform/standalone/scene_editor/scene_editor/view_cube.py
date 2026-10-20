"""Camera orientation indicator with clickable orthographic faces."""
import numpy as np
from PyQt6.QtCore import QPointF, Qt
from PyQt6.QtGui import QColor, QPainter, QPolygonF
from PyQt6.QtWidgets import QWidget


class ViewCube(QWidget):
    def __init__(self, viewport):
        super().__init__(viewport)
        self.viewport = viewport
        self.setFixedSize(94,100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip('Click a face for an orthographic view. Double-click for perspective.')
        self._faces = []

    def mousePressEvent(self,event):
        event.accept()

    def paintEvent(self, event):
        _,eye,right,up = self.viewport.camera()
        direction = (eye-self.viewport.target)/self.viewport.distance
        vertices = np.array([(x,y,z) for x in (-1,1) for y in (-1,1) for z in (-1,1)])
        points = [QPointF(47+19*(v@right),46-19*(v@up)) for v in vertices]
        faces = [((4,5,7,6),(1,0,0),'X','Right'),((0,2,3,1),(-1,0,0),'−X','Left'),
                 ((0,1,5,4),(0,-1,0),'Y','Front'),((2,6,7,3),(0,1,0),'Y','Back'),
                 ((1,3,7,5),(0,0,1),'Z','Top'),((0,4,6,2),(0,0,-1),'−Z','Bottom')]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        self._faces = []
        for indices,normal,label,view in sorted(faces,key=lambda face:np.dot(face[1],direction)):
            facing = float(np.dot(normal,direction))
            if facing <= 1e-5:
                continue
            polygon = QPolygonF([points[i] for i in indices])
            painter.setBrush(QColor.fromRgbF(.72+.18*facing,.69+.18*facing,.78+.18*facing))
            painter.setPen(QColor('#756780'))
            painter.drawPolygon(polygon)
            painter.setPen(QColor('#30243A'))
            painter.drawText(polygon.boundingRect(),Qt.AlignmentFlag.AlignCenter,label)
            self._faces.append((polygon,view))
        painter.end()

    def mouseReleaseEvent(self,event):
        if event.button() == Qt.MouseButton.LeftButton:
            for polygon,view in reversed(self._faces):
                if polygon.containsPoint(event.position(),Qt.FillRule.OddEvenFill):
                    self.viewport.set_camera_view(view)
                    break

    def mouseDoubleClickEvent(self,event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.viewport.set_camera_view('Perspective')
