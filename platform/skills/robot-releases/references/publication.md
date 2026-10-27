# SVN and GitHub publication

Read the current `AGENTS.md` Git rules before executing a publication command.
Use the user's current authorization and work branch, not a historical handoff's
permission. Preserve immutable versions, tags, releases and assets.

## Source publication

The current repository policy publishes source through
`python3 scripts/publish_changes.py`: source commit, SVN `dcommit`, then a disposable
LFS projection of the SVN-generated history to `github-svn-mirror`. The specific
helper is an allowed exception to the normal root `scripts/` search exclusion.

Do not directly push canonical git-svn `master`, push pre-dcommit history, or merge
projected mirror history into canonical SVN history. Use the helper's documented
resume modes for already-committed source and publication retries. Do not publish
to Gitea or GitLab unless the user changes the repository policy.

## Check the release publisher before using it

`packaging/robot/README.md` describes `release_robot.py publish`, but compare the
current implementation with `AGENTS.md` before executing it. At the time this
skill was updated, its `Workflow.publish()` directly pushed `HEAD` to GitHub
`master`, which conflicts with the mandatory projected-mirror policy.

Do not run a conflicting publisher or manually substitute a direct Git push.
Continue authorized artifact preparation/verification, identify the concrete
conflict, and resolve the publication path before the external mutation. Recheck
the implementation on future tasks; this note does not mean the code can never
be corrected. Do not conflate a passed local build with a completed publication.

## Artifact publication requirements

Official release artifacts must identify the actual SVN-synchronized source.
Source publication can rewrite commit identities; build after synchronization
when needed. An isolated local test build with `source_svn_revision: null` must
not be promoted as an official SVN-published artifact under a reused identity.

For the authorized, policy-compliant publisher:

1. Verify repository access and the intended destination without printing tokens.
2. Build/verify the exact component pair and check the completed report/checksum.
3. Create or verify exact component and robot tags, respecting the mirror's source
   identity rules. Never move, force-push, overwrite or delete conflicting tags.
4. Publish a draft release, upload matching archives/manifests/checksums and any
   required signatures, verify uploaded content, then make the release public.
5. On retry, reuse only identical assets and matching tags. Different bytes or
   conflicting identities require investigation or a new version.
6. Report source SVN revision, commit/mirror identity, tags, release URL and asset
   verification. If a stage fails, say what completed and what remains incomplete.

Preserve the station's configured provider and trust keys. Changing a repository
URL does not change the installed product or make incompatible components valid.
