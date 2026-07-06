# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Thin display wrappers for the route-5 element-table payload (records + field defs).

The route-5 payload is rows of plain dicts. A bare dict handed to a Grasshopper
panel renders as the useless string `IronPython.Runtime.PythonDictionary` (GH shows
whatever `.ToString()` returns, and a dict returns its type name, not its contents).
Wrapping each row in a small class whose `ToString()`/`__repr__` renders the actual
data lets the user *see* what they downloaded on the canvas.

The wrappers stay **dict-like** on purpose (`.get` / `[]` / `.items()` / `in`), so the
downstream `Organize Table` component (and any user script) reads fields exactly as if
they were still raw dicts - the wrapping is transparent to consumers, cosmetic to GH.
`to_dict()` is a public escape hatch back to the underlying dict for any consumer that
wants it raw.
"""

try:
    from typing import Any, ItemsView, Iterator, KeysView, ValuesView  # noqa: F401
except ImportError:
    pass  # IronPython 2.7


class _ReadableDict(object):
    """Read-only dict-like view that renders its *contents* (not its type) in GH.

    Base for the table wrappers. Holds one payload dict and forwards the read side
    of the mapping protocol to it. Subclasses only supply `__repr__`.
    """

    def __init__(self, _data):
        # type: (dict | None) -> None
        self._data = _data or {}

    def get(self, _key, _default=None):
        # type: (str, Any) -> Any
        return self._data.get(_key, _default)

    def keys(self):
        # type: () -> KeysView[str]
        return self._data.keys()

    def values(self):
        # type: () -> ValuesView
        return self._data.values()

    def items(self):
        # type: () -> ItemsView
        return self._data.items()

    def to_dict(self):
        # type: () -> dict
        """Return the underlying payload dict verbatim (escape hatch for raw access)."""
        return self._data

    def __getitem__(self, _key):
        # type: (str) -> Any
        return self._data[_key]

    def __contains__(self, _key):
        # type: (str) -> bool
        return _key in self._data

    def __iter__(self):
        # type: () -> Iterator[str]
        return iter(self._data)

    def __str__(self):
        return self.__repr__()

    def ToString(self):
        # -- GH calls .NET `ToString()` when displaying an object on the canvas.
        return self.__repr__()


class TableRecord(_ReadableDict):
    """One element-table row: `id` + typed built-in columns + `custom_values` / `custom_links` bags."""

    @property
    def id(self):
        # type: () -> Any
        """The row id - present on every table; used for cross-table joins downstream."""
        return self._data.get("id")

    def __repr__(self):
        return "TableRecord({})".format(self._data)


class FieldDef(_ReadableDict):
    """One field definition: `field_key`, `display_name`, `field_type`, `config`, `origin`, ..."""

    def __repr__(self):
        return "FieldDef({} [{}])".format(self._data.get("field_key"), self._data.get("field_type"))
