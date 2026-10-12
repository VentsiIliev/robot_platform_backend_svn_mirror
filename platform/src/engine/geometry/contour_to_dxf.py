"""Export image-space XY contours as closed CAD polylines."""
from pathlib import Path
import os
import tempfile

import ezdxf
from ezdxf import units, zoom
import numpy as np


def write_contour_dxf(path, contour, mm_per_pixel=None) -> Path:
    """Write a new DXF from an Nx2 or OpenCV Nx1x2 image contour.

    Coordinates are translated to the lower-left corner and Y is inverted
    to point upwards. A positive mm_per_pixel declares millimetre units;
    None preserves pixel distances and declares unitless coordinates.
    The input is unchanged and an existing destination is never overwritten.
    """
    scale = 1.0 if mm_per_pixel is None else float(mm_per_pixel)
    if not np.isfinite(scale) or scale <= 0:
        raise ValueError('Scale must be finite and positive')
    xy = np.asarray(contour, dtype=float)
    if xy.ndim == 3 and xy.shape[1:] == (1, 2):
        xy = xy[:, 0, :]
    if xy.ndim != 2 or xy.shape[1] != 2 or len(xy) < 3:
        raise ValueError('Contour must contain at least three XY points')
    if not np.isfinite(xy).all():
        raise ValueError('Contour coordinates must be finite')
    # Closed polylines do not need zero-length segments or a repeated endpoint.
    xy = xy[np.r_[True, np.any(np.diff(xy, axis=0) != 0, axis=1)]]
    if np.array_equal(xy[0], xy[-1]):
        xy = xy[:-1]
    if len(np.unique(xy, axis=0)) < 3:
        raise ValueError('Contour must contain at least three distinct points')
    origin = np.array([xy[:, 0].min(), xy[:, 1].max()])
    cad_xy = (xy - origin) * np.array([scale, -scale])
    if not np.isfinite(cad_xy).all():
        raise ValueError('Scaled contour coordinates must be finite')
    twice_area = np.sum(cad_xy[:, 0] * np.roll(cad_xy[:, 1], -1) -
                        cad_xy[:, 1] * np.roll(cad_xy[:, 0], -1))
    if not np.isfinite(twice_area) or twice_area == 0:
        raise ValueError('Contour must enclose a nonzero area')

    document = ezdxf.new('R2000', units=0 if mm_per_pixel is None else units.MM)
    document.layers.new('CONTOUR', dxfattribs={'color': 3})
    document.modelspace().add_lwpolyline(cad_xy, close=True, dxfattribs={'layer': 'CONTOUR', 'color': 3})
    document.header['$MEASUREMENT'] = 1
    document.header['$LUNITS'] = 2
    document.header['$LUPREC'] = 4
    document.header['$INSBASE'] = (0, 0, 0)
    zoom.extents(document.modelspace(), factor=1.15)
    destination = Path(path)
    if destination.suffix.lower() != '.dxf':
        destination = destination.with_suffix('.dxf')
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='ascii', suffix='.dxf',
                                         dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            document.write(stream)
            stream.flush()
            os.fsync(stream.fileno())
        # Verify the serialized file, not just the in-memory document.
        reopened = ezdxf.readfile(temporary)
        audit = reopened.audit()
        if audit.has_errors or audit.has_fixes:
            raise ValueError('DXF validation failed: file requires repairs')
        entities = list(reopened.modelspace())
        if (len(entities) != 1 or entities[0].dxftype() != 'LWPOLYLINE'
                or not entities[0].closed
                or reopened.units != document.units
                or not np.allclose(np.asarray(entities[0].get_points('xy')), cad_xy,
                                   rtol=1e-12, atol=1e-9)):
            raise ValueError('DXF validation failed: exported contour differs from capture')
        # Publish the validated file atomically without replacing an existing file.
        os.link(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination
