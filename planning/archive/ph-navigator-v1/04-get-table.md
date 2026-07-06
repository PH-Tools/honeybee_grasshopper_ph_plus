# 04 — `HBPH+ - PH-Nav Get Table` (generic tabular download)

**Status:** ✅ DONE — `gh_compo_io/ph_navigator/v1/table_get.py` +
`gh_compo_io/ph_navigator/v1/table_names.py` (`VALID_TABLE_NAMES`) +
`src/HBPH+ - PH-Nav Get Table.py` + `_component_info_.py` entry + re-exports.
Ed still builds the binary `.ghuser` and icon in Grasshopper (and can populate its
value-list dropdown from `VALID_TABLE_NAMES`). The `.ghuser` needs the added `_key`
input port and `record_collection_` output port (see the Inputs/Outputs tables below).
**Not yet run against a live route-5 payload** — `field_defs`/`records` shape is
trusted from the handoff contract; verify against a real download (as with the Phase
01 404 check).

**File:** `gh_compo_io/ph_navigator/v1/table_get.py`
**Class:** `GHCompo_PHNavV1GetTable`
**Route:** 5 — `GET /tables/{table_name}` (generic element tables)
**Purpose:** one downloader for all 12 row-based element types. Replaces the old
AirTable download path. Pure transport + parse — **no reshaping, no HB objects**
(that's the Organize Table component, `05-organize-table.md`).

## The 12 allowlisted tables

```
rooms · space_types · thermal_bridges · pumps · fans · ventilators ·
hot_water_heaters · hot_water_tanks · electric_heaters · appliances ·
heat_pump_indoor_units · heat_pump_outdoor_units
```

Unknown name → **422 `unknown_table`** with `details.valid_names` (the 12). Empty
table → `records: []` (not 404).

## Table-name value-list helper

**File:** `gh_compo_io/ph_navigator/v1/table_names.py` — export the 12 names as an
ordered constant `VALID_TABLE_NAMES` so:
- Get Table can validate `_table_name` client-side before the call, and
- Ed can populate a GH value-list dropdown from the same source of truth.

Keep this list identical to the backend allowlist; if 422 fires with a different
`valid_names`, log it (the plugin is stale).

## Inputs

| Port              | Type | Notes |
|-------------------|------|-------|
| `_project_number` | str  | `bt_number`. |
| `_table_name`     | str  | One of the 12 (value-list). Validate against `VALID_TABLE_NAMES`. |
| `_key`            | str  | Optional. Field to key `record_collection_` by (built-in column, else `custom_values`); empty → key by record `id`. |
| `_version`        | str  | Optional `version_id` pin. |
| `_url_base`       | str  | Optional dev override. |
| `_token`          | str  | Optional bearer. |
| `_download`       | bool | Gate the call. |

## Outputs

| Port          | Type       | Notes |
|---------------|------------|-------|
| `records_`    | list[`TableRecord`] | One row each: `id` + typed built-in columns + `custom_values` bag + `custom_links` bag. Dict-like wrapper (`.get`/`[]`/`.items()`) that renders its contents in a GH panel instead of `PythonDictionary`. Values verbatim. |
| `record_collection_` | `CustomCollection` | Same records, keyed by `_key` (or record `id` if no `_key`). Single-select keys resolve to their label; keys stringified. Feeds `Get From Custom Collection` for record↔geometry matching. Duplicate keys → `IGH.warning`. |
| `field_defs_` | list[`FieldDef`] | Field definitions (built-in + custom): `field_key`, `display_name`, `field_type`, `config`, `origin`, … Same dict-like display wrapper. |
| `table_name_` | str        | Echo the resolved table name (feeds Organize Table `_type`). |
| `json_`       | str        | Raw payload preview. |
| `last_modified_` | str     | Freshness. |

## Payload semantics (pass through verbatim — O5)

- **Single-select fields** → `{ "id", "label" }` in typed columns and in
  `custom_values`. Unset → `null`.
- **Cross-table references stay ids** (e.g. `outdoor_unit_id`) — join later.
- **Asset references stay ids.**
- **Raw stored fields only** — computed/formula rollups (e.g. rooms airflow) are
  **not** included yet (logged backend follow-up). Note this in the tooltip.

## Logic outline

1. `ready` = `_project_number and _table_name and _download`.
2. Validate `_table_name in VALID_TABLE_NAMES` → else `IGH.error` listing valid names
   (skip the network round-trip).
3. `client = PHNavV1Client(...)`; `records, field_defs = client.get_table(_table_name)`.
4. Return records/field_defs untouched (Organize Table interprets them).
5. Handle 422 (surface `details.valid_names`), empty table (`records: []` → warn, not error).

## Why generic (not 12 components)

The 12 tables share one response shape (`records` + `field_defs`). The only thing
that differs downstream is *how the columns map to HB consumers* — and that lives
in Organize Table's per-table mapping, not in 12 duplicate downloaders. One ghuser
to build, one class to maintain.

## Open questions

- ~~Emit `field_defs_` as raw dicts, or wrap in a tiny schema class for nicer GH
  preview?~~ **RESOLVED: wrap both.** A bare dict displays as
  `IronPython.Runtime.PythonDictionary` in a GH panel (the user can't see the data).
  Both `records_` and `field_defs_` are now wrapped in dict-like `TableRecord` /
  `FieldDef` (`v1/table_schema.py`, the AirTable `TableRecord` pattern) whose
  `ToString()` renders the contents. The wrappers keep `.get`/`[]`/`.items()`, so
  Organize Table reads them exactly like the raw dicts — the wrap is transparent to
  consumers, cosmetic to GH. `json_` is still built from the raw dicts (faithful JSON).
