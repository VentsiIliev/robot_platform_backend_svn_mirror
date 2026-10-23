"""Best-effort observation of ordered plans; never participates in motion decisions."""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import json
import math
from threading import RLock
from uuid import uuid4


class PreviewState:
    """Immutable snapshots of one chain, including partial preplanning and failures."""
    def __init__(self, send, *, frame, tip, tool_matrix=None):
        self.send = send
        self.lock = RLock()
        self.packet = dict(version=1, plan_id=uuid4().hex, revision=0, frame_id=frame,
                           tip_frame=tip, tool_matrix=tool_matrix, phase='starting',
                           segments=[], failure=None, error='')
        self.segments = {}
        self.start_state = None
        self.trajectories = {}

    def _emit(self):
        self.packet['revision'] += 1
        joints = getattr(self.start_state,'joint_state',None)
        self.packet['start_joints'] = dict(zip(joints.name,joints.position)) if joints is not None else {}
        self.send({**self.packet, 'segments':[dict(self.segments[i]) for i in sorted(self.segments)]},
                  self.start_state, [self.trajectories[i] for i in sorted(self.trajectories)])

    def planning(self, index, segment, state):
        with self.lock:
            if self.start_state is None:
                self.start_state = state
            previous = self.segments.get(index,{})
            self.segments[index] = {**previous, 'index':int(index),
                                   'label':str(segment.get('label') or f'segment_{index+1}'),
                                   'state':'planning'}
            self._emit()

    def tool(self,matrix):
        with self.lock:
            self.packet['tool_matrix'] = matrix.tolist()

    def planned(self, index, planned):
        trajectory = planned.get('trajectory')
        # Consumed members of blended/concatenated groups have no separate path.
        if trajectory is None or not trajectory.points:
            return
        names = list(trajectory.joint_names)
        points = trajectory.points
        stride = max(1,(len(points)-1+510)//511)
        selected = list(points[::stride])
        if selected[-1] is not points[-1]:
            selected.append(points[-1])
        positions = [list(point.positions) for point in selected]
        with self.lock:
            self.trajectories[index] = trajectory
            previous = self.segments.get(index,{})
            self.segments[index] = {**previous,'index':int(index),'label':str(planned.get('label') or f'segment_{index+1}'),
                                   'state':previous.get('state') if previous.get('state') in ('executing','done','failed') else 'ready',
                                   'joint_names':names,'positions':positions,
                                   'sampled':len(selected) != len(points),
                                   'original_points':len(points)}
            self._emit()

    def failed(self, index, error, *, target=None, scope='segment'):
        with self.lock:
            # Keep a more precise member failure when a surrounding group also fails.
            if self.packet['failure'] is not None:
                return
            previous = self.segments.get(index,{'index':int(index),'label':f'segment_{index+1}'})
            self.segments[index] = {**previous,'state':'failed'}
            target = [float(v) for v in target[:3]] if target is not None else None
            if target is not None and (len(target) != 3 or not all(math.isfinite(v) for v in target)):
                target = None
            self.packet.update(phase='planning_failed',error=str(error),failure=dict(index=int(index),scope=scope,
                target_xyz_mm=target,
                location_kind='requested_target' if target is not None else 'unknown',
                exact_location=False,reason=str(error)))
            self._emit()

    def status(self, updates):
        with self.lock:
            for state in updates.get('scheduler_segment_states',[]):
                index = state['segment_index']
                if index in self.segments and state['state'] != 'PENDING':
                    self.segments[index] = {**self.segments[index], 'state':state['state'].lower()}
            phase = updates.get('phase')
            if phase:
                self.packet['phase'] = phase
            if phase in ('stopped','cancelled','discarded'):
                self.segments.clear()
                self.trajectories.clear()
                self.packet['failure'] = None
            index = updates.get('current_segment_index')
            if index is not None and index in self.segments:
                state = {'executing':'executing','segment_completed':'done','segment_failed':'failed'}.get(phase)
                if state:
                    self.segments[index] = {**self.segments[index],'state':state}
            if phase in ('failed','error','rejected','segment_failed') and self.packet['failure'] is None:
                active = [i for i,s in self.segments.items() if s.get('state') in ('executing','failed')]
                failure_index = index if index is not None else (active[-1] if active else None)
                reason = updates.get('error') or f'{phase}: result={updates.get("result")}'
                self.packet.update(error=str(reason),failure=dict(index=failure_index,scope='execution' if active else 'chain',
                    target_xyz_mm=None,location_kind='unknown',exact_location=False,reason=str(reason)))
            self._emit()


class RosPreviewTransport:
    """Coalesce latest snapshots and serialize/publish off the planning thread."""
    def __init__(self,node):
        from rclpy.qos import QoSProfile,DurabilityPolicy,ReliabilityPolicy
        from std_msgs.msg import String
        from moveit_msgs.msg import DisplayTrajectory
        qos = QoSProfile(depth=1,durability=DurabilityPolicy.TRANSIENT_LOCAL,reliability=ReliabilityPolicy.RELIABLE)
        self.node = node
        self.events = node.create_publisher(String,'/ordered_motion/preview',qos)
        self.display = node.create_publisher(DisplayTrajectory,'/ordered_motion/display_planned_path',qos)
        self.pool = ThreadPoolExecutor(max_workers=1,thread_name_prefix='ordered-preview')
        self.lock = RLock()
        self.pending = None
        self.running = False
        self.closed = False
        self.last_display_key = None
        node.context.on_shutdown(self.close)

    def close(self):
        with self.lock:
            self.closed = True
            self.pending = None
        self.pool.shutdown(wait=False,cancel_futures=True)

    def send(self,packet,start,trajectories):
        with self.lock:
            if self.closed:
                return
            self.pending = packet,start,trajectories
            if not self.running:
                self.running = True
                self.pool.submit(self._drain)

    def _drain(self):
        from std_msgs.msg import String
        from moveit_msgs.msg import DisplayTrajectory,RobotTrajectory
        while True:
            with self.lock:
                item,self.pending = self.pending,None
                if item is None:
                    self.running = False
                    return
            packet,start,trajectories = item
            try:
                self.events.publish(String(data=json.dumps(packet,allow_nan=False)))
                # Standard MoveIt display output for RViz and other consumers.
                display_key = packet['plan_id'],tuple(id(t) for t in trajectories)
                if display_key == self.last_display_key:
                    continue
                msg = DisplayTrajectory()
                if start is not None:
                    msg.trajectory_start = deepcopy(start)
                for trajectory in trajectories:
                    robot = RobotTrajectory()
                    robot.joint_trajectory = deepcopy(trajectory)
                    msg.trajectory.append(robot)
                self.display.publish(msg)
                self.last_display_key = display_key
            except Exception as exc:
                self.node.get_logger().warning(f'Ordered preview unavailable: {exc}')


class NullPreview:
    """Observation must not turn a successful plan into a motion failure."""
    def planning(self,*args,**kwargs): pass
    def planned(self,*args,**kwargs): pass
    def failed(self,*args,**kwargs): pass
    def status(self,*args,**kwargs): pass
    def tool(self,*args,**kwargs): pass


def new_preview(node,*,frame,tip,tool_matrix=None):
    try:
        transport = getattr(node,'_ordered_preview_transport',None)
        if transport is None:
            transport = RosPreviewTransport(node)
            node._ordered_preview_transport = transport
        return PreviewState(transport.send,frame=frame,tip=tip,tool_matrix=tool_matrix)
    except Exception as exc:
        node.get_logger().warning(f'Ordered preview disabled: {exc}')
        return NullPreview()


def observe(preview,method,*args,**kwargs):
    """Do not change scheduling or propagate an observation error into motion."""
    try:
        getattr(preview,method)(*args,**kwargs)
    except Exception:
        # Publishing errors are logged by the transport; malformed diagnostic data
        # must not affect the controller or the original planner exception.
        pass
