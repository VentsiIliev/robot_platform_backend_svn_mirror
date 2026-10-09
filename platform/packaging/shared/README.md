# Shared packaging helpers

- `release_common.py`: source identity, complete-system configuration, checksums,
  component compatibility and archive handling.
- `gitea_release.py`: authenticated Gitea publication for complete-system and
  platform-only releases.

These are imported by release commands; they are not operator entry points.
