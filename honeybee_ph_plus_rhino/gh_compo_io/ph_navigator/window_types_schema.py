# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Schema classes for PH-Navigator Window Types API data."""

try:
    from typing import List, Dict, Optional, Any
except ImportError:
    pass  # IronPython 2.7


class GlazingData(object):
    """Schema for glazing data from PH-Navigator."""
    
    def __init__(self, data_dict):
        # type: (Dict[str, Any]) -> None
        self.id = str(data_dict.get("id", ""))
        self.name = data_dict.get("name", "")
        self.u_value_w_m2k = float(data_dict.get("u_value_w_m2k", 0.0))
        self.g_value = float(data_dict.get("g_value", 0.0))

    @property
    def display_name(self):
        return self.name


class FrameData(object):
    """Schema for frame data from PH-Navigator."""
    
    def __init__(self, data_dict):
        # type: (Dict[str, Any]) -> None
        self.id = str(data_dict.get("id", ""))
        self.name = data_dict.get("name", "")
        self.width_mm = float(data_dict.get("width_mm", 0.0))
        self.u_value_w_m2k = float(data_dict.get("u_value_w_m2k", 0.0))
        self.psi_glazing = float(data_dict.get("psi_glazing", 0.0))
        self.psi_install = float(data_dict.get("psi_install", 0.0))
        self.chi_value = float(data_dict.get("chi_value", 0.0))

    @property
    def display_name(self):
        return self.name

    @property
    def width_m(self):
        # type: () -> float
        """Get the width in meters."""
        return self.width_mm / 1000.0


class FramesData(object):
    """Schema for frames collection (left, right, top, bottom) from PH-Navigator."""
    
    def __init__(self, data_dict):
        # type: (Dict[str, Any]) -> None
        self.left = FrameData(data_dict.get("left", {})) if data_dict.get("left") else None
        self.right = FrameData(data_dict.get("right", {})) if data_dict.get("right") else None
        self.top = FrameData(data_dict.get("top", {})) if data_dict.get("top") else None
        self.bottom = FrameData(data_dict.get("bottom", {})) if data_dict.get("bottom") else None
    
    def get_all_frames(self):
        # type: () -> List[FrameData]
        """Get all non-None frame data objects."""
        frames = []
        for frame in [self.left, self.right, self.top, self.bottom]:
            if frame is not None:
                frames.append(frame)
        return frames
    
    def get_frame_by_side(self, side):
        # type: (str) -> Optional[FrameData]
        """Get frame data by side name."""
        return getattr(self, side, None)


class ElementData(object):
    """Schema for element data from PH-Navigator."""
    
    def __init__(self, data_dict):
        # type: (Dict[str, Any]) -> None
        self.id = int(data_dict.get("id", 0))
        self.name = data_dict.get("name", "")
        self.column_number = int(data_dict.get("column_number", 0))
        self.row_number = int(data_dict.get("row_number", 0))
        self.column_span = int(data_dict.get("column_span", 1))
        self.row_span = int(data_dict.get("row_span", 1))
        self.glazing = GlazingData(data_dict["glazing"]) if data_dict.get("glazing", None) else None
        self.frames = FramesData(data_dict.get("frames", {}))
    
    @property
    def element_id_suffix(self):
        # type: () -> str
        """Get the element ID suffix (C{column}_R{row})."""
        return "C{}_R{}".format(self.column_number, self.row_number)


class ApertureTypeData(object):
    """Schema for aperture type data from PH-Navigator."""
    
    def __init__(self, data_dict):
        # type: (Dict[str, Any]) -> None
        self.name = data_dict.get("name", "")
        self.display_name = data_dict.get("display_name", self.name)
        self.column_widths_mm = [float(w) for w in data_dict.get("column_widths_mm", [])]
        self.row_heights_mm = [float(h) for h in data_dict.get("row_heights_mm", [])]
        self.elements = [ElementData(elem) for elem in data_dict.get("elements", [])]
    
    def get_column_width_m(self, column_number):
        # type: (int) -> float
        """Get column width in meters for given column number."""
        if 0 <= column_number < len(self.column_widths_mm):
            return self.column_widths_mm[column_number] / 1000.0
        return 0.0
    
    def get_row_height_m(self, row_number):
        # type: (int) -> float
        """Get row height in meters for given row number (reversed for Rhino bottom-to-top ordering)."""
        # Reverse the row number to convert from API's top-to-bottom to Rhino's bottom-to-top
        reversed_row_number = len(self.row_heights_mm) - 1 - row_number
        if 0 <= reversed_row_number < len(self.row_heights_mm):
            return self.row_heights_mm[reversed_row_number] / 1000.0
        return 0.0
    
    def get_valid_elements(self):
        # type: () -> List[ElementData]
        """Get all valid (non-None) element data objects."""
        return [elem for elem in self.elements if elem is not None]

