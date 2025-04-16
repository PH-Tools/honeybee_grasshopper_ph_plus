# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Data Structure for the BuildingType Standard 'Variants' data."""

from functools import lru_cache
from typing import Callable

# ---------------------------------------------------------------------------------------


class Field:

    def __init__(
        self,
        _field_name: str,
        _row: int,
        _start_row_offset: Callable[[], int] = lambda: 0,
    ) -> None:
        self.field_name = _field_name
        self._row = _row
        self.start_row_offset = _start_row_offset

    @property
    def row(self) -> int:
        return self._row + self.start_row_offset()

    def __repr__(self):
        return f"{self.__class__.__name__}({self.field_name}, {self.row})"


class Section:

    FIELDS = []

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0) -> None:
        for i, field in enumerate(self.FIELDS, start=1):
            setattr(self, str(i), Field(field, i, get_start_offset))

    @lru_cache
    def start_row(self) -> int:
        rows = [v.row for v in self.__dict__.values() if isinstance(v, Field)]
        return sorted(rows)[0]

    @lru_cache
    def end_row(self) -> int:
        rows = [v.row for v in self.__dict__.values() if isinstance(v, Field)]
        return sorted(rows)[-1]

    @property
    def rows(self) -> list[Field]:
        return [v for v in self.__dict__.values() if isinstance(v, Field)]

    def __getitem__(self, name: str) -> Field:
        for field in self.rows:
            if field.field_name == name:
                return field

        valid_names = [v.field_name for v in self.rows]
        msg = f"Field: '{name}' not found in' {self.__class__.__name__}'.\n{valid_names}"
        raise Exception(msg)

    def __repr__(self):
        return f"{self.__class__.__name__}"


# ---------------------------------------------------------------------------------------


class Geometry(Section):

    FIELDS = [
        "GEOMETRY",
        "TFA",
        "VV",
        "Vn50",
        "Building Envelope Area",
        "Gross Volume",
        "Window Area (North)",
        "Window Area (East)",
        "Window Area (South)",
        "Window Area (West)",
        "Window Area (Horiz)",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class Envelope(Section):

    FIELDS = [
        "ENVELOPE",
        "Floor BG",
        "Wall BG",
        "Party Wall",
        "Wall AG",
        "Roof",
        "-",
        "-",
        "-",
        "-",
        "-",
        "Thermal Bridge Allowance (% increase)",
        "Volumetric Air Leakage Rate (n50)",
        "Envelope Air Leakage Rate (q50)",
        "Window U-value",
        "Window SHGC",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class Systems(Section):

    FIELDS = [
        "SYSTEMS",
        "Ventilation System",
        "Ventilation Unit HR Efficiency",
        "Ventilation Unit ER Efficiency",
        "System HR Efficiency",
        "Cold Air Duct Length (ea)",
        "Cold Air Duct Insulation Thickness",
        "Heating System",
        "Cooling System",
        "DHW System",
        " ",
        " ",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class CertificationLimits(Section):

    FIELDS = [
        "CERTIFICATION LIMITS",
        "Heat Demand Limit",
        "Sensible Cooling Demand Limit",
        "Latent Cooling Demand Limit",
        "Total Cooling Demand Limit",
        "Peak Heat Load Limit",
        "Peak Cooling Load Limit",
        "PE Limit",
        "PER Limit",
        "PHIUS Net Source Energy Limit",
        " ",
        " ",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class HeatingDemand(Section):

    FIELDS = [
        "HEAT DEMAND",
        "Walls (AG)",
        "Walls (BG)",
        "Roofs",
        "Floor Slabs",
        " ",
        " ",
        " ",
        "Windows",
        "Exterior door",
        "Thermal Bridges",
        "TB (Perimeter)",
        "TB (BG)",
        "Ventilation",
        "Heating Demand",
        "North",
        "East",
        "South",
        "West",
        "Horizontal",
        "Sum opaque areas",
        "Internal Gains",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class CoolingDemand(Section):

    FIELDS = [
        "COOLING DEMAND",
        "Cooling Demand",
        "Walls (AG)",
        "Walls (BG)",
        "Roofs",
        "Floor Slabs",
        " ",
        " ",
        " ",
        "Windows",
        "Exterior door",
        "Thermal Bridges",
        "TB (Perimeter)",
        "TB (BG)",
        "Ventilation (Basic)",
        "Ventilation (Addn'l)",
        "North",
        "East",
        "South",
        "West",
        "Horizontal",
        "Sum opaque areas",
        "Internal Gains",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class SiteEnergy(Section):

    FIELDS = [
        "SITE ENERGY",
        "Heating",
        "Cooling",
        "DHW",
        "Dishwashing",
        "Clothes Washing",
        "Clothes Drying",
        "Refrigerator",
        "Cooking",
        "PHI Lighting",
        "PHI Consumer Elec.",
        "PHI Small Appliances",
        "Phius Int. Lighting",
        "Phius Ext. Lighting",
        "Phius MEL",
        "Aux Elec",
        "Solar PV",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class PrimaryEnergy(Section):

    FIELDS = [
        "PRIMARY ENERGY",
        "Heating",
        "Cooling",
        "DHW",
        "Dishwashing",
        "Clothes Washing",
        "Clothes Drying",
        "Refrigerator",
        "Cooking",
        "PHI Lighting",
        "PHI Consumer Elec.",
        "PHI Small Appliances",
        "Phius Int. Lighting",
        "Phius Ext. Lighting",
        "Phius MEL",
        "Aux Elec",
        "Solar PV",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class CertificationResults(Section):

    FIELDS = [
        "CERTIFICATION RESULTS",
        "Heat Demand",
        "Sensible Cooling Demand",
        "Latent Cooling Demand",
        "Total Cooling Demand",
        "Peak Heat Load",
        "Peak Cooling Load ",
        "PE Demand",
        "PER Demand",
        " ",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class Airtightness(Section):

    FIELDS = [
        "AIRTIGHTNESS",
        "nV,system",
        "hHR",
        "Wind protection coefficient, e",
        "Wind protection coefficient, f",
        "Vn50",
        "VV",
        "Gt",
        " ",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class RValues(Section):

    FIELDS = [
        "R-VALUES",
        "01ud-",
        "02ud-",
        "03ud-",
        "04ud-",
        "05ud-",
        "06ud-",
        "07ud-",
        "08ud-",
        "09ud-",
        "10ud-",
        "Gt-A",
        "Gt-B",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class CertificationCompliant(Section):

    FIELDS = [
        "CERTIFICATION COMPLIANT",
        "Certification Compliant?",
        " ",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class PeakLoads(Section):

    FIELDS = [
        "PEAK LOADS",
        "Peak Heat Load",
        "Peak Sensible Cooling Load",
        "Peak Latent Cooling Load",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class CO2e(Section):

    FIELDS = [
        "CO2E",
        "Heating",
        "Cooling",
        "DHW",
        "Dishwashing",
        "Clothes Washing",
        "Clothes Drying",
        "Refrigerator",
        "Cooking",
        "PHI Lighting",
        "PHI Consumer Elec.",
        "PHI Small Appliances",
        "Phius Int. Lighting",
        "Phius Ext. Lighting",
        "Phius MEL",
        "Aux Elec",
        "IPCC Limit",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)


class PrimaryEnergyRenewable(Section):

    FIELDS = [
        "PER",
        "Heating",
        "Cooling",
        "DHW",
        "Dishwashing",
        "Clothes Washing",
        "Clothes Drying",
        "Refrigerator",
        "Cooking",
        "PHI Lighting",
        "PHI Consumer Elec.",
        "PHI Small Appliances",
        "Phius Int. Lighting",
        "Phius Ext. Lighting",
        "Phius MEL",
        "Aux Elec",
        "Solar PV",
        " ",
    ]

    def __init__(self, get_start_offset: Callable[[], int] = lambda: 0):
        super().__init__(get_start_offset)





# ---------------------------------------------------------------------------------------


class Variants:
    def __init__(self):
        self.geometry = Geometry(lambda: 315)
        self.envelope = Envelope(self.geometry.end_row)
        self.systems = Systems(self.envelope.end_row)
        self.certification_limits = CertificationLimits(self.systems.end_row)
        self.heating_demand = HeatingDemand(self.certification_limits.end_row)
        self.cooling_demand = CoolingDemand(self.heating_demand.end_row)
        self.site_energy = SiteEnergy(self.cooling_demand.end_row)
        self.primary_energy = PrimaryEnergy(self.site_energy.end_row)
        self.certification_results = CertificationResults(self.primary_energy.end_row)
        self.airtightness = Airtightness(self.certification_results.end_row)
        self.r_values = RValues(self.airtightness.end_row)
        self.certification_compliant = CertificationCompliant(self.r_values.end_row)
        self.peak_loads = PeakLoads(self.certification_compliant.end_row)
        self.co2e = CO2e(self.peak_loads.end_row)
        self.primary_energy_renewable = PrimaryEnergyRenewable(self.co2e.end_row)

    def __repr__(self):
        return f"{self.__class__.__name__}"


VARIANTS = Variants()

# print(f"> geometry: {VARIANTS.geometry.start_row()} - {VARIANTS.geometry.end_row()}")
# print(f"> envelope: {VARIANTS.envelope.start_row()} - {VARIANTS.envelope.end_row()}")
# print(f"> systems: {VARIANTS.systems.start_row()} - {VARIANTS.systems.end_row()}")
# print(f"> certification_limits: {VARIANTS.certification_limits.start_row()} - {VARIANTS.certification_limits.end_row()}")
# print(f"> heating_demand: {VARIANTS.heating_demand.start_row()} - {VARIANTS.heating_demand.end_row()}")
# print(f"> cooling_demand: {VARIANTS.cooling_demand.start_row()} - {VARIANTS.cooling_demand.end_row()}")
# print(f"> site_energy: {VARIANTS.site_energy.start_row()} - {VARIANTS.site_energy.end_row()}")
# print(f"> primary_energy: {VARIANTS.primary_energy.start_row()} - {VARIANTS.primary_energy.end_row()}")
# print(f"> certification_results: {VARIANTS.certification_results.start_row()} - {VARIANTS.certification_results.end_row()}")
# print(f"> airtightness: {VARIANTS.airtightness.start_row()} - {VARIANTS.airtightness.end_row()}")
# print(f"> r_values: {VARIANTS.r_values.start_row()} - {VARIANTS.r_values.end_row()}")
# print(f"> certification_compliant: {VARIANTS.certification_compliant.start_row()} - {VARIANTS.certification_compliant.end_row()}")
# print(f"> peak_loads: {VARIANTS.peak_loads.start_row()} - {VARIANTS.peak_loads.end_row()}")
# print(f"> co2e: {VARIANTS.co2e.start_row()} - {VARIANTS.co2e.end_row()}")
# print(f"> primary_energy_renewable: {VARIANTS.primary_energy_renewable.start_row()} - {VARIANTS.primary_energy_renewable.end_row()}")
