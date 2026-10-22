"""Admission before copying optional artifacts; reservations include running jobs."""
from __future__ import annotations

import threading


class WorkBudget:
    def __init__(self, *, max_jobs: int, max_units: int):
        if max_jobs <= 0 or max_units <= 0:
            raise ValueError('Work limits must be positive')
        self._max_jobs = max_jobs
        self._max_units = max_units
        self._jobs = 0
        self._units = 0
        self._lock = threading.Lock()

    def reserve(self, units: int):
        if type(units) is not int:
            raise ValueError('Work units must be an integer')
        with self._lock:
            if units < 0 or self._jobs >= self._max_jobs or self._units + units > self._max_units:
                return None
            self._jobs += 1
            self._units += units
        return _Reservation(self, units)

    @property
    def status(self):
        with self._lock:
            return {'jobs': self._jobs, 'units': self._units}


class _Reservation:
    def __init__(self, budget, units):
        self._budget = budget
        self._units = units
        self._released = False

    def release(self, _future=None):
        with self._budget._lock:
            if not self._released:
                self._released = True
                self._budget._jobs -= 1
                self._budget._units -= self._units
