# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Build HBPH Aperture 'Install Types' from the PH-Navigator route-3 `installs` block.

Not a component - a plain builder, parallel to the frame / glazing builders in
`v0/window_types_get.py`, but emitting aperture-INSTANCE data rather than
construction data.

The distinction matters and is the whole point of this module. Install condition
(mid-wall, buried jamb, party wall, mulled joint) is a property of *where a window
sits*, not of the window product, so it rides on the Aperture's PH-properties and
never on the shared WindowConstruction. Writing it into the construction is the
defect `honeybee_grasshopper_ph` issue #59 closed; see
`planning/features/phn-psi-install-per-edge/decisions.md` D-1.

PH-Navigator has already resolved each edge server-side (mull -> assigned ->
project default) and shipped the answer, so this module only translates - it never
re-derives a value. Two shapes arrive:

  * a library row, carrying an `apit_*` id, which becomes that id verbatim so the
    model round-trips back to PH-Navigator identifiably (D-4);
  * a mulled edge, carrying `null` id and name, which becomes an ordinary zero-psi
    Install Type under a deterministic content-keyed identifier (D-3). Content
    keying - never a uuid - is what makes a re-download idempotent instead of
    spraying hundreds of distinct single-use types into the HBJSON.
"""

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_energy_ph.construction.window import PhApertureInstallType, PhWindowFrame
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph: {}".format(e))

try:
    # -- Reuse the base repo's content-keying so anonymous Install Types built here
    # -- and ones built by hand on the canvas dedupe against each other.
    from honeybee_ph_rhino.gh_compo_io.apertures.win_create_install_type import (
        build_install_type,
        content_keyed_identifier,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino: {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1.window_types_schema import (
        ApertureTypeData,
        InstallData,
        InstallsData,
    )
except ImportError as e:
    raise ImportError("\nFailed to import from honeybee_ph_plus_rhino {}".format(e))


def _build_install_type(_install_data):
    # type: (InstallData) -> PhApertureInstallType
    """Translate one resolved edge into a new PhApertureInstallType."""
    if not _install_data.install_type_id:
        # -- Mulled edge: no library row to point at, so content-key it (D-3).
        return build_install_type(None, _install_data.psi_install_w_mk, _install_data.source)

    install_type = PhApertureInstallType(_install_data.install_type_id)
    install_type.display_name = _install_data.name or _install_data.install_type_id
    install_type.psi_install = _install_data.psi_install_w_mk
    install_type.source = _install_data.source
    return install_type


def _pooled_install_type(_install_data, _pool):
    # type: (InstallData | None, dict[str, PhApertureInstallType]) -> PhApertureInstallType | None
    """Return the pooled Install Type for one edge, building it on first sight.

    Pooling is by identifier, so a project with one Install Type across 200 windows
    produces one object rather than 200. `None` in means the server sent nothing for
    that side, and `None` out means 'inherit the construction frame default'.
    """
    if _install_data is None:
        return None

    if _install_data.install_type_id:
        identifier = _install_data.install_type_id
    else:
        identifier = content_keyed_identifier(_install_data.psi_install_w_mk)

    if identifier not in _pool:
        _pool[identifier] = _build_install_type(_install_data)
    return _pool[identifier]


def create_new_hbph_install_types(_aperture_types):
    # type: (list[ApertureTypeData]) -> dict[str, list[PhApertureInstallType | None]]
    """Build the per-element Install Types from the parsed PH-Navigator aperture types.

    Returns `{element_type_name: [top, right, bottom, left]}`, keyed to match the
    `constructions_` collection and the `srfc_names_` output of
    'HBPH+ - Create Window Geometry' (both `"{type}_C{col}_R{row}"`).

    Elements from a server that predates the `installs` contract carry no block at
    all and are skipped, so a legacy payload yields an empty dict rather than a
    collection full of nulls.
    """
    install_types_ = {}  # type: dict[str, list[PhApertureInstallType | None]]
    pool = {}  # type: dict[str, PhApertureInstallType]

    for aperture_type in _aperture_types:
        for element in aperture_type.elements:
            if element.installs is None:
                continue  # -- Legacy payload; nothing per-edge to deliver.

            install_types_[element.type_name] = [
                _pooled_install_type(element.installs.get_install_by_side(side), pool) for side in InstallsData.SIDES
            ]

    return install_types_


def create_effective_frames(_frame_types, _install_types):
    # type: (dict[str, PhWindowFrame], dict[str, list[PhApertureInstallType | None]]) -> dict[str, PhWindowFrame]
    """Build transient frames carrying the resolved per-edge psi-install, for U-w only.

    `iso_10077_1` includes the install psi in its U-w, so the EnergyPlus U-factor is
    psi-sensitive - and is wrong on a mulled edge while the frame still carries the
    uniform type default. Fixing that without writing instance data into the shared
    construction needs a throwaway duplicate, which is exactly what
    `honeybee_ph_utils.aperture_psi_install.resolve_effective_frame` does upstream for
    the same reason.

    These frames are for the U-w calculation and nothing else. They are never
    persisted: `WindowConstructionPhProperties.ph_frame` keeps the type defaults, and
    the per-edge truth lives on the Aperture (D-1 / D-5). `PhWindowFrame.__copy__`
    deep-copies all four elements, so the overwrite below cannot reach the shared
    `PhWindowFrameElement` pool.

    Returns `{element_type_name: PhWindowFrame}`, covering only the elements that
    actually have Install Types - anything else keeps its original frame.
    """
    effective_frames_ = {}  # type: dict[str, PhWindowFrame]

    for type_name, install_types in _install_types.items():
        frame = _frame_types.get(type_name, None)
        if frame is None:
            continue

        effective_frame = frame.duplicate()  # type: PhWindowFrame
        for side, install_type in zip(InstallsData.SIDES, install_types):
            if install_type is not None:
                getattr(effective_frame, side).psi_install = install_type.psi_install
        effective_frames_[type_name] = effective_frame

    return effective_frames_
