# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Functions for getting / sorting all the Honeybee-Model Thermal Bridges ."""

from collections import defaultdict

try:
    from typing import Dict, List, Set, Tuple
except ImportError:
    pass  # Python 2.7

try:
    from System import Object  # type: ignore
    from System.Drawing import Color  # type: ignore
except ImportError:
    pass  # Outside .NET

try:
    from Rhino.DocObjects import ObjectAttributes
    from Rhino.Geometry import Curve
except ImportError:
    pass  # Outside Rhino

try:
    from ladybug_rhino.fromgeometry import (
        from_face3d,
        from_linesegment3d,
        from_polyline3d,
    )
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee import model
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_energy_ph.construction import thermal_bridge
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")


class GHCompo_CreateThermalBridges(object):
    def __init__(
        self,
        _IGH,
        _hb_model,
        _highlight_outline_color,
        _highlight_outline_weight,
        _default_surface_color,
        _default_outline_color,
        _default_outline_weight,
    ):
        # type: (gh_io.IGH, model.Model, Color, float, Color, Color, float) -> None
        """
        Arguments:
        ----------
            * _IGH (gh_io.IGH): The Grasshopper Interface
            * _hb_model (model.Model): The Honeybee Model to use as the source.
            * _highlight_outline_color (System.Drawing.Color): The color to use for the TB Curve outlines
            * _highlight_outline_weight (float): The plot-weight to use for the TB Curve outlines.
            * _default_surface_color (System.Drawing.Color):
            * _default_outline_color (System.Drawing.Color):
            * _default_outline_weight (float):
        """

        self.IGH = _IGH
        self.hb_model = _hb_model
        self.highlight_outline_color = _highlight_outline_color
        self.highlight_outline_weight = _highlight_outline_weight
        self.default_surface_color = _default_surface_color
        self.default_outline_color = _default_outline_color
        self.default_outline_weight = _default_outline_weight

    def create_rh_attr_object(self, _IGH, _color, _weight):
        # type: (gh_io.IGH, Color, float) -> ObjectAttributes
        """Return a new Rhino.DocObjects.ObjectAttributes object with specified settings."""

        new_attr_obj = _IGH.Rhino.DocObjects.ObjectAttributes()

        new_attr_obj.ObjectColor = _color
        new_attr_obj.PlotColor = _color
        new_attr_obj.ColorSource = _IGH.Rhino.DocObjects.ObjectColorSource.ColorFromObject
        new_attr_obj.PlotColorSource = (
            _IGH.Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
        )

        new_attr_obj.PlotWeight = _weight
        new_attr_obj.PlotWeightSource = (
            _IGH.Rhino.DocObjects.ObjectPlotWeightSource.PlotWeightFromObject
        )

        # new_attr_obj.DisplayOrder = 0  # 1 = Front, -1 = Back

        return new_attr_obj

    def get_all_tb_groups_from_model(self, _hb_model):
        # type: (model.Model) -> Dict[str, List[thermal_bridge.PhThermalBridge]]
        """Return a Dict of all the unique TB objects found in the Model, grouped by display_name."""

        # -- First, get every unique TB object in the model
        all_tbs = {}
        for hb_room in _hb_model.rooms:
            for (
                tb_key,
                tb,
            ) in hb_room.properties.ph.ph_bldg_segment.thermal_bridges.items():
                all_tbs[tb_key] = tb

        # Now group the TBs by name
        tb_groups = defaultdict(list)
        for tb in all_tbs.values():
            tb_groups[tb.display_name].append(tb)

        return tb_groups

    def get_all_tb_names(self, _hb_model):
        # type: (model.Model) -> List[str]
        """Return a list of all the unique TB object display_names found in the model."""

        tb_names = set()
        for hb_room in _hb_model.rooms:
            for tb in hb_room.properties.ph.ph_bldg_segment.thermal_bridges.values():
                tb_names.add(tb.display_name)

        return sorted(list(tb_names))

    def get_tb_geometry(self, _hbph_tb):
        # type: (thermal_bridge.PhThermalBridge) -> Curve
        """Get the TB Geometry as a Rhino.Geometry.Curve (LineCurve or PolylineCurve)

        Arguments:
        ----------
            * _hbph_tb (thermal_bridge.PhThermalBridge):

        Returns:
        --------
            * (Rhino.Geometry.Curve)
        """
        try:
            return from_polyline3d(_hbph_tb.geometry)
        except:
            return from_linesegment3d(_hbph_tb.geometry)

    def run(self):
        # type: () -> Tuple
        """Return a Tuple of the geometry and attribute DataTrees with the TB data.

        Returns:
        --------
            * Tuple[Grasshopper.DataTree, Grasshopper.DataTree]
        """

        # -- Build the output Trees
        tb_geom_tree_ = self.IGH.Grasshopper.DataTree[Object]()
        tb_attr_tree_ = self.IGH.Grasshopper.DataTree[ObjectAttributes]()
        tb_names_tree_ = self.IGH.Grasshopper.DataTree[str]()
        tb_lengths_tree_ = self.IGH.Grasshopper.DataTree[float]()
        pth = self.IGH.Grasshopper.Kernel.Data.GH_Path

        if not self.hb_model:
            return tb_names_tree_, tb_geom_tree_, tb_attr_tree_, tb_lengths_tree_

        # -- Build the RH AttributeObjects
        rh_attr_surface_default = self.create_rh_attr_object(
            self.IGH, self.default_surface_color, 0
        )
        rh_attr_curve_highlight = self.create_rh_attr_object(
            self.IGH, self.highlight_outline_color, self.highlight_outline_weight
        )
        rh_attr_curve_default = self.create_rh_attr_object(
            self.IGH, self.default_outline_color, self.default_outline_weight
        )

        # -- Build the background building Mesh geometry which gets added to each output branch
        bldg_surface_geom = []
        bldg_surface_attrs = []

        for hb_room in self.hb_model.rooms:
            for hb_face in hb_room.faces:
                # -- Surface
                mesh = self.IGH.ghpythonlib_components.MeshColours(
                    from_face3d(hb_face.geometry), rh_attr_surface_default.ObjectColor
                )
                bldg_surface_geom.append(mesh)
                bldg_surface_attrs.append(rh_attr_surface_default)

                # -- Boundary Edges
                msh_edges = self.IGH.ghpythonlib_components.MeshEdges(mesh).naked_edges
                msh_boundary = self.IGH.ghpythonlib_components.JoinCurves(
                    msh_edges, preserve=False
                )
                if isinstance(msh_boundary, list):
                    bldg_surface_geom.extend(msh_boundary)
                    bldg_surface_attrs.extend(
                        [rh_attr_curve_default for _ in range(len((msh_boundary)))]
                    )
                else:
                    bldg_surface_geom.append(msh_boundary)
                    bldg_surface_attrs.append(rh_attr_curve_default)

        # -- Get all the TB objects from the model
        tb_groups = self.get_all_tb_groups_from_model(self.hb_model)

        # -- Build the thermal bridge curve geometry (with background meshes)
        for i, tb_name in enumerate(self.get_all_tb_names(self.hb_model)):
            # -- TB Geom and Rhino ObjectAttributes
            for tb in tb_groups[tb_name]:
                # -- Add the background model geom to each branch
                tb_geom_tree_.AddRange(bldg_surface_geom, pth(i))
                tb_attr_tree_.AddRange(bldg_surface_attrs, pth(i))

                # -- Add the new TB highlight Geometry
                tb_geom_tree_.Add(self.get_tb_geometry(tb), pth(i))
                tb_attr_tree_.Add(rh_attr_curve_highlight, pth(i))

            # -- TB Data
            tb_names_tree_.Add(tb_name, pth(i))
            tb_lengths_tree_.Add(sum(tb.length for tb in tb_groups[tb_name]), pth(i))

        return tb_names_tree_, tb_geom_tree_, tb_attr_tree_, tb_lengths_tree_
