# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Group Connected Faces."""


try:
    from typing import Any
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
    def __init__(self, _IGH, _hb_faces, _tolerance, _angle_tolerance_degrees, *args, **kwargs):
        # type: (gh_io.IGH, DataTree[face.Face], float | None, float | None, *Any, **Any) -> None
        self.IGH = _IGH
        self.hb_faces = _hb_faces or []
        self._tolerance = _tolerance
        self._angle_tolerance_degrees = _angle_tolerance_degrees

    @property
    def tolerance(self):
        # type: () -> float
        """Get the absolute tolerance for grouping faces."""
        return self._tolerance or self.IGH.ghdoc.ModelAbsoluteTolerance

    @property
    def angle_tolerance_degrees(self):
        # type: () -> float
        """Get the angle tolerance for grouping faces in degrees."""
        return self._angle_tolerance_degrees or self.IGH.ghdoc.ModelAngleToleranceDegrees

    def run(self):
        # type: () -> list[face.Face3D]
        hb_faces_ = DataTree[Object]()
        for i, b in enumerate(self.hb_faces.Branches):  # type: ignore
            for j, group in enumerate(face_tools.group_hb_faces(b, self.tolerance, self.angle_tolerance_degrees)):
                hb_faces_.AddRange(group, GH_Path(i, j))  # type: ignore
        return hb_faces_
