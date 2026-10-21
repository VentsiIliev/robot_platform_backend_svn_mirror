"""Strict parsers for control switches and general-purpose I/O."""
from dataclasses import dataclass


def boolean_field(data: dict | None, name: str) -> bool:
    if not isinstance(data, dict) or type(data.get(name)) is not bool:
        raise ValueError(f'{name} must be a boolean')
    return data[name]


def identifier(value, label='id') -> int:
    if isinstance(value, bool):
        raise ValueError(f'{label} must be a non-negative integer')
    if isinstance(value, str) and value.isascii() and value.isdigit():
        value = int(value)
    if type(value) is not int or value < 0:
        raise ValueError(f'{label} must be a non-negative integer')
    return value


@dataclass(frozen=True)
class DigitalOutputRequest:
    port: int
    value: int

    @classmethod
    def parse(cls, data: dict | None):
        if not isinstance(data, dict) or 'port' not in data or 'value' not in data:
            raise ValueError('port and value are required')
        port = identifier(data['port'], 'port')
        value = identifier(data['value'], 'value')
        if value not in (0, 1):
            raise ValueError('value must be 0 or 1')
        return cls(port, value)
