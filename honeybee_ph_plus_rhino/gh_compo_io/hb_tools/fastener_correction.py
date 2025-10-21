# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Add Fasteners to Construction."""

from math import pi

try:
    from honeybee_energy.construction.opaque import OpaqueConstruction
    from honeybee_energy.material.opaque import EnergyMaterial
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy:\n\t{}".format(e))

try:
    from honeybee_ph_utils.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from ph_units import converter, parser
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class ConversionError(Exception):
    def __init__(self, value, from_unit, to_unit):
        self.value = value
        self.from_unit = from_unit
        self.to_unit = to_unit

    def __str__(self):
        return "Failed to convert {} from {} to {}".format(self.value, self.from_unit, self.to_unit)


def convert_value(_value, _from_unit, _to_unit):
    # type: (float, str, str) -> float
    """Convert a value from one unit to another using ph_units converter.

    Args:
        _value (float): The numeric value to convert
        _from_unit (str): The unit to convert from (e.g., "M", "W/MK")
        _to_unit (str): The unit to convert to (e.g., "IN", "HR-FT2-F/BTU")
    Returns:
        float: The converted value in the target unit
    """
    result = converter.convert(_value, _from_unit, _to_unit)
    if result is None:
        raise ConversionError(_value, _from_unit, _to_unit)
    return result


def get_alpha(_recessed, _fastener_length, _insulation_thickness_m, _debug=False):
    # type: (bool, float, float, bool) -> float
    """Calculate alpha correction factor for mechanical fasteners per ISO 6946:2017 Section F.3.2.

    The alpha factor depends on whether the fastener fully penetrates the insulation layer:
    - For full penetration: α = 0.8
    - For recessed fasteners: α = 0.8 × (d₁/d₀)

    Args:
        _recessed (bool): True if fastener is recessed (partial penetration), False for full penetration
        _fastener_length (float): Length of fastener penetrating insulation layer (d₁) [m]
        _insulation_thickness_m (float): Thickness of insulation layer containing fastener (d₀) [m]

    Returns:
        float: Alpha correction factor (dimensionless)

    Note:
        See ISO 6946:2017 Figure F.1 for visual representation of recessed vs. full penetration.
    """
    if _recessed:
        result = 0.8 * (_fastener_length / _insulation_thickness_m)
    else:
        result = 0.8

    if _debug:
        print("Calculating alpha factor for fastener correction:")
        print("- Recessed Fasteners={}".format(_recessed))
        print("- d1 (fastener length)={:.6f} m".format(_fastener_length))
        print("- d0 (insulation thickness)={:.6f} m".format(_insulation_thickness_m))
        print("- alpha={:.6f}".format(result))

    return result


def calculate_layer_conductivity_with_fasteners(
    _recessed,
    _fastener_conductivity_w_mk,
    _fasteners_per_m2,
    _fastener_area_m2,
    _insulation_thickness_m,
    _fastener_length,
    _insulation_resistance_m2k_W,
    _assembly_resistance_m2k_W,
    _debug=False,
):
    # type: (bool, float, float, float, float, float, float, float, bool) -> float
    """Calculate adjusted thermal conductivity of insulation layer with mechanical fasteners.

    Matches the Phius Fastener Correction Calculator v25.1.0
    (https://www.phius.org/point-fastener-correction-calculator)

    Implements ISO 6946:2017 Section F.3 correction for mechanical fasteners that penetrate
    insulation layers. This includes wall ties between masonry leaves, roof fasteners, or
    fasteners in composite panel systems.

    The correction to thermal transmittance is calculated using:
        ΔU_f = alpha × ((lambda_f × A_f × n_f) / d_1) × (R_1 / R_tot)²

    Args:
        _recessed (bool): True if fastener is recessed (doesn't fully penetrate), False otherwise
        _fastener_conductivity_w_mk (float): Thermal conductivity of fastener material [W/(m·K)]
        _fasteners_per_m2 (float): Number of fasteners per square meter [1/m²]
        _fastener_area_m2 (float): Cross-sectional area of one fastener [m²]
        _insulation_thickness_m (float): Thickness of insulation layer containing fastener [m]
        _fastener_length (float): Length of fastener penetrating insulation layer [m]
        _insulation_resistance_m2k_W (float): Thermal resistance of insulation layer [m²·K/W]
        _assembly_resistance_m2k_W (float): Total thermal resistance of component [m²·K/W]

    Returns:
        float: Adjusted thermal conductivity of insulation layer [W/(m·K)]

    Note:
        - d_1 (fastener length) can exceed insulation thickness if fastener passes through at angle
        - For recessed fasteners, d_1 < insulation thickness and R_i = d_1 / thermal_conductivity
        - Implementation uses IP unit conversions to match Phius Excel calculator exactly
    """

    # Calculate the ISO 6946:2017 fastener correction factor in SI units
    alpha = get_alpha(_recessed, _fastener_length, _insulation_thickness_m, _debug)
    part_a = _fastener_conductivity_w_mk * _fastener_area_m2 * _fasteners_per_m2 / _fastener_length
    part_b = (_insulation_resistance_m2k_W / _assembly_resistance_m2k_W) ** 2
    delta_U_w_m2K = alpha * part_a * part_b

    # CRITICAL: Apply the fastener correction using IP units to match Phius Excel workbook exactly
    # The Excel workbook rounds the adjusted assembly resistance to 1 decimal place in IP units,
    # which creates a specific rounding behavior that cannot be replicated in SI units alone.
    IP_CONVERSION_FACTOR = 5.678264134  # W/m2-K to Btu/hr-ft2-F conversion

    delta_U_btu_hr_ft_F = delta_U_w_m2K / IP_CONVERSION_FACTOR
    assembly_resistance_hr_ft2_f_btu = _assembly_resistance_m2k_W * IP_CONVERSION_FACTOR

    # This rounding in IP units is the key to matching the Excel workbook exactly
    adjusted_assembly_resistance_hr_ft2_f_btu = round(
        1 / ((1 / assembly_resistance_hr_ft2_f_btu) + delta_U_btu_hr_ft_F), 1
    )

    # Calculate the change in assembly resistance and apply it to the insulation layer
    assembly_resistance_change_hr_ft2_f_btu = (
        assembly_resistance_hr_ft2_f_btu - adjusted_assembly_resistance_hr_ft2_f_btu
    )
    insulation_resistance_hr_ft2_f_btu = _insulation_resistance_m2k_W * IP_CONVERSION_FACTOR
    adjusted_insulation_resistance_hr_ft2_F_Btu = (
        insulation_resistance_hr_ft2_f_btu - assembly_resistance_change_hr_ft2_f_btu
    )

    # Convert back to SI units for final result
    adjusted_insulation_resistance_m2K_W = adjusted_insulation_resistance_hr_ft2_F_Btu / IP_CONVERSION_FACTOR
    adjusted_layer_conductivity_w_mk = _insulation_thickness_m / adjusted_insulation_resistance_m2K_W

    if _debug:
        print("Calculating Fastener Correction:")
        print("- alpha={:.6f}".format(alpha))
        print("- lambda_f={:.4f} W/mk".format(_fastener_conductivity_w_mk))
        print("- Recessed Fasteners={}".format(_recessed))
        print("- n_f={:.4f} number per m2".format(_fasteners_per_m2))
        print("- A_f={:.8f} m2".format(_fastener_area_m2))
        print("- d_0={:.6f} m".format(_insulation_thickness_m))
        print("- d_1={:.6f} m".format(_fastener_length))
        print("- R_1={:.6f} m2-K/W".format(_insulation_resistance_m2k_W))
        print("- R_tot={:.6f} m2-K/W".format(_assembly_resistance_m2k_W))
        print("- ΔU_f={:.8f} W/m2-K [{:.8f} Btu/hr-ft2-F]".format(delta_U_w_m2K, delta_U_btu_hr_ft_F))
        print("- Adjusted layer conductivity={:.5f} W/m-K ".format(adjusted_layer_conductivity_w_mk))

    return adjusted_layer_conductivity_w_mk


class GHCompo_AddFastenersToConstruction(object):
    FASTENER_MATERIALS = {
        1: 160.0,  # Aluminum
        2: 50.0,  # Mild Steel
        3: 17.0,  # Stainless Steel
        4: 0.21,  # Solid Plastic
    }

    def __init__(
        self,
        _IGH,
        _fastener_material,
        _recessed_fasteners,
        _fastener_diameter,
        _depth_of_fastener,
        _assembly_area,
        _fastener_count,
        _layer_,
        _construction,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, str, bool | None, float | None, float | None, float | None, float | None, int | None, OpaqueConstruction, list, dict) -> None
        self.IGH = _IGH
        self.fastener_material_type = input_to_int(_fastener_material)
        self.recessed_fasteners = _recessed_fasteners or False
        self.fastener_diameter_m = self.value_as_meter(_fastener_diameter or "0.125 IN")
        try:
            self.depth_of_fastener_m = self.value_as_meter(_depth_of_fastener)
        except ConversionError:
            self.depth_of_fastener_m = None
        self.assembly_area_m2 = self.value_as_meter_squared(_assembly_area or "1.0 M2")
        self.fastener_count = _fastener_count or 12.1094  # ~ 8" on center vertically, 16" on center horizontally
        self.layer = _layer_ or 0
        self.construction = _construction

        # --
        self.adjusted_layer_conductivity_w_mk = 0.0

    def value_as_meter(self, input_value):
        # type: (float | str | None) -> float
        """Convert input value to meters."""
        input_value, input_unit = parser.parse_input(str(input_value))
        result = converter.convert(input_value, input_unit or self.IGH.get_rhino_unit_system_name(), "M")
        if not result:
            raise ConversionError(input_value, input_unit, "M")
        return result

    def value_as_meter_squared(self, input_value):
        # type: (float | str | None) -> float
        """Convert input value to square meters."""
        input_value, input_unit = parser.parse_input(str(input_value))
        result = converter.convert(input_value, input_unit or self.IGH.get_rhino_areas_unit_name(), "M2")
        if not result:
            raise ConversionError(input_value, input_unit, "M2")
        return result

    @property
    def ready(self):
        # type: () -> bool
        if self.construction is None:
            return False
        if self.fastener_material_type is None:
            return False
        return True

    @property
    def fastener_conductivity_w_mk(self):
        # type: () -> float
        try:
            return self.FASTENER_MATERIALS[self.fastener_material_type or 1]
        except KeyError:
            valid_types = list(self.FASTENER_MATERIALS.keys())
            raise ValueError(
                "Invalid fastener material type: {}. Only {} are supported.".format(
                    self.fastener_material_type, valid_types
                )
            )

    @property
    def fasteners_per_m2(self):
        # type: () -> float
        return self.fastener_count / self.assembly_area_m2

    @property
    def fastener_area_m2(self):
        # type: () -> float
        return pi * (self.fastener_diameter_m / 2) ** 2

    @property
    def insulation_material(self):
        # type: () -> EnergyMaterial
        return self.construction.materials[self.layer]

    @property
    def adjusted_layer_resistivity_hr_ft2_F_btu_in(self):
        # type: () -> float
        result = convert_value(self.adjusted_layer_conductivity_w_mk, "W/MK", "HR-FT2-F/BTU-IN")
        return result

    @property
    def adjusted_layer_resistance_hr_ft2_F_btu(self):
        # type: () -> float
        return self.adjusted_layer_resistivity_hr_ft2_F_btu_in * convert_value(
            self.insulation_material.thickness, "M", "IN"
        )

    @property
    def adjusted_layer_resistance_m2k_W(self):
        # type: () -> float
        return convert_value(
            self.adjusted_layer_resistivity_hr_ft2_F_btu_in
            * convert_value(self.insulation_material.thickness, "M", "IN"),
            "HR-FT2-F/BTU",
            "M2K/W",
        )

    @property
    def fastener_diameter_in(self):
        # type: () -> float
        return convert_value(self.fastener_diameter_m, "M", "IN")

    @property
    def fastener_area_in2(self):
        # type: () -> float
        return convert_value(self.fastener_area_m2, "M2", "IN2")

    @property
    def assembly_area_ft2(self):
        # type: () -> float
        return convert_value(self.assembly_area_m2, "M2", "FT2")

    @property
    def insulation_thickness_in(self):
        # type: () -> float
        return convert_value(self.insulation_material.thickness, "M", "IN")

    @property
    def insulation_r_value_hr_ft2_F_btu(self):
        # type: () -> float
        return convert_value(self.insulation_material.u_value, "W/M2K", "HR-FT2-F/BTU")

    @property
    def insulation_r_value_per_inch_hr_ft2_F_btu_in(self):
        # type: () -> float
        return self.insulation_r_value_hr_ft2_F_btu / self.insulation_thickness_in

    @property
    def fastener_depth_in(self):
        # type: () -> float
        return convert_value(self.fastener_depth_m, "M", "IN")

    @property
    def fastener_depth_m(self):
        # type: () -> float
        return self.depth_of_fastener_m or self.insulation_material.thickness

    @property
    def assembly_r_value_hr_ft2_F_btu(self):
        # type: () -> float
        return convert_value(self.construction.u_factor, "W/M2K", "HR-FT2-F/BTU")

    def get_Phius_worksheet_inputs(self):
        # type: () -> list[str]
        """Return a list of strings containing the Phius worksheet input data."""
        lines = []

        lines.append("Inputs for Phius Point Fastener Correction Calculator v25.1.0 (2025.04)")
        lines.append(
            "  Adjusted Insulation R-value per inch: {:.4f} hr-ft2-F/Btu-in".format(
                self.adjusted_layer_resistivity_hr_ft2_F_btu_in
            )
        )
        lines.append(
            "  Adjusted Insulation R-Value [R1a]: {:.4f} hr-ft2-F/Btu ".format(
                self.adjusted_layer_resistance_hr_ft2_F_btu
            )
        )
        lines.append("  Recessed Fasteners?: {}".format("Yes" if self.recessed_fasteners else "No"))
        lines.append("  Fastener Material: {}".format(self.fastener_material_type))
        lines.append("  Fastener Diameter [Df]: {:.4f} in".format(self.fastener_diameter_in))
        lines.append("  Area Fasteners [Af]: {:.6f} in2".format(self.fastener_area_in2))
        lines.append("  Assembly Area: {:.4f} ft2".format(self.assembly_area_ft2))
        lines.append("  Fastener Count: {:.4f}".format(self.fastener_count))
        lines.append("  Depth of Insulation [d0]: {:.4f} in".format(self.insulation_thickness_in))
        lines.append(
            "  Insulation R-Value per Inch: {:.4f} hr-ft2-F/Btu-in".format(
                self.insulation_r_value_per_inch_hr_ft2_F_btu_in
            )
        )
        lines.append("  Insulation R-Value: {:.4f} hr-ft2-F/Btu".format(self.insulation_r_value_hr_ft2_F_btu))
        lines.append("  Depth of Fastener [d1]: {:.4f} in".format(self.fastener_depth_in))
        lines.append("  Homogeneous R-Value: {:.4f} ft2-hr-F/Btu".format(self.assembly_r_value_hr_ft2_F_btu))

        return lines

    def run(self):
        # type: () -> tuple[OpaqueConstruction, list[str]]
        if not self.ready:
            return self.construction, []

        # -- Calculate the adjusted conductivity of the insulation layer
        print("Adjusting the Material: {}".format(self.insulation_material.display_name))
        self.adjusted_layer_conductivity_w_mk = calculate_layer_conductivity_with_fasteners(
            self.recessed_fasteners,
            self.fastener_conductivity_w_mk,
            self.fasteners_per_m2,
            self.fastener_area_m2,
            self.insulation_material.thickness,
            self.depth_of_fastener_m or self.insulation_material.thickness,
            self.insulation_material.r_value,
            1 / self.construction.u_factor,
            _debug=False,
        )

        # -- Build the new Material with adjusted R-value
        new_material = EnergyMaterial(
            identifier=self.insulation_material.display_name + " w/ Fasteners",
            thickness=self.insulation_material.thickness,
            conductivity=self.adjusted_layer_conductivity_w_mk,
            density=self.insulation_material.density,
            specific_heat=self.insulation_material.specific_heat,
            roughness=self.insulation_material.roughness,
            solar_absorptance=self.insulation_material.solar_absorptance,
            thermal_absorptance=self.insulation_material.thermal_absorptance,
            visible_absorptance=self.insulation_material.visible_absorptance,
        )

        new_materials = [mat for mat in self.construction.materials]
        new_materials[self.layer] = new_material

        # -- Build a new construction with the new layer
        construction_ = OpaqueConstruction(
            identifier=self.construction.identifier,
            materials=new_materials,
        )

        return construction_, self.get_Phius_worksheet_inputs()
