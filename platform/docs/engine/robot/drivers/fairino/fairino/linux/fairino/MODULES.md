# Module reference: `src/engine/robot/drivers/fairino/fairino/linux/fairino`

[Package guide](README.md) · [Complete source index](../../../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [Robot.py](#robotpy)
- [__init__.py](#__init__py)
- [setup.py](#setuppy)

## `Robot.py`

Source: [src/engine/robot/drivers/fairino/fairino/linux/fairino/Robot.py](../../../../../../../../src/engine/robot/drivers/fairino/fairino/linux/fairino/Robot.py).

Imports (including optional/function-local imports; not a startup dependency list): `Cython.Compiler.Options`, `ctypes`, `datetime`, `functools`, `hashlib`, `logging`, `logging.handlers`, `os`, `queue`, `socket`, `struct`, `sys`, `threading`, `time`, `xmlrpc.client`.

Module declarations (expressions are shown without evaluating them):

```python
is_init = False
```

### `ROBOT_AUX_STATE`

```python
class ROBOT_AUX_STATE(Structure):
```

### `EXT_AXIS_STATUS`

```python
class EXT_AXIS_STATUS(Structure):
```

### `RobotStatePkg`

```python
class RobotStatePkg(Structure):
```

### `BufferedFileHandler`

```python
class BufferedFileHandler(RotatingFileHandler):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False)
```

```python
def emit(self, record)
```

### `LogWriterThread`

```python
class LogWriterThread(threading.Thread):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, queue, log_handler)
```

```python
def run(self)
```

### `calculate_file_md5`

```python
def calculate_file_md5(file_path)
```

### `xmlrpc_timeout`

```python
def xmlrpc_timeout(func)
```

### `RobotError`

```python
class RobotError:
```

Declared fields/defaults:

```python
ERR_SUCCESS = 0
ERR_POINTTABLE_NOTFOUND = -7
ERR_SAVE_FILE_PATH_NOT_FOUND = -6
ERR_NOT_FOUND_LUA_FILE = -5
ERR_RPC_ERROR = -4
ERR_SOCKET_COM_FAILED = -2
ERR_OTHER = -1
```

### `RPC`

```python
class RPC:
```

Declared fields/defaults:

```python
ip_address = '192.168.58.2'
logger = None
log_output_model = -1
queue = Queue(maxsize=10000 * 1024)
logging_thread = None
is_conect = True
ROBOT_REALTIME_PORT = 20004
BUFFER_SIZE = 1024 * 8
thread = threading.Thread()
SDK_state = True
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, ip='192.168.58.2')
```

```python
def connect_to_robot(self)
```

连接到机器人的实时端口

```python
def reconnect(self)
```

自动重连

```python
def robot_state_routine_thread(self)
```

处理机器人状态数据包的线程例程

```python
def setup_logging(self, output_model=1, file_path='', file_num=5)
```

用于处理日志

```python
def start_logging_thread(self, log_handler)
```

创建线程进行日志存储

```python
def join_logging_thread(self)
```

通知日志线程停止

```python
def set_log_level(self, lvl)
```

设置日志记录等级

```python
def log_call(func)
```

记录函数调用的日志操作

```python
def log_debug(self, message)
```

用于记录debug等级日志

```python
def log_info(self, message)
```

用于记录info等级日志

```python
def log_warning(self, message)
```

用于记录warning等级日志

```python
def log_error(self, message)
```

用于记录errror等级日志

```python
def send_message(self, message)
```

创建tcp连接发送消息

```python
@log_call
@xmlrpc_timeout
def GetSDKVersion(self)
```

```python
@log_call
@xmlrpc_timeout
def GetControllerIP(self)
```

```python
@log_call
@xmlrpc_timeout
def Mode(self, state)
```

```python
@log_call
@xmlrpc_timeout
def DragTeachSwitch(self, state)
```

```python
@log_call
@xmlrpc_timeout
def IsInDragTeach(self)
```

```python
@log_call
@xmlrpc_timeout
def RobotEnable(self, state)
```

```python
@log_call
@xmlrpc_timeout
def StartJOG(self, ref, nb, dir, max_dis, vel=20.0, acc=100.0)
```

```python
@log_call
@xmlrpc_timeout
def StopJOG(self, ref)
```

```python
@log_call
@xmlrpc_timeout
def ImmStopJOG(self)
```

```python
@log_call
@xmlrpc_timeout
def MoveJ(self, joint_pos, tool, user, desc_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], vel=20.0, acc=0.0, ovl=100.0, exaxis_pos=[0.0, 0.0, 0.0, 0.0], blendT=-1.0, offset_flag=0, offset_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
```

```python
@log_call
@xmlrpc_timeout
def MoveL(self, desc_pos, tool, user, joint_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], vel=20.0, acc=0.0, ovl=100.0, blendR=-1.0, exaxis_pos=[0.0, 0.0, 0.0, 0.0], search=0, offset_flag=0, offset_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], overSpeedStrategy=0, speedPercent=10)
```

```python
@log_call
@xmlrpc_timeout
def MoveC(self, desc_pos_p, tool_p, user_p, desc_pos_t, tool_t, user_t, joint_pos_p=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], joint_pos_t=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], vel_p=20.0, acc_p=100.0, exaxis_pos_p=[0.0, 0.0, 0.0, 0.0], offset_flag_p=0, offset_pos_p=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], vel_t=20.0, acc_t=100.0, exaxis_pos_t=[0.0, 0.0, 0.0, 0.0], offset_flag_t=0, offset_pos_t=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ovl=100.0, blendR=-1.0)
```

```python
@log_call
@xmlrpc_timeout
def Circle(self, desc_pos_p, tool_p, user_p, desc_pos_t, tool_t, user_t, joint_pos_p=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], joint_pos_t=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], vel_p=20.0, acc_p=0.0, exaxis_pos_p=[0.0, 0.0, 0.0, 0.0], vel_t=20.0, acc_t=0.0, exaxis_pos_t=[0.0, 0.0, 0.0, 0.0], ovl=100.0, offset_flag=0, offset_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
```

```python
@log_call
@xmlrpc_timeout
def NewSpiral(self, desc_pos, tool, user, param, joint_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], vel=20.0, acc=0.0, exaxis_pos=[0.0, 0.0, 0.0, 0.0], ovl=100.0, offset_flag=0, offset_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
```

```python
@log_call
@xmlrpc_timeout
def ServoMoveStart(self)
```

```python
@log_call
@xmlrpc_timeout
def ServoMoveEnd(self)
```

```python
@log_call
@xmlrpc_timeout
def ServoJ(self, joint_pos, axisPos, acc=0.0, vel=0.0, cmdT=0.008, filterT=0.0, gain=0.0)
```

```python
@log_call
@xmlrpc_timeout
def ServoCart(self, mode, desc_pos, pos_gain=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0], acc=0.0, vel=0.0, cmdT=0.008, filterT=0.0, gain=0.0)
```

```python
@log_call
@xmlrpc_timeout
def ServoJTStart(self)
```

```python
@log_call
@xmlrpc_timeout
def ServoJT(self, torque, interval)
```

```python
@log_call
@xmlrpc_timeout
def ServoJTEnd(self)
```

```python
@log_call
@xmlrpc_timeout
def MoveCart(self, desc_pos, tool, user, vel=20.0, acc=0.0, ovl=100.0, blendT=-1.0, config=-1)
```

```python
@log_call
@xmlrpc_timeout
def SplineStart(self)
```

```python
@log_call
@xmlrpc_timeout
def SplinePTP(self, joint_pos, tool, user, desc_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], vel=20.0, acc=100.0, ovl=100.0)
```

```python
@log_call
@xmlrpc_timeout
def SplineEnd(self)
```

```python
@log_call
@xmlrpc_timeout
def NewSplineStart(self, type, averageTime=2000)
```

```python
@log_call
@xmlrpc_timeout
def NewSplinePoint(self, desc_pos, tool, user, lastFlag, joint_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], vel=0.0, acc=0.0, ovl=100.0, blendR=0.0)
```

```python
@log_call
@xmlrpc_timeout
def NewSplineEnd(self)
```

```python
@log_call
@xmlrpc_timeout
def StopMotion(self)
```

```python
@log_call
@xmlrpc_timeout
def PauseMotion(self)
```

```python
@log_call
@xmlrpc_timeout
def ResumeMotion(self)
```

```python
@log_call
@xmlrpc_timeout
def PointsOffsetEnable(self, flag, offset_pos)
```

```python
@log_call
@xmlrpc_timeout
def PointsOffsetDisable(self)
```

```python
@log_call
@xmlrpc_timeout
def SetDO(self, id, status, smooth=0, block=0)
```

```python
@log_call
@xmlrpc_timeout
def SetToolDO(self, id, status, smooth=0, block=0)
```

```python
@log_call
@xmlrpc_timeout
def SetAO(self, id, value, block=0)
```

```python
@log_call
@xmlrpc_timeout
def SetToolAO(self, id, value, block=0)
```

```python
@log_call
def GetDI(self, id, block=0)
```

```python
@log_call
def GetToolDI(self, id, block=0)
```

```python
@log_call
@xmlrpc_timeout
def WaitDI(self, id, status, maxtime, opt)
```

```python
@log_call
@xmlrpc_timeout
def WaitMultiDI(self, mode, id, status, maxtime, opt)
```

```python
@log_call
@xmlrpc_timeout
def WaitToolDI(self, id, status, maxtime, opt)
```

```python
@log_call
@xmlrpc_timeout
def GetAI(self, id, block=0)
```

```python
@log_call
@xmlrpc_timeout
def GetToolAI(self, id, block=0)
```

```python
@log_call
@xmlrpc_timeout
def GetAxlePointRecordBtnState(self)
```

```python
@log_call
@xmlrpc_timeout
def GetToolDO(self)
```

```python
@log_call
@xmlrpc_timeout
def GetDO(self)
```

```python
@log_call
@xmlrpc_timeout
def WaitAI(self, id, sign, value, maxtime, opt)
```

```python
@log_call
@xmlrpc_timeout
def WaitToolAI(self, id, sign, value, maxtime, opt)
```

```python
@log_call
@xmlrpc_timeout
def SetSpeed(self, vel)
```

```python
@log_call
@xmlrpc_timeout
def SetSysVarValue(self, id, value)
```

```python
@log_call
@xmlrpc_timeout
def SetToolPoint(self, point_num)
```

```python
@log_call
@xmlrpc_timeout
def ComputeTool(self)
```

```python
@log_call
@xmlrpc_timeout
def SetTcp4RefPoint(self, point_num)
```

```python
@log_call
@xmlrpc_timeout
def ComputeTcp4(self)
```

```python
@log_call
@xmlrpc_timeout
def SetToolCoord(self, id, t_coord, type, install, toolID, loadNum)
```

```python
@log_call
@xmlrpc_timeout
def SetToolList(self, id, t_coord, type, install, loadNum)
```

```python
@log_call
@xmlrpc_timeout
def SetExTCPPoint(self, point_num)
```

```python
@log_call
@xmlrpc_timeout
def ComputeExTCF(self)
```

```python
@log_call
@xmlrpc_timeout
def SetExToolCoord(self, id, etcp, etool)
```

```python
@log_call
@xmlrpc_timeout
def SetExToolList(self, id, etcp, etool)
```

```python
@log_call
@xmlrpc_timeout
def SetWObjCoordPoint(self, point_num)
```

```python
@log_call
@xmlrpc_timeout
def ComputeWObjCoord(self, method, refFrame)
```

```python
@log_call
@xmlrpc_timeout
def SetWObjCoord(self, id, coord, refFrame)
```

```python
@log_call
@xmlrpc_timeout
def SetWObjList(self, id, coord, refFrame)
```

```python
@log_call
@xmlrpc_timeout
def SetLoadWeight(self, weight)
```

```python
@log_call
@xmlrpc_timeout
def SetRobotInstallPos(self, method)
```

```python
@log_call
@xmlrpc_timeout
def SetRobotInstallAngle(self, yangle, zangle)
```

```python
@log_call
@xmlrpc_timeout
def SetLoadCoord(self, x, y, z)
```

```python
@log_call
@xmlrpc_timeout
def WaitMs(self, t_ms)
```

```python
@log_call
@xmlrpc_timeout
def SetAnticollision(self, mode, level, config)
```

```python
@log_call
@xmlrpc_timeout
def SetCollisionStrategy(self, strategy, safeTime=1000, safeDistance=100, safetyMargin=[10, 10, 10, 10, 10, 10])
```

```python
@log_call
@xmlrpc_timeout
def SetLimitPositive(self, p_limit)
```

```python
@log_call
@xmlrpc_timeout
def SetLimitNegative(self, n_limit)
```

```python
@log_call
@xmlrpc_timeout
def ResetAllError(self)
```

```python
@log_call
@xmlrpc_timeout
def FrictionCompensationOnOff(self, state)
```

```python
@log_call
@xmlrpc_timeout
def SetFrictionValue_level(self, coeff)
```

```python
@log_call
@xmlrpc_timeout
def SetFrictionValue_wall(self, coeff)
```

```python
@log_call
@xmlrpc_timeout
def SetFrictionValue_ceiling(self, coeff)
```

```python
@log_call
@xmlrpc_timeout
def SetFrictionValue_freedom(self, coeff)
```

```python
@log_call
@xmlrpc_timeout
def GetRobotInstallAngle(self)
```

```python
@log_call
@xmlrpc_timeout
def GetSysVarValue(self, id)
```

```python
@log_call
@xmlrpc_timeout
def GetActualJointPosDegree(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetActualJointPosRadian(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetActualJointSpeedsDegree(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetActualJointAccDegree(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetTargetTCPCompositeSpeed(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetActualTCPCompositeSpeed(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetTargetTCPSpeed(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetActualTCPSpeed(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetActualTCPPose(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetActualTCPNum(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetActualWObjNum(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetActualToolFlangePose(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetInverseKin(self, type, desc_pos, config=-1)
```

```python
@log_call
@xmlrpc_timeout
def GetInverseKinRef(self, type, desc_pos, joint_pos_ref)
```

```python
@log_call
@xmlrpc_timeout
def GetInverseKinHasSolution(self, type, desc_pos, joint_pos_ref)
```

```python
@log_call
@xmlrpc_timeout
def GetForwardKin(self, joint_pos)
```

```python
@log_call
@xmlrpc_timeout
def GetJointTorques(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetTargetPayload(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetTargetPayloadCog(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetTCPOffset(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetWObjOffset(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetJointSoftLimitDeg(self, flag=1)
```

```python
@log_call
@xmlrpc_timeout
def GetSystemClock(self)
```

```python
@log_call
@xmlrpc_timeout
def GetRobotCurJointsConfig(self)
```

```python
@log_call
@xmlrpc_timeout
def GetDefaultTransVel(self)
```

```python
@log_call
@xmlrpc_timeout
def GetRobotMotionDone(self)
```

```python
@log_call
@xmlrpc_timeout
def GetRobotErrorCode(self)
```

```python
@log_call
@xmlrpc_timeout
def GetRobotTeachingPoint(self, name)
```

```python
@log_call
@xmlrpc_timeout
def GetMotionQueueLength(self)
```

```python
@log_call
@xmlrpc_timeout
def GetRobotEmergencyStopState(self)
```

```python
@log_call
@xmlrpc_timeout
def GetSafetyStopState(self)
```

```python
@log_call
@xmlrpc_timeout
def GetSDKComState(self)
```

```python
@log_call
@xmlrpc_timeout
def GetSSHKeygen(self)
```

```python
@log_call
@xmlrpc_timeout
def SetSSHScpCmd(self, mode, sshname, sship, usr_file_url, robot_file_url)
```

```python
@log_call
@xmlrpc_timeout
def ComputeFileMD5(self, file_path)
```

```python
@log_call
@xmlrpc_timeout
def GetSoftwareVersion(self)
```

```python
@log_call
@xmlrpc_timeout
def GetSlaveHardVersion(self)
```

```python
@log_call
@xmlrpc_timeout
def GetSlaveFirmVersion(self)
```

```python
@log_call
@xmlrpc_timeout
def GetDHCompensation(self)
```

```python
@log_call
@xmlrpc_timeout
def SetTPDParam(self, name, period_ms, type=1, di_choose=0, do_choose=0)
```

```python
@log_call
@xmlrpc_timeout
def SetTPDStart(self, name, period_ms, type=1, di_choose=0, do_choose=0)
```

```python
@log_call
@xmlrpc_timeout
def SetWebTPDStop(self)
```

```python
@log_call
@xmlrpc_timeout
def SetTPDDelete(self, name)
```

```python
@log_call
@xmlrpc_timeout
def LoadTPD(self, name)
```

```python
@log_call
@xmlrpc_timeout
def GetTPDStartPose(self, name)
```

```python
@log_call
@xmlrpc_timeout
def MoveTPD(self, name, blend, ovl)
```

```python
@log_call
@xmlrpc_timeout
def LoadTrajectoryJ(self, name, ovl, opt=1)
```

```python
@log_call
@xmlrpc_timeout
def MoveTrajectoryJ(self)
```

```python
@log_call
@xmlrpc_timeout
def GetTrajectoryStartPose(self, name)
```

```python
@log_call
@xmlrpc_timeout
def GetTrajectoryPointNum(self)
```

```python
@log_call
@xmlrpc_timeout
def SetTrajectoryJSpeed(self, ovl)
```

```python
@log_call
@xmlrpc_timeout
def SetTrajectoryJForceTorque(self, ft)
```

```python
@log_call
@xmlrpc_timeout
def SetTrajectoryJForceFx(self, fx)
```

```python
@log_call
@xmlrpc_timeout
def SetTrajectoryJForceFy(self, fy)
```

```python
@log_call
@xmlrpc_timeout
def SetTrajectoryJForceFz(self, fz)
```

```python
@log_call
@xmlrpc_timeout
def SetTrajectoryJTorqueTx(self, tx)
```

```python
@log_call
@xmlrpc_timeout
def SetTrajectoryJTorqueTy(self, ty)
```

```python
@log_call
@xmlrpc_timeout
def SetTrajectoryJTorqueTz(self, tz)
```

```python
@log_call
@xmlrpc_timeout
def LoadDefaultProgConfig(self, flag, program_name)
```

```python
@log_call
@xmlrpc_timeout
def ProgramLoad(self, program_name)
```

```python
@log_call
@xmlrpc_timeout
def GetCurrentLine(self)
```

```python
@log_call
@xmlrpc_timeout
def ProgramRun(self)
```

```python
@log_call
@xmlrpc_timeout
def ProgramPause(self)
```

```python
@log_call
@xmlrpc_timeout
def ProgramResume(self)
```

```python
@log_call
@xmlrpc_timeout
def ProgramStop(self)
```

```python
@log_call
@xmlrpc_timeout
def GetProgramState(self)
```

```python
@log_call
@xmlrpc_timeout
def GetLoadedProgram(self)
```

```python
@log_call
@xmlrpc_timeout
def GetGripperConfig(self)
```

```python
@log_call
@xmlrpc_timeout
def ActGripper(self, index, action)
```

```python
@log_call
@xmlrpc_timeout
def MoveGripper(self, index, pos, vel, force, maxtime, block, type, rotNum, rotVel, rotTorque)
```

```python
@log_call
@xmlrpc_timeout
def GetGripperMotionDone(self)
```

```python
@log_call
@xmlrpc_timeout
def SetGripperConfig(self, company, device, softversion=0, bus=0)
```

```python
@log_call
@xmlrpc_timeout
def ComputePrePick(self, desc_pos, zlength, zangle)
```

```python
@log_call
@xmlrpc_timeout
def ComputePostPick(self, desc_pos, zlength, zangle)
```

```python
@log_call
@xmlrpc_timeout
def FT_GetConfig(self)
```

```python
@log_call
@xmlrpc_timeout
def FT_SetConfig(self, company, device, softversion=0, bus=0)
```

```python
@log_call
@xmlrpc_timeout
def FT_Activate(self, state)
```

```python
@log_call
@xmlrpc_timeout
def FT_SetZero(self, state)
```

```python
@log_call
@xmlrpc_timeout
def FT_SetRCS(self, ref, coord=[0, 0, 0, 0, 0, 0])
```

```python
@log_call
@xmlrpc_timeout
def FT_PdIdenCompute(self)
```

```python
@log_call
@xmlrpc_timeout
def FT_PdIdenRecord(self, tool_id)
```

```python
@log_call
@xmlrpc_timeout
def FT_PdCogIdenCompute(self)
```

```python
@log_call
@xmlrpc_timeout
def FT_PdCogIdenRecord(self, tool_id, index)
```

```python
@log_call
@xmlrpc_timeout
def FT_GetForceTorqueRCS(self)
```

```python
@log_call
@xmlrpc_timeout
def FT_GetForceTorqueOrigin(self)
```

```python
@log_call
@xmlrpc_timeout
def FT_Guard(self, flag, sensor_num, select, force_torque, max_threshold, min_threshold)
```

```python
@log_call
@xmlrpc_timeout
def FT_Control(self, flag, sensor_num, select, force_torque, gain, adj_sign, ILC_sign, max_dis, max_ang, filter_Sign=0, posAdapt_sign=0, isNoBlock=0)
```

```python
@log_call
@xmlrpc_timeout
def FT_SpiralSearch(self, rcs, ft, dr=0.7, max_t_ms=60000, max_vel=5)
```

```python
@log_call
@xmlrpc_timeout
def FT_RotInsertion(self, rcs, ft, orn, angVelRot=3, angleMax=45, angAccmax=0, rotorn=1)
```

```python
@log_call
@xmlrpc_timeout
def FT_LinInsertion(self, rcs, ft, disMax, linorn, lin_v=1.0, lin_a=1.0)
```

```python
@log_call
@xmlrpc_timeout
def FT_CalCenterStart(self)
```

```python
@log_call
@xmlrpc_timeout
def FT_CalCenterEnd(self)
```

```python
@log_call
@xmlrpc_timeout
def FT_FindSurface(self, rcs, dir, axis, disMax, ft, lin_v=3.0, lin_a=0.0)
```

```python
@log_call
@xmlrpc_timeout
def FT_ComplianceStop(self)
```

```python
@log_call
@xmlrpc_timeout
def FT_ComplianceStart(self, p, force)
```

```python
@log_call
@xmlrpc_timeout
def LoadIdentifyDynFilterInit(self)
```

```python
@log_call
@xmlrpc_timeout
def LoadIdentifyDynVarInit(self)
```

```python
@log_call
@xmlrpc_timeout
def LoadIdentifyMain(self, joint_torque, joint_pos, t)
```

```python
@log_call
@xmlrpc_timeout
def LoadIdentifyGetResult(self, gain)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorStartEnd(self, status)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorPointIORecord(self)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorPointARecord(self)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorRefPointRecord(self)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorPointBRecord(self)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorIODetect(self, max_t)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorGetTrackData(self, mode)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorTrackStart(self, status)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorTrackEnd(self)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorSetParam(self, param)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorCatchPointComp(self, cmp)
```

```python
@log_call
@xmlrpc_timeout
def ConveyorTrackMoveL(self, name, tool, wobj, vel=20, acc=100, ovl=100, blendR=-1.0)
```

```python
@log_call
@xmlrpc_timeout
def ARCStart(self, ioType, arcNum, timeout)
```

```python
@log_call
@xmlrpc_timeout
def ARCEnd(self, ioType, arcNum, timeout)
```

```python
@log_call
@xmlrpc_timeout
def WeldingSetCurrentRelation(self, currentMin, currentMax, outputVoltageMin, outputVoltageMax, AOIndex)
```

```python
@log_call
@xmlrpc_timeout
def WeldingSetVoltageRelation(self, weldVoltageMin, weldVoltageMax, outputVoltageMin, outputVoltageMax, AOIndex)
```

```python
@log_call
@xmlrpc_timeout
def WeldingGetCurrentRelation(self)
```

```python
@log_call
@xmlrpc_timeout
def WeldingGetVoltageRelation(self)
```

```python
@log_call
@xmlrpc_timeout
def WeldingSetCurrent(self, ioType, current, AOIndex, blend)
```

```python
@log_call
@xmlrpc_timeout
def WeldingSetVoltage(self, ioType, voltage, AOIndex, blend)
```

```python
@log_call
@xmlrpc_timeout
def WeaveSetPara(self, weaveNum, weaveType, weaveFrequency, weaveIncStayTime, weaveRange, weaveLeftRange, weaveRightRange, additionalStayTime, weaveLeftStayTime, weaveRightStayTime, weaveCircleRadio, weaveStationary, weaveYawAngle=0)
```

```python
@log_call
@xmlrpc_timeout
def WeaveOnlineSetPara(self, weaveNum, weaveType, weaveFrequency, weaveIncStayTime, weaveRange, weaveLeftStayTime, weaveRightStayTime, weaveCircleRadio, weaveStationary)
```

```python
@log_call
@xmlrpc_timeout
def WeaveStart(self, weaveNum)
```

```python
@log_call
@xmlrpc_timeout
def WeaveEnd(self, weaveNum)
```

```python
@log_call
@xmlrpc_timeout
def SetForwardWireFeed(self, ioType, wireFeed)
```

```python
@log_call
@xmlrpc_timeout
def SetReverseWireFeed(self, ioType, wireFeed)
```

```python
@log_call
@xmlrpc_timeout
def SetAspirated(self, ioType, airControl)
```

```python
@log_call
@xmlrpc_timeout
def GetSegmentWeldPoint(self, startPos, endPos, startDistance)
```

```python
@log_call
@xmlrpc_timeout
def SegmentWeldStart(self, startDesePos, endDesePos, startJPos, endJPos, weldLength, noWeldLength, weldIOType, arcNum, weldTimeout, isWeave, weaveNum, tool, user, vel=20.0, acc=0.0, ovl=100.0, blendR=-1.0, exaxis_pos=[0.0, 0.0, 0.0, 0.0], search=0, offset_flag=0, offset_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
```

```python
@log_call
@xmlrpc_timeout
def SegmentWeldEnd(self, ioType, arcNum, timeout)
```

```python
@log_call
@xmlrpc_timeout
def LoggerInit(self, output_model=1, file_path='', file_num=5)
```

```python
@log_call
@xmlrpc_timeout
def SetLoggerLevel(self, lvl=1)
```

```python
@log_call
@xmlrpc_timeout
def PointTableDownLoad(self, point_table_name, save_file_path)
```

```python
@log_call
@xmlrpc_timeout
def PointTableUpLoad(self, point_table_file_path)
```

```python
@log_call
@xmlrpc_timeout
def PointTableSwitch(self, point_table_name)
```

```python
@log_call
@xmlrpc_timeout
def PointTableUpdateLua(self, point_table_name, lua_file_name)
```

```python
@log_call
@xmlrpc_timeout
def LuaDownLoad(self, fileName, savePath)
```

```python
def LuaUpload(self, filePath)
```

```python
@log_call
@xmlrpc_timeout
def LuaDelete(self, fileName)
```

```python
@log_call
@xmlrpc_timeout
def GetLuaList(self)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoSetParam(self, servoId, servoCompany, servoModel, servoSoftVersion, servoResolution, axisMechTransRatio)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoGetParam(self, servoId)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoEnable(self, servoId, status)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoSetControlMode(self, servoId, mode)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoSetTargetPos(self, servoId, pos, speed, acc)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoSetTargetSpeed(self, servoId, speed, acc)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoSetTargetTorque(self, servoId, torque)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoHoming(self, servoId, mode, searchVel, latchVel, acc)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoClearError(self, servoId)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoGetStatus(self, servoId)
```

```python
@log_call
@xmlrpc_timeout
def AuxServosetStatusID(self, servoId)
```

```python
@log_call
@xmlrpc_timeout
def SetExDevProtocol(self, protocol)
```

```python
@log_call
@xmlrpc_timeout
def GetExDevProtocol(self)
```

```python
@log_call
@xmlrpc_timeout
def SetOaccScale(self, acc)
```

```python
@log_call
@xmlrpc_timeout
def MoveAOStart(self, AONum, maxTCPSpeed=1000, maxAOPercent=100, zeroZoneCmp=20)
```

```python
@log_call
@xmlrpc_timeout
def MoveAOStop(self)
```

```python
@log_call
@xmlrpc_timeout
def MoveToolAOStart(self, AONum, maxTCPSpeed=1000, maxAOPercent=100, zeroZoneCmp=20)
```

```python
@log_call
@xmlrpc_timeout
def MoveToolAOStop(self)
```

```python
@log_call
@xmlrpc_timeout
def ExtDevSetUDPComParam(self, ip, port, period, lossPkgTime, lossPkgNum, disconnectTime, reconnectEnable, reconnectPeriod, reconnectNum)
```

```python
@log_call
@xmlrpc_timeout
def ExtDevGetUDPComParam(self)
```

```python
@log_call
@xmlrpc_timeout
def ExtDevLoadUDPDriver(self)
```

```python
@log_call
@xmlrpc_timeout
def ExtDevUnloadUDPDriver(self)
```

```python
@log_call
@xmlrpc_timeout
def ExtDevUDPClientComReset(self)
```

```python
@log_call
@xmlrpc_timeout
def ExtDevUDPClientComClose(self)
```

```python
@log_call
@xmlrpc_timeout
def SetRobotPosToAxis(self, installType)
```

```python
@log_call
@xmlrpc_timeout
def SetAxisDHParaConfig(self, axisConfig, axisDHd1, axisDHd2, axisDHd3, axisDHd4, axisDHa1, axisDHa2, axisDHa3, axisDHa4)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisParamConfig(self, axisId, axisType, axisDirection, axisMax, axisMin, axisVel, axisAcc, axisLead, encResolution, axisOffect, axisCompany, axisModel, axisEncType)
```

```python
@log_call
@xmlrpc_timeout
def GetExAxisDriverConfig(self, axisId)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisSetRefPoint(self, pointNum)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisComputeECoordSys(self)
```

```python
@log_call
@xmlrpc_timeout
def SetRefPointInExAxisEnd(self, pos)
```

```python
@log_call
@xmlrpc_timeout
def PositionorSetRefPoint(self, pointNum)
```

```python
@log_call
@xmlrpc_timeout
def PositionorComputeECoordSys(self)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisActiveECoordSys(self, axisCoordNum, toolNum, coord, calibFlag)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisServoOn(self, axisID, status)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisSetHoming(self, axisID, mode, searchVel, latchVel)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisStartJog(self, axisID, direction, vel, acc, maxDistance)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisStopJog(self, axisID)
```

```python
@log_call
@xmlrpc_timeout
def SetAuxDO(self, DONum, bOpen, smooth, block)
```

```python
@log_call
@xmlrpc_timeout
def SetAuxAO(self, AONum, value, block)
```

```python
@log_call
@xmlrpc_timeout
def SetAuxDIFilterTime(self, filterTime)
```

```python
@log_call
@xmlrpc_timeout
def SetAuxAIFilterTime(self, AINum, filterTime)
```

```python
@log_call
@xmlrpc_timeout
def WaitAuxDI(self, DINum, bOpen, time, errorAlarm)
```

```python
@log_call
@xmlrpc_timeout
def WaitAuxAI(self, AINum, sign, value, time, errorAlarm)
```

```python
@log_call
@xmlrpc_timeout
def GetAuxDI(self, DINum, isNoBlock)
```

```python
@log_call
@xmlrpc_timeout
def GetAuxAI(self, AINum, isNoBlock)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisMove(self, pos, ovl)
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisSyncMoveJ(self, joint_pos, desc_pos, tool, user, exaxis_pos, vel=20.0, acc=0.0, ovl=100.0, blendT=-1.0, offset_flag=0, offset_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisSyncMoveL(self, joint_pos, desc_pos, tool, user, exaxis_pos, vel=20.0, acc=0.0, ovl=100.0, blendR=-1.0, search=0, offset_flag=0, offset_pos=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
```

```python
@log_call
@xmlrpc_timeout
def ExtAxisSyncMoveC(self, joint_pos_p, desc_pos_p, tool_p, user_p, exaxis_pos_p, joint_pos_t, desc_pos_t, tool_t, user_t, exaxis_pos_t, vel_p=20.0, acc_p=100.0, offset_flag_p=0, offset_pos_p=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], vel_t=20.0, acc_t=100.0, offset_flag_t=0, offset_pos_t=[0.0, 0.0, 0.0, 0.0, 0.0, 0.0], ovl=100.0, blendR=-1.0)
```

```python
@log_call
@xmlrpc_timeout
def WireSearchStart(self, refPos, searchVel, searchDis, autoBackFlag, autoBackVel, autoBackDis, offectFlag)
```

```python
@log_call
@xmlrpc_timeout
def WireSearchEnd(self, refPos, searchVel, searchDis, autoBackFlag, autoBackVel, autoBackDis, offectFlag)
```

```python
@log_call
@xmlrpc_timeout
def GetWireSearchOffset(self, seamType, method, varNameRef, varNameRes)
```

```python
@log_call
@xmlrpc_timeout
def WireSearchWait(self, varname)
```

```python
@log_call
@xmlrpc_timeout
def SetPointToDatabase(self, varName, pos)
```

```python
@log_call
@xmlrpc_timeout
def ArcWeldTraceControl(self, flag, delaytime, isLeftRight, klr, tStartLr, stepMaxLr, sumMaxLr, isUpLow, kud, tStartUd, stepMaxUd, sumMaxUd, axisSelect, referenceType, referSampleStartUd, referSampleCountUd, referenceCurrent)
```

```python
@log_call
@xmlrpc_timeout
def ArcWeldTraceExtAIChannelConfig(self, channel)
```

```python
@log_call
@xmlrpc_timeout
def EndForceDragControl(self, status, asaptiveFlag, interfereDragFlag, M, B, K, F, Fmax, Vmax)
```

```python
@log_call
@xmlrpc_timeout
def SetForceSensorDragAutoFlag(self, status)
```

```python
@log_call
@xmlrpc_timeout
def ForceAndJointImpedanceStartStop(self, status, impedanceFlag, lamdeDain, KGain, BGain, dragMaxTcpVel, dragMaxTcpOriVel)
```

```python
@log_call
@xmlrpc_timeout
def GetForceAndTorqueDragState(self)
```

```python
@log_call
@xmlrpc_timeout
def SetForceSensorPayload(self, weight)
```

```python
@log_call
@xmlrpc_timeout
def SetForceSensorPayloadCog(self, x, y, z)
```

```python
@log_call
@xmlrpc_timeout
def GetForceSensorPayload(self)
```

```python
@log_call
@xmlrpc_timeout
def GetForceSensorPayloadCog(self)
```

```python
@log_call
@xmlrpc_timeout
def ForceSensorAutoComputeLoad(self)
```

```python
@log_call
@xmlrpc_timeout
def ForceSensorSetSaveDataFlag(self, recordCount)
```

```python
@log_call
@xmlrpc_timeout
def ForceSensorComputeLoad(self)
```

```python
@log_call
@xmlrpc_timeout
def AxleSensorConfig(self, idCompany, idDevice, idSoftware, idBus)
```

```python
@log_call
@xmlrpc_timeout
def AxleSensorConfigGet(self)
```

```python
@log_call
@xmlrpc_timeout
def AxleSensorActivate(self, actFlag)
```

```python
@log_call
@xmlrpc_timeout
def AxleSensorRegWrite(self, devAddr, regHAddr, regLAddr, regNum, data1, data2, isNoBlock)
```

```python
@log_call
@xmlrpc_timeout
def SetOutputResetCtlBoxDO(self, resetFlag)
```

```python
@log_call
@xmlrpc_timeout
def SetOutputResetCtlBoxAO(self, resetFlag)
```

```python
@log_call
@xmlrpc_timeout
def SetOutputResetAxleDO(self, resetFlag)
```

```python
@log_call
@xmlrpc_timeout
def SetOutputResetAxleAO(self, resetFlag)
```

```python
@log_call
@xmlrpc_timeout
def SetOutputResetExtDO(self, resetFlag)
```

```python
@log_call
@xmlrpc_timeout
def SetOutputResetExtAO(self, resetFlag)
```

```python
@log_call
@xmlrpc_timeout
def SetOutputResetSmartToolDO(self, resetFlag)
```

```python
@log_call
@xmlrpc_timeout
def WeaveStartSim(self, weaveNum)
```

```python
@log_call
@xmlrpc_timeout
def WeaveEndSim(self, weaveNum)
```

```python
@log_call
@xmlrpc_timeout
def WeaveInspectStart(self, weaveNum)
```

```python
@log_call
@xmlrpc_timeout
def WeaveInspectEnd(self, weaveNum)
```

```python
@log_call
@xmlrpc_timeout
def WeldingSetProcessParam(self, id, startCurrent, startVoltage, startTime, weldCurrent, weldVoltage, endCurrent, endVoltage, endTime)
```

```python
@log_call
@xmlrpc_timeout
def WeldingGetProcessParam(self, id)
```

```python
@log_call
@xmlrpc_timeout
def SetAirControlExtDoNum(self, DONum)
```

```python
@log_call
@xmlrpc_timeout
def SetArcStartExtDoNum(self, DONum)
```

```python
@log_call
@xmlrpc_timeout
def SetWireReverseFeedExtDoNum(self, DONum)
```

```python
@log_call
@xmlrpc_timeout
def SetWireForwardFeedExtDoNum(self, DONum)
```

```python
@log_call
@xmlrpc_timeout
def SetArcDoneExtDiNum(self, DINum)
```

```python
@log_call
@xmlrpc_timeout
def SetWeldReadyExtDiNum(self, DINum)
```

```python
@log_call
@xmlrpc_timeout
def SetExtDIWeldBreakOffRecover(self, reWeldDINum, abortWeldDINum)
```

```python
@log_call
@xmlrpc_timeout
def SetCollisionDetectionMethod(self, method)
```

```python
@log_call
@xmlrpc_timeout
def SetStaticCollisionOnOff(self, status)
```

```python
@log_call
@xmlrpc_timeout
def SetPowerLimit(self, status, power)
```

```python
@log_call
@xmlrpc_timeout
def SetRobotRealtimeStateSamplePeriod(self, period)
```

```python
@log_call
@xmlrpc_timeout
def GetRobotRealtimeStateSamplePeriod(self)
```

```python
@log_call
@xmlrpc_timeout
def GetJointDriverTorque(self)
```

```python
@log_call
@xmlrpc_timeout
def GetJointDriverTemperature(self)
```

```python
@log_call
@xmlrpc_timeout
def ArcWeldTraceReplayStart(self)
```

```python
@log_call
@xmlrpc_timeout
def ArcWeldTraceReplayEnd(self)
```

```python
@log_call
@xmlrpc_timeout
def MultilayerOffsetTrsfToBase(self, pointo, pointX, pointZ, dx, dz, dry)
```

```python
@log_call
@xmlrpc_timeout
def AngularSpeedStart(self, ratio)
```

```python
@log_call
@xmlrpc_timeout
def AngularSpeedEnd(self)
```

```python
@log_call
@xmlrpc_timeout
def SoftwareUpgrade(self, filePath, block)
```

```python
@log_call
@xmlrpc_timeout
def GetSoftwareUpgradeState(self)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoSetAcc(self, acc, dec)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoSetEmergencyStopAcc(self, acc, dec)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoGetEmergencyStopAcc(self)
```

```python
@log_call
@xmlrpc_timeout
def AuxServoGetAcc(self)
```

```python
@log_call
@xmlrpc_timeout
def GetAxleCommunicationParam(self)
```

```python
@log_call
@xmlrpc_timeout
def SetAxleCommunicationParam(self, baudRate, dataBit, stopBit, verify, timeout, timeoutTimes, period)
```

```python
@log_call
@xmlrpc_timeout
def SetAxleFileType(self, type)
```

```python
@log_call
@xmlrpc_timeout
def SetAxleLuaEnable(self, enable)
```

```python
@log_call
@xmlrpc_timeout
def SetRecoverAxleLuaErr(self, enable)
```

```python
@log_call
@xmlrpc_timeout
def GetAxleLuaEnableStatus(self)
```

```python
@log_call
@xmlrpc_timeout
def SetAxleLuaEnableDeviceType(self, forceSensorEnable, gripperEnable, IOEnable)
```

```python
@log_call
@xmlrpc_timeout
def GetAxleLuaEnableDeviceType(self)
```

```python
@log_call
@xmlrpc_timeout
def GetAxleLuaEnableDevice(self)
```

```python
@log_call
@xmlrpc_timeout
def SetAxleLuaGripperFunc(self, id, func)
```

```python
@log_call
@xmlrpc_timeout
def GetAxleLuaGripperFunc(self, id)
```

```python
@log_call
@xmlrpc_timeout
def SetCtrlOpenLUAName(self, id, name)
```

```python
@log_call
@xmlrpc_timeout
def GetCtrlOpenLUAName(self)
```

```python
@log_call
@xmlrpc_timeout
def LoadCtrlOpenLUA(self, id)
```

```python
@log_call
@xmlrpc_timeout
def UnloadCtrlOpenLUA(self, id)
```

```python
@log_call
@xmlrpc_timeout
def SetCtrlOpenLuaErrCode(self, id)
```

```python
@log_call
@xmlrpc_timeout
def SlaveFileWrite(self, type, slaveID, fileName)
```

```python
@log_call
@xmlrpc_timeout
def SetSysServoBootMode(self)
```

```python
@log_call
@xmlrpc_timeout
def AxleLuaUpload(self, filePath)
```

```python
@log_call
@xmlrpc_timeout
def TractorEnable(self, enable)
```

```python
@log_call
@xmlrpc_timeout
def TractorHoming(self)
```

```python
@log_call
@xmlrpc_timeout
def TractorMoveL(self, distance, vel)
```

```python
@log_call
@xmlrpc_timeout
def TractorMoveC(self, radio, angle, vel)
```

```python
@log_call
@xmlrpc_timeout
def TractorStop(self)
```

```python
@log_call
@xmlrpc_timeout
def SetWireSearchExtDIONum(self, searchDoneDINum, searchStartDONum)
```

```python
@log_call
@xmlrpc_timeout
def SetWeldMachineCtrlModeExtDoNum(self, DONum)
```

```python
@log_call
@xmlrpc_timeout
def SetWeldMachineCtrlMode(self, mode)
```

```python
@log_call
@xmlrpc_timeout
def CloseRPC(self)
```

```python
@log_call
@xmlrpc_timeout
def SavePoint(self, name, update_allprogramfile=0)
```

```python
@log_call
@xmlrpc_timeout
def SingularAvoidStart(self, protectMode, minShoulderPos=100, minElbowPos=50, minWristPos=10)
```

```python
@log_call
@xmlrpc_timeout
def SingularAvoidEnd(self)
```

## `__init__.py`

Source: [src/engine/robot/drivers/fairino/fairino/linux/fairino/__init__.py](../../../../../../../../src/engine/robot/drivers/fairino/fairino/linux/fairino/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `setup.py`

Source: [src/engine/robot/drivers/fairino/fairino/linux/fairino/setup.py](../../../../../../../../src/engine/robot/drivers/fairino/fairino/linux/fairino/setup.py).

Imports (including optional/function-local imports; not a startup dependency list): `Cython.Build`, `distutils.core`.

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.
