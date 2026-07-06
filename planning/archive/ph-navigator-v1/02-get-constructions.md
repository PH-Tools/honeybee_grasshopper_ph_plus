# 02 — `HBPH+ - PH-Nav Get Constructions` (opaque constructions)

**Status:** ✅ DONE — `gh_compo_io/ph_navigator/v1/constructions_get.py` +
`src/HBPH+ - PH-Nav Get Constructions.py` + `_component_info_.py` entry + re-exports.
Ed still builds the binary `.ghuser` and icon in Grasshopper.

**File:** `gh_compo_io/ph_navigator/v1/constructions_get.py`
**Class:** `GHCompo_PHNavV1GetConstructions`
**Route:** 2 — `GET /constructions/hbjson` (RICH payload)
**Purpose:** V1 twin of the V0 `constructions_get`. Downloads opaque assemblies as
Honeybee `hbjson` and rebuilds `OpaqueConstruction` objects. Dedicated (not the
generic Get Table) because the payload is full hbjson, not rows.

## What changed vs V0

- New endpoint + shared `PHNavV1Client` (TLS/auth/parse/errors centralized).
- **No `offset` loop** — single request.
- Payload key is still **`hb_constructions`**: `{ "<assembly name>": OpaqueConstruction.to_dict() }`,
  **single-encoded** (no nested `json.loads` on the value — V0's string-check hack
  is no longer needed).
- Round-trips richer PH props: `PhColor`, division grid, `honeybee_energy_ref`
  datasheet/photo refs, and the `ph_nav` external id. `honeybee-ref==0.2.1` (pin;
  0.2.6 layout is broken).
- Material identifier carries the IP-thickness suffix: `"{name} [ X.X in]"` (unchanged).
- **Asset refs are `phn-asset:<asset_id>` locators**, not signed URLs — pass through
  verbatim; resolve to bytes later only if needed.
- **409 `duplicate_assembly_names`** (`details.duplicate_names`) → surface as an
  error telling the user to rename in the web app. (New failure mode to handle.)

## Inputs

| Port              | Type | Notes |
|-------------------|------|-------|
| `_project_number` | str  | `bt_number`. |
| `_version`        | str  | Optional `version_id` pin (from Get Versions). |
| `_url_base`       | str  | Optional dev override. |
| `_token`          | str  | Optional bearer. |
| `_download`       | bool | Gate the call. |

## Outputs

| Port             | Type                              | Notes |
|------------------|-----------------------------------|-------|
| `constructions_` | CustomCollection[OpaqueConstruction] | Rebuilt HB-Energy constructions, keyed by assembly name. Same output type as Get Apertures (unified). |
| `last_modified_` | str                               | Envelope `last_modified` (freshness). |

## Logic outline

1. `ready` = `_project_number and _download`.
2. `client = PHNavV1Client(IGH, _project_number, _url_base, _token, _version)`.
3. `hb_constructions = client.get_constructions_hbjson()` → `{name: dict}`.
4. Rebuild `{name: OpaqueConstruction.from_dict(d)}` and return
   `CustomCollection.from_dict(...)` (keyed by assembly name — the shared collection
   constructor, so this getter emits the same output type as Get Apertures).
5. Wrap **only the `from_dict` rebuild** in try/except → `IGH.error` (malformed
   payload). **Transport / HTTP / 409 `duplicate_assembly_names` are NOT
   special-cased here** — the shared `PHNavV1Client` already surfaces them
   generically (`_format_details` renders `details.duplicate_names`), returning
   `None` + `IGH.error`; the component just bails on `None`. This is the intended
   altitude: the component owns only object-rebuild, the client owns all HTTP.

## Dependencies

- `honeybee_energy.construction.opaque.OpaqueConstruction`
- `honeybee_energy.material.opaque.EnergyMaterial`
- `honeybee_energy_ph.properties.materials.opaque` (`PhColor`, `PhDivisionGrid`,
  `EnergyMaterialPhProperties`)
- `honeybee-ref==0.2.1` (`DocumentReference`, `ImageReference`,
  `_HBObjectWithReferences`, `add_external_identifier("ph_nav", ...)`)

## Open questions

- ~~Do we also emit the raw `json_` preview string?~~ **RESOLVED: yes.** Added a
  `json_` output (`json.dumps(payload, indent=2, ensure_ascii=False)`). It is built
  *before* the `from_dict` rebuild and emitted on both the success and the
  rebuild-failure paths, so a malformed payload can still be inspected — the case
  the preview exists to diagnose.
- Hybrid/steel-stud layers come as a `PhDivisionGrid` with equivalent conductivity
  (density/specific-heat from base material — documented V1 limitation). The
  component does **no special handling** — `OpaqueConstruction.from_dict` is trusted
  to reconstitute the grid on its own. **To confirm live** against a real hybrid /
  steel-stud assembly (as with the Phase 01 404 check).
- ~~**Material missing thermal-mass props → opt-in `user_defaults` mode.**~~
  **RESOLVED (2026-07-05):** backend shipped the opt-in mode; the GH client is now
  wired to it (see **GH-side follow-up** below — ✅ DONE). A material lacking only
  `density_kg_m3` / `specific_heat_j_kgk` no longer 422s the route-2 export — it is
  exported with PH-neutral defaults and an `IGH.warning`. Missing `conductivity_w_mk`
  still 422s. Backend as-built contract archived at
  `ph-navigator-v2/planning/archive/dated/2026-07-05/gh-material-thermal-defaults/`.

## GH-side follow-up — wire `user_defaults` ✅ DONE

Shipped in `PHNavV1Client` (`v1/client.py`) against the as-built backend contract:

1. **Send the mode.** `get_constructions_hbjson()` sends
   **`on_missing_thermal=user_defaults`** on `GET /constructions/hbjson` (via a
   generic `_query` dict threaded through `_project_url`/`get`/`_payload`). Server
   default is `strict`, so opting in is explicit. Effect: a material missing only
   its thermal-mass fields is exported with PH-neutral defaults (density 600,
   specific-heat 1000) instead of failing the whole export. **Missing
   `conductivity_w_mk` still 422s** — it drives the U-value, so that stays a hard
   error the user fixes in the web app.

2. **Surface `warnings`.** New `_surface_warnings()` reads the envelope's
   `warnings: []` (route-agnostic `{code, message, details}`) and calls
   `IGH.warning(message + _format_details(details))` for each — reusing the same
   scalar-bag renderer as error `details`, so the user sees *which* assembly /
   material got defaulted.

3. **Surfaced generically for every route.** `_surface_warnings` is invoked from
   `_validate_envelope` (the shared parse path all getters funnel through), so any
   future route that emits warnings gets it for free — symmetric with how errors
   already surface via `IGH.error`. Zero per-component code.
