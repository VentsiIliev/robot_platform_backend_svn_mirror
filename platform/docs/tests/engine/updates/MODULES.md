# Module reference: `tests/engine/updates`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_factory_defaults.py](#test_factory_defaultspy)
- [test_gitea_release.py](#test_gitea_releasepy)
- [test_installer_remote_support.py](#test_installer_remote_supportpy)
- [test_local_release_scripts.py](#test_local_release_scriptspy)
- [test_platform_publication.py](#test_platform_publicationpy)
- [test_platform_updates.py](#test_platform_updatespy)
- [test_release_targets.py](#test_release_targetspy)
- [test_robot_release_workflow.py](#test_robot_release_workflowpy)
- [test_target_scripts.py](#test_target_scriptspy)

## `__init__.py`

Source: [tests/engine/updates/__init__.py](../../../../tests/engine/updates/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_factory_defaults.py`

Source: [tests/engine/updates/test_factory_defaults.py](../../../../tests/engine/updates/test_factory_defaults.py).

Imports (including optional/function-local imports; not a startup dependency list): `json`, `pathlib`, `src.engine.updates.factory_defaults`, `tempfile`, `unittest`, `unittest.mock`.

### `FactoryDefaultsTests`

```python
class FactoryDefaultsTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def save(self)
```

```python
def test_standalone_seed_creates_profile_settings_once(self)
```

```python
def test_an_existing_empty_file_is_preserved(self)
```

```python
def test_rejects_wrong_profile_before_writing(self)
```

```python
def test_rejects_accounts_and_calibration_as_factory_files(self)
```

```python
def test_symlink_cannot_redirect_factory_settings(self)
```

```python
def test_a_competing_writer_wins(self)
```

```python
def test_system_storage_migrates_legacy_data_before_factory_seeding(self)
```

```python
def test_migration_rejects_conflicting_storage(self)
```

```python
def test_fresh_system_storage_has_no_profile_directory(self)
```

## `test_gitea_release.py`

Source: [tests/engine/updates/test_gitea_release.py](../../../../tests/engine/updates/test_gitea_release.py).

Gitea publication checks without contacting SVN, Gitea, or hardware.

Imports (including optional/function-local imports; not a startup dependency list): `hashlib`, `importlib.util`, `json`, `pathlib`, `requests`, `tempfile`, `unittest`, `unittest.mock`.

Module declarations (expressions are shown without evaluating them):

```python
MODULE = Path(__file__).resolve().parents[3] / 'packaging/shared/gitea_release.py'
spec = importlib.util.spec_from_file_location('gitea_release_tests', MODULE)
gitea = importlib.util.module_from_spec(spec)
```

### `digest`

```python
def digest(path)
```

### `GiteaReleaseTests`

```python
class GiteaReleaseTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def request(self, method, path, **kwargs)
```

```python
def publish(self)
```

```python
def test_creates_draft_uploads_three_assets_then_publishes(self)
```

```python
def test_failed_upload_leaves_release_as_draft(self)
```

```python
def test_mismatched_existing_release_is_never_overwritten(self)
```

```python
def test_corrupt_archive_fails_before_network(self)
```

```python
def test_wrong_remote_tag_blocks_release_creation(self)
```

```python
def test_published_release_missing_assets_is_not_modified(self)
```

```python
def test_multipart_upload_length_matches_streamed_body(self)
```

```python
def test_retry_checks_existing_asset_bytes_and_uploads_only_missing_files(self)
```

```python
def test_retry_rejects_different_uploaded_bytes(self)
```

```python
def test_remote_urls_with_credentials_are_rejected(self)
```

```python
def test_http_errors_do_not_expose_server_response_or_token(self)
```

## `test_installer_remote_support.py`

Source: [tests/engine/updates/test_installer_remote_support.py](../../../../tests/engine/updates/test_installer_remote_support.py).

Imports (including optional/function-local imports; not a startup dependency list): `importlib.util`, `pathlib`, `subprocess`, `tempfile`, `types`, `unittest`, `unittest.mock`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('platform_installer', ROOT / 'packaging/runtime/manage.py')
manager = importlib.util.module_from_spec(spec)
```

### `RemoteSupportInstallTests`

```python
class RemoteSupportInstallTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_desktop_install_elevates_only_support_step_and_passes_vendor(self)
```

```python
def test_privileged_install_uses_original_desktop_user(self)
```

```python
def test_failed_support_step_reports_retry_without_success(self)
```

```python
def test_missing_payload_does_not_run_privileged_command(self)
```

### `LauncherRefreshTests`

```python
class LauncherRefreshTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_launcher_executes_new_helper_after_activation(self)
```

## `test_local_release_scripts.py`

Source: [tests/engine/updates/test_local_release_scripts.py](../../../../tests/engine/updates/test_local_release_scripts.py).

Imports (including optional/function-local imports; not a startup dependency list): `importlib.util`, `json`, `pathlib`, `platform`, `sys`, `tempfile`, `unittest`, `unittest.mock`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('platform_local_release', ROOT / 'packaging/platform/local_release.py')
local_release = importlib.util.module_from_spec(spec)
```

### `LocalReleaseTests`

```python
class LocalReleaseTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_selects_latest_semantic_version_for_target_and_architecture(self)
```

```python
def test_run_uses_installed_helper_and_its_configuration(self)
```

```python
def test_run_rejects_another_robot_system_installation(self)
```

## `test_platform_publication.py`

Source: [tests/engine/updates/test_platform_publication.py](../../../../tests/engine/updates/test_platform_publication.py).

Platform Actions checks with fake artifacts and no external publication.

Imports (including optional/function-local imports; not a startup dependency list): `importlib.util`, `json`, `pathlib`, `subprocess`, `tempfile`, `unittest`, `unittest.mock`.

Module declarations (expressions are shown without evaluating them):

```python
PLATFORM = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('platform_publication', PLATFORM / 'packaging/platform/publish_platform.py')
pub = importlib.util.module_from_spec(spec)
```

### `PlatformPublicationTests`

```python
class PlatformPublicationTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def save(self)
```

```python
def invoke(self)
```

```python
def test_uses_existing_wrapper_and_attaches_installer_update_and_checksums(self)
```

```python
def test_retry_reuses_verified_artifacts_without_rebuilding(self)
```

```python
def test_cached_installer_corruption_is_rejected(self)
```

```python
def test_missing_svn_revision_blocks_build_and_api(self)
```

```python
def test_existing_tag_on_different_commit_blocks_build(self)
```

```python
def test_failed_build_blocks_tag_creation_and_upload(self)
```

```python
def test_wrong_manifest_revision_is_rejected(self)
```

## `test_platform_updates.py`

Source: [tests/engine/updates/test_platform_updates.py](../../../../tests/engine/updates/test_platform_updates.py).

Imports (including optional/function-local imports; not a startup dependency list): `io`, `json`, `os`, `pathlib`, `platform`, `src.engine.repositories.settings_service_factory`, `src.engine.updates.config`, `src.engine.updates.files`, `src.engine.updates.migrations`, `src.engine.updates.paths`, `src.engine.updates.releases`, `src.engine.updates.updater`, `src.shared_contracts.declarations`, `subprocess`, `tarfile`, `tempfile`, `tests.engine.repositories.test_settings_service_factory`, `unittest`, `unittest.mock`.

### `UpdateTests`

```python
class UpdateTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def release(self, version, schema=1, migrations=None)
```

```python
def install(self, version='1.0.0')
```

```python
def seed(self)
```

```python
def test_update_preserves_every_unmodified_file_byte_for_byte(self)
```

```python
def test_explicit_migrations_preserve_values_unknown_fields_and_workpieces(self)
```

```python
def test_failed_migration_leaves_current_release_and_storage_unchanged(self)
```

```python
def test_runtime_lock_blocks_activation(self)
```

```python
def test_failure_after_data_swap_restores_data_and_release(self)
```

```python
def test_failed_activation_preserves_previous_rollback_snapshot(self)
```

```python
def test_recovery_syncs_backup_directory_before_removing_journal(self)
```

```python
def test_activation_refreshes_tools_and_rollback_restores_them(self)
```

```python
def test_failed_activation_restores_tools(self)
```

```python
def test_recover_after_interrupted_activation(self)
```

```python
def test_rollback_restores_old_schema_and_preserves_post_update_snapshot(self)
```

```python
def test_reject_version_reuse(self)
```

```python
def test_reject_wrong_product(self)
```

```python
def test_archive_traversal_links_and_storage_are_rejected(self)
```

```python
def test_archive_size_limit(self)
```

```python
def test_configuration_rejects_numeric_public_key_with_clear_error(self)
```

```python
def test_local_feed_checks_stages_and_preserves_settings_without_a_key(self)
```

```python
def test_local_feed_reports_missing_manifest_and_rejects_file_escape(self)
```

```python
def test_local_feed_enforces_checksum_before_staging(self)
```

```python
def test_configuration_rejects_http_missing_key_and_relative_root(self)
```

```python
def test_signed_manifest_verification_and_tampering(self)
```

```python
def test_installer_imports_profiles_and_preserves_configuration_on_reinstall(self)
```

```python
def test_candidate_self_test_failure_does_not_stage_or_replace_release(self)
```

```python
def test_settings_factory_reads_existing_external_profile_settings(self)
```

```python
def test_profiles_use_external_root_without_collisions(self)
```

## `test_release_targets.py`

Source: [tests/engine/updates/test_release_targets.py](../../../../tests/engine/updates/test_release_targets.py).

Imports (including optional/function-local imports; not a startup dependency list): `importlib.util`, `io`, `json`, `os`, `pathlib`, `platform`, `src.bootstrap.startup_config`, `src.engine.updates.config`, `src.engine.updates.updater`, `subprocess`, `tarfile`, `tempfile`, `unittest`, `unittest.mock`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('platform_release_targets', ROOT / 'packaging/platform/targets.py')
targets = importlib.util.module_from_spec(spec)
```

### `ReleaseTargetTests`

```python
class ReleaseTargetTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def archive(self, target_name, version='1.0.0', *, override=None, factory=None)
```

```python
def test_each_target_has_a_unique_product_and_valid_bootstrap_provider(self)
```

```python
def test_dedicated_configuration_and_installation_paths_do_not_collide(self)
```

```python
def test_each_target_has_its_own_matching_source_configuration(self)
```

```python
def test_shared_editor_can_load_without_the_paint_package(self)
```

```python
def test_legacy_paint_paths_are_preserved_when_already_installed(self)
```

```python
def test_tray_install_rejects_an_automatic_dryer_release(self)
```

```python
def test_same_product_with_wrong_profile_is_rejected(self)
```

```python
def test_separate_products_can_use_the_same_version_and_different_repositories(self)
```

```python
def test_installer_creates_each_products_source_file_and_preserves_it(self)
```

```python
def test_release_builder_rejects_a_bundle_for_another_profile(self)
```

```python
def test_release_archive_carries_runnable_updater_sources(self)
```

```python
def test_activation_seeds_factory_files_without_replacing_existing_settings(self)
```

```python
def test_activation_moves_legacy_profile_storage_and_rollback_restores_it(self)
```

## `test_robot_release_workflow.py`

Source: [tests/engine/updates/test_robot_release_workflow.py](../../../../tests/engine/updates/test_robot_release_workflow.py).

Release orchestration checks using temporary fake components, without hardware.

Imports (including optional/function-local imports; not a startup dependency list): `importlib.util`, `json`, `os`, `package_robot`, `pathlib`, `release_common`, `subprocess`, `sys`, `test_packaging`, `unittest`, `unittest.mock`.

Module declarations (expressions are shown without evaluating them):

```python
PLATFORM = Path(__file__).resolve().parents[3]
spec = importlib.util.spec_from_file_location('robot_release_workflow', PLATFORM / 'packaging/robot/release_robot.py')
workflow = importlib.util.module_from_spec(spec)
```

### `RobotReleaseWorkflowTests`

```python
class RobotReleaseWorkflowTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def archive(self)
```

```python
def test_actual_archive_installs_and_self_tests_in_temporary_root(self)
```

```python
def test_bad_checksum_stops_before_installation(self)
```

```python
def test_embedded_manifest_mismatch_stops_before_installation(self)
```

```python
def test_existing_components_are_reused_without_rebuild(self)
```

```python
def test_invalid_existing_component_does_not_trigger_rebuild(self)
```

```python
def test_only_missing_component_is_built(self)
```

```python
def test_dirty_source_blocks_all_build_commands(self)
```

```python
def test_existing_robot_release_cannot_be_overwritten(self)
```

```python
def test_failed_stage_is_recorded_and_propagated(self)
```

```python
def test_publish_orders_svn_before_tests_build_verify_and_upload(self)
```

```python
def test_failed_svn_publication_blocks_build_and_gitea_upload(self)
```

```python
def test_actions_rejects_source_without_svn_revision_before_network(self)
```

## `test_target_scripts.py`

Source: [tests/engine/updates/test_target_scripts.py](../../../../tests/engine/updates/test_target_scripts.py).

Verify target dispatch and build failures without starting robot hardware.

Imports (including optional/function-local imports; not a startup dependency list): `build_and_release`, `importlib.util`, `json`, `os`, `pathlib`, `shutil`, `subprocess`, `sys`, `tempfile`, `unittest`, `unittest.mock`.

Module declarations (expressions are shown without evaluating them):

```python
ROOT = Path(__file__).resolve().parents[3]
```

### `TargetScriptTests`

```python
class TargetScriptTests(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_every_wrapper_dispatches_fixed_target_from_another_directory(self)
```

```python
def test_build_verifies_before_packaging_and_forwards_options(self)
```

```python
def test_failed_self_test_never_packages_release(self)
```

```python
def test_invalid_arguments_do_not_start_build(self)
```

```python
def test_each_target_uses_its_own_version_file_and_forwards_options(self)
```

```python
def test_missing_or_invalid_version_file_stops_before_build(self)
```
