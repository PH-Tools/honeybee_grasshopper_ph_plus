# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Get From Custom Collection."""

try:
    from typing import Any
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
    def __init__(self, _IGH, _collection, _keys, _strict=False, *args, **kwargs):
        # type: (gh_io.IGH, CustomCollection, list[str], bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.collection = _collection
        self.keys = _keys
        self.strict = _strict

    def run(self):
        # type: () -> list
        if not self.collection or not self.keys:
            return []

        if self.strict == True:
            try:
                return [self.collection[key] for key in self.keys]
            except KeyError:
                self.IGH.error(
                    "Key(s): {} not found in collection.".format(
                        [k for k in self.keys if k not in self.collection]
                    )
                )
                return []
        else:
            return [self.collection.get(key, None) for key in self.keys]
