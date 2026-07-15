# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get Object Attributes."""

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
    from System import Object  # type: ignore
except Exception:
    pass  # Outside Rhino

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")


class GHCompo_GetObjectAttributes(object):
    def __init__(self, _IGH, _objects, _keys):
        # type: (gh_io.IGH, list[object], list[str]) -> None
        self.IGH = _IGH
        self.objects = _objects
        self.keys = _keys

    def clean_key(self, _key):
        # type: (str) -> str
        """Returns the input key, cleaned and upper-cased."""
        return str(_key).strip().upper()

    def get_item_from_object(self, _obj, _key):
        # type: (Any, Any) -> Any
        # Try getting with the 'clean' key
        try:
            return getattr(_obj, self.clean_key(_key))
        except Exception:
            # try getting with the raw key
            return getattr(_obj, _key)

    def add_item_to_output(self, _item, _output, path_idx):
        # type: (Any, Any, int) -> Any

        if isinstance(_item, list):
            _output.AddRange(_item, GH_Path(path_idx))
        else:
            _output.Add(_item, GH_Path(path_idx))
        return _output

    def run(self):
        # type: () -> DataTree
        """Return a DataTree with the values gotten from the objects."""

        values_ = DataTree[Object]()

        for obj in self.objects:
            for path_idx, key in enumerate(self.keys):
                data_item = self.get_item_from_object(obj, key)
                self.add_item_to_output(data_item, values_, path_idx)

        return values_
