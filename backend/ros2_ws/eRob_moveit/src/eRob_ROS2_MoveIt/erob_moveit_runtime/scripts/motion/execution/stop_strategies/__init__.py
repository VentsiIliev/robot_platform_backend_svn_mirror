"""Named collision stop strategies. Add implementations to STRATEGIES to extend."""
from .base import StopPlan, StopStrategy
from .planned_path import PlannedPathStop
from .measured_ruckig import MeasuredRuckigStop

STRATEGIES = {
    PlannedPathStop.name: PlannedPathStop,
    MeasuredRuckigStop.name: MeasuredRuckigStop,
}


def collision_strategy_name(config):
    name = getattr(config, 'EXECUTOR_COLLISION_STOP_STRATEGY', None)
    if name is not None:
        return str(name).strip().lower()
    # Compatibility for existing external robot/profile overrides. Named setting wins.
    if bool(getattr(config, 'EXECUTOR_COLLISION_STOP_USE_MEASURED_STATE', False)):
        return MeasuredRuckigStop.name
    return PlannedPathStop.name


def create_collision_stop_strategy(config) -> StopStrategy:
    name = collision_strategy_name(config)
    try:
        implementation = STRATEGIES[name]
    except KeyError:
        raise ValueError(f'Unknown collision stop strategy {name!r}; choose from {sorted(STRATEGIES)}') from None
    return implementation(config)
