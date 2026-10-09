# Installed runtime tools

`manage.py` is copied into installed `tools/` directories by both packaging
workflows. It provides installation, launch, update-service, recovery and rollback
commands using the system Python. The update implementation lives in
`src/engine/updates/`. Installed filenames and archive paths remain stable.

See [complete robot operation](../robot/README.md) and
[platform-only operation](../platform/README.md).
