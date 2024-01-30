# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get From Custom Collection."""

try:
    from typing import Dict, List
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")

try:
    from honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection import (
        CustomCollection,
    )
except:
    raise ImportError("Failed to import honeybee_ph_plus_rhino")


class GHCompo_GetFromCustomCollection(object):
    def __init__(self, _IGH, _collection, _keys, *args, **kwargs):
        # type: (gh_io.IGH, CustomCollection, List[str], List, Dict) -> None
        self.IGH = _IGH
        self.collection = _collection
        self.keys = _keys

    def run(self):
        # type: () -> List
        if not self.collection or not self.keys:
            return []

        return [self.collection.get(key, None) for key in self.keys]
