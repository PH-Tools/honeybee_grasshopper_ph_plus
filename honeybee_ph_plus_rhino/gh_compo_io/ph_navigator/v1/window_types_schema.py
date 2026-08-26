# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Schema classes for the PH-Navigator V1 aperture-types payload (route 3).

Forked from the frozen `v0/window_types_schema.py`. The V1 route-3 payload has the
same overall grid shape, but emits an explicit JSON `null` for numeric fields that
are simply unset (notably `psi_install_w_mk`). A plain `dict.get(key, default)` does
NOT substitute the default for a present-but-null value - it returns `None` - so the
V0 schema's `float(dict.get(...))` raised (`float(None)` -> a NullReferenceException
in IronPython). This fork routes every numeric coercion through `_as_float` /
`_as_int`, which map `None` (missing OR present-null) to the default. V0 stays frozen
and keeps its own copy for the legacy app.
"""

from copy import copy

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7


def _as_float(_value, _default):
    # type: (Any, float) -> float
    """Coerce to float, mapping a missing / present-but-null value to `_default`."""
    if _value is None:
        return float(_default)
    return float(_value)


def _as_int(_value, _default):
    # type: (Any, int) -> int
    """Coerce to int, mapping a missing / present-but-null value to `_default`."""
    if _value is None:
        return int(_default)
    return int(_value)


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
            _u_value_w_m2k=_as_float(_data_dict.get("u_value_w_m2k"), 0.0),
            _g_value=_as_float(_data_dict.get("g_value"), 0.0),
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
            _glazing_type=GlazingType.from_dict(_data_dict.get("glazing_type") or {}),
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
        return "GlazingData(_name={}, _glazing_type={})".format(self.name, self.glazing_type.name)

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
        self,
        _name,
        _width_mm,
        _u_value_w_m2k,
        _psi_g_w_mk,
        _psi_install_w_mk,
        _chi_value_w_k,
    ):
        # type: (str, float, float, float, float, float) -> None
        self.name = _name
        self.width_mm = _width_mm
        self.u_value_w_m2k = _u_value_w_m2k
        self.psi_g_w_mk = _psi_g_w_mk
        self.psi_install_w_mk = _psi_install_w_mk
        self.chi_value_w_k = _chi_value_w_k

    @classmethod
    def from_dict(cls, _data_dict):
        # type: (dict[str, Any]) -> FrameType
        """Create a FrameType object from a dictionary.

        `psi_install_w_mk` is routinely emitted as `null` (unset) on route 3, so it
        defaults to 0.04 W/mK here - a standard PH install-psi placeholder, matching
        the V0 default.

        NOTE: this field is the *frame-product type default* only. A current PH-Nav
        server deliberately writes the uniform project-default psi-install into every
        side here, never a per-edge value, so that an older client (which shares one
        frame element across every edge using the product) cannot mis-apply it. The
        per-edge truth lives in the sibling `installs` block - see `InstallsData`.
        The 0.04 fallback below is therefore legacy-only: it can only be reached by a
        payload from a server that predates the `installs` contract.
        """
        return cls(
            _name=_data_dict.get("name", ""),
            _width_mm=_as_float(_data_dict.get("width_mm"), 0.100),
            _u_value_w_m2k=_as_float(_data_dict.get("u_value_w_m2k"), 1.0),
            _psi_g_w_mk=_as_float(_data_dict.get("psi_g_w_mk"), 0.04),
            _psi_install_w_mk=_as_float(_data_dict.get("psi_install_w_mk"), 0.04),
            _chi_value_w_k=_as_float(_data_dict.get("chi_value"), 0.0),
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
            _psi_g_w_mk=self.psi_g_w_mk,
            _psi_install_w_mk=self.psi_install_w_mk,
            _chi_value_w_k=self.chi_value_w_k,
        )

    def __str__(self):
        # type: () -> str
        """String representation of the FrameType object."""
        return "FrameType(_name={}, _width_mm={}, _u_value_w_m2k={}, _psi_glazing={}, _psi_install={}, _chi_value={})".format(
            self.name,
            self.width_mm,
            self.u_value_w_m2k,
            self.psi_g_w_mk,
            self.psi_install_w_mk,
            self.chi_value_w_k,
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
            FrameType.from_dict(_data_dict.get("frame_type") or {}),
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
            _left=FrameData.from_dict(_data_dict.get("left") or {}),
            _right=FrameData.from_dict(_data_dict.get("right") or {}),
            _top=FrameData.from_dict(_data_dict.get("top") or {}),
            _bottom=FrameData.from_dict(_data_dict.get("bottom") or {}),
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


class InstallData(object):
    """Schema for one edge's resolved Psi-Install condition from PH-Navigator.

    Route 3 resolves each glazed element's four edges server-side (mull -> assigned
    -> project default) and ships the answer here, so the client never re-derives it.
    `install_type_id` / `name` are `None` on an interior (mulled) edge, which carries
    `psi_install_w_mk = 0.0` and `source = "mull"`.
    """

    def __init__(self, _install_type_id, _name, _psi_install_w_mk, _source):
        # type: (str | None, str | None, float, str) -> None
        self.install_type_id = _install_type_id
        self.name = _name
        self.psi_install_w_mk = _psi_install_w_mk
        self.source = _source

    @classmethod
    def from_dict(cls, _data_dict):
        # type: (dict[str, Any]) -> InstallData
        """Create an InstallData object from a dictionary.

        Unlike the frame fields, `psi_install_w_mk` defaults to 0.0 rather than 0.04:
        this block is the resolved per-edge truth, so an absent value means 'no
        install thermal bridge', never 'assume the usual placeholder'.
        """
        return cls(
            _install_type_id=_data_dict.get("install_type_id"),
            _name=_data_dict.get("name"),
            _psi_install_w_mk=_as_float(_data_dict.get("psi_install_w_mk"), 0.0),
            _source=_data_dict.get("source") or "",
        )

    @property
    def display_name(self):
        return self.name

    @property
    def is_mull(self):
        # type: () -> bool
        """True if this edge is an interior (mulled) joint rather than a library assignment."""
        return self.source == "mull"

    def __copy__(self):
        # type: () -> InstallData
        """Create a copy of this InstallData object."""
        return InstallData(
            _install_type_id=self.install_type_id,
            _name=self.name,
            _psi_install_w_mk=self.psi_install_w_mk,
            _source=self.source,
        )

    def __str__(self):
        # type: () -> str
        """String representation of the InstallData object."""
        return "InstallData(_install_type_id={}, _name={}, _psi_install_w_mk={}, _source={})".format(
            self.install_type_id, self.name, self.psi_install_w_mk, self.source
        )

    def __repr__(self):
        # type: () -> str
        return str(self)

    def ToString(self):
        # type: () -> str
        return str(self)


class InstallsData(object):
    """Schema for the per-edge Psi-Install collection from PH-Navigator.

    Parallel to `FramesData`, with two deliberate differences:

    1. Side order is top / right / bottom / left - the `PhWindowFrame` element order
       that every downstream consumer uses - rather than `FramesData`'s historical
       left / right / top / bottom. `SIDES` is the single source of that order.
    2. A missing or null side stays `None` instead of becoming a zero-valued object.
       Fabricating a 0.0 here would silently assert 'no thermal bridge' for an edge
       the server said nothing about.
    """

    SIDES = ("top", "right", "bottom", "left")

    def __init__(self, _top, _right, _bottom, _left):
        # type: (InstallData | None, InstallData | None, InstallData | None, InstallData | None) -> None
        self.top = _top
        self.right = _right
        self.bottom = _bottom
        self.left = _left

    @classmethod
    def from_dict(cls, _data_dict):
        # type: (dict[str, Any]) -> InstallsData
        """Create an InstallsData object from a dictionary."""
        # -- NOTE: splatted positionally, so `SIDES` must stay in the same order as
        # -- `__init__`'s parameters. `test_get_all_installs_is_top_right_bottom_left`
        # -- pins that order.
        sides = []
        for side in cls.SIDES:
            side_dict = _data_dict.get(side)
            sides.append(InstallData.from_dict(side_dict) if side_dict else None)
        return cls(*sides)

    def get_install_by_side(self, _side):
        # type: (str) -> InstallData | None
        """Get the install data by side name, or None if that side has no data."""
        return getattr(self, _side, None)

    def get_all_installs(self):
        # type: () -> list[InstallData | None]
        """Get all four installs in top / right / bottom / left order.

        NOTE: unlike `FramesData.get_all_frames`, this does NOT drop `None` entries.
        The result is consumed positionally against `SIDES`, so filtering would
        misalign the remaining sides.
        """
        return [self.get_install_by_side(side) for side in self.SIDES]

    def __copy__(self):
        # type: () -> InstallsData
        """Create a copy of this InstallsData object."""
        return InstallsData(
            copy(self.top),
            copy(self.right),
            copy(self.bottom),
            copy(self.left),
        )

    def __str__(self):
        # type: () -> str
        """String representation of the InstallsData object."""
        return "InstallsData(_top={}, _right={}, _bottom={}, _left={})".format(
            self.top, self.right, self.bottom, self.left
        )

    def __repr__(self):
        # type: () -> str
        return str(self)

    def ToString(self):
        # type: () -> str
        return str(self)


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
        _installs=None,
    ):
        # type: (str, str, int, int, int, int, GlazingData, FramesData, InstallsData | None) -> None
        self.aperture_type_name = _aperture_type_name
        self.name = _name
        self.column_number = _column_number
        self.row_number = _row_number
        self.column_span = _column_span
        self.row_span = _row_span
        self.glazing = _glazing
        self.frames = _frames
        # -- `None` (not an empty InstallsData) when the payload carries no `installs`
        # -- block at all, ie. a server older than the per-edge contract. Downstream
        # -- treats that as 'legacy payload, behave exactly as before'.
        self.installs = _installs

    @property
    def type_name(self):
        # type: () -> str
        """Get the type-name of the element with the Col and Row position. ie: 'A_C1_R2'."""
        return "{}_C{}_R{}".format(self.aperture_type_name, self.column_number, self.row_number)

    @classmethod
    def from_dict(cls, _data_dict, _aperture_type_name=""):
        # type: (dict[str, Any], str) -> ElementData
        """Create an ElementData object from a dictionary."""

        installs_dict = _data_dict.get("installs")
        return cls(
            _aperture_type_name=_aperture_type_name,
            _name=_data_dict.get("name", ""),
            _column_number=_as_int(_data_dict.get("column_number"), 0),
            _row_number=_as_int(_data_dict.get("row_number"), 0),
            _column_span=_as_int(_data_dict.get("col_span"), 1),
            _row_span=_as_int(_data_dict.get("row_span"), 1),
            _glazing=GlazingData.from_dict(_data_dict.get("glazing") or {}),
            _frames=FramesData.from_dict(_data_dict.get("frames") or {}),
            _installs=InstallsData.from_dict(installs_dict) if installs_dict else None,
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
            copy(self.installs),
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

    def __init__(self, _name, _display_name, _column_widths_mm, _row_heights_mm, _elements):
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
            _column_widths_mm=[_as_float(w, 0.0) for w in (_data_dict.get("column_widths_mm") or [])],
            _row_heights_mm=[_as_float(h, 0.0) for h in (_data_dict.get("row_heights_mm") or [])],
            _elements=[
                ElementData.from_dict(elem, _data_dict.get("name", "")) for elem in (_data_dict.get("elements") or [])
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
                new_elem.row_number = len(self.row_heights_mm) - 1 - elem.row_number - elem.row_span + 1
                elements_.append(new_elem)
        return elements_
