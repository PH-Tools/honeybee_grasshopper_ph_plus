# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Schema classes for PH-Navigator Window Types API data."""

from copy import copy

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7


class GlazingType(object):
    """Schema for glazing type data from PH-Navigator."""

    def __init__(self, _name, _u_value_w_m2k, _g_value):
        # type: (str, float, float) -> None
        self.name = _name
        self.u_value_w_m2k = _u_value_w_m2k
        self.g_value = _g_value

    @classmethod
    def from_dict(cls, _data_dict):
        # type: (dict[str, Any]) -> GlazingType
        """Create a GlazingType object from a dictionary."""
        return cls(
            _name=_data_dict.get("name", ""),
            _u_value_w_m2k=float(_data_dict.get("u_value_w_m2k", 0.0)),
            _g_value=float(_data_dict.get("g_value", 0.0)),
        )

    def __copy__(self):
        # type: () -> GlazingType
        """Create a copy of this GlazingType object."""
        return GlazingType(
            _name=self.name,
            _u_value_w_m2k=self.u_value_w_m2k,
            _g_value=self.g_value,
        )

    def __str__(self):
        # type: () -> str
        """String representation of the GlazingType object."""
        return "GlazingType(_name={}, _u_value_w_m2k={}, _g_value={})".format(
            self.name, self.u_value_w_m2k, self.g_value
        )

    def __repr__(self):
        # type: () -> str
        """Get a string representation of the GlazingType object."""
        return self.__str__()

    def ToString(self):
        # type: () -> str
        """Get a string representation of the GlazingType object."""
        return self.__str__()


class GlazingData(object):
    """Schema for glazing data from PH-Navigator."""

    def __init__(self, _name, _glazing_type):
        # type: (str, GlazingType) -> None
        self.name = _name
        self.glazing_type = _glazing_type

    @classmethod
    def from_dict(cls, _data_dict):
        # type: (dict[str, Any]) -> GlazingData
        """Create a GlazingData object from a dictionary."""
        return cls(
            _name=_data_dict.get("name", ""),
            _glazing_type=GlazingType.from_dict(_data_dict["glazing_type"]),
        )

    @property
    def display_name(self):
        return self.name

    def __copy__(self):
        # type: () -> GlazingData
        """Create a copy of this GlazingData object."""
        return GlazingData(
            _name=self.name,
            _glazing_type=copy(self.glazing_type),
        )

    def __str__(self):
        # type: () -> str
        """String representation of the GlazingData object."""
        return "GlazingData(_name={}, _glazing_type={})".format(
            self.name, self.glazing_type.name
        )

    def __repr__(self):
        # type: () -> str
        """Get a string representation of the GlazingData object."""
        return self.__str__()

    def ToString(self):
        # type: () -> str
        """Get a string representation of the GlazingData object."""
        return self.__str__()


class FrameType(object):
    """Schema for frame-type data from PH-Navigator."""

    def __init__(
        self, _name, _width_mm, _u_value_w_m2k, _psi_glazing, _psi_install, _chi_value
    ):
        # type: (str, float, float, float, float, float) -> None
        self.name = _name
        self.width_mm = _width_mm
        self.u_value_w_m2k = _u_value_w_m2k
        self.psi_glazing = _psi_glazing
        self.psi_install = _psi_install
        self.chi_value = _chi_value

    @classmethod
    def from_dict(cls, _data_dict):
        # type: (dict[str, Any]) -> FrameType
        """Create a FrameType object from a dictionary."""
        return cls(
            _name=_data_dict.get("name", ""),
            _width_mm=float(_data_dict.get("width_mm", 0.0)),
            _u_value_w_m2k=float(_data_dict.get("u_value_w_m2k", 0.0)),
            _psi_glazing=float(_data_dict.get("psi_glazing", 0.0)),
            _psi_install=float(_data_dict.get("psi_install", 0.0)),
            _chi_value=float(_data_dict.get("chi_value", 0.0)),
        )

    @property
    def display_name(self):
        return self.name

    @property
    def width_m(self):
        # type: () -> float
        """Get the width in meters."""
        return self.width_mm / 1000.0 if self.width_mm else 0.0

    def __copy__(self):
        # type: () -> FrameType
        """Create a copy of this FrameType object."""
        return FrameType(
            _name=self.name,
            _width_mm=self.width_mm,
            _u_value_w_m2k=self.u_value_w_m2k,
            _psi_glazing=self.psi_glazing,
            _psi_install=self.psi_install,
            _chi_value=self.chi_value,
        )

    def __str__(self):
        # type: () -> str
        """String representation of the FrameType object."""
        return "FrameType(_name={}, _width_mm={}, _u_value_w_m2k={}, _psi_glazing={}, _psi_install={}, _chi_value={})".format(
            self.name,
            self.width_mm,
            self.u_value_w_m2k,
            self.psi_glazing,
            self.psi_install,
            self.chi_value,
        )

    def __repr__(self):
        # type: () -> str
        return str(self)

    def ToString(self):
        # type: () -> str
        return str(self)


class FrameData(object):
    """Schema for frame data from PH-Navigator."""

    def __init__(self, _name="", _frame_type=None):
        # type: (str, Any) -> None
        self.name = _name
        self.frame_type = _frame_type  # type: FrameType | None

    @classmethod
    def from_dict(cls, _data_dict):
        # type: (dict[str, Any]) -> FrameData
        """Create a FrameData object from a dictionary."""
        return cls(
            _data_dict.get("name", ""),
            FrameType.from_dict(_data_dict["frame_type"]),
        )

    @property
    def display_name(self):
        return self.name

    def __copy__(self):
        # type: () -> FrameData
        """Create a copy of this FrameData object."""
        return FrameData(
            self.name,
            copy(self.frame_type),
        )

    def __str__(self):
        # type: () -> str
        """String representation of the FrameData object."""
        return "FrameData(_name={}, _frame_type={})".format(
            self.name, self.frame_type.name if self.frame_type else "None"
        )

    def __repr__(self):
        # type: () -> str
        """Get a string representation of the FrameData object."""
        return self.__str__()

    def ToString(self):
        # type: () -> str
        return str(self)


class FramesData(object):
    """Schema for frames collection (left, right, top, bottom) from PH-Navigator."""

    def __init__(self, _left, _right, _top, _bottom):
        # type: (FrameData | None, FrameData | None, FrameData | None, FrameData | None) -> None
        self.left = _left
        self.right = _right
        self.top = _top
        self.bottom = _bottom

    @classmethod
    def from_dict(cls, _data_dict):
        # type: (dict[str, Any]) -> FramesData
        """Create a FramesData object from a dictionary."""
        return cls(
            _left=FrameData.from_dict(_data_dict["left"]),
            _right=FrameData.from_dict(_data_dict["right"]),
            _top=FrameData.from_dict(_data_dict["top"]),
            _bottom=FrameData.from_dict(_data_dict["bottom"]),
        )

    def get_all_frames(self):
        # type: () -> list[FrameData]
        """Get all non-None frame data objects."""
        frames = []
        for frame in [self.left, self.right, self.top, self.bottom]:
            if frame is not None:
                frames.append(frame)
        return frames

    def get_frame_by_side(self, _side):
        # type: (str) -> FrameData | None
        """Get frame data by side name."""
        return getattr(self, _side, None)

    def __copy__(self):
        # type: () -> FramesData
        """Create a copy of this FramesData object."""
        return FramesData(
            copy(self.left),
            copy(self.right),
            copy(self.top),
            copy(self.bottom),
        )

    def __str__(self):
        return "FramesData(_left={}, _right={}, _top={}, _bottom={})".format(
            self.left, self.right, self.top, self.bottom
        )

    def __repr__(self):
        # type: () -> str
        """Get a string representation of the FramesData object."""
        return self.__str__()

    def ToString(self):
        # type: () -> str
        """Get a string representation of the FramesData object."""
        return self.__str__()


class ElementData(object):
    """Schema for element data from PH-Navigator."""

    def __init__(
        self,
        _aperture_type_name,
        _name,
        _column_number,
        _row_number,
        _column_span,
        _row_span,
        _glazing,
        _frames,
    ):
        # type: (str, str, int, int, int, int, GlazingData, FramesData) -> None
        self.aperture_type_name = _aperture_type_name
        self.name = _name
        self.column_number = _column_number
        self.row_number = _row_number
        self.column_span = _column_span
        self.row_span = _row_span
        self.glazing = _glazing
        self.frames = _frames

    @property
    def type_name(self):
        # type: () -> str
        """Get the type-name of the element with the Col and Row position. ie: 'A_C1_R2'."""
        return "{}_C{}_R{}".format(
            self.aperture_type_name, self.column_number, self.row_number
        )

    @classmethod
    def from_dict(cls, _data_dict, _aperture_type_name=""):
        # type: (dict[str, Any], str) -> ElementData
        """Create an ElementData object from a dictionary."""

        return cls(
            _aperture_type_name=_aperture_type_name,
            _name=_data_dict.get("name", ""),
            _column_number=int(_data_dict.get("column_number", 0)),
            _row_number=int(_data_dict.get("row_number", 0)),
            _column_span=int(_data_dict.get("col_span", 1)),
            _row_span=int(_data_dict.get("row_span", 1)),
            _glazing=GlazingData.from_dict(_data_dict["glazing"]),
            _frames=FramesData.from_dict(_data_dict["frames"]),
        )

    def __copy__(self):
        # type: () -> ElementData
        """Create a copy of this ElementData object."""
        return ElementData(
            self.aperture_type_name,
            self.name,
            self.column_number,
            self.row_number,
            self.column_span,
            self.row_span,
            copy(self.glazing),
            copy(self.frames),
        )

    def __str__(self):
        # type: () -> str
        """String representation of the ElementData object."""
        return "ElementData(_aperture_type_name={}, _name={}, _column_number={}, _row_number={}, _column_span={}, _row_span={})".format(
            self.aperture_type_name,
            self.name,
            self.column_number,
            self.row_number,
            self.column_span,
            self.row_span,
        )

    def __repr__(self):
        # type: () -> str
        """Get a string representation of the ElementData object."""
        return self.__str__()

    def ToString(self):
        # type: () -> str
        """Get a string representation of the ElementData object."""
        return self.__str__()


class ApertureTypeData(object):
    """Schema for aperture type data from PH-Navigator."""

    def __init__(
        self, _name, _display_name, _column_widths_mm, _row_heights_mm, _elements
    ):
        # type: (str, str, list[float], list[float], list[ElementData]) -> None
        self.name = _name
        self.display_name = _display_name
        self.column_widths_mm = _column_widths_mm
        self.row_heights_mm = _row_heights_mm
        self.elements = _elements

    @property
    def elements(self):
        # type: () -> list[ElementData]
        """Get the elements for this aperture type."""
        return self._elements

    @elements.setter
    def elements(self, _elements):
        # type: (list[ElementData]) -> None
        """Set the elements for this aperture type."""
        self._elements = self.reverse_elements_row_order(_elements)

    @classmethod
    def from_dict(cls, _data_dict):
        # type: (dict[str, Any]) -> ApertureTypeData
        """Create an ApertureTypeData object from a dictionary."""

        return cls(
            _name=_data_dict.get("name", ""),
            _display_name=_data_dict.get("display_name", _data_dict.get("name", "")),
            _column_widths_mm=[float(w) for w in _data_dict.get("column_widths_mm", [])],
            _row_heights_mm=[float(h) for h in _data_dict.get("row_heights_mm", [])],
            _elements=[
                ElementData.from_dict(elem, _data_dict.get("name", ""))
                for elem in _data_dict.get("elements", [])
            ],
        )

    def get_column_width_m(self, _column_number):
        # type: (int) -> float
        """Get column width in meters for given column number."""

        if 0 <= _column_number < len(self.column_widths_mm):
            return self.column_widths_mm[_column_number] / 1000.0
        return 0.0

    def get_row_height_m(self, _row_number):
        # type: (int) -> float
        """Get row height in meters for given row number (reversed for Rhino bottom-to-top ordering)."""

        # Reverse the row number to convert from API's top-to-bottom to Rhino's bottom-to-top
        reversed_row_number = len(self.row_heights_mm) - 1 - _row_number
        if 0 <= reversed_row_number < len(self.row_heights_mm):
            return self.row_heights_mm[reversed_row_number] / 1000.0
        return 0.0

    def reverse_elements_row_order(self, _elements):
        # type: (list[ElementData]) -> list[ElementData]
        """
        Return a copy of the input elements list, filtering out None values and reversing
        the row-order so that the elements are built in Rhino's bottom-to-top order.
        """

        elements_ = []
        for elem in _elements:
            if elem is not None:
                new_elem = copy(elem)
                # Reverse the row number for Rhino's bottom-to-top ordering
                new_elem.row_number = (
                    len(self.row_heights_mm) - 1 - elem.row_number - elem.row_span + 1
                )
                elements_.append(new_elem)
        return elements_
