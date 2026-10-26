"""Diagnostic line/arc refit with shared boundary points (position continuity only)."""
import copy
import math

import numpy as np
from scipy.optimize import minimize_scalar


def connect_primitives(processed, primitives, tolerance):
    result = []
    count = len(processed)
    for primitive in primitives:
        p = copy.deepcopy(primitive)
        start = p['start_idx']
        pts = processed[np.arange(start, start+p['n_pts']) % count]
        first, last = pts[0], pts[-1]
        chord = last-first
        length = float(np.linalg.norm(chord))
        if p['type'] == 'arc' and length > 1e-9:
            midpoint = (first+last)/2
            normal = np.array([-chord[1], chord[0]])/length
            initial = float((np.asarray(p['center'])-midpoint) @ normal)
            def error(offset):
                center = midpoint+offset*normal
                radius = np.linalg.norm(first-center)
                return float(np.mean((np.linalg.norm(pts-center, axis=1)-radius)**2))
            bound = max(abs(initial)*4, length*10, 1.0)
            fit = minimize_scalar(error, bounds=(-bound,bound), method='bounded')
            if not fit.success:
                raise ValueError('Endpoint-constrained arc fit failed.')
            center = midpoint+float(fit.x)*normal
            radius = float(np.linalg.norm(first-center))
            angles = np.unwrap(np.arctan2(pts[:,1]-center[1],pts[:,0]-center[0]))
            sweep = float(angles[-1]-angles[0])
            p.update(center=center.tolist(), radius=radius,
                     start_deg=math.degrees(float(angles[0])), sweep_deg=math.degrees(sweep),
                     length=abs(sweep)*radius)
            residual = np.abs(np.linalg.norm(pts-center,axis=1)-radius)
        elif p['type'] == 'line':
            p.update(p0=first.tolist(),p1=last.tolist(),length=length)
            t=np.clip((pts-first)@chord/max(length**2,1e-20),0,1)
            residual=np.linalg.norm(pts-(first+t[:,None]*chord),axis=1)
        else:
            # A single full-circle arc has no distinct boundary to constrain.
            residual=np.abs(np.linalg.norm(pts-np.asarray(p['center']),axis=1)-p['radius'])
        p['max_err']=float(residual.max())
        p['within_tol']=p['max_err'] <= tolerance
        result.append(p)
    return result


def scale_primitives(primitives, scale, origin):
    result=copy.deepcopy(primitives)
    for p in result:
        for key in ('p0','p1','center'):
            if key in p:p[key]=(np.asarray(p[key])*scale+origin).tolist()
        for key in ('radius','length','max_err'):
            if key in p:p[key]*=scale
    return result


def primitive_distances(points, primitive):
    """Exact point distances to a finite line segment or circular arc."""
    points = np.asarray(points, float)
    if primitive['type'] == 'line':
        first, last = np.asarray(primitive['p0']), np.asarray(primitive['p1'])
        chord = last-first
        t = np.clip((points-first)@chord/max(float(chord@chord), 1e-20), 0, 1)
        return np.linalg.norm(points-(first+t[:, None]*chord), axis=1)
    center = np.asarray(primitive['center'])
    radius = primitive['radius']
    start = math.radians(primitive['start_deg'])
    sweep = math.radians(primitive['sweep_deg'])
    angles = np.arctan2(points[:, 1]-center[1], points[:, 0]-center[0])
    progress = ((angles-start) * (1 if sweep >= 0 else -1)) % (2*math.pi)
    first = center+radius*np.array([math.cos(start), math.sin(start)])
    last = center+radius*np.array([math.cos(start+sweep), math.sin(start+sweep)])
    radial = np.abs(np.linalg.norm(points-center, axis=1)-radius)
    endpoints = np.minimum(np.linalg.norm(points-first,axis=1),np.linalg.norm(points-last,axis=1))
    return np.where(progress <= abs(sweep)+1e-10, radial, endpoints)


def refit_original_contour(original, processed, primitives, tolerance):
    """Refit original-point spans, splitting until every assigned vertex passes.

    Endpoints are original vertices shared by neighbouring spans. This bounds
    original-vertex distance, not tangency, reverse distance or physical accuracy.
    """
    from .decompose import fit_circle
    original = np.asarray(original, float)
    if tolerance <= 0 or len(original) < 3 or not np.isfinite(original).all():
        raise ValueError('Original contour and positive tolerance are required.')
    seeds = [processed[p['start_idx']] for p in primitives]
    boundaries = sorted(set(int(np.argmin(np.linalg.norm(original-point,axis=1))) for point in seeds))
    if len(boundaries) < 2:
        boundaries = [0, len(original)//2]
    result = []
    pending = []
    for i,a in enumerate(boundaries):
        b=boundaries[(i+1)%len(boundaries)]
        if b<=a:b+=len(original)
        pending.append((a,b))
    pending.reverse()
    while pending:
        a,b=pending.pop()
        indices=np.arange(a,b+1)%len(original)
        pts=original[indices]
        chord=pts[-1]-pts[0]
        line={'type':'line','p0':pts[0].tolist(),'p1':pts[-1].tolist(),
              'length':float(np.linalg.norm(chord))}
        candidates=[line]
        if len(pts)>=4 and np.linalg.norm(chord)>1e-9:
            circle=fit_circle(pts)
            if circle is not None:
                seed={'type':'arc','center':circle['c'].tolist(),'radius':float(circle['r']),
                      'start_idx':0,'n_pts':len(pts)}
                try:
                    arc=connect_primitives(pts,[seed],tolerance)[0]
                    if abs(arc['sweep_deg'])<=360+1e-7:
                        candidates.append(arc)
                except (ValueError,ArithmeticError,np.linalg.LinAlgError):
                    pass
        errors=[primitive_distances(pts,p) for p in candidates]
        # Prefer a line whenever it passes; otherwise the lower-error model.
        choice=0 if errors[0].max()<=tolerance else int(np.argmin([e.max() for e in errors]))
        best, error=candidates[choice], errors[choice]
        maximum=float(error.max())
        if maximum <= tolerance or b-a<=1:
            best.update(max_err=maximum,within_tol=maximum<=tolerance,
                        source_start_idx=int(a%len(original)),source_end_idx=int(b%len(original)),
                        n_pts=len(pts),acceptance_basis='assigned original contour vertices')
            result.append(best)
        else:
            split=int(np.argmax(error[1:-1]))+1
            pending.append((a+split,b))
            pending.append((a,a+split))
    return result
