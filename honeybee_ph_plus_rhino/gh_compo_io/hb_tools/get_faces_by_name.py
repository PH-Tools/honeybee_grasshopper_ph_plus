# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Get Faces by Name."""

try:
    from typing import Any, Dict, List, Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room, face
except ImportError as e:
    raise ImportError("Failed to import honeybee")

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")


class GHCompo_GetFacesByName(object):
    def __init__(self, _IGH, _face_names, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, List[str], List[room.Room], List[Any], Dict[str, Any]) -> None
        self.IGH = _IGH
        self.face_names = _face_names or []
        self.hb_rooms = _hb_rooms or []

    def run(self):
        # type: () -> List[face.Face3D]
        hb_faces_ = []

        for hb_room in self.hb_rooms:
            all_room_faces = hb_room.faces + hb_room.apertures
            for hb_face in all_room_faces:
                for face_name in self.face_names:
                    if face_name in hb_face.display_name:
                        self.face_names.remove(face_name)
                        hb_faces_.append(hb_face.duplicate())
                        break

        if len(self.face_names) > 0:
            self.IGH.warning(
                "Failed to find the following faces: {}".format(self.face_names)
            )

        return hb_faces_
