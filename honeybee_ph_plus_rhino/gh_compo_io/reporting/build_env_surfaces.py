# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Functions for getting / sorting all the Honeybee-Model Envelope Surfaces. """

from collections import defaultdict

try:
    from typing import Any, Dict, List, Tuple
except ImportError:
    pass  # Python 2.7

try:
    from System import Object  # type: ignore
    from System.Drawing import Color  # type: ignore
except ImportError:
    pass  # Outside .NET

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path
    from Rhino.DocObjects import ObjectAttributes
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee import face, model
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ladybug_rhino.fromgeometry import from_face3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("\nFailed to import honeybee_ph_rhino")


class GHCompo_CreateEnvelopeSurfaces(object):
    def __init__(
        self,
        _IGH,
        _hb_model,
        _highlight_surface_color,
        _highlight_outline_color,
        _highlight_outline_weight,
        _default_surface_color,
        _default_outline_color,
        _default_outline_weight,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, model.Model, Color, Color, float, Color, Color, float, List[Any], Dict[Any, Any]) -> None
        self.IGH = _IGH
        self.hb_model = _hb_model
        self.highlight_surface_color = _highlight_surface_color
        self.highlight_outline_color = _highlight_outline_color
        self.highlight_outline_weight = _highlight_outline_weight
        self.default_surface_color = _default_surface_color
        self.default_outline_color = _default_outline_color
        self.default_outline_weight = _default_outline_weight

    def create_rh_attr_object(self, _color, _weight):
        # type: (Color, float) -> ObjectAttributes
        """Return a new Rhino.DocObjects.ObjectAttributes object with specified settings."""

        new_attr_obj = self.IGH.Rhino.DocObjects.ObjectAttributes()

        new_attr_obj.ObjectColor = _color
        new_attr_obj.PlotColor = _color
        new_attr_obj.ColorSource = (
            self.IGH.Rhino.DocObjects.ObjectColorSource.ColorFromObject
        )
        new_attr_obj.PlotColorSource = (
            self.IGH.Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
        )

        new_attr_obj.PlotWeight = _weight
        new_attr_obj.PlotWeightSource = (
            self.IGH.Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
        )

        # new_attr_obj.DisplayOrder = 0  # 1 = Front, -1 = Back

        return new_attr_obj

    def get_hb_face_groups_from_model(self, _hb_model):
        # type: (model.Model) -> Dict[str, List[face.Face]]
        """Return a dict with Honeybee-Faces grouped by their Construction-Name."""

        if not _hb_model:
            return {}

        face_groups = defaultdict(list)
        for hb_room in _hb_model.rooms:
            for hb_face in hb_room.faces:
                hb_face_constr_name = hb_face.properties.energy.construction.display_name
                hb_face_constr_name = hb_face_constr_name.strip()
                face_groups[hb_face_constr_name].append(hb_face)

        return face_groups

    def get_all_construction_names(self, _hb_model):
        # type: (model.Model) -> List[str]
        """Returns a sorted list of all the construction names found in the Honeybee-Model."""
        if not _hb_model:
            return []

        hb_cont_names = set()
        for hb_room in _hb_model.rooms:
            for hb_face in hb_room.faces:
                hb_cont_names.add(hb_face.properties.energy.construction.display_name)
        return sorted(list(hb_cont_names))

    def run(self):
        # type: () -> Tuple
        """Returns a tuple of the DataTrees with all the Surface Data and geometry from the HB-Model.

        Arguments:
        ----------
            * _IGH (gh_io.IGH): The Grasshopper Interface
            * _hb_model (model.Model): The Honeybee Model to use as the source.
            * _highlight_surface_color (System.Drawing.Color): The color to use for the Mesh surfaces
            * _highlight_outline_color (System.Drawing.Color): The color to use for the Mesh outlines
            * _highlight_outline_weight (float): The plot-weight to use for the Mesh outlines.
            * _default_surface_color (System.Drawing.Color):
            * _default_outline_color (System.Drawing.Color):
            * _default_outline_weight (float):

        Returns:
        --------
            * (Tuple[DataTree, DataTree, DataTree, DataTree]):
        """

        # -- Output Trees
        face_const_names_ = self.IGH.Grasshopper.DataTree[str]()
        face_geometry_ = self.IGH.Grasshopper.DataTree[Object]()
        face_rh_attributes_ = self.IGH.Grasshopper.DataTree[ObjectAttributes]()
        face_areas_ = self.IGH.Grasshopper.DataTree[float]()
        pth = self.IGH.Grasshopper.Kernel.Data.GH_Path

        # -- Build the RH AttributeObjects
        rh_attr_surface_highlight = self.create_rh_attr_object(
            self.highlight_surface_color, 0
        )
        rh_attr_surface_default = self.create_rh_attr_object(
            self.default_surface_color, 0
        )
        rh_attr_curve_highlight = self.create_rh_attr_object(
            self.highlight_outline_color, self.highlight_outline_weight
        )
        rh_attr_curve_default = self.create_rh_attr_object(
            self.default_outline_color, self.default_outline_weight
        )

        # -- Get all the exterior surfaces from the Model
        hb_face_groups = self.get_hb_face_groups_from_model(self.hb_model)

        # -- Create the mesh surfaces and edges from the HB-Faces
        for i, const_name in enumerate(self.get_all_construction_names(self.hb_model)):
            face_const_names_.Add(const_name, pth(i))
            face_areas_.Add(sum(f.area for f in hb_face_groups[const_name]), pth(i))

            for hb_room in self.hb_model.rooms:
                for hb_face in hb_room.faces:
                    # -- Choose the right colors
                    if hb_face.properties.energy.construction.display_name == const_name:
                        surface_color = rh_attr_surface_highlight
                        crv_color = rh_attr_curve_highlight
                    else:
                        surface_color = rh_attr_surface_default
                        crv_color = rh_attr_curve_default

                    # -- Create the Mesh Surface
                    mesh = self.IGH.ghpythonlib_components.MeshColours(
                        from_face3d(hb_face.geometry), surface_color.ObjectColor
                    )
                    face_geometry_.Add(mesh, pth(i))
                    face_rh_attributes_.Add(surface_color, pth(i))

                    # -- Create the Mesh Boundary Edges
                    msh_edges = self.IGH.ghpythonlib_components.MeshEdges(
                        mesh
                    ).naked_edges
                    msh_boundary = self.IGH.ghpythonlib_components.JoinCurves(
                        msh_edges, preserve=False
                    )
                    if isinstance(msh_boundary, list):
                        # If boundary is more than one curve, its a donut shaped face....
                        for crv in msh_boundary:
                            face_geometry_.Add(crv, pth(i))
                            face_rh_attributes_.Add(crv_color, pth(i))
                    else:
                        face_geometry_.Add(msh_boundary, pth(i))
                        face_rh_attributes_.Add(crv_color, pth(i))

        return (face_const_names_, face_geometry_, face_rh_attributes_, face_areas_)
