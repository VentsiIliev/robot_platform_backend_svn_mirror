# Per-RobotSystem update sources

Each system can declare its own remote update source in
`src/robot_systems/SYSTEM/storage/update_source.json`. In
`config/release_targets.json`, point its `update_source` field at that file:

```json
"update_source": "src/robot_systems/paint_tray_dry/storage/update_source.json"
```

The path must remain inside the selected system package, and the declaration's
`product` must match that release target. Each system/profile has its own
declaration, even if several share one repository. If `update_source` is omitted,
packaging supplies a disabled configuration. The installer copies the selected
source into the station's machine-owned `updates.json` only on first install;
subsequent application releases cannot silently replace its source or trust keys.

## Repository type and URL

| `repository_type` | `repository_url` | Release layout |
|---|---|---|
| `github` | `https://github.com/OWNER/REPO` | Published release tagged `SYSTEM/robot/vVERSION`, with manifest/signature/archive assets |
| `gitlab` | `https://HOST/GROUP/SUBGROUP/REPO` | Release with the same tag and named `assets.links`; prefer `direct_asset_url` |
| `svn` | `https://HOST/svn/REPO/path/to/FEED` | Versioned `CHANNEL/latest.json`, signature and referenced archive |
| `feed` | `https://HOST/path/to/FEED` or an absolute local directory | `CHANNEL/latest.json`, signature and referenced archive |
| `gitea` | HTTP(S) owner/repository URL | Existing Gitea release-asset format, retained for compatibility |

GitHub and GitLab have different release APIs; a generic Git remote cannot
identify the binary-release distribution format. SVN/feed sources contain ready
archives. Updates do not compile a Git or SVN source checkout on the station.
Repository selection cannot change the installed robot target or component pair.

Example GitHub declaration (enable only after supplying the station's key):

```json
{
  "enabled": false,
  "repository_type": "github",
  "repository_url": "https://github.com/VentsiIliev/robot_platform_backend_svn_mirror",
  "public_key": null,
  "product": "paint-tray-dry-robot",
  "channel": "stable",
  "timeout_seconds": 30
}
```

For GitLab under `/gitlab`, configure both the project URL and API base:

```json
{
  "repository_type": "gitlab",
  "repository_url": "https://gitlab.example/gitlab/robots/tray-dryer",
  "api_url": "https://gitlab.example/gitlab/api/v4"
}
```

This snippet replaces the source fields in a complete declaration, not its
product/channel/trust fields. Normal GitLab installations derive `/api/v4`
automatically. Add `token_file` only in machine configuration for a private
GitHub/GitLab project. Do not embed credentials into source or release archives.

SVN requires the station user's non-interactive SVN authentication and trusted
TLS certificate. An SVN source can use `timeout_seconds: 1200` for large archive
downloads; it is an overall transfer timeout. Place signed feed files under a
dedicated versioned directory and use immutable versioned archive names.

## Existing stations and publication

Editing a system declaration affects newly built bundles and first installs.
On an existing station, stop the application/updater before editing `updates.json`,
set its provider and URL, retain the product and public-key path, provision the
provider's credentials if needed, then restart the update service and check.
Do not carry a Gitea token across to a new host/provider.

The complete robot publisher defaults to `github-svn-mirror` and `GITHUB_TOKEN`:

```bash
.venv/bin/python -B packaging/robot/release_robot.py publish paint_tray_dry --signing-key /secure/path/signing-key.pem
```

It preserves SVN-first source publication, exact component tags, draft-first
asset publication and verification. Configurable GitLab/SVN downloads do not
change the current publication policy: publish to SVN and GitHub. No GitLab or
SVN-feed publication occurs merely by selecting those download providers.

API references: [GitHub releases](https://docs.github.com/en/rest/releases/releases),
[GitHub assets](https://docs.github.com/en/rest/releases/assets),
[GitLab releases](https://docs.gitlab.com/api/releases/),
[GitLab token authentication](https://docs.gitlab.com/api/rest/authentication/).
