"""Read-only geometry metrics in the stored workpiece coordinate units."""
from math import hypot, isfinite

def _points(contour):
    result = []
    if not isinstance(contour, (list, tuple)):
        return result
    for point in contour:
        while isinstance(point, (list, tuple)) and len(point) == 1:
            point = point[0]
        try:
            x, y = (float(point[0]), float(point[1]))
            if isfinite(x) and isfinite(y):
                result.append((x, y))
        except (TypeError, ValueError, IndexError, KeyError):
            continue
    return result

def summarize_geometry(raw):
    """Measure the outline and stored spray polylines; do not join separate paths."""
    if not isinstance(raw, dict):
        return None
    outline = _points(raw.get('contour', []))
    paths = []
    pattern = raw.get('sprayPattern', {})
    if not isinstance(pattern, dict):
        pattern = {}
    for data in (pattern.get('Contour', []), pattern.get('Fill', [])):
        if isinstance(data, dict):
            data = [data]
        if isinstance(data, list) and data:
            if isinstance(data[0], dict):
                paths.extend((_points(segment.get('contour', [])) for segment in data))
            else:
                paths.append(_points(data))
    paths = [path for path in paths if path]
    all_points = outline + [point for path in paths for point in path]
    if not all_points:
        return None
    xs, ys = zip(*all_points)
    measured_paths = paths or ([outline + outline[:1]] if len(outline) > 2 else [outline])
    length = sum((hypot(b[0] - a[0], b[1] - a[1]) for path in measured_paths for a, b in zip(path, path[1:])))
    return {'points': len(all_points), 'path_length': length, 'dimensions': f'{max(xs) - min(xs):.1f} × {max(ys) - min(ys):.1f} mm'}
