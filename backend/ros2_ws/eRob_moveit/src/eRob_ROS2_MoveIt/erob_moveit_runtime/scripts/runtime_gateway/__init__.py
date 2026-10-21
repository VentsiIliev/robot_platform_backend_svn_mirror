"""Runtime contract; local backend dependencies load only when explicitly requested."""
from .base import RuntimeGateway

__all__ = ['RuntimeGateway', 'LocalRuntimeGateway']


def __getattr__(name):
    if name == 'LocalRuntimeGateway':
        from .local import LocalRuntimeGateway
        return LocalRuntimeGateway
    raise AttributeError(name)
