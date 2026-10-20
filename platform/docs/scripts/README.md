# `scripts/` — Maintenance and diagnostic runners

This directory contains calibration migration, machine probes, dependency/package checks, asset/configuration tools and the paint shaft-alignment proving runner. These are explicit development/maintenance entry points, not automatically loaded GUI applications.

[Publish changes to SVN and GitHub](publish_changes.md) documents `publish_changes.py`, which stages/commits on `master`, runs `git svn dcommit`, then publishes an LFS projection of SVN history to GitHub without rewriting the git-svn checkout. It supports dry runs and publication retries without another commit.

The [module reference](MODULES.md) records every directly contained Python tool, arguments represented by functions/classes, imports and source descriptions. Subdirectory guides cover shared helpers and multi-file runners. Also see the source-owned [servo pickup runner guide](../../scripts/test_servo_pickup_procedure.md) and [shaft alignment runner guide](../../scripts/paint_shaft_alignment/README.md).

Read a tool's `main()`/argument parser before running it. Some runners communicate with live robots, move hardware, or write calibration/settings data; importing or compiling their source for documentation does not validate their hardware behavior. Migration tools should operate on an explicitly chosen system/profile and reviewed data copy.

Relevant script regression tests live in [tests/scripts](../tests/scripts/README.md). Shared production abstractions belong in `engine`, while machine-specific composition belongs in `robot_systems`; scripts may assemble them for diagnostics.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

[Resource reference](RESOURCES.md) — non-Python files and their formats; values remain in the owning storage/source files.

| Source subdirectory | Guide |
|---|---|
| `paint_shaft_alignment/` | [paint_shaft_alignment](paint_shaft_alignment/README.md) |

[Complete source index](../SOURCE_INDEX.md).
<!-- source-navigation:end -->
