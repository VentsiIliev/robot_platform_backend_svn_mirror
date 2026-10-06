# Module reference: `tests/applications/user_management`

[Package guide](README.md) · [Complete source index](../../../SOURCE_INDEX.md)

Generated from Python ASTs. Signatures, declared defaults, imports and docstrings reflect the checked-out source. No runtime code is imported. Use the guide for lifecycle, workflows and known limitations; use source links for implementation details.

## Files

- [__init__.py](#__init__py)
- [test_csv_user_repository.py](#test_csv_user_repositorypy)
- [test_permissions_controller.py](#test_permissions_controllerpy)
- [test_permissions_model.py](#test_permissions_modelpy)
- [test_stub_user_management_service.py](#test_stub_user_management_servicepy)
- [test_user_domain.py](#test_user_domainpy)
- [test_user_management_application_service.py](#test_user_management_application_servicepy)
- [test_user_management_controller.py](#test_user_management_controllerpy)
- [test_user_management_factory.py](#test_user_management_factorypy)
- [test_user_management_model.py](#test_user_management_modelpy)
- [test_user_management_view.py](#test_user_management_viewpy)

## `__init__.py`

Source: [tests/applications/user_management/__init__.py](../../../../tests/applications/user_management/__init__.py).

No top-level functions, classes or public value declarations; inspect the source for imports or entry-point statements.

## `test_csv_user_repository.py`

Source: [tests/applications/user_management/test_csv_user_repository.py](../../../../tests/applications/user_management/test_csv_user_repository.py).

Imports (including optional/function-local imports; not a startup dependency list): `os`, `src.applications.user_management.domain.csv_user_repository`, `src.applications.user_management.domain.default_schema`, `src.applications.user_management.domain.user_schema`, `tempfile`, `unittest`.

### `_record`

```python
def _record(uid, first='Alice', last='Test', role='Admin', email='a@b.com')
```

### `TestCsvUserRepositoryInit`

```python
class TestCsvUserRepositoryInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_creates_file_if_not_exists(self)
```

```python
def test_get_all_returns_empty_on_fresh_file(self)
```

```python
def test_get_schema_returns_schema(self)
```

### `TestCsvUserRepositoryAdd`

```python
class TestCsvUserRepositoryAdd(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_add_returns_true_for_new_record(self)
```

```python
def test_add_persists_record(self)
```

```python
def test_add_returns_false_for_duplicate_id(self)
```

```python
def test_add_multiple_records(self)
```

### `TestCsvUserRepositoryGetById`

```python
class TestCsvUserRepositoryGetById(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_get_by_id_returns_correct_record(self)
```

```python
def test_get_by_id_returns_none_for_missing(self)
```

### `TestCsvUserRepositoryUpdate`

```python
class TestCsvUserRepositoryUpdate(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_update_existing_returns_true(self)
```

```python
def test_update_existing_persists_change(self)
```

```python
def test_update_nonexistent_returns_false(self)
```

```python
def test_update_does_not_change_count(self)
```

### `TestCsvUserRepositoryDelete`

```python
class TestCsvUserRepositoryDelete(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_delete_existing_returns_true(self)
```

```python
def test_delete_removes_record(self)
```

```python
def test_delete_leaves_other_records_intact(self)
```

```python
def test_delete_nonexistent_returns_false(self)
```

### `TestCsvUserRepositoryExists`

```python
class TestCsvUserRepositoryExists(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_exists_true_for_added_record(self)
```

```python
def test_exists_false_for_missing(self)
```

```python
def test_exists_false_after_delete(self)
```

## `test_permissions_controller.py`

Source: [tests/applications/user_management/test_permissions_controller.py](../../../../tests/applications/user_management/test_permissions_controller.py).

Tests for src/applications/user_management/controller/permissions_controller.y_pixels Covers the pure controller logic: load populates the view, checkbox signals are forwarded to the model, and the deferral notice is shown on load. Qt is fully mocked — no display required.

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.controller.permissions_controller`, `src.applications.user_management.model.permissions_model`, `unittest`, `unittest.mock`.

### `_make_model`

```python
def _make_model(app_ids: list=None, perms: dict=None) -> PermissionsModel
```

### `_make_view`

```python
def _make_view()
```

### `TestPermissionsControllerLoad`

```python
class TestPermissionsControllerLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_set_permissions_on_view(self)
```

```python
def test_load_shows_deferral_notice(self)
```

### `TestPermissionsControllerCheckbox`

```python
class TestPermissionsControllerCheckbox(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_permission_toggled_delegates_to_model(self)
```

```python
def test_permission_toggled_refreshes_view(self)
```

## `test_permissions_model.py`

Source: [tests/applications/user_management/test_permissions_model.py](../../../../tests/applications/user_management/test_permissions_model.py).

Tests for src/applications/user_management/model/permissions_model.y_pixels PermissionsModel wraps IPermissionsAdminService and provides the pure logic for the App Permissions tab: reading the current permissions, toggling a single role for an app, and persisting immediately via the service.

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.model.permissions_model`, `src.engine.auth.i_permissions_admin_service`, `unittest`, `unittest.mock`.

### `_svc`

```python
def _svc(perms: dict=None) -> IPermissionsAdminService
```

### `_model`

```python
def _model(svc, known_app_ids, role_values=None, default_role_values=None)
```

### `TestPermissionsModelInit`

```python
class TestPermissionsModelInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_known_app_ids_returns_provided_list(self)
```

```python
def test_get_role_values_returns_all_three_roles(self)
```

### `TestGetPermissions`

```python
class TestGetPermissions(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_returns_stored_roles_for_known_app(self)
```

```python
def test_defaults_to_admin_for_unlisted_known_app(self)
```

```python
def test_excludes_stale_apps_not_in_known_list(self)
```

```python
def test_all_known_apps_present_in_result(self)
```

### `TestSetPermission`

```python
class TestSetPermission(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_adding_role_calls_set_permissions_with_role_included(self)
```

```python
def test_removing_role_calls_set_permissions_without_role(self)
```

```python
def test_set_permission_passes_correct_app_id(self)
```

```python
def test_adding_already_present_role_is_idempotent(self)
```

```python
def test_removing_absent_role_is_safe(self)
```

```python
def test_set_permission_persists_immediately(self)
```

```python
def test_unlisted_app_gets_admin_default_before_toggling(self)
```

If service has no entry for an app, default to ['Admin'] before toggle.

## `test_stub_user_management_service.py`

Source: [tests/applications/user_management/test_stub_user_management_service.py](../../../../tests/applications/user_management/test_stub_user_management_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.domain.default_schema`, `src.applications.user_management.domain.user_schema`, `src.applications.user_management.service.stub_user_management_service`, `unittest`.

### `_record`

```python
def _record(uid, first='New', last='User', role='Operator', email='new@test.com')
```

### `TestStubUserManagementServiceSchema`

```python
class TestStubUserManagementServiceSchema(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_schema_returns_default_schema(self)
```

```python
def test_accepts_custom_schema(self)
```

### `TestStubUserManagementServiceGetAll`

```python
class TestStubUserManagementServiceGetAll(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_all_users_returns_two_stub_records(self)
```

```python
def test_get_all_users_contains_alice(self)
```

```python
def test_get_all_users_returns_independent_list(self)
```

### `TestStubUserManagementServiceAdd`

```python
class TestStubUserManagementServiceAdd(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_add_user_new_id_returns_true(self)
```

```python
def test_add_user_duplicate_id_returns_false(self)
```

```python
def test_add_user_increases_count(self)
```

### `TestStubUserManagementServiceUpdate`

```python
class TestStubUserManagementServiceUpdate(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_update_user_existing_returns_true(self)
```

```python
def test_update_user_persists_change(self)
```

```python
def test_update_user_not_found_returns_false(self)
```

### `TestStubUserManagementServiceDelete`

```python
class TestStubUserManagementServiceDelete(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_delete_user_existing_returns_true(self)
```

```python
def test_delete_user_removes_from_list(self)
```

```python
def test_delete_user_not_found_returns_false(self)
```

### `TestStubUserManagementServiceQrAndEmail`

```python
class TestStubUserManagementServiceQrAndEmail(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_generate_qr_returns_true(self)
```

```python
def test_generate_qr_path_is_none(self)
```

```python
def test_send_access_package_returns_true(self)
```

```python
def test_send_access_package_message_contains_email(self)
```

## `test_user_domain.py`

Source: [tests/applications/user_management/test_user_domain.py](../../../../tests/applications/user_management/test_user_domain.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.domain.default_schema`, `src.applications.user_management.domain.user`, `src.applications.user_management.domain.user_schema`, `unittest`.

### `TestUserRecord`

```python
class TestUserRecord(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_returns_value(self)
```

```python
def test_get_returns_default_for_missing(self)
```

```python
def test_get_returns_explicit_default(self)
```

```python
def test_set_updates_value(self)
```

```python
def test_get_id_returns_id_key_value(self)
```

```python
def test_to_dict_returns_copy(self)
```

```python
def test_to_dict_is_independent_copy(self)
```

```python
def test_from_dict_round_trips(self)
```

```python
def test_repr_contains_data(self)
```

### `TestUserSchema`

```python
class TestUserSchema(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def setUp(self)
```

```python
def test_get_table_fields_returns_visible_fields(self)
```

```python
def test_get_table_headers_returns_labels(self)
```

```python
def test_get_filterable_labels_starts_with_all(self)
```

```python
def test_get_filterable_labels_excludes_masked(self)
```

```python
def test_get_filterable_labels_includes_non_masked(self)
```

### `TestFieldDescriptor`

```python
class TestFieldDescriptor(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_defaults(self)
```

```python
def test_combo_with_options(self)
```

```python
def test_mask_in_table(self)
```

### `TestUser`

```python
class TestUser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_full_name(self)
```

```python
def test_to_dict_contains_all_fields(self)
```

```python
def test_to_dict_role_is_value(self)
```

```python
def test_from_dict_creates_user(self)
```

```python
def test_from_dict_invalid_role_defaults_operator(self)
```

```python
def test_from_dict_email_none_when_empty(self)
```

```python
def test_from_dict_email_set_when_present(self)
```

### `TestRoleEnum`

```python
class TestRoleEnum(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_admin_value(self)
```

```python
def test_operator_value(self)
```

```python
def test_viewer_value(self)
```

### `TestUserFieldEnum`

```python
class TestUserFieldEnum(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_id_value(self)
```

```python
def test_first_name_value(self)
```

```python
def test_password_value(self)
```

## `test_user_management_application_service.py`

Source: [tests/applications/user_management/test_user_management_application_service.py](../../../../tests/applications/user_management/test_user_management_application_service.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.domain.default_schema`, `src.applications.user_management.domain.i_user_repository`, `src.applications.user_management.domain.user_schema`, `src.applications.user_management.service.user_management_application_service`, `sys`, `unittest`, `unittest.mock`.

### `_make_repo`

```python
def _make_repo(schema=None)
```

### `_record`

```python
def _record(uid, email='')
```

### `TestAppServiceSchema`

```python
class TestAppServiceSchema(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_schema_delegates_to_repo(self)
```

### `TestAppServiceGetAll`

```python
class TestAppServiceGetAll(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_get_all_users_delegates_to_repo(self)
```

### `TestAppServiceAddUser`

```python
class TestAppServiceAddUser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_add_user_success(self)
```

```python
def test_add_user_duplicate_returns_false(self)
```

```python
def test_add_user_exception_returns_false(self)
```

### `TestAppServiceUpdateUser`

```python
class TestAppServiceUpdateUser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_update_user_success(self)
```

```python
def test_update_user_not_found_returns_false(self)
```

```python
def test_update_user_exception_returns_false(self)
```

### `TestAppServiceDeleteUser`

```python
class TestAppServiceDeleteUser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_delete_user_success(self)
```

```python
def test_delete_user_not_found_returns_false(self)
```

```python
def test_delete_user_exception_returns_false(self)
```

### `TestAppServiceGenerateQr`

```python
class TestAppServiceGenerateQr(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_generate_qr_success_with_mocked_qrcode(self)
```

```python
def test_generate_qr_exception_returns_false(self)
```

### `TestAppServiceSendAccessPackage`

```python
class TestAppServiceSendAccessPackage(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_no_email_returns_false(self)
```

```python
def test_email_sender_missing_returns_false(self)
```

```python
def test_email_sender_success_with_mock(self)
```

## `test_user_management_controller.py`

Source: [tests/applications/user_management/test_user_management_controller.py](../../../../tests/applications/user_management/test_user_management_controller.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.user_management.controller.user_management_controller`, `src.applications.user_management.domain.default_schema`, `src.applications.user_management.domain.user_schema`, `src.applications.user_management.model.user_management_model`, `src.applications.user_management.view.user_management_view`, `sys`, `unittest`, `unittest.mock`.

### `_record`

```python
def _record(uid, first='Alice', email='a@b.com')
```

### `_make_model`

```python
def _make_model(records=None)
```

### `_make_view`

```python
def _make_view()
```

### `_make_ctrl`

```python
def _make_ctrl(records=None)
```

### `TestUserManagementControllerLoad`

```python
class TestUserManagementControllerLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_load_connects_all_signals(self)
```

```python
def test_load_calls_refresh(self)
```

### `TestUserManagementControllerRefresh`

```python
class TestUserManagementControllerRefresh(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_refresh_loads_from_model_and_sets_view(self)
```

```python
def test_refresh_status_includes_count(self)
```

### `TestUserManagementControllerOnAdd`

```python
class TestUserManagementControllerOnAdd(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}._UserDialog')
def test_rejected_dialog_does_not_call_model(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}._UserDialog')
def test_accepted_calls_add_user(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}._UserDialog')
def test_success_refreshes_view(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}._UserDialog')
def test_failure_shows_warning(self, MockDialog, mock_warn)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}._UserDialog')
def test_value_error_shows_invalid_input_warning(self, MockDialog, mock_warn)
```

### `TestUserManagementControllerOnEdit`

```python
class TestUserManagementControllerOnEdit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}._UserDialog')
def test_rejected_dialog_does_not_call_model(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}._UserDialog')
def test_accepted_calls_update_user(self, MockDialog)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}._UserDialog')
def test_failure_shows_warning(self, MockDialog, mock_warn)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
@patch(f'{_CTRL_MOD}._UserDialog')
def test_value_error_shows_warning(self, MockDialog, mock_warn)
```

### `TestUserManagementControllerOnDelete`

```python
class TestUserManagementControllerOnDelete(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_cancelled_does_not_call_model(self, mock_ask)
```

```python
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_confirmed_calls_delete_user(self, mock_ask)
```

```python
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_success_refreshes_view(self, mock_ask)
```

```python
@patch(f'{_CTRL_MOD}.ask_yes_no')
def test_failure_sets_status_only(self, mock_ask)
```

### `TestUserManagementControllerOnQr`

```python
class TestUserManagementControllerOnQr(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
@patch(f'{_CTRL_MOD}.show_warning')
def test_generate_qr_failure_shows_warning(self, mock_warn)
```

```python
@patch(f'{_CTRL_MOD}._QrDialog')
def test_generate_qr_success_opens_dialog(self, MockDialog)
```

### `TestUserManagementControllerOnFilter`

```python
class TestUserManagementControllerOnFilter(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_empty_value_shows_all_records(self)
```

```python
def test_all_column_shows_all_records(self)
```

```python
def test_filter_by_first_name_returns_matching(self)
```

```python
def test_filter_masked_field_shows_all(self)
```

```python
def test_filter_status_shows_match_counts(self)
```

## `test_user_management_factory.py`

Source: [tests/applications/user_management/test_user_management_factory.py](../../../../tests/applications/user_management/test_user_management_factory.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtWidgets`, `src.applications.user_management.controller.user_management_controller`, `src.applications.user_management.service.i_user_management_service`, `src.applications.user_management.service.stub_user_management_service`, `src.applications.user_management.user_management_factory`, `src.applications.user_management.view.user_management_view`, `sys`, `unittest`, `unittest.mock`.

### `TestUserManagementFactory`

```python
class TestUserManagementFactory(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_build_returns_user_management_view(self)
```

```python
def test_build_attaches_controller_to_view(self)
```

```python
def test_build_calls_get_all_users_on_load(self)
```

```python
def test_two_builds_produce_independent_views(self)
```

```python
def test_view_schema_matches_service_schema(self)
```

## `test_user_management_model.py`

Source: [tests/applications/user_management/test_user_management_model.py](../../../../tests/applications/user_management/test_user_management_model.py).

Imports (including optional/function-local imports; not a startup dependency list): `src.applications.user_management.domain.default_schema`, `src.applications.user_management.domain.user_schema`, `src.applications.user_management.model.user_management_model`, `src.applications.user_management.service.i_user_management_service`, `unittest`, `unittest.mock`.

### `_make_service`

```python
def _make_service(records=None)
```

### `_record`

```python
def _record(uid)
```

### `TestUserManagementModelInit`

```python
class TestUserManagementModelInit(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_schema_is_loaded_from_service(self)
```

```python
def test_get_users_empty_before_load(self)
```

### `TestUserManagementModelLoad`

```python
class TestUserManagementModelLoad(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_load_calls_get_all_users(self)
```

```python
def test_load_returns_records(self)
```

```python
def test_load_updates_internal_cache(self)
```

```python
def test_save_is_noop(self)
```

### `TestUserManagementModelAddUser`

```python
class TestUserManagementModelAddUser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_add_user_success_refreshes_records(self)
```

```python
def test_add_user_failure_does_not_refresh(self)
```

```python
def test_add_user_returns_service_result(self)
```

### `TestUserManagementModelUpdateUser`

```python
class TestUserManagementModelUpdateUser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_update_user_success_refreshes_records(self)
```

```python
def test_update_user_failure_does_not_refresh(self)
```

### `TestUserManagementModelDeleteUser`

```python
class TestUserManagementModelDeleteUser(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_delete_user_success_refreshes_records(self)
```

```python
def test_delete_user_failure_does_not_refresh(self)
```

### `TestUserManagementModelQrAndEmail`

```python
class TestUserManagementModelQrAndEmail(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
def test_generate_qr_delegates_to_service(self)
```

```python
def test_send_access_package_delegates_to_service(self)
```

## `test_user_management_view.py`

Source: [tests/applications/user_management/test_user_management_view.py](../../../../tests/applications/user_management/test_user_management_view.py).

Imports (including optional/function-local imports; not a startup dependency list): `PyQt6.QtCore`, `PyQt6.QtWidgets`, `pathlib`, `pl_gui.shell.ui.LanguageSelectorWidget`, `src.applications.user_management.domain.default_schema`, `src.applications.user_management.domain.user_schema`, `src.applications.user_management.service.stub_user_management_service`, `src.applications.user_management.user_management_factory`, `src.applications.user_management.view.user_management_view`, `src.engine.localization.localization_service`, `sys`, `tempfile`, `unittest`.

### `_record`

```python
def _record(uid, first='Alice', last='Test', role='Admin', email='a@b.com')
```

### `TestUserManagementViewSetUsers`

```python
class TestUserManagementViewSetUsers(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_set_users_populates_rows(self)
```

```python
def test_set_users_replaces_previous_rows(self)
```

```python
def test_set_users_empty_clears_table(self)
```

```python
def test_set_users_masks_password_column(self)
```

```python
def test_set_users_stores_record_in_user_role(self)
```

### `TestUserManagementViewSetStatus`

```python
class TestUserManagementViewSetStatus(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def test_set_status_updates_label(self)
```

```python
def test_set_status_empty(self)
```

### `TestUserManagementViewSelectedRecord`

```python
class TestUserManagementViewSelectedRecord(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def test_selected_record_returns_none_when_no_selection(self)
```

```python
def test_selected_record_returns_record_after_selection(self)
```

### `TestUserManagementViewButtonStates`

```python
class TestUserManagementViewButtonStates(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def test_edit_delete_qr_buttons_disabled_initially(self)
```

```python
def test_buttons_enabled_after_row_selection(self)
```

```python
def test_buttons_disabled_after_table_cleared(self)
```

### `TestUserManagementViewSignals`

```python
class TestUserManagementViewSignals(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def test_add_button_emits_add_requested(self)
```

```python
def test_refresh_button_emits_refresh_requested(self)
```

```python
def test_edit_button_emits_edit_requested_with_record(self)
```

```python
def test_delete_button_emits_delete_requested_with_record(self)
```

```python
def test_qr_button_emits_qr_requested_with_record(self)
```

```python
def test_filter_button_emits_filter_changed(self)
```

```python
def test_clear_button_resets_filter_and_emits_all(self)
```

```python
def test_clean_up_returns_none(self)
```

### `TestUserManagementLocalizationRegression`

```python
class TestUserManagementLocalizationRegression(unittest.TestCase):
```

Directly declared public methods and constructor (inherited methods are documented on their base class):

```python
@classmethod
def setUpClass(cls)
```

```python
def setUp(self)
```

```python
def tearDown(self)
```

```python
def test_selector_retranslates_embedded_user_management_view(self)
```
