# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Infiltration from ACH."""


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
    from honeybee.room import Room
    from honeybee.face import Face
    from honeybee.boundarycondition import Outdoors, Ground
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph.properties.room import RoomPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


def face_is_exposed(_face):
    # type: (Face) -> bool
    """Check if the Honeybee-face is exposed to OUTDOORS or GROUND."""
    return isinstance(_face.boundary_condition, Outdoors) or isinstance(
        _face.boundary_condition, Ground
    )


class GHCompo_CalculateInfiltrationFromACH(object):

    def __init__(self, _IGH, _ach_at_50Pa, _hb_rooms, *args, **kwargs):
        # type: (gh_io.IGH, float, list[Room], *Any, **Any) -> None
        self.IGH = _IGH
        self.ach_at_50Pa = _ach_at_50Pa
        self.hb_rooms = _hb_rooms

    @property
    def ready(self):
        # type: () -> bool

        if self.ach_at_50Pa is None:
            return False

        if not self.hb_rooms:
            return False

        # -- Warn if no Spaces found
        for room in self.hb_rooms:
            room_prop_ph = getattr(room.properties, "ph")  # type: RoomPhProperties
            if not room_prop_ph.spaces:
                msg = "No spaces found in Room: '{}'".format(room.display_name)
                self.IGH.error(msg)
                return False

        return True

    def get_net_volume(self):
        # type: () -> float | None
        """Get total net volume (m3) from the Honeybee-Rooms."""
        rh_doc_unit = self.IGH.get_rhino_volume_unit_name()

        # --- Get total Net Volume
        vn50 = sum(
            space.net_volume
            for room in self.hb_rooms
            for space in getattr(room.properties, "ph").spaces
        )
        print("Total Net Volume: {:,.2f} [{}]".format(vn50, rh_doc_unit))
        
        # -- Convert to M3
        vn50_m3 = convert(vn50, rh_doc_unit, "M3")
        print("Total Net Volume: {:,.2f} [M3]".format(vn50_m3))
        if vn50_m3 is None:
            msg = "Failed to convert net volume: '{}' to M3".format(vn50)
            self.IGH.error(msg)

        return vn50_m3

    def get_exposed_area(self):
        # type: () -> float | None
        """Get total exposed envelope face (m2) area from the Honeybee-Rooms."""
        exposed_area = sum(
            face.area
            for room in self.hb_rooms
            for face in room.faces
            if face_is_exposed(face)
        )
        print(
            "Total Exposed Area: {:,.2f} [{}]".format(
                exposed_area, self.IGH.get_rhino_areas_unit_name()
            )
        )
        exposed_area_m2 = convert(
            exposed_area, self.IGH.get_rhino_areas_unit_name(), "M2"
        )
        print("Total Exposed Area: {:,.2f} [M2]".format(exposed_area_m2))
        if exposed_area_m2 is None:
            msg = "Failed to convert exposed area: '{}' to M2".format(exposed_area)
            self.IGH.error(msg)
            return None
        
        return exposed_area_m2

    def run(self):
        # type: () -> float | None
        """Calculate Infiltration Rate (M3/S-M2) from ACH at 50Pa."""

        if not self.ready:
            return None

        # --
        vn50_m3 = self.get_net_volume()
        if vn50_m3 is None:
            return None

        # --
        airflow_m3_second = (vn50_m3 * self.ach_at_50Pa) / 3600
        print("Total Airflow: {:,.4f} [M3/S]".format(airflow_m3_second))

        # --
        exposed_area_m2 = self.get_exposed_area()
        if exposed_area_m2 is None:
            return None

        # --
        infiltration_rate = airflow_m3_second / exposed_area_m2
        print(
            "Infiltration Rate: {:,.4f}-M3/S / {:,.2f}-M2 = {:,.5f} [M3/S-M2]".format(
                airflow_m3_second, exposed_area_m2, infiltration_rate
            )
        )

        return infiltration_rate
