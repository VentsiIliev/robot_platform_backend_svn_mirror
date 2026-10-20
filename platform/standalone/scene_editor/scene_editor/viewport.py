"""OpenGL viewport. Object edits change matrices, never rebuild mesh vertices."""
import ctypes
import math

import numpy as np
from OpenGL import GL
from OpenGL.GL.shaders import compileProgram, compileShader
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtWidgets import QApplication, QLabel

from .model import Pose, Scene, translated_poses
from .styles import PALETTES, viewport_colors

_VERTEX = '''#version 330 core
layout(location=0) in vec3 position;
layout(location=1) in vec3 normal;
uniform mat4 model;
uniform mat4 view_projection;
out vec3 surface_normal;
void main() {
    gl_Position = view_projection * model * vec4(position, 1.0);
    surface_normal = mat3(transpose(inverse(model))) * normal;
}
'''
_FRAGMENT = '''#version 330 core
in vec3 surface_normal;
uniform vec4 color;
uniform bool unlit;
uniform bool selected;
out vec4 pixel;
void main() {
    if (unlit) { pixel = color; return; }
    vec3 n = normalize(surface_normal);
    float light = 0.32 + 0.53 * abs(dot(n, normalize(vec3(0.45, -0.5, 0.8))))
                       + 0.15 * abs(dot(n, normalize(vec3(-0.7, 0.3, 0.4))));
    vec3 base = selected ? mix(color.rgb, vec3(1.0, 0.7, 0.3), 0.2) : color.rgb;
    pixel = vec4(base * light, color.a);
}
'''


def _normalized(value):
    return value / max(np.linalg.norm(value), 1e-12)


class Viewport(QOpenGLWidget):
    selected = pyqtSignal(object)
    selection_changed = pyqtSignal(object, object)
    pose_dragged = pyqtSignal(object, object, int)
    group_dragged = pyqtSignal(object, int)
    error = pyqtSignal(str)
    cancel_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = Scene()
        self.selected_id = None
        self.selected_ids = set()
        self.mode = 'view'
        self.editable = True
        self.selection_only = False
        self.axis = 'Z'
        self.target = np.zeros(3)
        self.distance = 1600.
        self.yaw, self.elevation = 45., 28.
        self._program = None
        self._buffers = {}
        self._line_vao = self._line_vbo = None
        self._error = None
        self._drag = None
        self._gesture = 0
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMinimumSize(320, 260)
        self._help = QLabel('Click to select · Drag selected primitive: move · Right/empty drag: orbit · Wheel: zoom', self)
        self._stats = QLabel(self)
        for label in (self._help, self._stats):
            label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._help.setWordWrap(True)
        self.set_theme(viewport_colors(PALETTES['light']))

    def set_theme(self, colors):
        self._view_colors = dict(colors)
        for label in (self._help, self._stats):
            label.setStyleSheet('background: transparent; color: '+colors['overlay']+';')
        self.update()

    def _rgb(self, role):
        color = self._view_colors[role]
        return tuple(int(color[index:index+2],16)/255 for index in (1,3,5))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._help.setGeometry(14, 8, max(self.width()-28, 1), 45)
        self._stats.setGeometry(14, self.height()-30, max(self.width()-28, 1), 24)

    def initializeGL(self):
        try:
            self._program = compileProgram(compileShader(_VERTEX,GL.GL_VERTEX_SHADER),compileShader(_FRAGMENT,GL.GL_FRAGMENT_SHADER))
            self._uniform = {name:GL.glGetUniformLocation(self._program,name) for name in ('model','view_projection','color','unlit','selected')}
            self._line_vao,self._line_vbo = self._new_buffer()
            self.context().aboutToBeDestroyed.connect(self.cleanup)
        except Exception as exc:
            self._fail(exc)

    def _new_buffer(self):
        vao,vbo = int(GL.glGenVertexArrays(1)),int(GL.glGenBuffers(1))
        GL.glBindVertexArray(vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,vbo)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0,3,GL.GL_FLOAT,False,24,ctypes.c_void_p(0))
        GL.glEnableVertexAttribArray(1)
        GL.glVertexAttribPointer(1,3,GL.GL_FLOAT,False,24,ctypes.c_void_p(12))
        GL.glBindVertexArray(0)
        return vao,vbo

    def _mesh_buffer(self, mesh):
        key = id(mesh)
        if key not in self._buffers:
            vao,vbo = self._new_buffer()
            data = mesh.gpu_data()
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER,vbo)
            GL.glBufferData(GL.GL_ARRAY_BUFFER,data.nbytes,data,GL.GL_STATIC_DRAW)
            self._buffers[key] = (mesh,vao,vbo,len(mesh.vertices)*3)
        return self._buffers[key]

    def camera(self):
        yaw,elevation = np.radians([self.yaw,self.elevation])
        eye = self.target + self.distance*np.array([np.cos(elevation)*np.cos(yaw),np.cos(elevation)*np.sin(yaw),np.sin(elevation)])
        forward = _normalized(self.target-eye)
        right = _normalized(np.cross(forward,[0.,0.,1.]))
        up = np.cross(right,forward)
        view = np.eye(4)
        view[:3,:3] = np.array([right,up,-forward])
        view[:3,3] = -view[:3,:3] @ eye
        near,far = max(self.distance/1000,.001),max(self.distance*100,1000.)
        f = 1/math.tan(math.radians(45)/2)
        projection = np.zeros((4,4))
        projection[0,0] = f/max(self.width()/max(self.height(),1),.01)
        projection[1,1] = f
        projection[2,2],projection[2,3] = (far+near)/(near-far),2*far*near/(near-far)
        projection[3,2] = -1
        return projection @ view,eye,right,up

    def fit(self, selected=False):
        obj = self.current_object()
        chosen = [item for item in self.scene.objects if item.id in self.selection_ids() and item.visible]
        bounds = Scene(chosen).bounds() if selected and chosen else self.scene.bounds()
        self.target = bounds.mean(axis=0)
        radius = max(np.linalg.norm(bounds[1]-bounds[0])/2,1.)
        aspect = max(self.width()/max(self.height(), 1), .01)
        half_angle = min(math.radians(22.5), math.atan(math.tan(math.radians(22.5))*aspect))
        self.distance = radius/max(math.sin(half_angle),.001)*1.15
        self.update()

    def current_object(self):
        return next((obj for obj in self.scene.objects if obj.id == self.selected_id),None)

    def set_scene(self, scene):
        self.scene = scene
        self.selected_id = None
        self.selected_ids.clear()
        self.fit()

    def selection_ids(self):
        return self.selected_ids | ({self.selected_id} if self.selected_id else set())

    def set_selected(self, object_id, selected_ids=None):
        self.selected_id = object_id
        self.selected_ids = set(selected_ids) if selected_ids is not None else ({object_id} if object_id else set())
        self.update()

    def paintGL(self):
        if self._program and not self._error:
            try:
                self._render(False)
            except Exception as exc:
                self._fail(exc)
        if self._error:
            self._help.setText('3D renderer unavailable: '+self._error)
        else:
            self._stats.setText(f'{len(self.scene.objects)} objects  ·  {len(self.selection_ids())} selected  ·  {sum(len(obj.mesh.vertices) for obj in self.scene.objects if obj.visible):,} triangles  ·  mm')

    def _render(self, picking):
        GL.glViewport(0,0,int(self.width()*self.devicePixelRatioF()),int(self.height()*self.devicePixelRatioF()))
        # Qt's compositor can change these between frames. Restore masks before
        # clearing, otherwise old depth values can obscure newly moved objects.
        GL.glDepthMask(GL.GL_TRUE)
        GL.glColorMask(GL.GL_TRUE, GL.GL_TRUE, GL.GL_TRUE, GL.GL_TRUE)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glDisable(GL.GL_SCISSOR_TEST)
        GL.glDisable(GL.GL_STENCIL_TEST)
        GL.glClearColor(0,0,0,1) if picking else GL.glClearColor(*self._rgb('background'),1)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDisable(GL.GL_CULL_FACE)
        GL.glDisable(GL.GL_BLEND)
        if picking:
            GL.glDisable(GL.GL_DITHER)
            GL.glDisable(GL.GL_MULTISAMPLE)
            GL.glDisable(GL.GL_FRAMEBUFFER_SRGB)
        GL.glUseProgram(self._program)
        vp,eye,_,_ = self.camera()
        GL.glUniformMatrix4fv(self._uniform['view_projection'],1,GL.GL_TRUE,np.asarray(vp,dtype=np.float32))
        visible = [(index,obj) for index,obj in enumerate(self.scene.objects) if obj.visible and obj.color[3] > 0]
        if not picking:
            self._draw_grid()
            visible.sort(key=lambda pair:(pair[1].color[3] < .999,-np.linalg.norm(pair[1].world_bounds().mean(axis=0)-eye)))
        for index,obj in visible:
            _,vao,_,count = self._mesh_buffer(obj.mesh)
            if picking:
                code = index+1
                color = ((code&255)/255,((code>>8)&255)/255,((code>>16)&255)/255,1)
            else:
                color = obj.color
                if color[3] < .999:
                    GL.glEnable(GL.GL_BLEND)
                    GL.glBlendFunc(GL.GL_SRC_ALPHA,GL.GL_ONE_MINUS_SRC_ALPHA)
                    GL.glDepthMask(GL.GL_FALSE)
            GL.glUniformMatrix4fv(self._uniform['model'],1,GL.GL_TRUE,np.asarray(obj.matrix(),dtype=np.float32))
            GL.glUniform4f(self._uniform['color'],*color)
            GL.glUniform1i(self._uniform['unlit'],int(picking))
            GL.glUniform1i(self._uniform['selected'],int(obj.id in self.selection_ids() and not picking))
            GL.glBindVertexArray(vao)
            GL.glDrawArrays(GL.GL_TRIANGLES,0,count)
            GL.glDepthMask(GL.GL_TRUE)
        GL.glDisable(GL.GL_BLEND)
        if not picking:
            self._draw_selection()
        GL.glBindVertexArray(0)
        GL.glUseProgram(0)
        live = {id(obj.mesh) for obj in self.scene.objects}
        for key in set(self._buffers)-live:
            _,vao,vbo,_ = self._buffers.pop(key)
            GL.glDeleteBuffers(1,[vbo]);GL.glDeleteVertexArrays(1,[vao])

    def _lines(self, vertices, color):
        if not len(vertices): return
        data = np.zeros((len(vertices),6),dtype=np.float32)
        data[:,:3] = vertices
        GL.glUniformMatrix4fv(self._uniform['model'],1,GL.GL_TRUE,np.eye(4,dtype=np.float32))
        GL.glUniform4f(self._uniform['color'],*color)
        GL.glUniform1i(self._uniform['unlit'],1)
        GL.glUniform1i(self._uniform['selected'],0)
        GL.glBindVertexArray(self._line_vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER,self._line_vbo)
        GL.glBufferData(GL.GL_ARRAY_BUFFER,data.nbytes,data,GL.GL_DYNAMIC_DRAW)
        GL.glDrawArrays(GL.GL_LINES,0,len(vertices))

    def _draw_grid(self):
        span = max(self.distance,1.)
        step = 10**math.floor(math.log10(span/12))
        if span/step > 30: step *= 2
        center = np.round(self.target[:2]/step)*step
        extent = step*15
        lines = []
        for index in range(-15,16):
            x,y = center + index*step
            # A slight offset keeps a surface at Z=0 clear of coplanar grid lines.
            lines.extend([[x,center[1]-extent,-.1],[x,center[1]+extent,-.1],
                          [center[0]-extent,y,-.1],[center[0]+extent,y,-.1]])
        self._lines(lines,(*self._rgb('grid'),1))
        self._lines([[-extent,0,0],[extent,0,0]],(.55,.22,.25,1))
        self._lines([[0,-extent,0],[0,extent,0]],(.22,.5,.34,1))

    def _draw_selection(self):
        obj = self.current_object()
        if obj is None: return
        lines=[]
        for item in self.scene.objects:
            if item.id not in self.selection_ids() or not item.visible:
                continue
            low,high = item.world_bounds()
            corners = np.array([[x,y,z] for x in (low[0],high[0]) for y in (low[1],high[1]) for z in (low[2],high[2])])
            for index in range(8):
                for axis in (1,2,4):
                    other=index^axis
                    if other > index: lines.extend([corners[index],corners[other]])
        self._lines(lines,(*self._rgb('selection'),1))
        GL.glDisable(GL.GL_DEPTH_TEST)
        pivot = obj.world_pivot()
        length = max(np.linalg.norm(self.camera()[1]-pivot)*.075,.1)
        for index,color in enumerate(((.95,.3,.32,1),(.25,.85,.47,1),(.32,.57,1.,1))):
            endpoint = pivot.copy();endpoint[index] += length
            self._lines([pivot,endpoint],color)
        GL.glEnable(GL.GL_DEPTH_TEST)

    def _pick(self, point):
        if not self._program or self._error or not self.isValid(): return None
        self.makeCurrent()
        try:
            self._render(True)
            ratio = self.devicePixelRatioF()
            pixel = GL.glReadPixels(int(point.x()*ratio),int((self.height()-1-point.y())*ratio),1,1,GL.GL_RGBA,GL.GL_UNSIGNED_BYTE)
            rgb = np.frombuffer(pixel,dtype=np.uint8)
            code = int(rgb[0])+(int(rgb[1])<<8)+(int(rgb[2])<<16)
            self._render(False)
        finally:
            self.doneCurrent()
        return self.scene.objects[code-1].id if 0 < code <= len(self.scene.objects) else None

    def mousePressEvent(self, event):
        self.setFocus()
        selection_only = self.selection_only
        point=event.position().toPoint()
        obj=self.current_object()
        previous_selection = self.selected_id
        previous_ids = self.selection_ids()
        picked = None
        if event.button() == Qt.MouseButton.LeftButton:
            picked=self._pick(point)
            modifiers = event.modifiers()
            if not selection_only and modifiers & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier):
                ids = set(previous_ids)
                if picked is not None:
                    if picked in ids and modifiers & Qt.KeyboardModifier.ControlModifier:
                        ids.remove(picked)
                    else:
                        ids.add(picked)
                primary = picked if picked in ids else next((item.id for item in self.scene.objects if item.id in ids),None)
                self.selection_changed.emit(ids, primary)
                self._drag = None
                return
            if picked is not None:
                if not selection_only and picked in previous_ids:
                    self.selection_changed.emit(previous_ids,picked)
                else:
                    self.set_selected(picked);self.selected.emit(picked)
                obj=self.current_object()
            elif self.mode == 'view':
                self.set_selected(None);self.selected.emit(None);obj=None
        if selection_only:
            self._drag = None
            return
        if event.button() == Qt.MouseButton.LeftButton and picked is not None and picked not in previous_ids:
            # This gesture selects a different object; a subsequent gesture may
            # move it. Never combine selection with a transform or camera drag.
            self._drag = None
            return
        action, axis = 'view', self.axis
        members = [item for item in self.scene.objects if item.id in self.selection_ids()]
        group = len(members) > 1
        if self.editable and event.button() == Qt.MouseButton.LeftButton and picked in previous_ids and picked is not None and obj is not None and not any(item.locked for item in members):
            if self.mode in ('move', 'rotate') and not (group and self.mode == 'rotate'):
                action = self.mode
            elif self.mode == 'view' and (group or (obj.mesh.primitive and obj.mesh.primitive.get('kind') in ('box','cylinder','sphere'))):
                action, axis = 'move', 'Screen'
        self._gesture += 1
        self._drag = {'start':point,'last':point,'button':event.button(),'pose':obj.pose if obj else None,'id':obj.id if obj else None,
                      'action':action,'axis':axis,'started':False,'members':members if group else []}
        if action != 'view':
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._drag is None: return
        point=event.position().toPoint();last=self._drag['last'];delta=point-last;self._drag['last']=point
        button=self._drag['button']
        obj=self.current_object()
        if button == Qt.MouseButton.MiddleButton:
            _,_,right,up=self.camera()
            scale=2*self.distance*math.tan(math.radians(22.5))/max(self.height(),1)
            self.target += (-right*delta.x()+up*delta.y())*scale
        elif button == Qt.MouseButton.LeftButton and self.editable and self._drag['action'] != 'view' and obj is not None and not obj.locked and obj.id == self._drag['id']:
            start=self._drag['pose'];total=point-self._drag['start']
            if not self._drag['started'] and total.manhattanLength() < QApplication.startDragDistance():
                return
            self._drag['started'] = True
            if self._drag['action'] == 'move':
                _,eye,right,up=self.camera()
                parent = obj.parent_matrix()
                local_pivot = np.asarray(start.translation) + start.pivot
                start_pivot = parent[:3,:3] @ local_pivot + parent[:3,3]
                forward = _normalized(self.target-eye)
                depth = max(float(np.dot(start_pivot-eye, forward)), .001)
                scale=2*depth*math.tan(math.radians(22.5))/max(self.height(),1)
                movement=(right*total.x()-up*total.y())*scale
                if self._drag['axis'] != 'Screen':
                    axis='XYZ'.index(self._drag['axis']);movement=np.eye(3)[axis]*movement[axis]
                if self._drag['members']:
                    if any(item.locked for item in self.scene.objects if item.id in self.selection_ids()):
                        return
                    poses = translated_poses(self._drag['members'],movement)
                    self.group_dragged.emit(poses,self._gesture)
                    self.update()
                    return
                movement = parent[:3,:3].T @ movement
                pose=Pose(tuple(np.asarray(start.translation)+movement),start.rotation,start.pivot)
            else:
                rotation=list(start.rotation);axis='XYZ'.index(self._drag['axis'] if self._drag['axis'] != 'Screen' else 'Z')
                rotation[axis] += (total.x()-total.y())*.4
                pose=Pose(start.translation,tuple(rotation),start.pivot)
            self.pose_dragged.emit(obj.id,pose,self._gesture)
        else:
            self.yaw -= delta.x()*.4
            self.elevation=float(np.clip(self.elevation+delta.y()*.35,-89,89))
        self.update()

    def mouseReleaseEvent(self, event):
        self._drag=None
        self.unsetCursor()

    def wheelEvent(self, event):
        self.distance=float(np.clip(self.distance*math.exp(-event.angleDelta().y()/120*.15),.01,1e10))
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.cancel_requested.emit()
        elif event.key() == Qt.Key.Key_F:
            self.fit(True)
        else:
            super().keyPressEvent(event)

    def cleanup(self):
        if not self._program or not self.isValid(): return
        self.makeCurrent()
        try:
            for _,vao,vbo,_ in self._buffers.values():
                GL.glDeleteBuffers(1,[vbo]);GL.glDeleteVertexArrays(1,[vao])
            self._buffers.clear()
            if self._line_vbo: GL.glDeleteBuffers(1,[self._line_vbo])
            if self._line_vao: GL.glDeleteVertexArrays(1,[self._line_vao])
            GL.glDeleteProgram(self._program)
            self._program=None
        finally:
            self.doneCurrent()

    def _fail(self, error):
        self._error=str(error)
        self.error.emit(self._error)
