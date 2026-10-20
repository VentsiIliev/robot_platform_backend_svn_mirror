"""STL and primitive geometry, independent of Qt and robot software."""
from dataclasses import dataclass, field
from pathlib import Path
import os
import struct
import tempfile

import numpy as np

_STL_RECORD = np.dtype([('normal', '<f4', (3,)), ('vertices', '<f4', (3, 3)), ('attribute', '<u2')])


@dataclass(eq=False)
class Mesh:
    vertices: np.ndarray
    source: Path | None = None
    primitive: dict | None = None
    normals: np.ndarray = field(init=False, repr=False)
    bounds: np.ndarray = field(init=False)

    def __post_init__(self):
        self.vertices = np.asarray(self.vertices, dtype=np.float32)
        if self.vertices.ndim != 3 or self.vertices.shape[1:] != (3, 3) or not len(self.vertices):
            raise ValueError('A mesh must contain triangles with three XYZ vertices.')
        if not np.isfinite(self.vertices).all():
            raise ValueError('Mesh coordinates must be finite numbers.')
        self.bounds = np.array([self.vertices.min(axis=(0, 1)), self.vertices.max(axis=(0, 1))], dtype=np.float64)
        self.normals = np.cross(self.vertices[:, 1] - self.vertices[:, 0], self.vertices[:, 2] - self.vertices[:, 0])
        lengths = np.linalg.norm(self.normals, axis=1)
        valid = lengths > 1e-20
        self.normals[valid] /= lengths[valid, None]
        self.normals[~valid] = 0
        self.vertices.flags.writeable = False
        self.normals.flags.writeable = False

    def gpu_data(self):
        data = np.empty((len(self.vertices), 3, 6), dtype=np.float32)
        data[:, :, :3] = self.vertices
        data[:, :, 3:] = self.normals[:, None, :]
        return data


def read_stl(path):
    path = Path(path).resolve()
    with path.open('rb') as stream:
        header = stream.read(84)
        count = struct.unpack('<I', header[80:84])[0] if len(header) == 84 else 0
        if count and path.stat().st_size == 84 + count * 50:
            records = np.fromfile(stream, dtype=_STL_RECORD, count=count)
            return Mesh(np.ascontiguousarray(records['vertices']), source=path)
    vertices = []
    try:
        with path.open('r', encoding='ascii') as stream:
            if not stream.readline().lstrip().lower().startswith('solid'):
                raise ValueError('The file is neither a valid binary STL nor an ASCII STL.')
            for line in stream:
                parts = line.split()
                if parts and parts[0].lower() == 'vertex':
                    if len(parts) != 4:
                        raise ValueError('Invalid STL vertex record.')
                    vertices.append([float(value) for value in parts[1:]])
    except UnicodeError as exc:
        raise ValueError(f'Invalid or truncated STL: {path.name}') from exc
    if not vertices or len(vertices) % 3:
        raise ValueError('An STL must contain complete triangles.')
    return Mesh(np.asarray(vertices, dtype=np.float32).reshape(-1, 3, 3), source=path)


def make_box(size):
    size = np.asarray(size, dtype=float)
    if size.shape != (3,) or not np.isfinite(size).all() or (size <= 0).any():
        raise ValueError('Box dimensions must be three positive values in mm.')
    points = np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]], dtype=np.float32) * size / 2
    indices = [[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[3,7,6],[3,6,2],[0,4,7],[0,7,3],[1,2,6],[1,6,5]]
    return Mesh(points[indices], primitive={'kind': 'box', 'size_mm': size.tolist()})


def make_cylinder(radius, length, segments=48):
    radius, length = float(radius), float(length)
    if not np.isfinite([radius, length]).all() or radius <= 0 or length <= 0:
        raise ValueError('Cylinder radius and length must be positive values in mm.')
    angles = np.arange(segments) * (2 * np.pi / segments)
    bottom = np.column_stack((radius * np.cos(angles), radius * np.sin(angles), np.full(segments, -length/2)))
    top = bottom.copy(); top[:, 2] = length/2
    triangles = []
    for index in range(segments):
        other = (index + 1) % segments
        triangles += [[bottom[index], bottom[other], top[other]], [bottom[index], top[other], top[index]],
                      [[0,0,-length/2], bottom[other], bottom[index]], [[0,0,length/2], top[index], top[other]]]
    return Mesh(np.asarray(triangles), primitive={'kind': 'cylinder', 'radius_mm': radius, 'length_mm': length})


def make_sphere(radius, rings=20, segments=40):
    radius = float(radius)
    if not np.isfinite(radius) or radius <= 0:
        raise ValueError('Sphere radius must be positive.')
    points = []
    for latitude in np.linspace(-np.pi/2, np.pi/2, rings + 1):
        points.append([[radius*np.cos(latitude)*np.cos(angle), radius*np.cos(latitude)*np.sin(angle), radius*np.sin(latitude)]
                       for angle in np.arange(segments)*2*np.pi/segments])
    points = np.asarray(points)
    triangles = []
    for row in range(rings):
        for col in range(segments):
            other = (col+1) % segments
            if row: triangles.append([points[row,col],points[row,other],points[row+1,col]])
            if row < rings-1: triangles.append([points[row,other],points[row+1,other],points[row+1,col]])
    return Mesh(np.asarray(triangles), primitive={'kind': 'sphere', 'radius_mm': radius})


def mesh_from_primitive(spec):
    kind = spec.get('kind')
    if kind == 'box': return make_box(spec['size_mm'])
    if kind == 'cylinder': return make_cylinder(spec['radius_mm'], spec['length_mm'])
    if kind == 'sphere': return make_sphere(spec['radius_mm'])
    raise ValueError(f'Unknown primitive: {kind}')


def export_stl(mesh, matrix, destination):
    """Bake the full transform into a new binary STL in mm, retaining every face."""
    destination = Path(destination).resolve()
    if mesh.source is not None and destination == mesh.source.resolve():
        raise ValueError('Export to a new file so the source STL stays unchanged.')
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (4, 4) or not np.isfinite(matrix).all():
        raise ValueError('Invalid export transform.')
    descriptor, temporary = tempfile.mkstemp(prefix='.stl-', dir=destination.parent)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            stream.write(b'Standalone Scene Editor - coordinates in millimeters'.ljust(80, b' '))
            stream.write(struct.pack('<I', len(mesh.vertices)))
            for start in range(0, len(mesh.vertices), 100_000):
                vertices = mesh.vertices[start:start+100_000].astype(np.float64)
                vertices = vertices @ matrix[:3,:3].T + matrix[:3,3]
                normals = np.cross(vertices[:,1]-vertices[:,0], vertices[:,2]-vertices[:,0])
                lengths = np.linalg.norm(normals, axis=1)
                good = lengths > 1e-20
                normals[good] /= lengths[good,None]
                normals[~good] = 0
                records = np.zeros(len(vertices), dtype=_STL_RECORD)
                records['vertices'], records['normal'] = vertices, normals
                stream.write(records.tobytes())
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)
