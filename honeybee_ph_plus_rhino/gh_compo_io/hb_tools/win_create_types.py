# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Create Window Types."""

from collections import OrderedDict, defaultdict
from copy import copy

try:
    from itertools import izip  # type: ignore
except ImportError:
    izip = zip  # Python 3

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from Rhino.Geometry import Brep, LineCurve, Plane, Point3d, Vector3d  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from ph_units.converter import convert
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))


class BuildOriginPlaneError(Exception):
    """Custom Error for the Window Builder."""

    def __init__(self, _start_pt, _end_pt):
        # type: (Point3d, Point3d) -> None
        self.message = (
            "Error: Something went wrong building the Origin-Planes for "
            "the window with base-curve with Start-Point: {} and End-Point: {}. Note this window builder ONLY works for vertical "
            "planar windows. Skylights or windows on sloped surfaces are not supported.".format(_start_pt, _end_pt)
        )
        super().__init__(self.message)


class WindowElement(object):
    """A Dataclass for a single Window 'Element' (sash) which can be added to a WindowType."""

    width_m = ghio_validators.UnitM("width_m")
    height_m = ghio_validators.UnitM("height_m")

    def __init__(self, _width_m, _height_m, _col, _row):
        # type: (float, float, int, int) -> None
        self.width_m = float(_width_m)
        self.height_m = float(_height_m)
        self.col = int(_col)
        self.row = int(_row)

    def get_display_name(self):
        # type: () -> str
        return "{}{}".format(self.col, self.row)

    def __str__(self):
        # type: () -> str
        return "{}( width_m={}, height_m={}, col={}, row={} )".format(
            self.__class__.__name__, self.width_m, self.height_m, self.col, self.row
        )

    def __repr__(self):
        # type: () -> str
        return str(self)

    def ToString(self):
        # type: () -> str
        return str(self)


class WindowUnitType(object):
    """A Class to organize a single Window 'Type' with all its WindowElements."""

    def __init__(self, _IGH, _type_name, _spacer_m=0.0):
        # type: (gh_io.IGH, str, float) -> None
        self.IGH = _IGH
        self.type_name = _type_name
        self.spacer_m = _spacer_m
        self.elements = []  # type: list[WindowElement]

    @staticmethod
    def elements_by_column(_elements):
        # type: (list[WindowElement]) -> list[list[WindowElement]]
        """Return a list with lists of WindowElements sorted by their column"""
        # -- Sort the WindowElements by their column name
        d = defaultdict(list)
        for element in _elements:
            d[element.col].append(element)

        # -- Convert the dict to a list of lists
        output = []
        for k in sorted(d.keys()):
            output.append(d[k])
        return output

    @staticmethod
    def elements_by_row(_elements):
        # type: (list[WindowElement]) -> list[WindowElement]
        """Return a lists of WindowElements sorted by their row."""
        return sorted(_elements, key=lambda e: e.row)

    @property
    def x_vector(self):
        # type: () -> Vector3d
        if not self.base_curve:
            raise ValueError("Error: window {} is missing a base_curve?".format(self.type_name))
        start_pt, end_pt = self.IGH.ghc.EndPoints(self.base_curve)
        return self.IGH.ghc.Vector2Pt(start_pt, end_pt, True).vector

    @property
    def y_vector(self):
        # type: () -> Vector3d
        return self.IGH.ghc.UnitZ(1)

    def build_origin_plane(self, _base_curve):
        # type: (LineCurve) -> Plane
        start_pt, end_pt = self.IGH.ghc.EndPoints(_base_curve)
        pl = self.IGH.ghc.ConstructPlane(start_pt, self.x_vector, self.y_vector)
        if not pl:
            raise BuildOriginPlaneError(
                start_pt,
                end_pt,
            )

        return pl

    def build_origin_point(self, _base_curve):
        # type: (LineCurve) -> Point3d
        """Get the origin point of the base curve."""
        return self.build_origin_plane(_base_curve).Origin

    def build_srfc_base_crv(self, _width_m, _origin_plane, _doc_units):
        # type: (float, Plane, str) -> LineCurve
        """Build the surface base curve for the window (in Rhino doc units)."""

        pt_1 = _origin_plane.Origin
        move_width_m = _width_m - self.spacer_m
        move_width_in_doc_units = convert(move_width_m, "M", _doc_units)
        move_vector = self.IGH.ghc.Amplitude(self.x_vector, move_width_in_doc_units)
        pt_2 = self.IGH.ghc.Move(pt_1, move_vector).geometry
        return self.IGH.ghc.Line(pt_1, pt_2)

    def get_cumulative_row_heights_m(self):
        # type: () -> list[float]
        """Returns a list of the cumulative row-heights starting from 0. ie: [0.0, 3.4, 5.6]"""

        row_heights_dict = defaultdict(list)
        for element in self.elements:
            row_heights_dict[int(element.row)].append(float(element.height_m))

        row_heights_ = [0.0]  # starting position
        for k in sorted(row_heights_dict.keys()):
            row_heights_.append(row_heights_[k] + min(row_heights_dict[k]))
        # print("Cumulative Row Heights: {}".format(row_heights_))
        return row_heights_

    def get_cumulative_col_widths_m(self):
        # type: () -> list[float]
        """Returns a list of the cumulative column-widths starting from 0. ie: [0.0, 3.4, 5.6]"""

        col_widths_dict = defaultdict(list)
        for element in self.elements:
            col_widths_dict[int(element.col)].append(float(element.width_m))

        col_widths_ = [0.0]  # starting position
        for k in sorted(col_widths_dict.keys()):
            col_widths_.append(col_widths_[k] + min(col_widths_dict[k]))
        # print("Cumulative Column Widths: {}".format(col_widths_))
        return col_widths_

    def build(self, _base_curve):
        # type: (LineCurve) -> tuple[list[Brep], OrderedDict[int, dict[str, Any]]]
        """Create the window's Rhino geometry based on the Elements."""

        # 1) -- Get the Base-Plane and create a starting origin plane from it
        self.base_curve = _base_curve
        origin_plane = self.build_origin_plane(_base_curve)

        # 2) -- Walk through each column, and each row in each column
        cum_row_heights_m_ = self.get_cumulative_row_heights_m()
        cum_col_widths_m_ = self.get_cumulative_col_widths_m()

        # 3) -- Create the surfaces and ID data
        surfaces_ = []
        id_data_ = OrderedDict()
        rh_doc_units = self.IGH.get_rhino_unit_system_name()
        for i, col_element_lists in enumerate(self.elements_by_column(self.elements)):
            column_elements_origin_plane = copy(origin_plane)  # type: Plane

            # 1) -- Move the origin plane 'over' to the next column
            col_width_in_doc_units = convert(cum_col_widths_m_[i], "M", rh_doc_units)
            column_elements_origin_plane = self.IGH.ghc.Move(
                column_elements_origin_plane,
                self.IGH.ghc.Amplitude(self.x_vector, col_width_in_doc_units),
            ).geometry

            for row_element in self.elements_by_row(col_element_lists):
                row_elements_origin_plane = copy(column_elements_origin_plane)  # type: Plane

                # 2) -- Move the origin plane 'up' to the starting row position
                row_height_in_doc_units = convert(cum_row_heights_m_[row_element.row], "M", rh_doc_units)
                row_elements_origin_plane = self.IGH.ghc.Move(
                    row_elements_origin_plane,
                    self.IGH.ghc.Amplitude(self.y_vector, row_height_in_doc_units),
                ).geometry

                # 3) Build the Window Element Surface
                base_curve = self.build_srfc_base_crv(row_element.width_m, row_elements_origin_plane, rh_doc_units)
                row_element_height_in_doc_units = convert(row_element.height_m, "M", rh_doc_units)
                surfaces_.append(
                    self.IGH.ghc.Extrude(
                        base_curve,
                        self.IGH.ghc.Amplitude(self.y_vector, row_element_height_in_doc_units),
                    )
                )

                # 4)-- Keep track of the id-data for the surface
                el_name = row_element.get_display_name()
                el_id_data = {}
                el_id_data["type_name"] = self.type_name
                el_id_data["row"] = row_element.row
                el_id_data["col"] = row_element.col
                id_data_[el_name] = el_id_data

        return surfaces_, id_data_

    def __str__(self):
        # type: () -> str
        return "{}(type_name={}, elements={})".format(self.__class__.__name__, self.type_name, self.elements)

    def __repr__(self):
        # type: () -> str
        return str(self)

    def ToString(self):
        return str(self)


class GHCompo_CreateWindowUnitTypes(object):
    def __init__(self, _IGH, _type_names, _widths, _heights, _pos_cols, _pos_rows):
        # type: (gh_io.IGH, list[str], list[float], list[float], list[int], list[int]) -> None
        self.IGH = _IGH
        self.type_names = _type_names
        self.widths = [convert(w, self.IGH.get_rhino_unit_system_name(), "M") or 1.0 for w in _widths]
        self.heights = [convert(h, self.IGH.get_rhino_unit_system_name(), "M") or 1.0 for h in _heights]
        self.pos_cols = _pos_cols
        self.pos_rows = _pos_rows

    def run(self):
        # type: () -> list[WindowUnitType]

        # ------------------------------------------------------------------------------
        # -- Sort all the input data and group by 'Type Name'

        # -- Build up all the types
        window_types = {}
        for type_name in self.type_names:
            window_types[type_name] = WindowUnitType(self.IGH, type_name)

        # -- Add the window elements (sashes) to the types
        input_lists = izip(self.type_names, self.widths, self.heights, self.pos_cols, self.pos_rows)
        for input_data in input_lists:
            type_name, width, height, pos_col, pos_row = input_data
            window_types[type_name].elements.append(WindowElement(width, height, pos_col, pos_row))

        return [window_types[k] for k in sorted(window_types.keys())]
