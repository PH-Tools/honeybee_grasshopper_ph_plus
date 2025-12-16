# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Get Shading Factors from DesignPH."""

try:
    from typing import Dict, List, Tuple
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee.aperture import Aperture
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class ShadingRow(object):
    def __init__(self, data):
        # type: (List[str]) -> None
        """data = ['1', 'C.0.1', '4 - South Windows', '0.91', '2.03', 'Wall_002_S', '0.22', '0.23']"""
        self.row_number = data[0]
        self.display_name = data[1]
        self.group_type = data[2]
        self.width_m = data[3]
        self.height_m = data[4]
        self.host_wall = data[5]
        self.winter_shading_factor = float(data[6])
        self.summer_shading_factor = float(data[7])


def _split_list_at_none(lst):
    # type: (List[str]) -> List[List[str]]
    """Split a list of items: [a, b, '', '', c, d] -> [[a, b, c], [c, d]]"""
    result = []
    sub_list = []
    for item in lst:
        if item is not "":
            sub_list.append(item)
        elif sub_list:
            result.append(sub_list)
            sub_list = []
    if sub_list:
        result.append(sub_list)
    return result


class GHCompo_GetDesignPHShadingFactors(object):
    def __init__(self, _IGH, _hb_apertures, _data, *args, **kwargs):
        # type: (gh_io.IGH, List[Aperture], List[str], List, Dict) -> None
        self.IGH = _IGH
        self.hb_apertures = _hb_apertures
        self.data = _data

    def _parse_data(self):
        # type: () -> Dict[str, ShadingRow]
        # --- Organize the input data from DesignPH
        shading_row_data = {}
        for data in _split_list_at_none(self.data):
            new_shading_row = ShadingRow(data)
            shading_row_data[new_shading_row.display_name] = new_shading_row

        return shading_row_data

    def run(self):
        # type: () -> Tuple[List[float],List[float]]

        # --- Output the Shading Factors in the same order as the apertures
        shading_row_data = self._parse_data()
        winter_shading_factors_, summer_shading_factors_ = [], []
        for hb_ap in self.hb_apertures:
            # -- Try to find the shading factor for the aperture
            try:
                d = shading_row_data[hb_ap.display_name]
            except KeyError:
                msg = "Failed to find any shading factor data for the aperture '{}'.".format(hb_ap.display_name)
                self.IGH.warning(msg)
                d = None

            # -- Add the aperture's shading factor, if it exists
            if d:
                winter_shading_factors_.append(d.winter_shading_factor)
                summer_shading_factors_.append(d.summer_shading_factor)
            else:
                winter_shading_factors_.append(None)
                summer_shading_factors_.append(None)

        return winter_shading_factors_, summer_shading_factors_
