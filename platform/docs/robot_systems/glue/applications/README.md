# Glue-owned applications

Concrete glue screens live here rather than directly under the glue system root. `dashboard/` presents the production process/service, `glue_settings/` edits glue process/catalog settings, and `dispense_channel_settings/` edits declared logical channel configuration. Their model/controller/view/service layers follow the shared application lifecycle.

Glue system `application_wiring.py` supplies runtime services and `ApplicationSpec` factories; bootstrap stores descriptors and invokes factories only on first open. Shared screens remain under `src/applications/`. Follow the source navigation for every owned screen and its MVC subpackages.

<!-- source-navigation:start -->
## Source navigation

[Module reference](MODULES.md) — signatures, fields, imports and source links for every Python file in this directory.

| Source subdirectory | Guide |
|---|---|
| `dashboard/` | [dashboard](dashboard/README.md) |
| `dispense_channel_settings/` | [dispense_channel_settings](dispense_channel_settings/README.md) |
| `glue_process_driver/` | [glue_process_driver](glue_process_driver/README.md) |
| `glue_settings/` | [glue_settings](glue_settings/README.md) |

[Complete source index](../../../SOURCE_INDEX.md).
<!-- source-navigation:end -->
