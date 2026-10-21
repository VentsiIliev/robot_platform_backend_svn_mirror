"""Four gateway-backed APIs with a backwards-compatible RuntimeApi facade."""
from .contracts import ApiResponse

__all__ = ['ApiResponse', 'RuntimeApi']


def __getattr__(name):
    if name == 'RuntimeApi':
        from .handlers import RuntimeApi
        return RuntimeApi
    raise AttributeError(name)
