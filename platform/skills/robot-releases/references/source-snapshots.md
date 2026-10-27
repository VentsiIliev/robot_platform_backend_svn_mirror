# Scoped source snapshots and external dependencies

Use this reference when a local release must coexist with unrelated working
edits, or a dependency was changed outside the platform checkout.

## Isolate a local test build

1. Inspect the combined repository's status and diffs. Identify an explicit list
   of intended files/hunks with the user when scope is unclear. Include required
   new files, localization, tests and version changes. Do not include calibration,
   credentials, debug output, unrelated feature work or deleted runtime logs.
2. Choose an isolated destination with enough space. A local clone is useful when
   writing the original repository's Git metadata is restricted:

   ```bash
   git clone --local --shared /absolute/path/to/combined-checkout /absolute/path/to/release-snapshot
   ```

   A shared clone depends on the original object store. Do not treat it as a
   permanent source backup, move it to another machine, or publish from it without
   understanding that dependency. Use an independent clone for durable handoff.
3. Apply only the intended working edits to the clone. Inspect mixed files by
   hunk; never copy an unfinished feature accidentally or silently strip user
   work without resolving release scope.
4. Create an explicit local release branch. Preserve the approved backend
   version/profile while setting the new release/platform versions.
5. Reuse the tested `.venv` only when appropriate. A symlink named `.venv` may not
   match an existing `.venv/` ignore pattern. An exact local `.git/info/exclude`
   entry for this environment link is acceptable; ignoring changed source is not.
6. For component reuse, copy the existing immutable backend component directory,
   including its archive and manifest, to the snapshot's expected
   `releases/TARGET/backend/VERSION/`. Validate identity and SHA256 through the
   existing workflow. Never edit its manifest to conceal a mismatch.
7. Run targeted checks, review the scoped diff, stage the explicit paths, and
   create the local source commit required by the build gate. Confirm the entire
   snapshot is clean. The original checkout must remain untouched.
8. Follow the main skill's check/build/verify steps. After success, retain the
   archive, checksum, manifest, verification report and source/dependency
   provenance outside temporary storage. A local commit with no SVN revision
   must not be described as an official SVN-published release.

Do not switch branches, reset files or commit unrelated work in the user's
original checkout to simulate a clean build. Do not invent a new artifact
identity for already-created immutable versions.

## Include the dependency that was actually tested

For `contour_editor` and similar external packages:

1. Read the owning source repository's `AGENTS.md`. Establish whether the request
   is a local trial or an actual dependency release; their publication rules may
   differ.
2. Resolve the imported module location using the build `.venv`, inspect installed
   distribution metadata, and compare with the requested source. Editing
   `/home/ilv/contour_editor-plugin` does not automatically replace a normal
   installed package.
3. For a local trial, build a local wheel from the scoped source, install it into
   the build environment, and test the affected behavior. Record the wheel hash,
   source revision/diff and package version with the release evidence. An unchanged
   version label alone cannot identify locally modified dependency contents.
4. For an official release, use the dependency's authorized release workflow and
   an immutable reference. Update the platform's existing pinned reference in
   accordance with the owning repository's instructions. Do not silently publish
   another repository or disguise a local patched wheel as the upstream release.
5. After freezing, inspect the PyInstaller archive/TOC metadata or exercise an
   appropriate frozen check to establish that the changed modules are present.
   When useful, compare extracted code with the tested dependency while ignoring
   build-specific filenames. Keep the required frozen startup self-test too.

Do not reinstall the old dependency from `requirements.txt` after testing a local
patch and then assume the patch is in the executable. Conversely, do not claim a
build is reproducible from an old immutable pin when it used a patched local wheel.
