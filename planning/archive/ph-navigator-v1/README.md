# PH-Navigator V1 — GH Component Plan

Migration of the PH-Navigator getter components from the **V0** app
(`ph-dash-0cye.onrender.com`, ad-hoc endpoints) to the **V1** app read API
(`api.ph-nav.com/api/v1/gh`, the contract in `CLIENT_HANDOFF.md`).

**Docs in this folder:** `00`-shared-client · `01`-get-versions ·
`02`-get-constructions · `03`-get-apertures · `04`-get-table · `05`-organize-table ·
`06`-gh-io-helper · `outputs.md` (Ed's per-table desired output ports).

> Naming note: the *app* generation is **V1** (new) vs **V0** (old). The V1
> backend route prefix happens to be `/api/v1/gh`, and its handoff doc calls the
> wire-contract "V2" internally (`schema_version: 1`). In this repo we name
> everything **V1** after the app generation. The one concrete number the client
> must check is the envelope `schema_version` (currently `1`).

## Guiding decisions

- **V0 stays frozen.** The existing `HBPH+ - PH-Navigator Get Constructions` and
  `HBPH+ - PH-Navigator Get Window Types` components keep working against the old
  app for legacy projects. Their code now lives in
  `gh_compo_io/ph_navigator/v0/` (moved, re-exported from the package `__init__`
  so the old `src/` wrappers resolve unchanged). **Do not edit V0 behavior.**
- **V1 is a new, parallel set of components**, not a `version` switch bolted onto
  the V0 components (that was the PRD's option — we rejected it for clarity).
  New code lives in `gh_compo_io/ph_navigator/v1/`.
- **Download vs. organize is split** (Ed's call). One component fetches raw data;
  a separate component reshapes it into HB-consumer-ready outputs. More
  components, but more transparency and flexibility on the canvas.
- **Constructions and Apertures stay dedicated** download+build components, as in
  V0 — their payloads are rich (`hbjson` / denormalized grid) and their job is to
  emit real Honeybee objects, not rows. They sit on the shared client internally.
- **The 12 tabular element types are generalized**, not 12 near-identical
  components: one generic **Get Table** downloader (value-list of the 12 names) +
  one generic **Organize Table** component with *dynamic outputs* keyed on the
  table name (the `create_elec_equip.py` dynamic-node pattern, applied to the
  output side).

## Component inventory (what needs building)

| # | Component (canvas name)                  | Route(s) | gh_compo_io file            | Kind |
|---|------------------------------------------|----------|-----------------------------|------|
| ✅ | *(shared)* `PHNavV1Client`               | all      | `v1/client.py`              | module, no ghuser — **DONE** |
| 1 ✅| `HBPH+ - PH-Nav Get Versions`            | 1        | `v1/versions_get.py`        | resolver / version pinning — **DONE** (code; `.ghuser` pending) |
| 2 ✅| `HBPH+ - PH-Nav Get Constructions`       | 2        | `v1/constructions_get.py`   | dedicated, builds `OpaqueConstruction` — **DONE** (code; `.ghuser` pending) |
| 3 ✅| `HBPH+ - PH-Nav Get Apertures`           | 3        | `v1/apertures_get.py`       | dedicated, builds `WindowUnitType` + `WindowConstruction` — **DONE** (code; `.ghuser` pending; route 4 unused) |
| 4 ✅| `HBPH+ - PH-Nav Get Table`               | 5        | `v1/table_get.py`           | generic download (records + field_defs) — **DONE** (code; `.ghuser` pending; not yet run live) |
| 5 ✅| `HBPH+ - PH-Nav Organize Table`          | —        | `v1/table_organize.py`      | generic reshape, **dynamic outputs** — **DONE** (code; `.ghuser` pending; not yet run live) |
| ✅ | *(helper)* Table-name value-list         | —        | `v1/table_names.py`         | `VALID_TABLE_NAMES` — 12 valid names for a GH value-list dropdown — **DONE** |

Each numbered row = one hand-built `.ghuser` (Ed builds these in Grasshopper once
the `gh_compo_io` files land). The shared client and value-list helper are plain
modules — the value-list can be a small component or just a documented constant.

## Data-flow (target canvas topology)

```
                        ┌─ Get Versions ─┐  (optional; pick a saved version_id)
                        │                ▼
_project_number ───────►│           _version ──┐
                        ▼                       ▼
              ┌──────────────────┐   ┌──────────────────────┐
              │ Get Constructions│   │ Get Apertures        │
              │  → OpaqueConstr. │   │  → WindowUnitType +   │
              └──────────────────┘   │    WindowConstruction │
                                     └──────────────────────┘

_table_name (value-list) ─► Get Table ─► records_ + field_defs_
                                              │
                                              ▼
                                     Organize Table (_type = table_name)
                                              │  dynamic outputs, e.g. for "ventilators":
                                              ├─ name_ ─► ... ─►┐
                                              ├─ unit_ ────────►│ HBPH - Create Ventilator
                                              └─ ... ──────────►┘
```

## Shared infrastructure to add

1. ✅ **`v1/client.py` — `PHNavV1Client`** — **DONE** (see `00-shared-client.md`).
   One place for: TLS-1.2 forcing, optional `Bearer` token, GET, single
   `json.loads`, envelope validation (`schema_version == 1`, pull
   `project`/`version_id`/`last_modified`), `?version=` pinning, and uniform error
   surfacing (404/401/403/409/422/429). No `offset` loop (the V0 vestige is gone in
   V1).
2. ✅ **`setup_component_outputs` helper** — **DONE** (in `ph_gh_component_io`,
   uncommitted). The output-side twin of `gh_io.setup_component_inputs`. Rewrites
   `ghenv.Component.Params.Output[i]` (`Name`/`NickName`/`Description`/`Access`) from
   a dict keyed by index. `ComponentOutput` + `setup_component_outputs` now consumed
   by the Organize Table component (`05`). Full spec in `06-gh-io-helper.md`.

## What Ed still needs to provide

- ✅ **Per-table output mappings** — provided in `outputs.md`, implemented as
  `OUTPUT_SPECS` in `table_organize.py`. 9 tables mapped; heat pumps deferred;
  `space_types` → warn + pass-through (O-E resolved).
- ✅ **`source_field_key` confirmation** — resolved by reading the backend row
  models (`ph-navigator-v2/backend/features/project_document/tables/*.py`) rather
  than guessing; the real built-in keys are encoded in `OUTPUT_SPECS`. Still worth
  **one live route-5 smoke-test per table** to confirm the serialized shape (empty
  table, single-select `{id,label}`, custom_values bag) — none captured as a fixture
  yet.
- **Auth story**: confirm whether GH clients send a `phn_mcp_…` bearer token or
  rely on anonymous read for the transition (handoff allows anonymous).
- **Prod base URL** confirmation (`https://api.ph-nav.com/api/v1/gh`) and whether
  a `_url_base` dev override input stays (V0 pattern: `http://127.0.0.1:8000`).

## Open questions

- **O-A**: Does Organize Table build HB objects itself, or only reshape rows and
  hand off to the existing `HBPH -/HBPH+` create-components? Current plan: *reshape
  only* (transparent, reuses tested builders). Revisit per-table if a builder
  doesn't exist.
- **O-B**: Cross-table joins (e.g. `heat_pump_indoor_units.outdoor_unit_id`) —
  deferred with heat pumps (`_type` in the heat-pump tables → `IGH.error`).
- **O-C** ✅: Single-select fields arrive as `{id, label}`. Organize Table emits the
  `label` (structural detection in `_flatten_option`); no port needs the `id` yet.
- **O-D**: Keep the V0 `_download`/`_get` boolean gate (network I/O) — recommend yes.
- **O-E** ✅: `space_types` → `IGH.warning` + pass-through on a `records_` port. Can
  grow its own port list later.
