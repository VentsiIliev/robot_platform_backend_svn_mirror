# Remote support resources

| File | Purpose |
| --- | --- |
| `release.conf` | Literal download base, release tag, package filename and expected package version |
| `install.sh` | Administrator-run initial machine provisioning |
| `install_openssh.sh` | Standalone OpenSSH installation, configuration validation and service activation |
| `install_rustdesk.sh` | Standalone branded RustDesk installation, legacy migration and service activation |
| `install_auto_login.sh` | Standalone installation of the shared automatic-login helper |
| `install_pl_remote_support.sh` | Branded package download and provisioning |
| `install_update_helper.sh` | Root-owned helper, trusted-source policy and scoped sudoers installation |
| `update_package.py` | Restricted automatic Debian package upgrade helper |
| `build_payload.py` | Release payload assembly |

The source directory is [packaging/remote_support](../../../packaging/remote_support/).
