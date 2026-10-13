# Paint preview geometry

`IPaintPreviewGeometry` is a two-method protocol for projected paths and workpiece-shape snapshots. Providers return data to the editor; they do not draw widgets or execute robot commands.

`PaintPreviewGeometry` is the default implementation. It receives a planning-context callback and uses the shared paint projection mathematics. Missing/invalid pivot poses produce empty previews as before. Pickup rotation, pivot offsets, selected-path constraints, and command-space alignment retain their existing behavior.

The editor adapter depends on the protocol. Composition in `application_wiring.py` selects the provider, so alternative visualization behavior requires no modification to production or motion execution. Process planning, operations, and workflow modules do not import visualization.

Shared source-path and anchor helpers remain in `processes/paint/planning/projection/inputs.py`, together with `PaintProjectionContext`. The runtime resolves those planning inputs but no longer generates preview paths or snapshots.

[Module reference](MODULES.md).
