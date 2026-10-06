# Module reference: `packaging/remote_support`

[Package guide](README.md) · [Complete source index](../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [build_payload.py](#build_payloadpy)

## `build_payload.py`

Source: [packaging/remote_support/build_payload.py](../../../packaging/remote_support/build_payload.py).

Stage the independent support installer for a product release bundle.

Imports (including optional/function-local imports; not a startup dependency list): `argparse`, `pathlib`, `shutil`.

### `build_payload`

```python
def build_payload(destination: Path, vendor_installer: Path | None=None) -> None
```
