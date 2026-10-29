# Paint dashboard events

`dashboard_events.py` owns the immutable live-view and message payloads plus their topics. Paint production publishes the events, and the dashboard controller subscribes and unsubscribes during its lifecycle.

The live-view payload contains pause state, optional image, and reason. Messages contain level, title, and message. The topics remain `paint/dashboard/live-view/state` and `paint/dashboard/message`.

This contract is specific to communication inside the paint system. It has only standard-library imports; it has no dependency on the engine, process implementation, or dashboard UI.

[Source](../../../../../src/robot_systems/paint/contracts/events/dashboard_events.py).

## Paint-head status and replay

`paint_head_check_events.py` defines `PaintHeadCheckTopics.STATUS`
(`paint/head-check/status`) and `REQUEST_STATUS`
(`paint/head-check/request-status`). The runtime dashboard observer publishes
immutable `PaintHeadCheckStatusEvent` values and replays its latest snapshot when
the dashboard loads. Consumers use increasing `revision` values to reject stale
delivery.

Events carry typed observation/failure evidence, optional previous observation
and `PaintHeadFeedbackMode`: CHECK, LIVE_GUIDANCE or GUIDANCE_ENDED. A CHECK failure
can preserve the last head state while displaying a separate acquisition notice.
LIVE_GUIDANCE failures clear correction cues rather than presenting old directions
as current. GUIDANCE_ENDED invalidates live feedback. The contract contains no Qt,
camera images or detector result types; it imports paint-domain values from
`contracts/paint_head_check/`.

See the [integration guide](../../paint_head_check/README.md) for lifecycle and
popup behavior. The dashboard bridges background events into Qt and pairs
subscriptions with unsubscriptions on stop.
