# Startup, fault recovery and shutdown

Tray release intentionally commits the placement and begins exit after commanding
vacuum off, without sensor release verification. This behavior is unchanged.

## Production lifecycle

The shared paint system requires healthy robot service state before every
RUNNING transition, including resume and manual/adjustment entry points.
Tray readiness remains an independent requirement.

Cycle failures and explicit process faults request motion halt on the hardware
worker. Fault handling preserves the current vacuum command because a workpiece
may still be held. Normal operator Stop retains its existing vacuum-off behavior.
A software halt request cannot establish that a disconnected controller stopped;
failed hardware commands remain errors in the process log.

System shutdown prevents further paint starts, signals cancellation, requests
halt, and waits up to five seconds for production and hardware-stop workers,
without holding the process state lock. Only after these workers finish does the
system disable the robot and close dependencies. Disable is attempted even if
the final halt request raises.

If workers miss the deadline, `ShutdownPendingError` leaves managed resources
owned by the system. A subsequent `stop()` retries shutdown. A blocked driver
cannot be killed safely by Python; station-level shutdown must handle this
reported failure rather than assuming transport cleanup completed.

## Startup rollback

A service builder transfers ownership when it returns. If a later builder or
system constructor fails, completed services are closed in reverse build order.
A builder that allocates and then raises remains responsible for its own partial
allocation.

`BaseRobotSystem.start()` rolls back failed injection or startup, including
services not yet registered by `on_start()`. Custom cleanup ownership is honored
so a resource delegated to a worker is not closed twice. Runtime resources must
be registered before starting them. The original startup exception is preserved
if cleanup also fails.

## Operator lights

Mappings must cover all process states before startup. Failed writes retain the
desired indication and retry after 0.25 seconds, doubling up to five seconds.
A new process state supersedes a pending retry immediately. Failures publish a
localized, deduplicated notification on each retry so subscribers created after
startup can receive it; successful recovery dismisses it.

`is_healthy()` and `last_error` are cached, nonblocking diagnostics. Healthy means
the requested writes succeeded, not physical lamp feedback. Partial successful
writes can leave mixed indications until retry succeeds.

The coordinator worker owns both output writes and transport closure. `stop()`
waits at most two seconds. If the worker is blocked, shutdown reports a timeout
and other managed cleanup can proceed; the light transport closes on that same
worker when the outstanding call returns. No other thread closes it underneath
a write. A permanently blocked driver can therefore retain this resource until
process exit.

## Composition boundaries

The paint system constructs one `PlateLayoutService` and injects it into the
executor, production service and dashboard. Drop-off state handlers call public
production methods, backed by the `IDropoffStrategy` protocol and `DropoffResult`.
Mutable unwind and prepositioning bookkeeping stays inside the executor.

Regression tests cover delayed workers, rollback, delegated cleanup, transient
light failures, retry supersession, fault halt/vacuum policy and unavailable
robot service. Physical commissioning must still check controller stop behavior
and held-part recovery on the installed machine.
