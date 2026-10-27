# Deliver a verified combined release on a LAN feed

This route serves already verified archives; it does not publish source or GitHub
releases. Use it when the station is configured for a trusted LAN/test feed and
the user has authorized that delivery. Infer an already-established destination;
ask if the destination or network exposure is new or unclear.

## 1. Identify the machine's actual source

For a combined installation, the normal paths on the **target machine** are:

```text
~/.local/share/robot-releases/TARGET/current/manifest.json
~/.local/share/robot-releases/TARGET/updates.json
```

Read only the source/product/channel/trust fields needed for diagnosis; do not
print tokens or credential contents. The current machine configuration overrides
what today's source checkout says: `updates.json` is seeded on first installation
and preserved on subsequent updates.

If machine access is unavailable, ask the operator to provide the selected fields.
Do not mistake the development host's settings for the target user's settings.
Read `docs/robot_systems/update_sources.md` when a provider change is actually
requested. Never switch a LAN test feed to GitHub just to clear a connection error.

## 2. Check connectivity without changing release metadata

- For `urlopen ... [Errno 111] Connection refused`, inspect the configured HTTP
  host/port or proxy. This error does not by itself mean an update package is bad.
- Verify the development host's address (`ip -brief address`) and listener
  (`ss -ltnp 'sport = :8768'`, substituting the actual port).
- A temporary updater's Unix-socket permission error in a sandbox is a separate
  issue; request the appropriate execution permission instead of changing the feed.
- Restore an authorized missing server, verify HTTP access, and report the version
  it currently serves. Restoring a server containing version N does not create N+1.

The known test layout is `platform/dist/install-tests/complete-updates/`, containing
`stable/latest.json`, `stable/manifest.json`, and versioned combined archives and
checksum files. Confirm the actual directory before using it. Do not hardcode a
previous machine's IP, port or latest version as a universal default.

## 3. Promote only a verified artifact

1. Find the successful build/verification report for the exact target/version.
   Require final `status: passed`, all required stages passed, and the expected
   archive identity and checksum. Do not accept a report for a fixture release,
   another target, a `check` run, or an earlier archive.
2. Recompute the candidate archive's SHA256 and compare it with its manifest,
   checksum file, and verification report. Confirm the intended platform/backend
   versions/profile. Keep the original immutable files unchanged.
3. Read the currently advertised manifest. If another release appeared since
   inspection, resolve that change rather than overwriting or downgrading it.
4. Copy the archive and `.sha256` into the selected channel directory first.
   Stage large copies under temporary names and rename them when complete. A
   matching destination artifact may be reused; different bytes under the same
   version/name are an error.
5. Hard links are optional. `EXDEV` means source and destination are on different
   filesystems/mounts: fall back to a staged copy, then verify its checksum.
6. Retain the prior advertised metadata and previous archives for rollback.
   Prepare the new `manifest.json` and `latest.json` from the verified release
   manifest, preserving the feed's existing expected format and trust policy.
7. Write metadata through same-directory temporary files and atomic replacement;
   publish `latest.json` last. Preserve the former feed on failure before promotion.
   Signed feeds require the correct signatures for the exact promoted bytes.
   Do not disable signature verification or replace the station's trusted key.
8. Save the artifact and report in durable storage, for example
   `platform/dist/touchscreen-releases/TARGET/VERSION/`; `/tmp` alone is insufficient.

## 4. Serve and verify the actual advertised URLs

When no intended listener is already running, this is an example server command:

```bash
python3 -m http.server 8768 --bind LAN_ADDRESS --directory /absolute/path/to/complete-updates
```

Replace `LAN_ADDRESS`, port and directory with verified values. Bind only the
intended interface and serve only the release feed, not the repository or home
directory. Do not kill an unfamiliar listener or install a permanent system
service without authorization. Obtain execution permission when sandboxing blocks
the required networking; do not silently work around that restriction.

Use an independent HTTP client against the LAN URL to verify:

- `CHANNEL/latest.json` returns HTTP 200 and advertises the intended version;
- the referenced archive URL responds successfully with the expected length;
- the served metadata's checksum matches the verified archive.

A successful local-file read is not a connectivity check. A host-side HTTP check
also does not prove that another machine can reach it: ask for a target-side check
when routing/firewall reachability is still unknown. Keep a temporary server alive
for the operator's download and explain that it depends on the host/process
remaining available. Report that this is a LAN release, not GitHub publication.

## 5. Machine handoff

Ask the operator to use **Check for updates**, confirm the intended version,
**Download update**, then **Install after application closes** and close the app.
The existing updater handles activation and preserves its machine data/settings.
Do not apply updates or start robot hardware remotely unless that action is also
authorized. Verify the installed version afterward when machine access permits.
