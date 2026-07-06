# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Shared client for the PH-Navigator V1 read API (`/api/v1/gh`).

Every V1 PH-Navigator GH component talks to the backend through this one class,
so that TLS setup, header/auth config, JSON parsing, envelope validation, and
HTTP-error surfacing live in a single place instead of being copy-pasted into
each component (as they were in V0).

Runtime target is Rhino/Grasshopper's IronPython 2.7 - transport is `System.Net`
only. The client never lets a raw `WebException` reach the canvas: on any failure
it logs a readable message via `IGH.error` and returns `None` / empty so the
downstream component can bail friendly.

The API uses a single, uniform response envelope on every route::

    { "schema_version": 1,
      "project": { "bt_number", "project_id", "name" },
      "version_id": "...", "last_modified": "...Z",
      "<payload key(s) per route>": ... }

`get()` validates `schema_version`, caches `project` / `version_id` /
`last_modified` for the caller to read back (change-detection keys on
`version_id` / `last_modified`, NEVER on payload bytes), and returns the full
envelope. The per-route convenience methods return just that route's payload.
"""

import json

try:
    from typing import Any  # noqa: F401
except ImportError:
    pass  # IronPython 2.7

try:
    import System.IO  # type: ignore
    import System.Net  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io. {}".format(e))


class PHNavV1Client(object):
    """Transport + envelope handling for the PH-Navigator V1 read API."""

    EXPECTED_SCHEMA_VERSION = 1
    DEFAULT_BASE = "https://api.ph-nav.com/api/v1/gh"

    def __init__(self, _IGH, _bt_number, _url_base=None, _token=None, _version=None):
        # type: (gh_io.IGH, str, str | None, str | None, str | None) -> None
        self.IGH = _IGH
        self.bt_number = _bt_number
        self.url_base = _url_base or self.DEFAULT_BASE
        self.token = _token
        self.version = _version

        # -- Envelope metadata from the most recent successful `get()`. Components
        # -- read these back to surface project info + version freshness.
        self.project = None  # type: dict | None
        self.version_id = None  # type: str | None
        self.last_modified = None  # type: str | None

    # -------------------------------------------------------------------------
    # -- Core request

    def get(self, _path="", _pin_version=True, _query=None):
        # type: (str, bool, dict | None) -> dict | None
        """GET one route, parse once, validate the envelope.

        Returns the full envelope dict on success. On any transport / HTTP /
        parse / schema error, logs via `IGH.error` and returns `None`.
        """
        url = self._project_url(_path, _pin_version, _query)
        self._force_tls_12(url)

        try:
            response = self._client().DownloadString(url)
        except System.Net.WebException as e:
            self.IGH.error(self._format_http_error(e))
            return None
        except Exception as e:
            self.IGH.error("PH-Navigator request failed:\n{}".format(e))
            return None

        try:
            envelope = json.loads(response)  # type: dict
        except Exception as e:
            self.IGH.error("Failed to parse the PH-Navigator response as JSON:\n{}".format(e))
            return None

        if not self._validate_envelope(envelope):
            return None

        return envelope

    # -------------------------------------------------------------------------
    # -- Per-route convenience methods
    #
    # Each returns the route's payload (or `None` / empty on failure). Read
    # `self.version_id` / `self.last_modified` afterwards for change-detection
    # and freshness display.

    def _payload(self, _path, _key, _default, _pin_version=True, _query=None):
        # type: (str, str, Any, bool, dict | None) -> Any
        """GET one route and return a single payload key (or `None` on failure)."""
        envelope = self.get(_path, _pin_version, _query)
        if envelope is None:
            return None
        return envelope.get(_key, _default)

    def get_versions(self):
        # type: () -> list | None
        """Route 1 - `GET /`: saved versions, newest first.

        `[{ version_id, saved_at, name, kind }]`. No `?version=` pin - this is
        how the caller *discovers* version ids.
        """
        return self._payload("", "versions", [], _pin_version=False)

    def get_constructions_hbjson(self):
        # type: () -> dict | None
        """Route 2 - `GET /constructions/hbjson`: `{ name: OpaqueConstruction.to_dict() }`.

        Opts into `on_missing_thermal=user_defaults`: a material missing only its
        thermal-mass fields (density / specific-heat) is exported with PH-neutral
        defaults + an envelope `warning` (surfaced automatically), instead of the
        whole export failing with 422. Missing `conductivity` still 422s.
        """
        return self._payload(
            "/constructions/hbjson", "hb_constructions", {}, _query={"on_missing_thermal": "user_defaults"}
        )

    def get_aperture_types(self):
        # type: () -> dict | None
        """Route 3 - `GET /aperture-types`: `{ name: <denormalized window-type grid> }`."""
        return self._payload("/aperture-types", "aperture_types", {})

    def get_aperture_constructions(self):
        # type: () -> dict | None
        """Route 4 - `GET /aperture-constructions/hbjson`: `{ element_id: WindowConstruction.to_dict() }`."""
        return self._payload("/aperture-constructions/hbjson", "hb_constructions", {})

    def get_table(self, _table_name):
        # type: (str) -> tuple[list | None, list | None]
        """Route 5 - `GET /tables/{name}`: generic element table.

        Returns `(records, field_defs)`, or `(None, None)` on failure. An empty
        table is a success with `([], field_defs)`, not an error.
        """
        envelope = self.get("/tables/{}".format(_table_name))
        if envelope is None:
            return None, None
        return envelope.get("records", []), envelope.get("field_defs", [])

    # -------------------------------------------------------------------------
    # -- Transport helpers

    def _project_url(self, _path="", _pin_version=True, _query=None):
        # type: (str, bool, dict | None) -> str
        """Build a route URL: `{base}/projects/{bt_number}{path}` + query string.

        Appends `?version=` when a version is pinned, plus any extra `_query`
        params (e.g. `on_missing_thermal`). Keys are sorted for stable output.
        """
        url = "{}/projects/{}{}".format(self.url_base, self.bt_number, _path)
        params = {}  # type: dict
        if _pin_version and self.version:
            params["version"] = self.version
        if _query:
            params.update(_query)
        if params:
            url += "?" + "&".join("{}={}".format(k, params[k]) for k in sorted(params))
        return url

    def _force_tls_12(self, _url):
        # type: (str) -> None
        """Force TLS 1.2 for https downloads; warn on legacy .NET that lacks it."""
        try:
            System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12
        except AttributeError:
            # -- TLS 1.2 is not provided by MacOS .NET in Rhino 5
            if _url.lower().startswith("https"):
                self.IGH.error("This system lacks the necessary security libraries to download over https.")

    def _client(self):
        # type: () -> System.Net.WebClient
        """Build a configured `WebClient`: JSON headers + Bearer token only when set."""
        client = System.Net.WebClient()
        client.Headers.Add("Content-type", "application/json")
        # -- Send the auth header ONLY when a token is set. Anonymous read must
        # -- send no header at all (V0's `Bearer None` bug is deliberately gone).
        if self.token:
            client.Headers.Add("Authorization", "Bearer {}".format(self.token))
        return client

    # -------------------------------------------------------------------------
    # -- Envelope + error handling

    def _validate_envelope(self, _envelope):
        # type: (dict) -> bool
        """Check `schema_version` and cache `project` / `version_id` / `last_modified`."""
        schema_version = _envelope.get("schema_version")
        if schema_version != self.EXPECTED_SCHEMA_VERSION:
            self.IGH.error(
                "PH-Navigator returned schema_version={}, but this plugin expects {}. "
                "The server has moved ahead of the plugin - please update HBPH+.".format(
                    schema_version, self.EXPECTED_SCHEMA_VERSION
                )
            )
            return False

        self.project = _envelope.get("project")
        self.version_id = _envelope.get("version_id")
        self.last_modified = _envelope.get("last_modified")
        self._surface_warnings(_envelope)
        return True

    def _surface_warnings(self, _envelope):
        # type: (dict) -> None
        """Surface any envelope `warnings` (non-fatal notes) as `IGH.warning`s.

        `warnings` lives on the shared envelope, so this fires for every route
        (empty `[]` = no-op). Each `{code, message, details}` mirrors the error
        envelope, so `_format_details` renders the `details` bag unchanged (e.g.
        which `assembly` / `project_material_id` got defaulted thermal props).
        """
        for warning in _envelope.get("warnings") or []:
            message = warning.get("message") or warning.get("code") or "(warning)"
            detail = self._format_details(warning.get("details"))
            if detail:
                message = "{}\n{}".format(message, detail)
            self.IGH.warning(message)

    def _format_http_error(self, _web_exception):
        # type: (System.Net.WebException) -> str
        """Turn a `WebException` into a readable message using the status code + JSON body."""
        response = _web_exception.Response
        if response is None:
            # -- No HTTP response at all (DNS failure, connection refused, timeout, ...)
            return "Could not reach the PH-Navigator server at:\n{}\n{}".format(
                self.url_base, _web_exception.Message
            )

        status = int(response.StatusCode)
        body = self._read_error_body(response)
        message = body.get("message") or "(no message from server)"
        hint = self._http_status_hint(status, body)

        msg = "PH-Navigator request failed [HTTP {}]: {}".format(status, message)
        if hint:
            msg += "\n{}".format(hint)
        return msg

    # -- Short, actionable client-side guidance per status code. The server's own
    # -- `message` (surfaced by `_format_http_error`) says *what* failed; these add
    # -- *what to do about it* for the codes the API contract defines. Codes that
    # -- carry server-listed `details` (409 duplicate_names, 422 valid_names) need
    # -- no entry - `_format_details` renders those generically.
    STATUS_HINTS = {
        404: "Unknown project number or version id. Check the '_project_number' input.",
        401: "The access token was rejected (invalid, expired, or revoked).",
        403: "The access token is scoped to a different project.",
        429: "Rate-limited by the server. Wait a moment and try again.",
    }

    def _http_status_hint(self, _status, _body):
        # type: (int, dict) -> str
        """Client-side guidance for a status code, plus any server-listed `details`."""
        lines = []
        if _status in self.STATUS_HINTS:
            lines.append(self.STATUS_HINTS[_status])
        details = self._format_details(_body.get("details"))
        if details:
            lines.append(details)
        return "\n".join(lines)

    def _format_details(self, _details):
        # type: (dict | None) -> str
        """Render the error `details` generically (no hardcoded keys), one line per field.

        Lists are comma-joined (e.g. `duplicate_names` on 409, `valid_names` on 422,
        `missing` on a material-export 422); scalars are shown as-is (e.g. `assembly`,
        `project_material_id`) so the user sees *which* item failed, not just that one
        did. Empty / null values are skipped. Keys are sorted for stable output (JSON
        object order is not preserved through `json.loads` on IronPython 2.7).
        """
        if not _details:
            return ""
        lines = []
        for key in sorted(_details.keys()):
            value = _details[key]
            if isinstance(value, (list, tuple)):
                if not value:
                    continue
                shown = ", ".join(str(v) for v in value)
            elif value is None or value == "":
                continue
            else:
                shown = str(value)
            lines.append("{}: {}".format(key.replace("_", " "), shown))
        return "\n".join(lines)

    def _read_error_body(self, _response):
        # type: (System.Net.HttpWebResponse) -> dict
        """Read and JSON-parse the error response body; empty dict on any failure."""
        reader = None
        try:
            reader = System.IO.StreamReader(_response.GetResponseStream())
            raw = reader.ReadToEnd()
        except Exception:
            return {}
        finally:
            # -- Always close the stream, even if the read above threw.
            if reader is not None:
                reader.Close()
        try:
            return json.loads(raw)
        except Exception:
            return {}
