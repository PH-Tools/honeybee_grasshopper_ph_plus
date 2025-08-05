# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Create Steel-Stud Construction."""

try:
    from typing import Any
except ImportError as e:
    pass  # IronPython 2.7

try:
    from honeybee.typing import clean_and_id_ep_string, clean_ep_string
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.lib.materials import opaque_material_by_identifier
    from honeybee_energy.material.opaque import EnergyMaterial
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_energy_ph.properties.materials.opaque import EnergyMaterialPhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_utils.aisi_s250_21 import (
        STEEL_CONDUCTIVITY,
        StudSpacingInches,
        StudThicknessMil,
        calculate_stud_cavity_effective_u_value,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


def get_hb_material(material):
    # type: (str | EnergyMaterial) -> EnergyMaterial
    if isinstance(material, str):
        return opaque_material_by_identifier(material)  # type: ignore
    return material


def get_air_cavity_material(_thickness_mm):
    # type: (float) -> EnergyMaterial
    """Get an 'Air-Cavity' Honeybee-Energy Material with the specified thickness."""

    return EnergyMaterial(
        identifier="AirCavity",
        thickness=_thickness_mm / 1000,
        conductivity=0.0381,
        density=1.2,
        specific_heat=1000,
    )


def clean_construction_name(_name):
    # type: (str | None) -> str
    """Clean the construction name and return a valid EnergyPlus string."""

    return (
        clean_and_id_ep_string("SteelStudConstruction")
        if _name is None
        else clean_ep_string(_name)
    )


class GHCompo_CreateSteelStudConstruction(object):

    stud_depth_mm = ghio_validators.UnitMM("stud_depth_mm")
    stud_spacing_mm = ghio_validators.UnitMM("stud_spacing_mm", default=406.4)
    stud_thickness_mm = ghio_validators.UnitMM("stud_thickness_mm", default=1.0922)
    stud_flange_width_mm = ghio_validators.UnitMM("stud_flange_width_mm", default=41.275)
    steel_conductivity_W_m_K = ghio_validators.UnitW_MK(
        "steel_conductivity_W_m_K", default=495.0
    )
    R_SE = 0.17  # hr-ft2-F/Btu
    R_SI = 0.68  # hr-ft2-F/Btu

    def __init__(
        self,
        _IGH,
        _construction_name,
        _ext_claddings,
        _ext_insulations,
        _ext_sheathings,
        _stud_layer_insulation,
        _stud_depth_mm,
        _stud_spacing_mm,
        _stud_thickness_mm,
        _stud_flange_width_mm,
        _steel_conductivity_W_m_K,
        _int_layers,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, str, list[EnergyMaterial], list[EnergyMaterial], list[EnergyMaterial], EnergyMaterial, float, float, float, float, float, list[EnergyMaterial], *Any, **Any) -> None
        self.IGH = _IGH
        self.construction_name = clean_construction_name(_construction_name)
        self.ext_claddings = [get_hb_material(m) for m in _ext_claddings]
        self.ext_insulations = [get_hb_material(m) for m in _ext_insulations]
        self.ext_sheathings = [get_hb_material(m) for m in _ext_sheathings]

        self.stud_layer_insulation = get_hb_material(
            _stud_layer_insulation
        ) or get_air_cavity_material(_stud_thickness_mm or 88.9)
        self.stud_depth_mm = _stud_depth_mm
        self.stud_spacing_mm = _stud_spacing_mm
        self.stud_thickness_mm = _stud_thickness_mm
        self.stud_flange_width_mm = _stud_flange_width_mm
        self.steel_conductivity_W_m_K = _steel_conductivity_W_m_K

        self._int_layers = [get_hb_material(m) for m in _int_layers]

    @property
    def r_IP_value_ext_cladding(self):
        # type: () -> float
        """Returns the R-Value of the external cladding in IP units."""

        # Get the IP R-Value of the external cladding
        total_r_value = 0.0
        for material in self.ext_claddings:
            total_r_value += material.r_value

        # Convert to IP units
        r_value_ip = convert(total_r_value, "M2-K/W", "HR-FT2-F/BTU") or 0.0
        return r_value_ip

    @property
    def r_IP_value_ext_insulation(self):
        # type: () -> float
        """Returns the R-Value of the external insulation in IP units."""

        # Get the IP R-Value of the external insulation
        total_r_value = 0.0
        for material in self.ext_insulations:
            total_r_value += material.r_value

        # Convert to IP units
        r_value_ip = convert(total_r_value, "M2-K/W", "HR-FT2-F/BTU") or 0.0
        return r_value_ip

    @property
    def r_IP_value_ext_sheathing(self):
        # type: () -> float
        """Returns the R-Value of the external sheathing in IP units."""

        # Get the IP R-Value of the external sheathing
        total_r_value = 0.0
        for material in self.ext_sheathings:
            total_r_value += material.r_value

        # Convert to IP units
        r_value_ip = convert(total_r_value, "M2-K/W", "HR-FT2-F/BTU") or 0.0
        return r_value_ip

    @property
    def r_IP_value_stud_cavity_insulation(self):
        # type: () -> float
        """Returns the R-Value of the stud cavity insulation in IP units."""
        return (
            convert(self.stud_layer_insulation.r_value, "M2-K/W", "HR-FT2-F/BTU") or 0.0
        )

    @property
    def r_IP_value_int_sheathing(self):
        # type: () -> float
        """Returns the R-Value of the internal sheathing in IP units."""

        # Get the IP R-Value of the internal sheathing
        total_r_value = 0.0
        for material in self._int_layers:
            total_r_value += material.r_value

        # Convert to IP units
        r_value_ip = convert(total_r_value, "M2-K/W", "HR-FT2-F/BTU") or 0.0
        return r_value_ip

    @property
    def stud_spacing_inch(self):
        # type: () -> StudSpacingInches
        """Returns a StudSpacingInches enum object."""

        stud_spacing_inches = convert(self.stud_spacing_mm, "MM", "INCH") or 16.0

        # Find the nearest stud spacing in inches
        ALLOWED = [int(_) for _ in StudSpacingInches.allowed]
        return StudSpacingInches(min(ALLOWED, key=lambda x: abs(x - stud_spacing_inches)))

    @property
    def stud_thickness_mils(self):
        # type: () -> StudThicknessMil
        """Returns a StudThicknessMil enum object."""

        stud_thickness_mil = convert(self.stud_thickness_mm, "MM", "MIL") or 43.0

        # Find the nearest stud thickness in mils
        ALLOWED = [int(_) for _ in StudThicknessMil.allowed]
        return StudThicknessMil(min(ALLOWED, key=lambda x: abs(x - stud_thickness_mil)))

    @property
    def stud_flange_width_inch(self):
        # type: () -> float
        """Returns the stud flange width in inches."""

        return convert(self.stud_flange_width_mm, "MM", "INCH") or 1.625

    @property
    def stud_depth_inch(self):
        # type: () -> float
        """Returns the stud depth in inches."""
        if not self.stud_depth_mm:
            depth = convert(self.stud_layer_insulation.thickness, "M", "INCH")
        else:
            depth = convert(self.stud_depth_mm, "MM", "INCH")
        if not depth:
            raise Exception("Error getting Stud depth?")
        return depth

    @property
    def stud_depth_m(self):
        # type: () -> float
        """Returns the stud depth in meters."""
        if not self.stud_depth_mm:
            depth = self.stud_layer_insulation.thickness
        else:
            depth = self.stud_depth_mm / 1000
        return depth

    @property
    def steel_conductivity(self):
        # type: () -> float
        """Returns the steel conductivity in BTU/HR-FT-F."""

        conductivity_IP = convert(self.steel_conductivity_W_m_K, "W/MK", "BTU/HR-FT-F")
        if not conductivity_IP:
            conductivity_IP = STEEL_CONDUCTIVITY[self.stud_thickness_mils]
        return conductivity_IP

    def get_stud_layer_u_value(self):
        # type: () -> float
        """Calculate the U-Value of the stud layer using the 'calculate_stud_cavity_effective_u_value' function."""

        print("- " * 20)
        print("MATERIAL LAYERS:")
        print("R-se=R-{:.2f}".format(self.R_SE))
        print("r_IP_value_ext_cladding=R-{:.2f}".format(self.r_IP_value_ext_cladding))
        print("r_IP_value_ext_insulation=R-{:.2f}".format(self.r_IP_value_ext_insulation))
        print("r_IP_value_ext_sheathing=R-{:.2f}".format(self.r_IP_value_ext_sheathing))
        print(
            "r_IP_value_stud_cavity_insulation=R-{:.2f}".format(
                self.r_IP_value_stud_cavity_insulation
            )
        )
        print("r_IP_value_int_sheathing=R-{:.2f}".format(self.r_IP_value_int_sheathing))
        print("R-si=R-{:.2f}".format(self.R_SI))
        print("- " * 20)
        print("STEEL STUD ATTRIBUTES:")
        print("stud_spacing_inch={:.2f}".format(float(self.stud_spacing_inch.value)))
        print("stud_thickness_mils={:.0f}".format(float(self.stud_thickness_mils.value)))
        print("stud_flange_width_inch={:.3f}".format(self.stud_flange_width_inch))
        print("stud_depth_inch={:.2f}".format(self.stud_depth_inch))
        print("steel_conductivity={:.0f}".format(self.steel_conductivity))

        # Note: all values need to be converted to 'IP' units for this calculation
        u_IP = calculate_stud_cavity_effective_u_value(
            _r_ext_cladding=self.r_IP_value_ext_cladding,
            _r_ext_insulation=self.r_IP_value_ext_insulation,
            _r_ext_sheathing=self.r_IP_value_ext_sheathing,
            _r_cavity_insulation=self.r_IP_value_stud_cavity_insulation,
            _stud_spacing_inch=self.stud_spacing_inch,
            _stud_thickness_mil=self.stud_thickness_mils,
            _stud_flange_width_inch=self.stud_flange_width_inch,
            _stud_depth_inch=self.stud_depth_inch,
            _steel_conductivity=self.steel_conductivity,
            _r_int_sheathing=self.r_IP_value_int_sheathing,
            _r_se=self.R_SE,
            _r_si=self.R_SI,
        )

        print(" -" * 20)
        print("RESULTS:")
        print("Stud-layer U-Value (IP): {:.3f} Btu/hr-ft2-F".format(u_IP))
        print("Stud-layer R-Value (IP): {:.2f} hr-ft2-F/Btu".format(1 / u_IP))
        percent_reduction = (
            self.r_IP_value_stud_cavity_insulation - 1 / u_IP
        ) / self.r_IP_value_stud_cavity_insulation
        print("Stud-layer: {:.1f} % reduction in R-Value".format(percent_reduction * 100))

        u_SI = convert(u_IP, "BTU/HR-FT2-F", "W/M2-K")
        print("Stud-Layer U-Value (SI): {:.3f} W/m2-K".format(u_SI))
        if not u_SI:
            raise Exception("Error converting {} t o W/m2-K".format(u_IP))

        conductivity_W_mk = u_SI * (
            self.stud_depth_m or self.stud_layer_insulation.thickness
        )
        print("Stud-Layer lambda: {:.3f} W/m-K".format(conductivity_W_mk))

        return conductivity_W_mk

    def get_new_energy_material(self):
        # type: () -> EnergyMaterial
        """Create a new Honeybee-EnergyMaterial for the steel-stud layer."""

        # Figure out the equivalent thermal conductivity of the stud layer
        stud_layer_eq_conductivity_w_mk = self.get_stud_layer_u_value()

        # Build the stud layer material
        new_eq_stud_layer_material = EnergyMaterial(
            identifier="Steel-Stud Layer [" + self.stud_layer_insulation.identifier + "]",
            thickness=self.stud_depth_mm or self.stud_layer_insulation.thickness,
            conductivity=stud_layer_eq_conductivity_w_mk,
            density=self.stud_layer_insulation.density,
            specific_heat=self.stud_layer_insulation.specific_heat,
            roughness=self.stud_layer_insulation.roughness,
        )

        # Store the 'stud_layer_insulation' Material in the Division Grid so we can
        # pull it back out later on when / if we need it (reporting, etc.)
        # We won't worry about storing the stud material itself, or stud spacing
        # since that is already used to calculate the Heterogeneous U-Value
        existing_prop_ph = getattr(
            self.stud_layer_insulation.properties, "ph"
        )  # type: EnergyMaterialPhProperties
        new_prop_ph = getattr(
            new_eq_stud_layer_material.properties, "ph"
        )  # type: EnergyMaterialPhProperties
        new_prop_ph.ph_color = existing_prop_ph.ph_color
        new_prop_ph.divisions.steel_stud_spacing_mm = self.stud_spacing_mm
        new_prop_ph.divisions.set_row_heights([1])
        new_prop_ph.divisions.set_column_widths([1])
        new_prop_ph.divisions.set_cell_material(0, 0, self.stud_layer_insulation)
        return new_eq_stud_layer_material

    def get_construction_materials(self):
        # type: () -> list[EnergyMaterial]
        return (
            self.ext_claddings
            + self.ext_insulations
            + self.ext_sheathings
            + [self.get_new_energy_material()]
            + self._int_layers
        )

    def run(self):
        # type: () -> OpaqueConstruction | None
        """Return a new 'Steel-Stud' Honeybee-Energy Construction."""

        constr = OpaqueConstruction(
            self.construction_name, self.get_construction_materials()
        )
        constr.display_name = self.construction_name

        return constr
