# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Airtable Create Material Layers."""

try:
    from typing import (
        Any,
        Dict,
        ItemsView,
        Iterator,
        KeysView,
        List,
        Optional,
        Tuple,
        ValuesView,
    )
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.typing import clean_ep_string
except ImportError:
    raise ImportError("Failed to import honeybee")

try:
    from honeybee_energy.material.opaque import EnergyMaterial
except ImportError:
    raise Exception("Error importing honeybee_energy modules?")

try:
    from honeybee_energy_ph.properties.materials.opaque import EnergyMaterialPhProperties
except ImportError:
    raise ImportError("Failed to import honeybee_energy_ph")

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")

try:
    from honeybee_ph_utils.color import PhColor
except ImportError:
    raise ImportError("Failed to import honeybee_ph_utils")

try:
    from honeybee_ph_plus_rhino.gh_compo_io.airtable.download_data import (
        TableFields,
        TableRecord,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


AT_COLUMN_NAMES = {
    "name": "DISPLAY_NAME",
    "material": "LAYER MATERIAL",
    "thickness": "LAYER THICKNESS [MM]",
    "conductivity": "CONDUCTIVITY_W_MK",
    "density": "DENSITY_KG_M3",
    "specific_heat_capacity": "SPECIFIC_HEAT_CAPACITY_J_KG_K",
    "data": "DATA_SHEET",
    "notes": "NOTES",
    "link": "LINK",
}


class EpMaterialCollection(object):
    def __init__(self):
        # type: () -> None
        self._storage = {}  # type: Dict[str, EnergyMaterial]

    def keys(self):
        # type: () -> KeysView[str]
        return self._storage.keys()

    def values(self):
        # type: () -> ValuesView[EnergyMaterial]
        return self._storage.values()

    def items(self):
        # type: () -> ItemsView[str, EnergyMaterial]
        return self._storage.items()

    def __getitem__(self, key):
        # type: (str) -> EnergyMaterial
        return self._storage[key]

    def __setitem__(self, key, value):
        # type: (str, EnergyMaterial) -> None
        self._storage[key] = value

    def __iter__(self):
        # type: () -> Iterator[str]
        return iter(self._storage)

    def __len__(self):
        # type: () -> int
        return len(self._storage)

    def __contains__(self, key):
        # type: (str) -> bool
        return key in self._storage

    def __repr__(self):
        # type: () -> str
        return "EpMaterialCollection({})".format(self._storage)

    def __str__(self):
        # type: () -> str
        return "{}({} items)".format(self.__class__.__name__, len(self))

    def ToString(self):
        # type: () -> str
        return str(self)


class GHCompo_AirTableCreateMaterialLayers(object):
    DENSITY = 999.9999  # type: float
    SPEC_HEAT = 999.999  # type: float
    ROUGHNESS = "Rough"  # type: str
    THERM_ABS = 0.9  # type: float
    SOL_ABS = 0.7  # type: float
    VIS_ABS = 0.7  # type: float

    def __init__(self, IGH, _material_records, _layer_records, *args, **kwargs):
        # type: (gh_io.IGH, List[TableRecord], List[TableRecord], *Any, **Any) -> None
        self.IGH = IGH
        self.materials = self.create_material_dict(_material_records)
        self.layer_records = _layer_records
        self.material_layers_collection = EpMaterialCollection()

    def clean_name(self, _in):
        # type: (str) -> str
        """Clean the name of the material. Strip whitespace, remove commas."""
        return str(_in).strip().replace(",", "")

    def create_material_dict(self, _material_records):
        # type: (List[TableRecord]) -> Dict
        """Create a dictionary of materials from the AirTable Data."""
        return {record.ID: record.FIELDS for record in _material_records}

    def _layer_name(self, _layer_data):
        # type: (TableFields) -> str
        """Get the name of the layer from the TableFields dict."""
        try:
            return _layer_data[AT_COLUMN_NAMES["name"]]
        except KeyError:
            msg = "No Name found for the layer: {}".format(_layer_data)
            self.IGH.warning(msg)
            return "__unnamed__"

    def _layer_thickness_mm(self, _layer_data):
        # type: (TableFields) -> float
        """Get the thickness (MM) of the layer from the TableFields dict."""
        try:
            return float(_layer_data[AT_COLUMN_NAMES["thickness"]])
        except KeyError as e:
            layer_name = self._layer_name(_layer_data)
            msg = (
                "Failed to get the thickness of the layer: '{}'"
                "\nKey: '{}' was not found? Please check the AirTable field names.".format(
                    layer_name, e
                )
            )
            raise KeyError(msg)

    def _layer_conductivity_w_mk(self, _layer_material_data):
        # type: (TableFields) -> float
        """Get the conductivity (W/mk) of the layer from the TableFields dict."""
        try:
            return float(_layer_material_data[AT_COLUMN_NAMES["conductivity"]])
        except KeyError as e:
            layer_name = self._layer_name(_layer_material_data)
            msg = (
                "Failed to get the conductivity of the layer: '{}'"
                "\nKey: '{}' was not found? Please check the AirTable field names.".format(
                    layer_name, e
                )
            )
            raise KeyError(msg)

    def _layer_density_kg_m3(self, _layer_material_data):
        # type: (TableFields) -> float
        """Get the density (kg-m3) of the layer from the TableFields dict."""
        try:
            return float(_layer_material_data[AT_COLUMN_NAMES["density"]])
        except KeyError:
            return self.DENSITY

    def _layer_specific_heat_capacity_J_kg_K(self, _layer_material_data):
        # type: (TableFields) -> float
        """Get the Specific-Heat-Capacity (J/kg-k) of the layer from the TableFields dict."""
        try:
            return float(_layer_material_data[AT_COLUMN_NAMES["specific_heat_capacity"]])
        except KeyError:
            return self.SPEC_HEAT

    def _layer_material_color_argb(self, _layer_material_data):
        # type: (TableFields) -> Optional[PhColor]
        """Get the color of the layer from the TableFields dict."""
        try:
            color_string = _layer_material_data["ARGB_COLOR"]  # ie: "255,255,62,143"
        except KeyError:
            color_string = "255,255,255,255"  # White

        return PhColor.from_argb(*[int(_) for _ in color_string.split(",")])

    def create_ep_material(self, _record):
        # type: (TableRecord) -> Optional[EnergyMaterial]
        """Create the EnergyPlus Material Layers from the AirTable Data."""

        # -- Pull out the Layer Data
        layer_data = _record.FIELDS
        layer_mat_id_list = layer_data.get(AT_COLUMN_NAMES["material"], None)
        if not layer_mat_id_list:
            msg = "Layer Material not found for layer: {}".format(
                layer_data[AT_COLUMN_NAMES["name"]]
            )
            self.IGH.warning(msg)
            return None

        layer_thickness_mm = self._layer_thickness_mm(layer_data)
        layer_thickness_m = layer_thickness_mm / 1000.00
        layer_name = self._layer_name(layer_data)

        # -- Get the Layer's Material Data
        layer_mat_id = layer_mat_id_list[0]
        layer_mat = self.materials[layer_mat_id]

        # -- Build the HB-Material
        hb_mat = EnergyMaterial(
            clean_ep_string(self.clean_name(layer_name)),
            layer_thickness_m,
            self._layer_conductivity_w_mk(layer_mat),
            self._layer_density_kg_m3(layer_mat),
            self._layer_specific_heat_capacity_J_kg_K(layer_mat),
            self.ROUGHNESS,
            self.THERM_ABS,
            self.SOL_ABS,
            self.VIS_ABS,
        )

        # -- Set the Layer's Color
        mat_prop_ph = getattr(hb_mat.properties, "ph")  # type: EnergyMaterialPhProperties
        mat_prop_ph.ph_color = self._layer_material_color_argb(layer_mat)

        return hb_mat

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not self.layer_records:
            return False
        if not self.materials:
            return False
        return True

    def run(self):
        # type: () -> EpMaterialCollection
        """Run the component."""
        if not self.ready:
            return self.material_layers_collection

        for record in self.layer_records:
            mat = self.create_ep_material(record)
            if not mat:
                continue
            self.material_layers_collection[record.ID] = mat

        return self.material_layers_collection
