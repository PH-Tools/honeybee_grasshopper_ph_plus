# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Set Item In Custom Collection."""

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection import CustomCollection
except ImportError:
    raise ImportError("Failed to import honeybee_ph_plus_rhino")


class GHCompo_SetInCustomCollection(object):
    def __init__(self, _IGH, _collection, _key, _item, *args, **kwargs):
        # type: (gh_io.IGH, CustomCollection, str, Any, list, dict) -> None
        self.IGH = _IGH
        self.collection = _collection
        self.key = _key
        self.item = _item

    def run(self):
        # type: () -> CustomCollection
        if not self.collection or not self.key:
            return self.collection

        new_collection = CustomCollection()
        for k, v in self.collection.items():
            new_collection[k] = v
        new_collection[self.key] = self.item

        return new_collection
