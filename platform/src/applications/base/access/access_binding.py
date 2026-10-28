"""Compose authorization advice with normal UI state; keep enforcement in services."""
from dataclasses import dataclass

from .adapters import PresentationAdapter
from .contracts import (
    AccessRequirement, AccessVersion, ControlState, PresentationAccess,
)


@dataclass
class _Binding:
    adapter: PresentationAdapter
    requirement: AccessRequirement
    operational: ControlState
    access: PresentationAccess | None = None

    def apply(self) -> None:
        requirement = self.requirement
        if not requirement.protected:
            self.adapter.apply(self.operational)
            return
        access = self.access
        if access is None:
            self.adapter.apply(ControlState(False, False))
            return
        visible = self.operational.visible
        if requirement.feature:
            visible = visible and access.feature_visible
        if requirement.action:
            if requirement.hide_when_role_denied:
                visible = visible and access.role_eligible
            if requirement.hide_when_target_denied:
                visible = visible and access.action_allowed
        enabled = visible and self.operational.enabled
        if requirement.action:
            enabled = enabled and access.role_eligible and access.action_allowed
        self.adapter.apply(ControlState(visible, enabled))


class AccessBinding:
    """Controller-owned coordinator; call close() from controller.stop().

    Once bound, ordinary enabled/visible updates must use set_operational_state().
    Permission results must carry the expected session/policy/selection version.
    No service reference or role comparison is accepted here.
    """

    def __init__(self) -> None:
        self._bindings: dict[str, _Binding] = {}
        self._version: AccessVersion | None = None
        self._closed = False

    def register(
        self, key: str, adapter: PresentationAdapter,
        requirement: AccessRequirement = AccessRequirement(),
        *, operational: ControlState | None = None,
    ) -> None:
        if self._closed:
            raise RuntimeError("Access binding is closed")
        if not key or key in self._bindings:
            raise ValueError("Binding keys must be nonempty and unique")
        binding = _Binding(adapter, requirement,
                           operational if operational is not None else adapter.state())
        self._bindings[key] = binding
        binding.apply()

    def requirements(self) -> dict[str, AccessRequirement]:
        """Return declarations for controller/model permission queries."""
        return {key: binding.requirement for key, binding in self._bindings.items()}

    def invalidate(self, version: AccessVersion) -> None:
        """Call before refreshing after a session, policy, or selection change."""
        if self._closed:
            return
        self._version = version
        for binding in self._bindings.values():
            binding.access = None
            binding.apply()

    def apply_access(
        self, version: AccessVersion, states: dict[str, PresentationAccess],
    ) -> bool:
        """Reject stale batches; missing decisions deny rather than retain a grant."""
        if self._closed or self._version is None or version != self._version:
            return False
        unknown = states.keys() - self._bindings.keys()
        if unknown:
            raise ValueError("Access results contain unregistered bindings")
        for key, binding in self._bindings.items():
            binding.access = states.get(key)
            binding.apply()
        return True

    def set_operational_state(self, key: str, state: ControlState) -> None:
        if self._closed:
            return
        binding = self._bindings[key]
        binding.operational = state
        binding.apply()

    def replace_access(self, expected: AccessVersion, version: AccessVersion,
                       states: dict[str, PresentationAccess]) -> bool:
        """Atomically refresh the same session/selection without hiding allowed tabs.

        Session/selection changes still require invalidate(). Policy revisions may
        only advance. A reply based on an obsolete expected version is rejected.
        """
        if (self._closed or self._version != expected
                or (version.session_revision, version.selection_revision)
                != (expected.session_revision, expected.selection_revision)
                or version.policy_revision < expected.policy_revision):
            return False
        if states.keys() - self._bindings.keys():
            raise ValueError("Access results contain unregistered bindings")
        self._version = version
        return self.apply_access(version, states)

    def close(self) -> None:
        """Invalidate pending callbacks and release adapters before Qt teardown."""
        if self._closed:
            return
        self._closed = True
        for binding in self._bindings.values():
            binding.access = None
            binding.apply()
            binding.adapter.close()
        self._bindings.clear()
