# Paint dashboard events

`dashboard_events.py` owns the immutable live-view and message payloads plus their topics. Paint production publishes the events, and the dashboard controller subscribes and unsubscribes during its lifecycle.

The live-view payload contains pause state, optional image, and reason. Messages contain level, title, and message. The topics remain `paint/dashboard/live-view/state` and `paint/dashboard/message`.

This contract is specific to communication inside the paint system. It has only standard-library imports; it has no dependency on the engine, process implementation, or dashboard UI.

[Source](../../../../../src/robot_systems/paint/contracts/events/dashboard_events.py).
