# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Get Coplanar Face Groups."""

import math

try:
    from typing import Any, TypeVar, Union
except ImportError:
    pass  # IronPython 2.7

try:
    from System import Object # type: ignore
    from Grasshopper import DataTree # type: ignore
    from Grasshopper.Kernel.Data import GH_Path # type: ignore
except ImportError:
    raise ImportError("Failed to import Grasshopper libraries")

try:
    from honeybee.face import Face
    from honeybee.shade import Shade
except ImportError as e:
    raise ImportError("Failed to import honeybee")

try:
    T = TypeVar("T", bound="Union[Face, Shade]")
except Exception:
    pass  # IronPython 2.7

try:
    from honeybee_ph_utils.face_tools import sort_hb_faces_by_co_planar
except ImportError:
    raise ImportError("Failed to import honeybee_ph_utils")

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")


class GHCompo_GetCoPlanarFaceGroups(object):

    def __init__(self, IGH, _tolerance, _angle_tolerance_deg, _faces, *args, **kwargs):
        # type: (gh_io.IGH, float, float, list[Face], *Any, **Any) -> None
        self.IGH = IGH
        self._tolerance = _tolerance
        self._angle_tolerance_deg = _angle_tolerance_deg
        self.faces = _faces

    @property
    def tolerance(self):
        # type: () -> float
        return self._tolerance or self.IGH.ghdoc.ModelAbsoluteTolerance
    
    @property
    def angle_tolerance_deg(self):
        # type: () -> float
        return math.radians(self._angle_tolerance_deg or self.IGH.ghdoc.ModelAngleToleranceDegrees)

    def run(self):
        # type: () -> DataTree[list[Face | Shade]]

        output= DataTree[Object]()
        for i, group in enumerate(sort_hb_faces_by_co_planar(self.faces, self.tolerance, self.angle_tolerance_deg)):
            output.AddRange(group, GH_Path(i))
        
        return output
