# 00 — Shared client: `PHNavV1Client`

**Status:** ✅ DONE — implemented in `gh_compo_io/ph_navigator/v1/client.py`.

**File:** `gh_compo_io/ph_navigator/v1/client.py`
**Kind:** plain module (no `.ghuser`). Imported by every V1 component.
**Route(s):** all. Encapsulates the handoff's "IronPython 2.7 client constraints".

## Why

V0 duplicated TLS setup, `WebClient` config, JSON parsing, and an `offset` loop in
every component. V1 has a single, uniform response envelope and no offset loop, so
one client removes ~60 lines of copy-paste per component and gives us one place to
validate `schema_version` and surface HTTP errors consistently.

## Responsibilities

1. **Transport (IronPython/`System.Net` only).**
   - Force **TLS 1.2** (`ServicePointManager.SecurityProtocol = ...Tls12`), guarded
     for old MacOS/.NET (V0 already does this — reuse the guard + `IGH.error`).
   - `System.Net.WebClient`, **GET only**, simple headers.
   - Optional `Authorization: Bearer <token>` header **only when a token is set**
     (do NOT send `Bearer None` like V0 did — anonymous read must send no header).
   - `Content-type: application/json`.
   - **No `offset` query, no while-loop** — one request per route.
2. **Parse.** Exactly one `json.loads(response)` (V1 is single-encoded).
3. **Envelope validation.** Every route returns the common envelope. Validate:
   - `schema_version == EXPECTED_SCHEMA_VERSION (=1)` → else `IGH.error` "server
     moved ahead of plugin; update HBPH+" and bail friendly.
   - Extract `project` (`bt_number`, `project_id`, `name`), `version_id`,
     `last_modified` for change-detection / preview.
   - **Surface envelope `warnings`.** The shared envelope carries `warnings: []`
     (route-agnostic `{code, message, details}`). `_surface_warnings` (called from
     `_validate_envelope`) emits each as an `IGH.warning`, reusing `_format_details`
     — symmetric with error surfacing, so every route gets it for free. First
     producer: route 2 `on_missing_thermal=user_defaults` (see `02-…`).
4. **Version pinning + extra query params.** Optional `?version=<version_id>` when
   the caller pins; a generic `_query` dict threads any other params (e.g.
   `on_missing_thermal`) through `_project_url`/`get`/`_payload`, sorted-joined.
5. **Error mapping.** `WebException` → read the status code + JSON error body
   (`{error_code, message, request_id, details}`) → `IGH.error` with a readable
   message. Cover: 404 (bad bt_number/version), 401 (bad bearer), 403 (wrong
   project), 409 (duplicate names → surface `details.duplicate_names`), 422
   (unknown table → surface `details.valid_names`), 429 (rate-limited → suggest retry).

## Sketch (shape only — not final code)

```python
class PHNavV1Client(object):
    EXPECTED_SCHEMA_VERSION = 1
    DEFAULT_BASE = "https://api.ph-nav.com/api/v1/gh"

    def __init__(self, _IGH, _bt_number, _url_base=None, _token=None, _version=None):
        # type: (gh_io.IGH, str, str | None, str | None, str | None) -> None
        ...

    def _project_url(self, _path=""):
        # -> "{base}/projects/{bt_number}{path}"  (+ "?version=" if pinned)

    def _client(self):
        # WebClient + TLS1.2 + headers (+ Bearer only if token)

    def get(self, _path):
        # type: (str) -> dict   # GET + one json.loads + envelope check; raises/logs on HTTP error

    # convenience per route:
    def get_versions(self):                 # route 1  -> envelope["versions"]
    def get_constructions_hbjson(self):     # route 2  -> envelope["hb_constructions"]
    def get_aperture_types(self):           # route 3  -> envelope["aperture_types"]
    def get_aperture_constructions(self):   # route 4  -> envelope["hb_constructions"]
    def get_table(self, _table_name):       # route 5  -> (records, field_defs)
```

## Envelope handling (from handoff §"Common response envelope")

```json
{ "schema_version": 1, "project": {...}, "version_id": "...", "last_modified": "...Z", "<payload>": ... }
```

- **Change-detection key = `version_id` / `last_modified`, never payload bytes**
  (rich payloads carry generated ids and are not byte-stable). Expose
  `last_modified` + `version_id` as an output so downstream/Ed can see freshness.

## Notes / gotchas

- `Bearer None` bug in V0 (`client.Headers.Add("Authorization", "Bearer {}".format(None))`)
  — **do not replicate**. Send the header only when `_token` is truthy.
- Keep everything Py2.7: no f-strings, `# type:` comments, `str | None` only in comments.
- The client must degrade friendly (return `None`/empty + `IGH.error`) rather than
  throwing raw `WebException` to the canvas.

## Open questions

- Token source: component input `_token_`, an env var, or a shared GH sticky? (see
  README "auth story"). Default assumption: optional `_token_` input, anonymous if empty.
- Do we expose `_url_base` on every V1 component for local dev (V0 pattern), or
  centralize a DEV flag? Recommend a `_url_base` optional input, defaulting to prod.
