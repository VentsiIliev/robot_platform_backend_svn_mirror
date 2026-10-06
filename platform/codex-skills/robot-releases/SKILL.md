---
name: robot-releases
description: Continue this repository's combined platform/backend release packaging, installation, launch binding, or per-system paint override work using the recorded handoff. Use for these deployment tasks, not general robot motion or calibration changes.
---

# Robot release work

Read [references/handoff.md](references/handoff.md) before continuing deployment or
paint-profile override work. It records the repository locations, implemented
contracts, known installation-path confusion, verified results, and remaining work.
Treat its dated state as a starting point: inspect current source, configuration,
Git status, installed manifests, and artifacts before changing anything.

Read the repository's `platform/AGENTS.md` for architecture and Git rules, and
`deployment/README.md` for release usage. Keep release selection in
`platform/config/platform.json`; do not recreate a separate backend-target registry.

Preserve exact version pins and existing release archives/tags. Use hardware-free
self-tests for packaging checks; a normal GUI launch can enable drives and access
hardware. Historical commit/upload authorization is not permission for a new
external publication or unrelated change.
