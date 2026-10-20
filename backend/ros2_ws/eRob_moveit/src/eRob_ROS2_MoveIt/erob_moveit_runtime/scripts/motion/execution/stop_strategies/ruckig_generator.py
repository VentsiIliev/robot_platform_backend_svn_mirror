"""Measured-state collision braking. Independent of the operator path-stop profile."""
import ctypes
import math
from pathlib import Path
import time
import xml.etree.ElementTree as ET


class CollisionBrake:
    def __init__(self, library_path, names, limits, lower, upper):
        self.names = tuple(names)
        self.limits = limits
        self.lower = tuple(lower)
        self.upper = tuple(upper)
        if len(self.names) != 6 or len(set(self.names)) != 6:
            raise ValueError('collision brake requires six unique joint names')
        self.library = ctypes.CDLL(str(library_path))
        self.function = self.library.erob_collision_brake
        double_ptr = ctypes.POINTER(ctypes.c_double)
        self.function.argtypes = ([double_ptr]*8 + [ctypes.c_double]*3
                                  + [double_ptr, ctypes.c_int, ctypes.c_char_p, ctypes.c_int])
        self.function.restype = ctypes.c_int

    @classmethod
    def from_config(cls, config):
        import yaml
        from ament_index_python.packages import get_package_prefix, get_package_share_directory
        import os
        share = Path(get_package_share_directory(os.environ['EROB_CONFIG_PACKAGE']))
        active = str(getattr(config, 'ACTIVE_PROFILE', '') or '')
        candidate = share/'config'/active/'joint_limits.yaml'
        if not candidate.is_file():
            candidate = share/'config/joint_limits.yaml'
        raw = yaml.safe_load(candidate.read_text())['joint_limits']
        names = tuple(config.JOINT_NAMES)
        limits = {key: tuple(float(raw[name][key]) for name in names)
                  for key in ('max_velocity', 'max_acceleration', 'max_jerk')}
        for name, amax in zip(names, limits['max_acceleration']):
            if 'max_deceleration' in raw[name]:
                decel = abs(float(raw[name]['max_deceleration']))
                if not math.isfinite(decel) or decel <= 0:
                    raise ValueError('invalid joint deceleration limit')
                index = names.index(name)
                limits['max_acceleration'] = tuple(min(value, decel) if i == index else value
                                                  for i, value in enumerate(limits['max_acceleration']))
        urdf = ET.parse(config.URDF_PATH).getroot()
        joints = {joint.get('name'): joint for joint in urdf.findall('joint')}
        lower, upper = [], []
        for name in names:
            joint = joints[name]
            if joint.get('type') == 'continuous':
                lower.append(-math.inf)
                upper.append(math.inf)
            else:
                bound = joint.find('limit')
                lower.append(float(bound.attrib['lower']))
                upper.append(float(bound.attrib['upper']))
        library = Path(get_package_prefix('erob_moveit_runtime'))/'lib/liberob_collision_brake.so'
        return cls(library, names, limits, lower, upper)

    def generate(self, state, *, max_age_s, max_duration_s, max_travel_rad, sample_period_s,
                 now=None):
        now = time.monotonic() if now is None else now
        if state is None:
            raise ValueError('complete measured velocity/acceleration samples unavailable')
        if not math.isfinite(max_age_s) or max_age_s <= 0 or not 0 <= now-state.received_at <= max_age_s:
            raise ValueError('measured joint state is stale')
        index = {name: i for i, name in enumerate(state.names)}
        if len(index) != 6 or set(index) != set(self.names):
            raise ValueError('measured joint names do not match collision brake')
        order = [index[name] for name in self.names]
        vectors = [tuple(values[i] for i in order)
                   for values in (state.position, state.velocity, state.acceleration)]
        vectors += [self.limits[key] for key in ('max_velocity', 'max_acceleration', 'max_jerk')]
        vectors += [self.lower, self.upper]
        if any(len(values) != 6 for values in vectors):
            raise ValueError('incomplete collision braking state/limits')
        arrays = [(ctypes.c_double*6)(*values) for values in vectors]
        output = (ctypes.c_double*(1024*19))()
        error = ctypes.create_string_buffer(256)
        count = self.function(*arrays, max_travel_rad, max_duration_s, sample_period_s,
                              output, 1024, error, len(error))
        if count < 2:
            raise ValueError(error.value.decode('utf-8', errors='replace'))
        return [tuple(output[row*19:(row+1)*19]) for row in range(count)]
