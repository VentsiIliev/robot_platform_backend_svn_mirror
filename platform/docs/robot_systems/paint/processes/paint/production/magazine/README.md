# Magazine production support

`service.py` coordinates magazine capture positions, pickup/release targeting, and navigation recovery. `nesting.py` owns thread-safe work-area placement reservations and commit/cancel state. `outcomes.py` retains the established exhaustion/absence messages used by existing compatibility paths.

Work-area nesting belongs here because it owns reservation state for magazine transfers rather than providing only a geometry calculation.

[Module reference](MODULES.md).
