# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - PH-Nav Get Constructions."""

import json

try:
    from typing import Any  # noqa: F401
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_energy.construction.opaque import OpaqueConstruction
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy. {}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io. {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection import CustomCollection
except ImportError as e:
    raise ImportError("\nFailed to import from honeybee_ph_plus_rhino {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1.client import PHNavV1Client
except ImportError as e:
    raise ImportError("\nFailed to import PHNavV1Client. {}".format(e))


class GHCompo_PHNavV1GetConstructions(object):
    """Download a PH-Navigator project's opaque assemblies and rebuild `OpaqueConstruction`s.

    Route 2 (`GET /constructions/hbjson`) of the V1 read API. The payload is full
    Honeybee `hbjson` (`{ "<assembly name>": OpaqueConstruction.to_dict() }`,
    single-encoded), so this is a dedicated build component rather than the generic
    Get Table. `from_dict` round-trips the rich PH props (PhColor, division grid,
    `honeybee_energy_ref` datasheet/photo refs, `ph_nav` external id) on its own.

    All transport / parse / envelope / error handling (including 409
    `duplicate_assembly_names`) lives in `PHNavV1Client`; a failure there returns
    `None` after logging via `IGH.error`.
    """

    def __init__(self, _IGH, _project_number, _version, _url_base, _token, _download, *args, **kwargs):
        # type: (gh_io.IGH, str, str | None, str | None, str | None, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.project_number = _project_number
        self.version = _version
        self.url_base = _url_base
        self.token = _token
        self.download = _download

    @property
    def ready(self):
        # type: () -> bool
        return bool(self.download and self.project_number)

    def run(self):
        # type: () -> tuple[CustomCollection | None, str | None, str | None]
        """Download the assemblies and rebuild them into Honeybee-Energy constructions."""
        if not self.ready:
            return None, None, None

        client = PHNavV1Client(self.IGH, self.project_number, self.url_base, self.token, self.version)
        hb_constructions = client.get_constructions_hbjson()
        if hb_constructions is None:
            # -- The client already surfaced the failure via IGH.error.
            return None, None, None

        # -- Build the debug preview BEFORE the rebuild, so it is still emitted if
        # -- from_dict raises on a malformed payload (the case it helps diagnose).
        json_preview = json.dumps(hb_constructions, indent=2, ensure_ascii=False)

        # -- Keyed by the server's assembly name, emitted as a CustomCollection to match
        # -- the Get Apertures constructions output (one consistent getter output type).
        try:
            constructions = {name: OpaqueConstruction.from_dict(d) for name, d in hb_constructions.items()}
        except Exception as e:
            self.IGH.error("Failed to rebuild Honeybee Constructions from the PH-Navigator data.\n{}".format(e))
            return None, client.last_modified, json_preview

        return CustomCollection.from_dict(constructions), client.last_modified, json_preview
