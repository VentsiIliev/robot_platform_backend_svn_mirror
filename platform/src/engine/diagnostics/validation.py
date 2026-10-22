"""Bounded primitive snapshots; never invoke producer object formatting hooks."""
from __future__ import annotations

import math
import re
from dataclasses import fields, is_dataclass
from enum import Enum
from pathlib import PosixPath, WindowsPath, PurePosixPath, PureWindowsPath

MAX_STRING = 4096
MAX_ITEMS = 64
MAX_NODES = 256
MAX_DEPTH = 6
MAX_CHARACTERS = 16384
_OMIT = object()
_FORMAT = re.compile(r'%(?:\([^)]{1,128}\))?[#0 +\-]*(\d+)?(?:\.(\d+))?[hlL]?[diouxXeEfFgGcrsa%]')


class InvalidObservation(ValueError):
    """Producer data is invalid; this is not a persistence failure."""


class PrimitiveSnapshot:
    def __init__(self, *, max_nodes=MAX_NODES, max_items=MAX_ITEMS,
                 max_depth=MAX_DEPTH, max_characters=MAX_CHARACTERS,
                 expand_dataclasses=False):
        self.omitted = 0
        self.nodes = 0
        self.characters = 0
        self.max_nodes, self.max_items = max_nodes, max_items
        self.max_depth, self.max_characters = max_depth, max_characters
        self.expand_dataclasses = expand_dataclasses

    def copy(self, value, depth=0):
        self.nodes += 1
        if self.nodes > self.max_nodes or depth > self.max_depth:
            self.omitted += 1
            return _OMIT
        kind = type(value)
        if isinstance(value, Enum):
            # Explicit enum adapter; never format arbitrary producer objects.
            return self.copy(object.__getattribute__(value, '_value_'), depth + 1)
        if value is None or kind is bool:
            return value
        if kind is int and value.bit_length() <= 63:
            return value
        if kind is float and math.isfinite(value):
            return value
        if kind is str:
            remaining = max(0, min(MAX_STRING, self.max_characters - self.characters))
            result = value[:remaining]
            self.characters += len(result)
            if len(result) != len(value):
                self.omitted += 1
            return result
        if self.expand_dataclasses and not isinstance(value, type) and is_dataclass(value):
            # Explicit, domain-selected dataclasses only. Copy under the same
            # budgets instead of recursively allocating an unbounded asdict first.
            result = {}
            for index, field in enumerate(fields(value)):
                if index >= self.max_items or self.nodes >= self.max_nodes:
                    self.omitted += 1
                    break
                key = self.copy(field.name, depth + 1)
                if key is _OMIT or key != field.name:
                    self.omitted += 1
                    continue
                copied = self.copy(object.__getattribute__(value, field.name), depth + 1)
                if copied is not _OMIT:
                    result[key] = copied
            return result
        if kind in (list, tuple, dict):
            result = {} if kind is dict else []
            for index, item in enumerate(value):
                if index >= self.max_items or self.nodes >= self.max_nodes:
                    self.omitted += 1
                    break
                if kind is dict:
                    if type(item) is not str or len(item) > 128:
                        self.omitted += 1
                        continue
                    key = self.copy(item, depth + 1)
                    if key is _OMIT or key != item:
                        self.omitted += 1
                        continue
                    copied = self.copy(value[item], depth + 1)
                    if copied is not _OMIT:
                        result[key] = copied
                else:
                    copied = self.copy(item, depth + 1)
                    result.append(None if copied is _OMIT else copied)
            return result
        self.omitted += 1
        return _OMIT


def identifier(value):
    if type(value) is not str or not value or len(value) > 128:
        raise InvalidObservation('invalid_identifier')
    return value


def validate_core(payload):
    """Validate all accounting inputs before any database or memory effects."""
    identifier(payload['event']) if payload.get('event') is not None else None
    if type(payload['timestamp']) is not str or len(payload['timestamp']) > 64:
        raise InvalidObservation('invalid_timestamp')
    if type(payload['level']) is not str or len(payload['level']) > 32:
        raise InvalidObservation('invalid_level')
    omitted = payload.get('omitted_fields', 0)
    if type(omitted) is not int or not 0 <= omitted <= MAX_NODES * 4:
        raise InvalidObservation('invalid_omission_count')
    metrics = payload['metrics']
    if type(metrics) is not dict or len(metrics) > MAX_ITEMS:
        raise InvalidObservation('invalid_metrics')
    for name, value in metrics.items():
        identifier(name)
        if type(value) not in (int, float) or (type(value) is int and value.bit_length() > 63):
            raise InvalidObservation('invalid_metric')
        if not math.isfinite(value) or value < 0:
            raise InvalidObservation('invalid_metric')
    transition = payload['output']
    if transition is not None:
        if type(transition) not in (tuple, list) or len(transition) != 2:
            raise InvalidObservation('invalid_output')
        identifier(transition[0])
        if transition[1] is not None and type(transition[1]) is not bool:
            raise InvalidObservation('invalid_output')
    instant = payload['monotonic']
    if type(instant) not in (float, int) or not math.isfinite(instant) or instant < 0:
        raise InvalidObservation('invalid_timestamp')


def prepare(payload):
    validate_core(payload)
    # Accounting is mandatory. Optional diagnostics cannot discard a valid OFF.
    result = {key: payload[key] for key in ('timestamp', 'level', 'event', 'monotonic')}
    result['metrics'] = dict(payload['metrics'])
    result['output'] = tuple(payload['output']) if payload['output'] is not None else None
    omitted = payload.get('omitted_fields', 0)
    # Each envelope section has its own budget. A large configuration must not
    # erase the record's actor/correlation/source or exception identity.
    for key in ('context', 'fields'):
        snapshot = PrimitiveSnapshot()
        value = payload.get(key, {})
        if type(value) is not dict:
            snapshot.omitted += 1
            value = {}
        result[key] = snapshot.copy(value)
        if result[key] is _OMIT:
            result[key] = {}
        omitted += snapshot.omitted
    for key in ('message', 'traceback', 'logger', 'thread', 'source'):
        if key in payload:
            if key == 'traceback' and payload[key] is None:
                continue
            snapshot = PrimitiveSnapshot()
            value = snapshot.copy(payload[key])
            result[key] = value if type(value) is str else '[omitted]'
            omitted += snapshot.omitted
    result['omitted_fields'] = omitted
    return result


def message_snapshot(record):
    """Support bounded primitive %-formatting, without arbitrary __str__/repr."""
    snapshot = PrimitiveSnapshot()
    if type(record.msg) is not str or len(record.msg) > MAX_STRING:
        return '[message omitted]', 1
    template = record.msg
    raw_args = record.args
    # Known standard path values are a compatibility adapter, not default=str.
    def argument(value):
        if type(value) in (PosixPath, WindowsPath, PurePosixPath, PureWindowsPath):
            return str(value)[:MAX_STRING]
        return value
    if type(raw_args) is tuple and len(raw_args) <= MAX_ITEMS:
        raw_args = tuple(argument(value) for value in raw_args)
    args = snapshot.copy(raw_args)
    if snapshot.omitted:
        return template + ' [arguments omitted]', snapshot.omitted
    for match in _FORMAT.finditer(template):
        if any(int(size) > 256 for size in match.groups() if size):
            return '[message format omitted]', 1
    # Dynamic widths may request unbounded allocations, even with small arguments.
    if '*' in template:
        return '[message format omitted]', 1
    try:
        value = template % (tuple(args) if type(args) is list else args) if record.args else template
    except (TypeError, ValueError, OverflowError):
        return '[message format invalid]', 1
    return value[:MAX_STRING], int(len(value) > MAX_STRING)


def exception_snapshot(exc_info):
    """Bounded frame metadata, no locals, file reads, or exception formatting hooks."""
    if not exc_info or exc_info[1] is None:
        return None
    _, error, frame = exc_info
    chain, seen = [], set()
    while error is not None and id(error) not in seen and len(chain) < 4:
        seen.add(id(error))
        chain.append((error, frame))
        cause = BaseException.__getattribute__(error, '__cause__')
        if cause is None and not BaseException.__getattribute__(error, '__suppress_context__'):
            cause = BaseException.__getattribute__(error, '__context__')
        error = cause
        frame = BaseException.__getattribute__(cause, '__traceback__') if cause is not None else None
    lines, summaries, frames = ['Traceback (most recent call last):'], [], 0
    for error, frame in reversed(chain):
        while frame is not None and frames < 20:
            code = frame.tb_frame.f_code
            lines.append(f'  File "{code.co_filename[:256]}", line {frame.tb_lineno}, in {code.co_name[:128]}')
            frame = frame.tb_next
            frames += 1
        args = BaseException.__getattribute__(error, 'args')
        detail = args[0][:512] if args and type(args[0]) is str else '[exception arguments omitted]'
        summaries.append(f'{type(error).__name__[:128]}: {detail}')
    # Keep exception summaries even if the bounded frame section is truncated.
    tail = '\nCaused by / propagated as: '.join(summaries)
    return '\n'.join(lines)[:MAX_STRING - len(tail) - 1] + '\n' + tail
