# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Create Rhino Geometry."""

from collections import OrderedDict

try:
    from itertools import izip  # type: ignore
except ImportError:
    # Python 3
    izip = zip

try:
    from typing import Any, Dict, List, Tuple
except ImportError:
    pass  # Python 3

try:
    from Rhino.Geometry import Brep, LineCurve  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import win_create_types
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


class GHCompo_CreateWindowRhinoGeometry(object):
    NAME_FORMAT = "{}_C{}_R{}"

    def __init__(
        self, _IGH, _win_baselines, _win_names, _win_collection, *args, **kwargs
    ):
        # type: (gh_io.IGH, List[LineCurve], List[str], Dict[str, win_create_types.WindowUnitType], *Any, **Any) -> None
        self.IGH = _IGH
        self.win_collection = _win_collection
        self.win_baselines = _win_baselines
        self.win_names = _win_names

    def check_input(self):
        if not self.win_baselines or not self.win_names:
            return

        if len(self.win_baselines) != len(self.win_names):
            msg = "The number of window-baselines and window-names must be the same."
            raise Exception(msg)

    def check_result(self, _win_type, _srfcs, _names):
        if len(_srfcs) != len(_names):
            msg = "Failed to create window geometry for window type: {}".format(_win_type)
            raise Exception(msg)

    def create_names(self, _id_data):
        # type: (OrderedDict[int, Dict[str, Any]]) -> List[str]
        """Create names for the window surfaces."""
        names = []
        for id, data in _id_data.items():
            type_name = data["type_name"]
            col = data["col"]
            row = data["row"]
            try:
                names.append(self.NAME_FORMAT.format(type_name, col, row))
            except Exception as e:
                msg = (
                    "Error creating the window name using the format: '{}'? \n{}".format(
                        self.NAME_FORMAT, e
                    )
                )
                self.IGH.error(msg)
                names.append("{}".format(type_name))
        return names

    def run(self):
        # type: () -> Tuple[List[Brep], List[str]]
        """Return a list of window surfaces and their names."""
        self.check_input()

        win_surfaces_, surface_names_ = [], []
        for baseline, name in izip(self.win_baselines, self.win_names):
            try:
                win_type = self.win_collection[name]
            except KeyError:
                msg = (
                    "Failed to find window type named: '{}' in the window-type-collection?\n"
                    "Valid type-names include: [{}]".format(
                        name, ", ".join(list(self.win_collection.keys()))
                    )
                )
                raise KeyError(msg)
            surfaces, id_data = win_type.build(baseline)
            self.check_result(win_type, surfaces, id_data)
            win_surfaces_ += surfaces

            # -- Create the name from the id-data
            surface_names_ += self.create_names(id_data)

        return win_surfaces_, surface_names_
