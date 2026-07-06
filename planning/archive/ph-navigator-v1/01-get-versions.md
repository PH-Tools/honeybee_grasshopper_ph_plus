# 01 — `HBPH+ - PH-Nav Get Versions` (resolver / version pinning)

**Status:** ✅ DONE — `gh_compo_io/ph_navigator/v1/versions_get.py` +
`src/HBPH+ - PH-Nav Get Versions.py` + `_component_info_.py` entry + re-exports.
Ed still builds the binary `.ghuser` and icon in Grasshopper.

**File:** `gh_compo_io/ph_navigator/v1/versions_get.py`
**Class:** `GHCompo_PHNavV1GetVersions`
**Route:** 1 — `GET /` (resolver / metadata)
**Purpose:** list a project's saved versions so the user can pin a `version_id`
(certification-archive use case). Optional but useful — everything else defaults
to the active/latest saved version when no pin is given.

## Inputs

| Port            | Type   | Notes |
|-----------------|--------|-------|
| `_project_number` | str  | The `bt_number` (e.g. `2524`) — user-facing key, not a UUID. |
| `_url_base`     | str    | Optional dev override (default prod). |
| `_token`        | str    | Optional `phn_mcp_…` bearer. |
| `_get`          | bool   | Gate the network call. |

## Outputs

| Port            | Type        | Notes |
|-----------------|-------------|-------|
| `version_ids_`  | list[str]   | `version_id` for each saved version, newest first. |
| `versions_`     | list[str]   | Human-readable rows: `"{saved_at} · {name} · {kind}"` for a value-list / panel. |
| `kinds_`        | list[str]   | `working \| submitted \| closed \| snapshot`. |
| `project_`      | str         | `"{bt_number} · {name}"` from the envelope `project`. |

## Logic outline

1. `if not _get or not _project_number: return`.
2. `client = PHNavV1Client(IGH, _project_number, _url_base, _token)`.
3. `envelope = client.get_versions()` → `versions: [{version_id, saved_at, name, kind}]`
   (newest first, already ordered by server).
4. Fan out into the parallel output lists. Keep server order (do not re-sort).
5. Surface `project` in `project_`.

## Consumers

- `version_ids_` → a GH value-list / panel → feeds the `_version` input on
  Get Constructions / Get Apertures / Get Table for pinned reads.

## Open questions

- Do we want a paired "pick one" behavior, or just expose the list and let the
  user wire a value-list? Recommend: expose lists, let Ed drop a value-list.
- ~~404 when the project has *no* saved versions — surface as a friendly warning,
  not a hard error.~~ **RESOLVED (verified live 2026-07-05):** a project with zero
  saved versions is **not a reachable state**. PH-Navigator auto-creates a default
  `working` version at project creation, so every real project has ≥ 1 saved
  version. Confirmed against project `4567` ("Existing But Empty") — it still
  resolves with its default `working` version. Therefore route 1's **404 only ever
  means "unknown project number"**, which the client correctly surfaces as an error
  (verified against project `1234`). The component's `versions: []` branch is kept
  as a **defensive-only** guard (harmless if the ≥1-version invariant ever changes);
  it is not an expected user path, so no client-side 404-disambiguation is needed.
