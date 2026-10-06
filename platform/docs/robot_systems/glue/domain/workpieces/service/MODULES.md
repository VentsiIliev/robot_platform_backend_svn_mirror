# Module reference: `src/robot_systems/glue/domain/workpieces/service`

[Package guide](README.md) · [Complete source index](../../../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [i_workpiece_service.py](#i_workpiece_servicepy)
- [workpiece_service.py](#workpiece_servicepy)

## `__init__.py`

Source: [src/robot_systems/glue/domain/workpieces/service/__init__.py](../../../../../../src/robot_systems/glue/domain/workpieces/service/__init__.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.robot_systems.glue.domain.workpieces.service.i_workpiece_service`, `src.robot_systems.glue.domain.workpieces.service.workpiece_service`.

Package-level import/export surface:

```python
from src.robot_systems.glue.domain.workpieces.service.i_workpiece_service import IWorkpieceService
from src.robot_systems.glue.domain.workpieces.service.workpiece_service import WorkpieceService
```

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `i_workpiece_service.py`

Source: [src/robot_systems/glue/domain/workpieces/service/i_workpiece_service.py](../../../../../../src/robot_systems/glue/domain/workpieces/service/i_workpiece_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `abc`, `typing`.

### `IWorkpieceService`

```python
class IWorkpieceService(ABC):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@abstractmethod
def save(self, workpiece) -> tuple[bool, str]
```

```python
@abstractmethod
def load(self, workpiece_id: str)
```

```python
@abstractmethod
def list_all(self) -> List[dict]
```

```python
@abstractmethod
def delete(self, workpiece_id: str) -> tuple[bool, str]
```

```python
@abstractmethod
def get_thumbnail_bytes(self, workpiece_id: str) -> Optional[bytes]
```

```python
@abstractmethod
def workpiece_id_exists(self, workpiece_id: str) -> bool
```

```python
@abstractmethod
def update(self, storage_id: str, data: dict) -> tuple[bool, str]
```

## `workpiece_service.py`

Source: [src/robot_systems/glue/domain/workpieces/service/workpiece_service.py](../../../../../../src/robot_systems/glue/domain/workpieces/service/workpiece_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `logging`, `src.applications.workpiece_editor.editor_core`, `src.engine.robot.interfaces.tool_definition`, `src.robot_systems.glue.domain.workpieces.repository.i_workpiece_repository`, `src.robot_systems.glue.domain.workpieces.service.i_workpiece_service`, `traceback`, `typing`.

### `WorkpieceService`

```python
class WorkpieceService(IWorkpieceService):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def __init__(self, repository: IWorkpieceRepository, tool_provider: Optional[Callable[[], List[ToolDefinition]]]=None)
```

```python
def save(self, workpiece) -> tuple[bool, str]
```

```python
def load(self, workpiece_id: str)
```

```python
def list_all(self) -> List[dict]
```

```python
def delete(self, workpiece_id: str) -> tuple[bool, str]
```

```python
def get_thumbnail_bytes(self, workpiece_id: str) -> Optional[bytes]
```

```python
def workpiece_id_exists(self, workpiece_id: str) -> bool
```

```python
def update(self, storage_id: str, data: dict) -> tuple[bool, str]
```
