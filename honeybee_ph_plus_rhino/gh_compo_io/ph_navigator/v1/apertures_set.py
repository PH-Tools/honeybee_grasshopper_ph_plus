# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - PH-Nav Set Apertures."""

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
    from System import Object  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee: {}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io. {}".format(e))

try:
    from honeybee_ph.properties.aperture import AperturePsiInstalls
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph: {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection import CustomCollection
except ImportError as e:
    raise ImportError("\nFailed to import from honeybee_ph_plus_rhino {}".format(e))

# -- top / right / bottom / left, the PhWindowFrame element order. Shared with the
# -- builder's output order via AperturePsiInstalls so the two cannot drift apart.
SIDES = AperturePsiInstalls.SIDES


class GHCompo_PHNavV1SetApertures(object):
    """Assign PH-Navigator's per-edge Install Types onto Honeybee Apertures.

    The companion to 'HBPH+ - PH-Nav Get Apertures': that component downloads the
    per-edge psi-install conditions into an `install_types_` collection keyed by
    element type-name, and this one applies them to the Apertures actually placed in
    the model.

    Matching is by KEY, not by tree position. Each Aperture is looked up by its
    `display_name`, which is the name 'HBPH+ - Create Window Geometry' stamped on the
    surface it was built from (`"{type}_C{col}_R{row}"`). That makes the component
    immune to how the Aperture tree happens to be grafted or flattened - the failure
    this design exists to avoid is a positional match silently applying one element's
    psi-installs to every window in a branch. An Aperture whose name is not in the
    collection is passed through untouched and reported, never guessed at.

    Only the Aperture is modified. The window construction is never touched or
    duplicated: per-window install condition is aperture-INSTANCE data, resolved
    against the construction's frame-element defaults downstream by
    `honeybee_ph_utils.aperture_psi_install`. See `honeybee_grasshopper_ph` issue #59.
    """

    def __init__(self, _IGH, _apertures, _install_types, *args, **kwargs):
        # type: (gh_io.IGH, DataTree[Aperture], CustomCollection | None, *Any, **Any) -> None
        self.IGH = _IGH
        self.apertures = _apertures
        self.install_types = _install_types

    @property
    def ready(self):
        # type: () -> bool
        """True if there are both Apertures to modify and Install Types to assign."""
        if self.apertures is None or len(self.apertures.Branches) == 0:
            return False
        return bool(self.install_types) and len(self.install_types) > 0

    def run(self):
        # type: () -> tuple[DataTree[Aperture], list[str]]
        """Return the Apertures with their per-edge Install Types assigned, plus a report.

        The input tree structure is preserved path for path: this is a decorator, not
        a re-organizer, and the caller's downstream wiring should not shift underneath
        it. With no Install Types to apply the Apertures pass through unchanged.
        """
        if not self.ready:
            return self.apertures, []

        output_ = DataTree[Object]()
        unmatched = []  # type: list[str]

        for branch_idx, apertures in enumerate(self.apertures.Branches):
            # -- Re-use the input path rather than GH_Path(branch_idx): a nested input
            # -- tree ({0;0}, {0;1}, ...) must not be silently flattened to {0}, {1}.
            output_.AddRange(
                [self._set_aperture(ap, unmatched) for ap in apertures],
                self.apertures.Paths[branch_idx],
            )

        return output_, self._build_report(unmatched)

    def _set_aperture(self, _aperture, _unmatched):
        # type: (Aperture, list[str]) -> Aperture
        """Return a duplicate of the Aperture with its four Install Type slots set.

        Unmatched Apertures are returned as-is (not duplicated) and recorded: leaving
        the slots `None` means 'inherit the construction frame default', which is the
        honest answer when PH-Navigator sent nothing for this window.
        """
        install_types = self.install_types.get(_aperture.display_name, None)
        if install_types is None:
            _unmatched.append(_aperture.display_name)
            return _aperture

        if len(install_types) != len(SIDES):
            # -- Refuse a partial write: zip() would truncate silently and leave some
            # -- edges inheriting while others were assigned, which is unreadable in a
            # -- model and hard to trace back here.
            _unmatched.append(_aperture.display_name)
            self.IGH.warning(
                "Expected {} Install Types for Aperture '{}', got {}. Skipping it.".format(
                    len(SIDES), _aperture.display_name, len(install_types)
                )
            )
            return _aperture

        dup_aperture = _aperture.duplicate()  # type: Aperture
        aperture_install_types = dup_aperture.properties.ph.install_types
        for side, install_type in zip(SIDES, install_types):
            setattr(aperture_install_types, side, install_type)
        return dup_aperture

    def _build_report(self, _unmatched):
        # type: (list[str]) -> list[str]
        """Summarise the run, and warn on the canvas if any Aperture went unmatched."""
        if not _unmatched:
            return ["All {} Aperture(s) matched an Install Type set.".format(self._aperture_count)]

        msg = (
            "{} of {} Aperture(s) did not match any key in the Install-Type collection "
            "and were left to inherit their construction's frame defaults. Check that the "
            "Aperture names match the 'srfc_names_' output of 'HBPH+ - Create Window Geometry'.".format(
                len(_unmatched), self._aperture_count
            )
        )
        self.IGH.warning(msg)
        return [msg] + sorted(set(_unmatched))

    @property
    def _aperture_count(self):
        # type: () -> int
        """The total number of Apertures across every branch of the input tree."""
        return sum(len(branch) for branch in self.apertures.Branches)

    def __str__(self):
        return "{}()".format(self.__class__.__name__)
