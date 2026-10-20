#!/usr/bin/env python3
"""Run directly: python standalone/scene_editor/run.py [scene.scene.json]."""
import argparse
import sys

from PyQt6.QtGui import QSurfaceFormat
from PyQt6.QtWidgets import QApplication

from scene_editor.window import EditorWindow


def main():
    parser = argparse.ArgumentParser(description='Independent local 3D scene editor')
    parser.add_argument('scene', nargs='?', help='Scene JSON file to open')
    args = parser.parse_args()
    surface = QSurfaceFormat()
    surface.setVersion(3, 3)
    surface.setProfile(QSurfaceFormat.OpenGLContextProfile.CoreProfile)
    surface.setDepthBufferSize(24)
    QSurfaceFormat.setDefaultFormat(surface)
    app = QApplication(sys.argv[:1])
    app.setApplicationName('Scene Editor')
    app.setOrganizationName('Local Tools')
    window = EditorWindow()
    window.show()
    if args.scene:
        window.open_path(args.scene)
    return app.exec()


if __name__ == '__main__':
    sys.exit(main())
