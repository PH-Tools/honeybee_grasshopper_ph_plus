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
except Exception:
    pass  #  outside Rhino / Grasshopper

try:
    from honeybee.boundarycondition import Ground, Outdoors
    from honeybee.face import Face
    from honeybee.room import Room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.boundarycondition import Adiabatic
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_ph.properties.room import RoomPhProperties
    from honeybee_ph.space import Space
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
    """Check if the Honeybee-face is exposed to OUTDOORS or GROUND or ADIABATIC."""
    return isinstance(_face.boundary_condition, Outdoors) or isinstance(_face.boundary_condition, Ground) or isinstance(_face.boundary_condition, Adiabatic)


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

    def get_all_spaces(self):
        # type: () -> list[Space]
        """Get all the spaces from the Honeybee-Rooms."""
        all_spaces = [space for room in self.hb_rooms for space in getattr(room.properties, "ph").spaces]
        if not all_spaces:
            msg = "No Spaces found in Honeybee-Rooms." "\nBe sure to build Rooms before using this component."
            self.IGH.error(msg)
        return all_spaces

    def get_net_volume(self):
        # type: () -> float | None
        """Get total net volume (m3) from the Honeybee-Rooms."""
        rh_doc_unit = self.IGH.get_rhino_volume_unit_name()

        # --- Get total Net Volume
        vn50 = sum(space.net_volume for space in self.get_all_spaces())
        if vn50 is None:
            msg = "Failed to get Net Volume from Honeybee-Rooms"
            self.IGH.error(msg)
            return None

        # -- Convert to M3
        vn50_m3 = convert(vn50, rh_doc_unit, "M3")
        vn50_ft3 = convert(vn50, rh_doc_unit, "FT3")
        print("Total Net Volume: {:,.2f} M3 [{:,.2f} FT3]".format(vn50_m3, vn50_ft3))
        if vn50_m3 is None:
            msg = "Failed to convert net volume: '{}' to M3".format(vn50)
            self.IGH.error(msg)

        return vn50_m3

    def get_exposed_area(self):
        # type: () -> float | None
        """Get total exposed envelope face (m2) area from the Honeybee-Rooms."""
        exposed_area = sum(face.area for room in self.hb_rooms for face in room.faces if face_is_exposed(face))
        exposed_area_m2 = convert(exposed_area, self.IGH.get_rhino_areas_unit_name(), "M2")
        exposed_area_ft2 = convert(exposed_area_m2, "M2", "FT2")
        print("Total Envelope Area: {:,.2f} M2 [{:,.2f} FT2]".format(exposed_area_m2, exposed_area_ft2))
        if exposed_area_m2 is None:
            msg = "Failed to convert exposed area: '{}' to M2".format(exposed_area)
            self.IGH.error(msg)
            return None

        return exposed_area_m2

    def calculate_infiltration_rate_at_test_pressure(
        self,
        n_50,
        volume_m3,
        envelope_area_m2,
    ):
        # type: (float, float, float) -> float
        if n_50 < 0:
            raise ValueError("ACH50 must be non-negative")
        if volume_m3 <= 0 or envelope_area_m2 <= 0:
            raise ValueError("Volume and envelope_area must be positive")

        # Total volumetric flow at blower pressure
        q50 = n_50 * volume_m3 / 3600.0  # m3/s
        print(
            "Total Leakage Airflow at {:,.1f}-ACH@{:,.0f}Pa: {:,.6f} M3/S [{:,.3f} CFM]".format(
                self.ach_at_50Pa, 50.0, q50, convert(q50, "M3/S", "CFM")
            )
        )

        print(
            "Infiltration Rate at {:,.1f}-ACH@{:,.0f}Pa: {:,.6f} M3/S-M2 [{:,.3f} CFM/FT2]".format(
                self.ach_at_50Pa, 50.0, q50 / envelope_area_m2, convert(q50 / envelope_area_m2, "M3/S-M2", "CFM/FT2")
            )
        )
        return q50

    def calculate_infiltration_rate_at_resting_pressure(
        self,
        q50,
        envelope_area_m2,
        resting_pressure_Pa=4.0,
        blower_pressure_Pa=50.0,
        flow_exponent=0.65,
        air_density_kg_m3=1.2041,
    ):
        # type: (float, float, float, float, float, float) -> float
        """
        Convert ACH@50 to infiltration per exterior area at resting pressure (4Pa).

        Args:
            q_50 (float):
                Air changes per hour at 50 Pa [ACH]. Default: 1.0
            resting_pressure_Pa (float):
                Typical operating pressure [Pa]. Default: 4 Pa.
            blower_pressure_Pa (float):
                Reference blower-door pressure [Pa]. Default: 50 Pa.
            flow_exponent (float):
                Flow exponent n [-]. Default: 0.65.
            air_density_kg_m3 (float):
                Air density [kg/m3].

        Returns:
            float:
                Infiltration rate per exterior area at resting pressure
                [m3/s-m2].
        """
        if envelope_area_m2 <= 0:
            raise ValueError("Envelope-Area must be positive. Got: '{}' ?".format(envelope_area_m2))
    
        # Total mass flow at blower pressure
        m50 = q50 * air_density_kg_m3  # kg/s

        # Total leakage coefficient
        C_total = m50 / (blower_pressure_Pa**flow_exponent)

        # Normalize by envelope area
        C_area = C_total / envelope_area_m2  # kg/(m2·s·Pa^n)

        # Mass flow per area at resting pressure
        m_rest_area = C_area * (resting_pressure_Pa**flow_exponent)

        # Convert back to volumetric flow per area
        q_rest_area = m_rest_area / air_density_kg_m3
        print(
            "Total Leakage Airflow at {:,.1f}-ACH@{:,.0f}Pa: {:,.6f} M3/S [{:,.3f} CFM]".format(
                self.ach_at_50Pa, resting_pressure_Pa, q_rest_area, convert(q_rest_area, "M3/S", "CFM")
            )
        )
        print(
            "Infiltration Rate at {:,.1f}-ACH@{:,.0f}Pa: {:,.6f} M3/S-M2 [{:,.3f} CFM/FT2]".format(
                self.ach_at_50Pa, resting_pressure_Pa, q_rest_area, convert(q_rest_area, "M3/S-M2", "CFM/FT2")  
            )
        )
        return q_rest_area

    def run(self):
        # type: () -> tuple[float, float] | tuple[None, None]
        """Calculate Infiltration Rate (M3/S-M2) from ACH at 50Pa."""

        if not self.ready:
            return None, None

        # -- Get Total Building Net Volume (M3)
        vn50_m3 = self.get_net_volume()
        if vn50_m3 is None:
            return None, None

        # -- Get Total Building Exposed Area (M2)
        exposed_area_m2 = self.get_exposed_area()
        if exposed_area_m2 is None:
            return None, None

        # -- Calculate the Airflow Leakage Rate(M3/S-M2)
        infiltration_rate_at_50Pa = self.calculate_infiltration_rate_at_test_pressure(
            self.ach_at_50Pa,
            vn50_m3,
            exposed_area_m2,
        )
        infiltration_rate_at_4Pa = self.calculate_infiltration_rate_at_resting_pressure(
            infiltration_rate_at_50Pa,
            exposed_area_m2,
            resting_pressure_Pa=4.0,
            blower_pressure_Pa=50.0,
            flow_exponent=0.65,
            air_density_kg_m3=1.0,
        )

        return infiltration_rate_at_4Pa, infiltration_rate_at_50Pa
