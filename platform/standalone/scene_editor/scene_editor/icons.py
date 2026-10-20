"""Small code-native editor icons, rendered at the current theme color."""
from PyQt6.QtCore import QByteArray, Qt
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer

PATHS = {
    'mate': '<path d="m3 4 7 3v10l-7 3zm18 0-7 3v10l7 3zM10 12h4m-2-2 2 2-2 2"/>',
    'cube': '<path d="m12 2 9 5v10l-9 5-9-5V7zM3 7l9 5 9-5M12 12v10"/>',
    'select': '<path d="m5 3 13 10-7 1-3 7z"/>',
    'move': '<path d="M12 2v20M2 12h20M8 6l4-4 4 4M8 18l4 4 4-4M6 8l-4 4 4 4M18 8l4 4-4 4"/>',
    'rotate': '<path d="M20 10a8 8 0 1 0-2 8M20 3v7h-7"/>',
    'origin': '<circle cx="12" cy="12" r="6"/><path d="M12 2v7m0 6v7M2 12h7m6 0h7"/>',
    'grid': '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M9 3v18m6-18v18M3 9h18M3 15h18"/>',
    'frame': '<path d="M3 9V3h6m6 0h6v6M3 15v6h6m6 0h6v-6"/>',
    'plus': '<path d="M12 4v16M4 12h16"/>',
    'file': '<path d="M5 2h9l5 5v15H5zM14 2v6h5M8 13h8m-8 4h8"/>',
    'search': '<circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/>',
    'ros': '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 4 16 4 16 0V5M4 12c0 4 16 4 16 0"/>',
    'robot': '<path d="m5 21 3-7 6-4-3-5 4-3 5 8-3 4-6 3-1 4z"/><circle cx="8" cy="14" r="2"/><circle cx="15" cy="11" r="2"/>',
    'marker': '<path d="m12 2 10 19H2zM12 8v6m0 3v1"/>',
    'upload': '<path d="M6 18H5a4 4 0 0 1-1-8 8 8 0 0 1 15-1 5 5 0 0 1 0 10h-1M12 22V11m-4 4 4-4 4 4"/>',
    'snapshot': '<path d="M3 7h5l2-3h5l2 3h4v14H3z"/><circle cx="12" cy="14" r="4"/>',
    'copy': '<rect x="8" y="8" width="13" height="13" rx="2"/><path d="M16 8V3H3v13h5"/>',
    'trash': '<path d="M3 6h18M9 6V3h6v3M5 6l1 15h12l1-15M10 10v7m4-7v7"/>',
    'undo': '<path d="M8 5 3 10l5 5M3 10h11a6 6 0 0 1 0 12"/>',
    'redo': '<path d="m16 5 5 5-5 5m5-5H10a6 6 0 0 0 0 12"/>',
    'home': '<path d="m2 11 10-9 10 9M5 9v13h14V9M9 22v-8h6v8"/>',
    'eye': '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
}


def editor_icon(name, color='#905BA9', size=24):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"><g fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">{PATHS[name]}</g></svg>'
    renderer = QSvgRenderer(QByteArray(svg.encode()))
    pixmap = QPixmap(size*2,size*2)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    pixmap.setDevicePixelRatio(2)
    return QIcon(pixmap)


def object_category(obj):
    if obj.id.startswith('robot/'):
        return 'Robot'
    if obj.collision or obj.id.startswith(('world/','attached/')):
        return 'Collision'
    if obj.id.startswith('marker/'):
        return 'Marker'
    return 'Imported' if obj.mesh.source else 'Visual'
