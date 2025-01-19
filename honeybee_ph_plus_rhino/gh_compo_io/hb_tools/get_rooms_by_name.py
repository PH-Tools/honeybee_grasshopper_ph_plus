# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Get Rooms by Name."""

try:
    from typing import Any, Dict, List, Tuple
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee import room
except ImportError as e:
    raise ImportError("Failed to import honeybee")

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")


class GHCompo_GetRoomsByName(object):
    def __init__(self, _IGH, _room_names, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, List[str], List[room.Room], List[Any], Dict[str, Any]) -> None
        self.IGH = _IGH
        self.room_names = _room_names or []
        self.hb_rooms = _hb_rooms or []

    def run(self):
        # type: () -> List[room.Room]
        hb_rooms_ = []

        for hb_room in self.hb_rooms:
            for room_name in self.room_names:
                if room_name in hb_room.display_name:
                    self.room_names.remove(room_name)
                    hb_rooms_.append(hb_room.duplicate())
                    break

        if len(self.room_names) > 0:
            self.IGH.warning(
                "Failed to find the following rooms: {}".format(self.room_names)
            )

        return hb_rooms_
