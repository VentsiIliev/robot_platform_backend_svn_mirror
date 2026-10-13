import math, random, time
from dataclasses import dataclass
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient, QRadialGradient, QPen, QFont
from PySide6.QtWidgets import QWidget

PURPLE='#925cad'; DARK='#6f4388'; LIGHT='#b58bcf'; TRACK='#f1e9f6'; BORDER='#e8dfef'

def color(hexcode, alpha=255):
    c=QColor(hexcode); c.setAlpha(max(0,min(255,int(alpha)))); return c

@dataclass
class Particle:
    x:float; y:float; vx:float; vy:float; radius:float; grow:float; age:float; lifetime:float; alpha:float; shade:int

class FluidProgress(QWidget):
    """Base class. set_progress(0..100, speed_mb_s=0), set_waiting(bool), set_running(bool)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.progress=0.; self.speed=0.; self.waiting=False; self.running=False
        self.particles=[]; self.phase=0.; self._last=time.monotonic(); self._emit_acc=0.
        self.setMinimumWidth(240)
        self.timer=QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(33)

    def set_progress(self, percent, speed_mb_s=0):
        self.progress=max(0.,min(100.,float(percent))); self.speed=max(0.,float(speed_mb_s)); self.update()
    def set_waiting(self, waiting): self.waiting=bool(waiting); self.update()
    def set_running(self, running): self.running=bool(running); self.update()
    def reset(self):
        self.progress=0.; self.speed=0.; self.waiting=False; self.running=False; self.particles.clear(); self.update()
    def _tick(self):
        now=time.monotonic(); dt=min(.05,now-self._last); self._last=now; self.phase+=dt
        for p in self.particles:
            p.age+=dt; p.x+=(p.vx+math.sin(p.y*.05+self.phase*1.4+p.shade*2)*14)*dt
            p.y+=(p.vy+math.cos(p.x*.04+self.phase*1.1+p.shade)*8)*dt; p.radius+=p.grow*dt
        self.particles=[p for p in self.particles if p.age<p.lifetime]
        if self.running and self.progress<100:
            self._emit_acc+=dt*32*(.9 if self.waiting else .35+self.speed/8)
            while self._emit_acc>=1:
                self._emit_acc-=1; self._emit_particle()
        self.update()
    def _add_particle(self,x,y,vx,vy,r,grow,life,alpha):
        self.particles.append(Particle(x,y,vx,vy,r,grow,0,life,alpha,random.randrange(3)))
        if len(self.particles)>260: self.particles.pop(0)
    def _paint_particles(self,p):
        shades=['#b58bcf','#7e57a3','#d6bfe6']
        for pt in self.particles:
            opacity=pt.alpha*(1-pt.age/pt.lifetime)*min(1,pt.age*4)
            gradient=QRadialGradient(QPointF(pt.x,pt.y),max(1,pt.radius))
            gradient.setColorAt(0,color(shades[pt.shade],opacity*255)); gradient.setColorAt(1,color(shades[pt.shade],0))
            p.setBrush(gradient); p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(pt.x,pt.y),pt.radius,pt.radius)
    def _blobs(self,p,x0,x1,y0,y1,count,radius,alpha):
        for i in range(count):
            u=(i/count+self.phase*.025*(1 if i%2 else -1)+10)%1
            x=x0+(x1-x0)*u; y=y0+(y1-y0)*(.5+math.sin(self.phase*.8+i*2.1)*.32)
            g=QRadialGradient(QPointF(x,y),radius)
            g.setColorAt(0,color('#d6bfe6' if i%2 else LIGHT,alpha*255)); g.setColorAt(1,color(LIGHT,0))
            p.fillRect(QRectF(x-radius,y-radius,radius*2,radius*2),g)
    def _range(self):
        if self.waiting and self.running:
            head=(self.phase*.4)%1.35; return max(0,head-.35),head
        return 0.,self.progress/100
    def _emit_particle(self): pass

class InkBar(FluidProgress):
    def __init__(self,parent=None): super().__init__(parent); self.setFixedHeight(84)
    def _emit_particle(self):
        _,hi=self._range(); w=self.width()
        if hi>=1: return
        self._add_particle(hi*w+random.uniform(-2,2),random.uniform(17,67),random.uniform(18,60),random.uniform(-14,14),random.uniform(10,22),9,random.uniform(1.2,2.4),.38)
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w=self.width(); h=self.height(); rect=QRectF(.5,.5,w-1,h-1)
        clip=QPainterPath(); clip.addRoundedRect(rect,h/2,h/2)
        p.fillPath(clip,color(TRACK)); p.save(); p.setClipPath(clip)
        lo,hi=self._range(); x0=lo*w; x1=hi*w
        if x1>0 and x0<w:
            def wave(y,k): return math.sin(y*.16+self.phase*3*k)*5+math.sin(y*.07-self.phase*1.9*k)*3
            path=QPainterPath(); path.moveTo(-30 if x0<=0 else x0+wave(0,1),0)
            for y in range(4,h+1,4): path.lineTo(-30 if x0<=0 else x0+wave(y,1),y)
            for y in range(h,-1,-4): path.lineTo(w+30 if x1>=w else x1+wave(y,2),y)
            path.closeSubpath()
            g=QLinearGradient(max(0,x0),0,min(w,x1)+1,0); g.setColorAt(0,color(DARK)); g.setColorAt(.7,color(PURPLE)); g.setColorAt(1,color(LIGHT))
            p.fillPath(path,g); p.save(); p.setClipPath(path); self._blobs(p,max(0,x0),min(w,x1),0,h,6,h*.95,.35); p.restore()
        self._paint_particles(p); p.restore(); p.setBrush(Qt.BrushStyle.NoBrush); p.setPen(QPen(color(BORDER),1)); p.drawPath(clip)

class Vessel(FluidProgress):
    def __init__(self,parent=None): super().__init__(parent); self.setFixedHeight(300)
    def _level(self): return .5+.1*math.sin(self.phase*1.2) if self.waiting and self.running else self.progress/100
    def _emit_particle(self):
        level=self._level()
        if not 0<level<1:return
        self._add_particle(self.width()/2+random.uniform(-90,90),self.height()/2+112-level*224,random.uniform(-8,8),random.uniform(-46,-22),random.uniform(8,15),7,random.uniform(1.4,2.6),.4)
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        cx=self.width()/2; cy=self.height()/2; r=112; bottom=cy+r; level=self._level(); top=bottom-level*2*r
        circle=QPainterPath(); circle.addEllipse(QPointF(cx,cy),r,r)
        p.save(); p.setClipPath(circle); p.fillPath(circle,color(TRACK))
        def surface(k,ph,amp):
            path=QPainterPath(); path.moveTo(cx-r,bottom+2)
            for j in range(57):
                x=cx-r+j*4; y=top+math.sin(x*.045+self.phase*2*k+ph)*amp+math.sin(x*.1-self.phase*1.4*k)*amp*.4
                path.lineTo(x,y)
            path.lineTo(cx+r,bottom+2); path.closeSubpath(); return path
        liquid=None
        if level>0:
            amp=0 if level>=1 else 7
            p.fillPath(surface(1.3,1.7,amp*.9),color(LIGHT,140)); liquid=surface(1,0,amp)
            g=QLinearGradient(0,top,0,bottom); g.setColorAt(0,color(PURPLE)); g.setColorAt(1,color(DARK))
            p.fillPath(liquid,g); p.save(); p.setClipPath(liquid); self._blobs(p,cx-r,cx+r,top,bottom,5,r*.8,.3); p.restore()
        self._paint_particles(p)
        label='…' if self.waiting and self.running else f'{int(self.progress)}%'
        font=QFont('Ubuntu',34,QFont.Weight.Bold); p.setFont(font)
        bounds=QRectF(cx-r,cy-38,r*2,76)
        p.setPen(color('#241c2c')); p.drawText(bounds,Qt.AlignmentFlag.AlignCenter,label)
        if liquid:
            p.save(); p.setClipPath(liquid); p.setPen(color('#ffffff')); p.drawText(bounds,Qt.AlignmentFlag.AlignCenter,label); p.restore()
        p.restore(); p.setBrush(Qt.BrushStyle.NoBrush); p.setPen(QPen(color(BORDER),2)); p.drawPath(circle)

class PlumeLine(FluidProgress):
    def __init__(self,parent=None): super().__init__(parent); self.setFixedHeight(150)
    def _emit_particle(self):
        _,hi=self._range(); w=self.width()
        if hi>=1:return
        self._add_particle(max(4,min(w-4,hi*w))+random.uniform(-1,1),self.height()/2+random.uniform(-2,2),random.uniform(-46,-8),random.uniform(-26,26),random.uniform(6,14),14,random.uniform(1.4,2.8),.32)
    def paintEvent(self,event):
        p=QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w=self.width(); y=self.height()/2; lo,hi=self._range(); x0=lo*w; x1=max(0,min(w,hi*w))
        self._paint_particles(p)
        track=QPainterPath(); track.addRoundedRect(QRectF(0,y-4,w,8),4,4); p.fillPath(track,color(TRACK))
        if x1>x0:
            g=QLinearGradient(x0,0,x1+1,0); g.setColorAt(0,color(DARK)); g.setColorAt(.75,color(PURPLE)); g.setColorAt(1,color(LIGHT))
            p.save(); p.setClipPath(track); p.fillRect(QRectF(x0,y-4,x1-x0,8),g); p.restore()
        if 0<hi<=1 and self.running:
            hx=max(4,min(w-4,x1)); g=QRadialGradient(QPointF(hx,y),26)
            g.setColorAt(0,color(LIGHT,140)); g.setColorAt(1,color(LIGHT,0))
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(g); p.drawEllipse(QPointF(hx,y),26,26)
            p.setBrush(color('#ffffff')); p.drawEllipse(QPointF(hx,y),4.5,4.5)
