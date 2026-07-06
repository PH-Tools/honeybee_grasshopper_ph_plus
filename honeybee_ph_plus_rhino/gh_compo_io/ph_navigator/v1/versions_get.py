# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - PH-Nav Get Versions."""

try:
    from typing import Any  # noqa: F401
except ImportError:
    pass  # IronPython 2.7

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io. {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1.client import PHNavV1Client
except ImportError as e:
    raise ImportError("\nFailed to import PHNavV1Client. {}".format(e))


class GHCompo_PHNavV1GetVersions(object):
    """List a PH-Navigator project's saved versions so a user can pin a `version_id`.

    Route 1 (`GET /`) of the V1 read API. The output `version_ids_` feeds the
    `_version` input on the other `PH-Nav Get ...` components for pinned reads
    (certification-archive use case). With no pin, those components read the
    project's latest saved version.
    """

    def __init__(self, _IGH, _project_number, _url_base, _token, _get, *args, **kwargs):
        # type: (gh_io.IGH, str, str | None, str | None, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.project_number = _project_number
        self.url_base = _url_base
        self.token = _token
        self._get = _get

    @property
    def ready(self):
        # type: () -> bool
        return bool(self._get and self.project_number)

    def run(self):
        # type: () -> tuple[list, list, list, str | None]
        """Download the saved-version list and fan it out into parallel output ports."""
        if not self.ready:
            return [], [], [], None

        client = PHNavV1Client(self.IGH, self.project_number, self.url_base, self.token)
        versions = client.get_versions()
        if versions is None:
            # -- The client already surfaced the failure via IGH.error.
            return [], [], [], None

        if not versions:
            # -- Defensive only: PH-Navigator auto-creates a default 'working'
            # -- version at project creation, so a real project always has >= 1
            # -- saved version. A bad project number is a 404, handled upstream by
            # -- the client. This branch fires only if that invariant ever changes.
            self.IGH.warning("Project '{}' reported no saved versions.".format(self.project_number))

        # -- Keep the server's order (newest first); do not re-sort.
        version_ids = [v.get("version_id") for v in versions]
        version_rows = [self._version_row(v) for v in versions]
        kinds = [v.get("kind") for v in versions]

        return version_ids, version_rows, kinds, self._project_label(client.project)

    @staticmethod
    def _version_row(_version):
        # type: (dict) -> str
        """Format one saved version as `"{saved_at} · {name} · {kind}"` for a panel."""
        return u"{} · {} · {}".format(_version.get("saved_at"), _version.get("name"), _version.get("kind"))

    @staticmethod
    def _project_label(_project):
        # type: (dict | None) -> str | None
        """Format the envelope `project` as `"{bt_number} · {name}"` for display."""
        if not _project:
            return None
        return u"{} · {}".format(_project.get("bt_number"), _project.get("name"))
