"""Qt attributes required before lazy web-backed views can be imported."""
from PyQt6.QtCore import QCoreApplication, Qt


def prepare_qt_application() -> None:
    """Call before QApplication construction, including hardware-free self-tests."""
    QCoreApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
