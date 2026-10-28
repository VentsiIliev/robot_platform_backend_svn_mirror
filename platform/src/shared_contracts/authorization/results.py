"""A service either returns a value or a business failure, never both."""
from dataclasses import dataclass
from typing import Generic, TypeAlias, TypeVar

from .errors import ServiceError

T = TypeVar("T")


@dataclass(frozen=True)
class Success(Generic[T]):
    value: T


@dataclass(frozen=True)
class Failure:
    error: ServiceError


Result: TypeAlias = Success[T] | Failure
