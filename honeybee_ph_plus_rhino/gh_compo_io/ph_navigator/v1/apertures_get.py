# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - PH-Nav Get Apertures."""

import json

try:
    from typing import Any  # noqa: F401
except ImportError:
    pass  # IronPython 2.7

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io. {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection import CustomCollection

    # -- Parse with the V1 schema fork: the route-3 payload emits explicit JSON `null`
    # -- for unset numeric fields (e.g. `psi_install_w_mk`), which the V0 schema's
    # -- `float(dict.get(...))` cannot handle. `v1/window_types_schema.py` is null-safe.
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1.window_types_schema import ApertureTypeData

    # -- The build pipeline transforms schema objects -> HBPH objects (it never parses
    # -- raw dicts), so it does not diverge between V0/V1 and the frozen V0 helpers are
    # -- reused directly on our (duck-type-identical) V1 schema objects.
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v0.window_types_get import (
        create_hbph_glazing_types,
        create_new_hbph_frame_elements,
        create_new_hbph_frames,
        create_hbph_window_unit_types,
        create_hbph_ep_constructions,
    )
except ImportError as e:
    raise ImportError("\nFailed to import from honeybee_ph_plus_rhino {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1.client import PHNavV1Client
except ImportError as e:
    raise ImportError("\nFailed to import PHNavV1Client. {}".format(e))


class GHCompo_PHNavV1GetApertures(object):
    """Download a PH-Navigator project's aperture types and build HBPH window objects.

    Route 3 (`GET /aperture-types`) of the V1 read API. The payload is a
    denormalized grid per aperture type (`{ "<type name>": {...} }`); this component
    parses each into an `ApertureTypeData` and runs the shared build pipeline to emit
    two collections: `WindowUnitType`s (geometry) and `WindowConstruction`s (with rich
    `ph_frame` / `ph_glazing` props, U-value via ISO 10077-1).

    Route 4 (`GET /aperture-constructions/hbjson`) also exists, but only carries the
    minimal `EnergyWindowMaterialSimpleGlazSys` subset - strictly poorer than the
    local build here - so it is intentionally NOT called (see the phase doc). Building
    from route 3 alone gives both outputs from one request.

    All transport / parse / envelope / error handling (including 409
    `duplicate_aperture_type_names`) lives in `PHNavV1Client`; a failure there returns
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
        # type: () -> tuple[CustomCollection | None, CustomCollection | None, str | None, str | None]
        """Download the aperture types and build the window-unit-type + construction collections."""
        if not self.ready:
            return None, None, None, None

        client = PHNavV1Client(self.IGH, self.project_number, self.url_base, self.token, self.version)
        aperture_types_raw = client.get_aperture_types()
        if aperture_types_raw is None:
            # -- The client already surfaced the failure via IGH.error.
            return None, None, None, None

        # -- Build the debug preview BEFORE parsing, so a malformed payload can still
        # -- be inspected on the canvas (the case the preview exists to diagnose).
        json_preview = json.dumps(aperture_types_raw, indent=2, ensure_ascii=False)

        aperture_types = self._parse_aperture_types(aperture_types_raw)
        window_unit_types = CustomCollection.from_dict(create_hbph_window_unit_types(self.IGH, aperture_types))
        window_constructions = self._build_window_constructions(aperture_types)

        return window_unit_types, window_constructions, json_preview, client.last_modified

    def _parse_aperture_types(self, _raw):
        # type: (dict[str, dict]) -> list[ApertureTypeData]
        """Parse each raw aperture-type dict into an `ApertureTypeData` (skip + warn on failure)."""
        aperture_types = []
        for data in _raw.values():
            try:
                aperture_types.append(ApertureTypeData.from_dict(data))
            except Exception as e:
                self.IGH.warning("Failed to parse aperture type: {}".format(e))
        return aperture_types

    def _build_window_constructions(self, _aperture_types):
        # type: (list[ApertureTypeData]) -> CustomCollection
        """Build the `WindowConstruction` collection (glazings -> frames -> constructions)."""
        glazing_types = create_hbph_glazing_types(_aperture_types)
        frame_elements = create_new_hbph_frame_elements(_aperture_types)
        frame_types = create_new_hbph_frames(_aperture_types, frame_elements)
        return CustomCollection.from_dict(create_hbph_ep_constructions(_aperture_types, glazing_types, frame_types))
