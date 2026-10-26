"""Diagnostic periodic C2 curve and injected Paint arclength sampling."""
import json
import cv2
import numpy as np
from scipy.interpolate import CubicSpline
from .decompose import sample_primitive


def distances(points, path):
    vectors = np.diff(path, axis=0)
    squared = np.maximum(np.sum(vectors*vectors, axis=1), 1e-20)
    output = []
    for offset in range(0, len(points), 32):
        delta = points[offset:offset+32, None, :]-path[:-1]
        t = np.clip(np.sum(delta*vectors, axis=2)/squared, 0, 1)
        output.extend(np.sqrt(np.min(np.sum((delta-t[..., None]*vectors)**2, axis=2), axis=1)))
    return np.asarray(output)


def sample_tangent_path(entry, sampler):
    """Retain periodic spline coefficients; verify vertices and sampled tangents.

    C2 refers to the underlying spline, not its polyline discretization. Numerical
    minimum-speed and deviation checks are diagnostics, not motion certification.
    """
    paths = [sample_primitive(p, step=.25) for p in entry['primitives']]
    points = np.vstack(paths)
    points = points[np.r_[True, np.linalg.norm(np.diff(points,axis=0),axis=1)>1e-8]]
    if np.linalg.norm(points[-1]-points[0])<1e-8:points=points[:-1]
    if len(points)<3:raise ValueError('Not enough distinct points for a closed smooth curve.')
    points=np.vstack([points,points[0]])
    knots=np.r_[0,np.cumsum(np.linalg.norm(np.diff(points,axis=0),axis=1))]
    spline=CubicSpline(knots,points,bc_type='periodic',axis=0)
    parameter=np.linspace(0,knots[-1],max(100,int(np.ceil(knots[-1]/.05))+1))
    dense=spline(parameter)
    dense[-1]=dense[0]
    sampled=np.asarray(sampler(dense,spacing=1.0,closed=True),float)
    original=np.asarray(entry['points'],float)
    curve_error=float(distances(original,dense).max())
    sampled_error=float(distances(original,sampled).max())
    reverse_error=float(distances(dense,np.vstack([original,original[0]])).max())
    speed=float(np.linalg.norm(spline(parameter,1),axis=1).min())
    segments=np.diff(sampled,axis=0)
    lengths=np.linalg.norm(segments,axis=1)
    headings=segments/np.maximum(lengths[:,None],1e-12)
    turns=np.degrees(np.arccos(np.clip(np.sum(headings*np.roll(headings,1,axis=0),axis=1),-1,1)))
    tolerance=entry['tolerance_mm']
    return {'contour_index':entry['contour_index'], 'points':sampled.tolist(),
            'spacing_mm':1.0,'closed':True,'point_count':len(sampled),
            'curve_type':'periodic cubic spline (C2)',
            'spline_knots':knots.tolist(),'spline_coefficients':spline.c.tolist(),
            'coefficient_convention':'scipy PPoly: c[k,i]*(t-knots[i])**(3-k)',
            'original_to_curve_max_mm':curve_error,'original_to_sampled_max_mm':sampled_error,
            'curve_to_original_max_mm':reverse_error,
            'minimum_evaluated_speed':speed,'max_sampled_heading_change_deg':float(turns.max()),
            'min_segment_mm':float(lengths.min()),'max_segment_mm':float(lengths.max()),
            'tolerance_mm':tolerance,
            'status':'ok' if max(curve_error,sampled_error,reverse_error)<=tolerance and speed>1e-6 else 'outside_tolerance',
            'validation':'Distances evaluated on a 0.05 mm parameter grid; not a continuous error proof.'}


def build_sampled_result(robot_document, sampler):
    entries=[]
    for entry in robot_document['contours']:
        try:
            if entry['status']!='ok':raise ValueError('Contour decomposition is unavailable.')
            entries.append(sample_tangent_path(entry,sampler))
        except (ValueError,ArithmeticError) as exc:
            entries.append({'contour_index':entry['contour_index'],'status':'error','error':str(exc),'points':[]})
    document={'schema_version':1,'units':'mm','coordinate_space':'robot_xy_mm',
              'sampler':'Paint resample_contour_xy','contours':entries}
    canvas=np.full((700,1000,3),248,np.uint8)
    valid=[np.asarray(e['points']) for e in entries if e['points']]
    bad=sum(e['status']!='ok' for e in entries)
    cv2.putText(canvas,f'Sampled robot XY: 1 mm | periodic C2 source curve | checks failed: {bad}',
                (20,30),cv2.FONT_HERSHEY_SIMPLEX,.6,(35,35,35),1,cv2.LINE_AA)
    total = sum(e.get('point_count', 0) for e in entries)
    error = max((e.get('original_to_sampled_max_mm', 0) for e in entries), default=0)
    reverse = max((e.get('curve_to_original_max_mm', 0) for e in entries), default=0)
    cv2.putText(canvas, f'Points: {total} | original -> samples: {error:.3f} mm | curve -> original: {reverse:.3f} mm',
                (20,58),cv2.FONT_HERSHEY_SIMPLEX,.55,(35,35,35),1,cv2.LINE_AA)
    if valid:
        all_points=np.vstack(valid);lo,hi=all_points.min(0),all_points.max(0)
        scale=min(850/max(hi[0]-lo[0],1e-6),550/max(hi[1]-lo[1],1e-6));center=(lo+hi)/2
        for pts in valid:
            display=np.rint((pts-center)*[scale,-scale]+[500,340]).astype(np.int32)
            cv2.polylines(canvas,[display.reshape(-1,1,2)],True,(180,100,20),1,cv2.LINE_AA)
            for xy in display[:-1]:cv2.circle(canvas,tuple(xy),2,(20,20,180),-1)
        cv2.putText(canvas,f'X {lo[0]:.2f} .. {hi[0]:.2f} mm; Y {lo[1]:.2f} .. {hi[1]:.2f} mm; +Y up',
                    (20,670),cv2.FONT_HERSHEY_SIMPLEX,.6,(35,35,35),1,cv2.LINE_AA)
    return json.dumps(document,indent=2,allow_nan=False).encode(),canvas
