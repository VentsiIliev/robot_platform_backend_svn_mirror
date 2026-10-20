"""Profile composition shared by launch and the runtime configuration loader."""
from .composition import load_yaml_layers, resolve_robot_description

__all__ = ['load_yaml_layers', 'resolve_robot_description']
