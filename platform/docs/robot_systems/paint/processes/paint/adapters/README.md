# Workpiece editor adapter

`PaintWorkpiecePathExecutor` implements `IWorkpiecePathExecutor` by composing a `PaintExecutionRuntime` and an `IPaintPreviewGeometry` provider. The editor receives this adapter; production and magazine services receive the runtime itself.

The adapter owns the editor action ID/label, supported-mode policy, and compatibility preview aliases inherited from the editor contract. Preview requests go directly to the injected provider. Approved paint actions delegate to the prepared-cycle entry point. Direct path execution remains unsupported. The adapter does not acquire hardware services or expose runtime private fields.

[Module reference](MODULES.md).

## Replacing preview behavior

Implement `IPaintPreviewGeometry` and inject it in `application_wiring.py`:

```python
path_executor = PaintWorkpiecePathExecutor(runtime, preview=CustomPreviewGeometry(...))
```

No process change is required. The default is `PaintPreviewGeometry(runtime.prepare_projection_context)`. The planning callback supplies configuration, pivot/pickup geometry, and shared transform hooks; visualization chooses the displayed paths and snapshots. Approved execution still uses the runtime regardless of the preview provider.
