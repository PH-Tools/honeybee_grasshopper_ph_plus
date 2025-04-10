# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Create Clipping Plane Set."""

try:
    from typing import Any
except ImportError:
    pass # Python 2.7

try:
    from Rhino import Geometry as rg  # type: ignore
except ImportError:
    pass # Outside Rhino

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")


class ClippingPlaneLocation(object):
    """Temporary object to store Clipping Plane location and direction data."""

    def __init__(self, _origin, _normal):
        # type: (rg.Point3d, rg.Vector3d) -> None
        self.origin = _origin # type: rg.Point3d
        self.normal = _normal # type: rg.Vector3d

    def __str__(self):
        return "{}(origin={}, normal={})".format(
            self.__class__.__name__, self.origin, self.normal
        )

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)


def from_plane_and_offsets(_IGH, _plane, _offsets):
    #type: (gh_io.IGH, rg.Plane, tuple[float, float]) -> list[ClippingPlaneLocation]
    """Create a list of ClippingPlaneLocation objects from a plane and a list of offsets."""
    cps_ = []
    offset_plane_1 = _IGH.ghc.PlaneOffset(base_plane=_plane, offset=_offsets[0]) # type: rg.Plane
    cps_.append(ClippingPlaneLocation(offset_plane_1.Origin, offset_plane_1.Normal))

    offset_plane_2 = _IGH.ghc.PlaneOffset(base_plane=_plane, offset=_offsets[1]) # type: rg.Plane
    offset_plane_2 = _IGH.ghc.FlipPlane(offset_plane_2)
    cps_.append(ClippingPlaneLocation(offset_plane_2.Origin, offset_plane_2.Normal))

    return cps_

class GHCompo_CreateClippingPlaneSet(object):

    def __init__(
        self, _IGH, _plane, _offsets, *args, **kwargs
    ):
        # type: (gh_io.IGH, rg.Plane, list[float], *Any, **Any) -> None
        self.IGH = _IGH
        self.plane = _plane
        self.offsets = _offsets or [1.0, -1.0]
        
    def run(self):
        # type: () -> list[ClippingPlaneLocation] | None
        if not self.plane:
            return None
        
        if not len(self.offsets) >= 2:
            msg = "Error: The offsets list must contain at least two values."
            self.IGH.error(msg)
            return None
        
        return from_plane_and_offsets(self.IGH, self.plane, (self.offsets[0], self.offsets[1]))
        
