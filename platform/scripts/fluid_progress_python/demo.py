import math, sys
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (QApplication,QWidget,QVBoxLayout,QHBoxLayout,QGroupBox,QLabel,QPushButton,QSlider,QCheckBox,QScrollArea)
from widgets import InkBar,Vessel,PlumeLine

TOTAL=184.0
class Demo(QWidget):
    def __init__(self):
        super().__init__(); self.setWindowTitle('Fluid Progress — PySide6 widgets'); self.resize(850,820)
        self.loaded=0.; self.speed=0.; self.elapsed=0.; self.state='idle'
        root=QVBoxLayout(self); root.setSpacing(12)
        title=QLabel('Fluid progress · three native Qt widgets'); title.setObjectName('title'); root.addWidget(title)
        self.widgets=[]
        for label,klass in [('Ink bar',InkBar),('Vessel',Vessel),('Plume line',PlumeLine)]:
            group=QGroupBox(label); layout=QVBoxLayout(group); widget=klass(); layout.addWidget(widget)
            self.widgets.append(widget); root.addWidget(group)
        self.status=QLabel(); root.addWidget(self.status)
        controls=QHBoxLayout(); self.start=QPushButton('Start download'); self.reset_btn=QPushButton('Reset'); self.wait=QCheckBox('Waiting for server')
        for item in [self.start,self.reset_btn,self.wait]: controls.addWidget(item)
        root.addLayout(controls)
        scrub_row=QHBoxLayout(); scrub_row.addWidget(QLabel('Scrub'))
        self.scrub=QSlider(Qt.Orientation.Horizontal); self.scrub.setRange(0,1000); scrub_row.addWidget(self.scrub); root.addLayout(scrub_row)
        self.start.clicked.connect(self.toggle); self.reset_btn.clicked.connect(self.reset); self.wait.toggled.connect(self.wait_changed); self.scrub.sliderMoved.connect(self.scrubbed)
        self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(33)
        self.refresh()
        self.setStyleSheet('''QWidget {background:#f5f2f8;color:#241c2c;font:14px Ubuntu, sans-serif;} QGroupBox {background:white;border:1px solid #e8dfef;border-radius:14px;margin-top:12px;padding:12px;font-weight:bold;} QGroupBox::title {subcontrol-origin:margin;left:15px;padding:0 6px;color:#6f4388;} QLabel#title {font-size:23px;font-weight:bold;} QPushButton {background:#925cad;color:white;border:0;border-radius:9px;padding:12px;} QPushButton:hover {background:#6f4388;} QSlider::groove:horizontal {height:6px;background:#e8dfef;border-radius:3px;} QSlider::handle:horizontal {background:#925cad;width:16px;margin:-5px 0;border-radius:8px;}''')
    def toggle(self):
        if self.state=='downloading': self.state='paused'
        elif self.state=='done': self.loaded=0.; self.state='downloading'
        else: self.state='downloading'
        self.refresh()
    def reset(self):
        self.state='idle'; self.loaded=0.; self.speed=0.; self.wait.setChecked(False)
        for w in self.widgets:w.reset()
        self.refresh()
    def wait_changed(self,checked):
        if checked and self.state=='idle':self.state='downloading'
        self.refresh()
    def scrubbed(self,value):
        self.loaded=value/1000*TOTAL; self.state='done' if self.loaded>=TOTAL else 'paused'; self.speed=0.; self.refresh()
    def tick(self):
        dt=.033; self.elapsed+=dt
        if self.state=='downloading' and not self.wait.isChecked():
            target=5.6+2.4*math.sin(self.elapsed*.6)+1.1*math.sin(self.elapsed*1.9)
            self.speed+=(target-self.speed)*min(1,dt*3); self.loaded=min(TOTAL,self.loaded+self.speed*dt)
            if self.loaded>=TOTAL:self.state='done';self.speed=0
        else:self.speed+=(0-self.speed)*min(1,dt*6)
        self.refresh()
    def refresh(self):
        pct=100*self.loaded/TOTAL; active=self.state=='downloading'; waiting=active and self.wait.isChecked()
        for w in self.widgets:
            w.set_progress(pct,self.speed);w.set_running(active);w.set_waiting(waiting)
        if self.state=='idle':sub=f'{TOTAL:.0f} MB · ready to download'
        elif waiting:sub='Waiting for the server…'
        elif active:
            eta=round((TOTAL-self.loaded)/max(self.speed,.5));sub=f'{self.loaded:.1f} of {TOTAL:.0f} MB · {self.speed:.1f} MB/s · {eta} s left'
        elif self.state=='paused':sub=f'Paused at {self.loaded:.1f} of {TOTAL:.0f} MB'
        else:sub=f'Download complete · {TOTAL:.0f} MB'
        self.status.setText(f'calibration-models-v3.pkg    {"—" if waiting else str(int(pct))+"%"}    |    {sub}')
        self.start.setText({'idle':'Start download','downloading':'Pause','paused':'Resume','done':'Download again'}[self.state])
        if not self.scrub.isSliderDown():self.scrub.setValue(round(pct*10))

if __name__=='__main__':
    app=QApplication(sys.argv); window=Demo();window.show();sys.exit(app.exec())
