# Module reference: `src/applications/broker_debug`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [broker_debug_factory.py](#broker_debug_factorypy)
- [example_usage.py](#example_usagepy)

## `__init__.py`

Source: [src/applications/broker_debug/__init__.py](../../../src/applications/broker_debug/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.broker_debug.broker_debug_factory`, `src.applications.broker_debug.service.i_broker_debug_service`.

Package-level import/export surface:

```python
from src.applications.broker_debug.broker_debug_factory import BrokerDebugFactory
from src.applications.broker_debug.service.i_broker_debug_service import IBrokerDebugService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `broker_debug_factory.py`

Source: [src/applications/broker_debug/broker_debug_factory.py](../../../src/applications/broker_debug/broker_debug_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.base.application_factory`, `src.applications.base.i_application_controller`, `src.applications.base.i_application_model`, `src.applications.base.i_application_view`, `src.applications.broker_debug.controller.broker_debug_controller`, `src.applications.broker_debug.model.broker_debug_model`, `src.applications.broker_debug.service.i_broker_debug_service`, `src.applications.broker_debug.view.broker_debug_view`.

### `BrokerDebugFactory`

```python
class BrokerDebugFactory(ApplicationFactory):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self)
```

```python
def build(self, service, messaging=None, jog_service=None)
```

## `example_usage.py`

Source: [src/applications/broker_debug/example_usage.py](../../../src/applications/broker_debug/example_usage.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `logging`, `random`, `src.applications.broker_debug.broker_debug_factory`, `src.applications.broker_debug.service.broker_debug_application_service`, `src.applications.broker_debug.service.stub_broker_debug_service`, `src.engine.core.messaging_service`, `src.shared_contracts.events.vision_events`, `sys`, `threading`, `time`.

### `_simulate_traffic`

```python
def _simulate_traffic(messaging: MessagingService, stop: threading.Event) -> None
```

### `run_standalone`

```python
def run_standalone()
```
