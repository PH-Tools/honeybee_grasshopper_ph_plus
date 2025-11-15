# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Create ERV duct Model-Objects from a Honeybee Model's PH-HVAC Ventilation Systems."""

try:
    from System import Object # type: ignore
    from Grasshopper import DataTree # type: ignore
    from Grasshopper.Kernel.Data import GH_Path # type: ignore
    from Rhino.Geometry import PolylineCurve  # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import ghpythonlib or Grasshopper:\n\t{}".format(e))

try:
    from ladybug_rhino.fromgeometry import from_linesegment3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee.model import Model
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_phhvac.ducting import PhDuctElement, PhDuctSegment
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_phhvac:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
    from ph_gh_component_io.input_tools import input_to_int
except ImportError:
    raise ImportError("Failed to import ph_gh_component_io")


# ----------------------------------------------------------------------
# -- Helper Class and functions


class ErvDuctsContainer(object):
    def __init__(self, _parent_vent_unit_name, _ducts):
        self.parent_vent_unit_name = _parent_vent_unit_name
        self.ducts = _ducts

    def __str__(self):
        return "{}({}, [{} ducts])".format(self.__class__.__name__, self.parent_vent_unit_name, len(self.ducts))

    def ToString(self):
        return str(self)


def curve_from_segments(_IGH, _segments):
    # type: (gh_io.IGH, list[PhDuctSegment]) -> list[PolylineCurve]
    segment_curves = _IGH.ghc.JoinCurves([from_linesegment3d(s.geometry) for s in _segments], False)
    if not isinstance(segment_curves, list):  # Ensure consistent data structure
        segment_curves = [segment_curves]
    return segment_curves


def get_duct_block_name(_parent_name, _duct):
    # type: (str, PhDuctElement) -> str
    if _duct.is_round_duct:
        shape = "{}in Diam".format(_duct.segments[0].diameter)
    else:
        shape = "{}in x {}in".format(_duct.segments[0].height, _duct.segments[0].width)
    return "{} | {} | {}".format(_parent_name, "OA" if _duct.duct_type==1 else "EA", shape)


# ----------------------------------------------------------------------
# -- Component Interface Class


class GHCompo_BuildErvDucting(object):
    def __init__(self, _IGH, _hb_model, _duct_type):
        # type: (gh_io.IGH, Model, int) -> None
        self.IGH = _IGH
        self.hb_model = _hb_model
        self.duct_type = _duct_type

    @property
    def duct_type(self):
        # type: () -> int
        return self._duct_type

    @duct_type.setter
    def duct_type(self, value):
        # type: (int) -> None
        input_int = input_to_int(value, _default=1)
        if input_int in (1, 2):
            self._duct_type = input_int
        else:
            raise ValueError("Duct Type must be 1 (Supply) or 2 (Exhaust). Got: {}".format(value))

    @property
    def ready(self):
        # type: () -> bool
        return self.hb_model is not None

    @property
    def layer_name(self):
        # type: () -> str
        if self.duct_type == 1:
            return "OA"
        else:
            return "EA"

    def run(self):
        # type: () -> None | DataTree[Object]

        if not self.ready:
            return None

        # --------------------------------------------------------------------------------------------------------------
        # -- Get all of the HB-Ducting from each of the Ventilation Systems from the Model
        ph_ventilation_systems = {}
        for room in self.hb_model.rooms:
            vent_system = room.properties.ph_hvac.ventilation_system
            if not vent_system:
                continue
            ph_ventilation_systems[vent_system.display_name] = vent_system

        hb_ducts = DataTree[Object]()
        for i, k in enumerate(sorted(ph_ventilation_systems.keys())):
            vent_system = ph_ventilation_systems[k]

            if self.duct_type == 1:
                ducts = vent_system.supply_ducting
            else:
                ducts = vent_system.exhaust_ducting

            hb_ducts.Add(
                ErvDuctsContainer(vent_system.ventilation_unit.display_name, [d.duplicate() for d in ducts]), GH_Path(i)
            )

        # --------------------------------------------------------------------------------------------------------------
        # -- Wrap each of the HB-Duct Groups into a Model Object
        duct_model_objects_ = DataTree[Object]()
        ea_layer = self.IGH.ghc.ModelLayer(layer=self.layer_name, name=self.layer_name).layer
        for i, b in enumerate(hb_ducts.Branches):
            ducting_obj = b[0]
            for duct in ducting_obj.ducts:
                for curve in curve_from_segments(self.IGH, duct.segments):

                    # -- Build the actual Model Object
                    model_obj = self.IGH.ghc.ModelObject(
                        object=curve,
                        geometry=curve,
                        name=get_duct_block_name(ducting_obj.parent_vent_unit_name, duct),
                        layer=ea_layer,
                    ).object

                    # -- Store the parent unit-name
                    model_obj = self.IGH.ghc.UserText(
                        content=model_obj, keys=["parent_vent_unit_name"], values=[ducting_obj.parent_vent_unit_name]
                    ).content

                    # -- Package for Output
                    duct_model_objects_.Add(model_obj, GH_Path(duct_model_objects_.BranchCount + 1))

        # --------------------------------------------------------------------------------------------------------------
        # -- Output
        return duct_model_objects_
