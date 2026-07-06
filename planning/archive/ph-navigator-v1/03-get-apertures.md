# 03 — `HBPH+ - PH-Nav Get Apertures` (window types + constructions)

**Status:** ✅ DONE — `gh_compo_io/ph_navigator/v1/apertures_get.py` +
`src/HBPH+ - PH-Nav Get Apertures.py` + `_component_info_.py` entry + re-exports.
Ed still builds the binary `.ghuser` and icon in Grasshopper.

**File:** `gh_compo_io/ph_navigator/v1/apertures_get.py`
**Class:** `GHCompo_PHNavV1GetApertures`
**Routes:** 3 — `GET /aperture-types` (denormalized grid). Route 4
(`GET /aperture-constructions/hbjson`) is **intentionally not called** — see
"Decisions" below.
**Purpose:** V1 twin of V0 `window_types_get`. Builds `WindowUnitType` collection +
`WindowConstruction` collection. Dedicated component; reuses most of the V0
build logic and the V0 schema classes (which the handoff says route 3 was designed
to satisfy — "satisfies the existing V1 client parser `window_types_schema.py`").

## Reuse strategy — AS BUILT: split (build reused, schema forked)

The V0 build pipeline (`create_hbph_glazing_types`, `create_new_hbph_frame_elements`,
`create_new_hbph_frames`, `create_hbph_window_unit_types`, `create_hbph_ep_constructions`)
is **directly reused by import** — it transforms schema objects, never parses dicts,
so it does not diverge. The `window_types_schema.py` dataclasses had to be **forked**
into `v1/` (the fallback), because the real route-3 payload emits `null` numerics the
V0 parser chokes on. See **Decisions** below for the full rationale. Original options
weighed pre-implementation:

- ~~(preferred) Import both build helpers + schema from `v0/`.~~ Schema reuse failed
  on the live payload (`float(null)` on `psi_install_w_mk`).
- **(fallback, taken) Fork the schema into `v1/`**, null-safe. Build helpers stay
  imported from `v0/`.

## Payload deltas vs V0 (from handoff route 3)

- Payload key is **`aperture_types`**: `{ "<type name>": {…} }` (V0 used `apertures`).
- Grid dims: `row_heights_mm`, `column_widths_mm`. **Row order top-to-bottom**
  (row 0 = top); V0's reverse-for-Rhino logic in `ApertureTypeData` still applies.
- `row_span`/`col_span` are **counts** (server maps V2 inclusive tuples → counts).
  Matches the V0 schema's `col_span`/`row_span` int fields.
- **`psi_install_w_mk` IS emitted now** (V0 defaulted 0.04). Read it straight.
- **`chi_value` is OMITTED** → default `0.0` client-side (V0 schema already
  defaults `_chi_value_w_k` from `chi_value` with 0.0 fallback — OK as-is).
- `glazing.glazing_type` now carries extra fields (`id`, `specification_status`,
  `manufacturer`, `brand`); frames carry `id`, `operation`, etc. Schema currently
  ignores the extras — fine, but consider surfacing `manufacturer`/`spec_status`.
- **Operation** block (`{type: swing|slide, directions: [...]}` | null=Fixed) is
  **new** — V0 schema drops it. If we want operable-window geometry/logic, extend
  the schema + `WindowElement`. Flag for Ed.
- **409 `duplicate_aperture_type_names`** — new failure mode to surface.
- Route 4 (`aperture-constructions/hbjson`) provides `WindowConstruction.from_dict`
  objects keyed by `"{aperture}_C{col}_R{row}"`, each an
  `EnergyWindowMaterialSimpleGlazSys` (u_factor = ISO 10077-1 element U, shgc =
  glazing g_value default 0.5, vt 0.6). This is the **minimal stable subset**; the
  handoff says build `ph_frame`/`ph_glazing` in GH from route-3 data (as V0 does
  via `create_new_hbph_window_material` + `iso_10077_1.calculate_window_uw`).

## Inputs / Outputs

Inputs: `_project_number`, `_version`, `_url_base`, `_token`, `_download` (as route 2).

| Output          | Type                        | Notes |
|-----------------|-----------------------------|-------|
| `window_types_` | CustomCollection[WindowUnitType] | → `HBPH+ - Create Window Geometry`. |
| `constructions_`| CustomCollection[WindowConstruction] | HBPH window constructions. |
| `json_`         | str                         | Raw payload preview (V0 parity). |
| `last_modified_`| str                         | Freshness. |

## Logic outline

1. `ready` = `_project_number and _download`.
2. `client = PHNavV1Client(...)`.
3. `aperture_types_raw = client.get_aperture_types()` (route 3).
4. `aperture_types = [ApertureTypeData.from_dict(v) for v in aperture_types_raw.values()]`
   (reuse V0 schema; wrap each in try/except with `IGH.warning`).
5. Build glazings → frame-elements → frames → window-unit-types → EP-constructions
   using the V0 helpers.
6. *(decision)* build window EP-constructions locally (V0 path, via ISO 10077-1)
   **or** consume route 4's `WindowConstruction.from_dict` directly. Recommend:
   keep the V0 local build (richer `ph_frame`/`ph_glazing`), treat route 4 as
   optional/secondary. Revisit if route 4's element-U is the desired source of truth.

## Decisions (as-built)

- **Route 3 only; route 4 not called.** Building locally from route 3 (via the V0
  ISO-10077-1 pipeline) yields richer `WindowConstruction`s (with `ph_frame` /
  `ph_glazing`) than route 4's minimal `EnergyWindowMaterialSimpleGlazSys` subset,
  and gets both outputs (`window_types_` + `constructions_`) from **one** request.
  Route 4 stays available if its element-U ever becomes the desired source of truth.
- **Fork the schema; reuse the build helpers.** The *build pipeline* (`create_hbph_*`
  in `v0/window_types_get.py`) transforms schema objects -> HBPH objects and never
  parses raw dicts, so it does not diverge — V1 imports it directly and runs it on
  V1 schema objects (duck-type-identical). The *schema*, however, **had to be forked**
  into `v1/window_types_schema.py`: route 3 emits an explicit JSON `null` for unset
  numeric fields (`psi_install_w_mk` — 196× in project 2524), and `dict.get(key, dflt)`
  returns `None` for a present-but-null key, so the V0 `float(dict.get(...))` raised
  (`float(None)` -> `NullReferenceException` in IronPython, failing **all 27** types).
  The fork routes every numeric coercion through null-safe `_as_float` / `_as_int`
  helpers. This is the plan's sanctioned fallback ("copy the schema into v1/ if V1's
  grid shape diverges"). V0 stays frozen. *(Original plan assumed "read psi_install
  straight"; the real payload proved it is routinely null — hence the fork.)*
- **Outputs:** `window_types_`, `constructions_`, `json_` (raw preview, built before
  parsing so a malformed payload is still inspectable — parity with Get
  Constructions), `last_modified_`.
- **Per-item parse resilience:** each aperture-type dict is parsed independently
  (`_parse_aperture_types`); a single malformed entry is skipped with `IGH.warning`
  rather than zeroing the whole download.

## Follow-ups (for the eventual V0 retirement — not now)

Residual couplings/duplication vs. the frozen V0 module, all forced by the freeze
(editing V0 is out of bounds) and left deliberately:

- **Build pipeline still imported from `v0/`.** `create_hbph_*` should be **lifted out
  of `v0/` into a neutral module** that both versions import, rather than left to rot
  in a retired version's namespace. (V1 now has its own schema; only the build helpers
  still reach into `v0/`.)
- **Schema is now duplicated** (`v0/window_types_schema.py` ≈ `v1/window_types_schema.py`,
  the V1 copy null-safe). At V0 retirement, delete the V0 copy and keep the null-safe
  V1 one as the single source.
- V0's aperture-parse loop lives as a **bound method**
  (`GHCompo_PHNavGetWindowTypes.convert_json_data_to_aperture_types`), so it is not
  importable; V1 re-implements the same ~10-line loop as `_parse_aperture_types`.
  When the pipeline moves to the neutral module, promote this to a shared function
  and collapse the two copies.

## Open questions

- **Operable windows**: adopt the new `operation` block now, or defer? (schema +
  `WindowElement` change). **Deferred** — the reused V0 schema drops the block; no
  operable-window geometry/logic yet. Flag for Ed if/when needed.
- **Hybrid/steel-stud & live payload shape**: confirm route-3 grid parses cleanly
  against a real project (as with the Phase 01/02 live checks) — Ed to verify in GH.
