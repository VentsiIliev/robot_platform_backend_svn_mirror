# Shared packaging helpers

- `release_common.py`: source identity, complete-system configuration, checksums,
  component compatibility and archive handling.
- `github_release.py`: current complete-system publication to GitHub, including
  exact source-tag checks, draft uploads and verified asset reuse.
- `gitea_release.py`: legacy Gitea publication implementation retained for
  compatibility/reference; Gitea is not a current publication destination.

These are imported by release commands; they are not operator entry points.
