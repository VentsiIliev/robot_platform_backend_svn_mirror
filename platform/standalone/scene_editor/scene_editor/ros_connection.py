"""Optional subprocess transport. Importing this module does not import ROS."""
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import weakref

import numpy as np
from PyQt6.QtCore import QObject, QTimer, pyqtSignal

from .geometry import Mesh, mesh_from_primitive, read_stl
from .model import Pose, Scene, SceneObject


@dataclass(frozen=True)
class RosOptions:
    fixed_frame: str = 'base_link'
    scene_topic: str = '/monitored_planning_scene'
    scene_service: str = '/get_planning_scene'
    apply_service: str = '/apply_planning_scene'
    description_topic: str = '/robot_description'
    tf_topic: str = '/tf'
    tf_static_topic: str = '/tf_static'
    marker_topics: tuple = ('/rviz_visual_tools', '/safety_walls', '/active_tool_markers')
    python: str = '/usr/bin/python3'
    ros_setup: str = ''
    workspace_setup: str = ''
    domain: int | None = None


def ros_environment(options):
    environment = dict(os.environ)
    environment.pop('PYTHONHOME', None)
    if options.domain is not None:
        environment['ROS_DOMAIN_ID'] = str(options.domain)
    return environment


def ros_command(options, helper, arguments):
    command = [options.python, '-u', '-B', str(Path(__file__).with_name(helper)), *arguments]
    if options.ros_setup or options.workspace_setup:
        setup = 'set -e; if [[ -n "$1" ]]; then source "$1" >/dev/null; fi; if [[ -n "$2" ]]; then source "$2" >/dev/null; fi; shift 2; exec "$@"'
        command = ['bash', '--noprofile', '--norc', '-c', setup, 'scene-editor',
                   options.ros_setup, options.workspace_setup, *command]
    return command


def collision_operation(options, request):
    """One explicit, bounded operation. Run in a file/IO worker, never the GUI."""
    from .collision import validate_request
    request = validate_request(request)
    arguments = ['--scene-service', options.scene_service, '--apply-service', options.apply_service,
                 '--fixed-frame', options.fixed_frame,
                 '--tf-topic', options.tf_topic, '--tf-static-topic', options.tf_static_topic]
    command = ros_command(options, 'collision_helper.py', arguments)
    try:
        completed = subprocess.run(command, input=json.dumps(request, allow_nan=False)+'\n',
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                   encoding='utf-8', errors='replace', env=ros_environment(options), timeout=25)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError('ROS operation timed out. Its result may be unknown; inspect the live scene before retrying.') from exc
    for line in reversed(completed.stdout.splitlines()):
        try:
            packet = json.loads(line)
        except ValueError:
            continue
        if isinstance(packet, dict) and packet.get('protocol') == 'scene-editor-collision-v1':
            if not packet.get('success'):
                raise RuntimeError(packet.get('message', 'MoveIt rejected the collision operation.'))
            return packet
    raise RuntimeError('ROS helper failed: '+completed.stdout[-1800:])


class RobotDescriptionUnavailable(RuntimeError):
    """No running description publisher or usable ROS environment was found."""


def resolved_robot_snapshot(options):
    """Read the running resolved URDF once and load static zero-joint visuals."""
    from .urdf import load_urdf
    command = ros_command(options,'description_helper.py',
                          ['--description-topic',options.description_topic,'--timeout','5'])
    try:
        completed = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                                   text=True,encoding='utf-8',errors='replace',
                                   env=ros_environment(options),timeout=12)
    except (subprocess.TimeoutExpired,OSError) as exc:
        raise RobotDescriptionUnavailable('Cannot read robot_description: '+str(exc)) from exc
    packet = None
    for line in reversed(completed.stdout.splitlines()):
        try:
            candidate = json.loads(line)
        except ValueError:
            continue
        if isinstance(candidate,dict) and candidate.get('protocol') == 'scene-editor-description-v1':
            packet = candidate
            break
    if packet is None:
        raise RobotDescriptionUnavailable('ROS description helper unavailable: '+completed.stdout[-1500:])
    if not packet.get('success'):
        error = RobotDescriptionUnavailable if packet.get('unavailable') else RuntimeError
        raise error(packet.get('message','Cannot resolve the running robot description.'))
    packages = packet.get('packages',{})
    def package(name):
        if name not in packages:
            raise LookupError(name)
        return packages[name]
    roots = [str(Path(options.workspace_setup).expanduser().parent)] if options.workspace_setup else []
    with tempfile.TemporaryDirectory(prefix='scene-editor-description-') as directory:
        path = Path(directory)/'robot.urdf'
        path.write_text(packet['xml'],encoding='utf-8')
        scene = load_urdf(path,package_resolver=package,search_roots=roots)
    for index,obj in enumerate(scene.objects):
        obj.id = f'robot/resolved/{index}'
    return scene


class SceneDecoder:
    def __init__(self, cache_directory):
        self.directory = Path(cache_directory).resolve()
        self.meshes = weakref.WeakValueDictionary()

    def decode(self, rows):
        scene = Scene()
        ids = set()
        for row in rows:
            geometry = row['geometry']
            key = json.dumps(geometry, sort_keys=True)
            mesh = self.meshes.get(key)
            if mesh is None:
                if 'stl' in geometry:
                    mesh = read_stl(geometry['stl'])
                elif 'primitive' in geometry:
                    mesh = mesh_from_primitive(geometry['primitive'])
                else:
                    path = Path(geometry['npy']).resolve()
                    if not path.is_relative_to(self.directory):
                        raise ValueError('ROS geometry cache path is outside the session directory')
                    mesh = Mesh(np.load(path, allow_pickle=False))
                self.meshes[key] = mesh
            obj = SceneObject(row['name'], mesh, Pose(row['translation'], row['rotation']),
                              row['unit_scale'], row['color'], id=row['id'])
            if obj.id in ids:
                raise ValueError('Duplicate ROS scene object ID')
            ids.add(obj.id)
            scene.objects.append(obj)
        return scene


class RosConnection(QObject):
    status = pyqtSignal(object)
    stopped = pyqtSignal(str)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.options = options
        self._lock = threading.Lock()
        self._latest = None
        self._process = None
        self._stop = threading.Event()
        self._thread = None

    def start(self):
        if self._thread is not None:
            raise RuntimeError('A ROS connection can only be started once')
        self._thread = threading.Thread(target=self._read, name='scene-editor-ros', daemon=True)
        self._thread.start()

    def take_latest(self):
        """Take the newest complete frame, dropping obsolete UI updates."""
        with self._lock:
            scene, self._latest = self._latest, None
        return scene

    def stop(self):
        self._stop.set()
        with self._lock:
            process = self._process
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except ProcessLookupError:
                pass
            # The UI never blocks on process shutdown.
            QTimer.singleShot(2000, self._kill_if_running)

    def _kill_if_running(self):
        with self._lock:
            process = self._process
        if process is not None and process.poll() is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass

    def _command(self, directory):
        options = self.options
        arguments = ['--cache', directory]
        for name in ('fixed_frame', 'scene_topic', 'scene_service', 'description_topic', 'tf_topic', 'tf_static_topic'):
            arguments.extend(['--'+name.replace('_', '-'), getattr(options, name)])
        arguments.extend(['--marker-topics', *options.marker_topics])
        return ros_command(options, 'ros_helper.py', arguments)

    def _read(self):
        error, logs = '', []
        try:
            with tempfile.TemporaryDirectory(prefix='scene-editor-ros-') as directory:
                decoder = SceneDecoder(directory)
                environment = ros_environment(self.options)
                if self._stop.is_set():
                    return
                process = subprocess.Popen(self._command(directory), stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, text=True, encoding='utf-8',
                                           errors='replace', bufsize=1, env=environment)
                with self._lock:
                    self._process = process
                if self._stop.is_set():
                    process.terminate()
                for line in process.stdout:
                    if self._stop.is_set():
                        continue
                    try:
                        packet = json.loads(line)
                    except json.JSONDecodeError:
                        logs.append(line.strip())
                        logs = logs[-8:]
                        continue
                    if not isinstance(packet, dict) or packet.get('protocol') != 'scene-editor-ros-v1':
                        continue
                    if packet['type'] == 'scene':
                        try:
                            scene = decoder.decode(packet['objects'])
                            scene.reference_frame = packet['fixed_frame']
                            with self._lock:
                                self._latest = scene
                        except Exception as exc:
                            self.status.emit({'type': 'warning', 'message': 'Scene geometry: '+str(exc)})
                    else:
                        if packet['type'] == 'error':
                            error = packet['message']
                        self.status.emit(packet)
                process.stdout.close()
                returncode = process.wait(timeout=3)
                if returncode and not error:
                    error = '\n'.join(logs) or f'ROS helper exited with code {returncode}'
        except Exception as exc:
            error = str(exc)
        finally:
            with self._lock:
                process = self._process
            if process is not None and process.poll() is None:
                process.kill()
                process.wait()
            self.stopped.emit('' if self._stop.is_set() else error or 'ROS helper disconnected')
