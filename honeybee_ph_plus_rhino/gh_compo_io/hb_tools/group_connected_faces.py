# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Group Connected Faces."""


try:
    from typing import Any, Dict, List, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from System import Object  # type: ignore
except:
    pass  #  outside Rhino / Grasshopper

try:
    from honeybee import face
except ImportError as e:
    raise ImportError("Failed to import honeybee")

try:
    from honeybee_ph_utils import face_tools
except ImportError:
    raise ImportError("Failed to import honeybee_ph_utils")

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")


class GHCompo_GroupConnectedFaces(object):
    def __init__(
        self, _IGH, _hb_faces, _tolerance, _angle_tolerance_degrees, *args, **kwargs
    ):
        # type: (gh_io.IGH, List[face.Face], Optional[float], Optional[float], List[Any], Dict[str, Any]) -> None
        self.IGH = _IGH
        self.hb_faces = _hb_faces or []
        self.tolerance = _tolerance or self.IGH.ghdoc.ModelAbsoluteTolerance
        self.angle_tolerance_degrees = (
            _angle_tolerance_degrees or self.IGH.ghdoc.ModelAngleToleranceDegrees
        )

    def run(self):
        # type: () -> List[face.Face3D]
        hb_faces_ = DataTree[Object]()
        face_groups = face_tools.group_hb_faces(
            self.hb_faces, self.tolerance, self.angle_tolerance_degrees
        )
        for i, l in enumerate(face_groups):
            hb_faces_.AddRange(l, GH_Path(i))
        return hb_faces_
