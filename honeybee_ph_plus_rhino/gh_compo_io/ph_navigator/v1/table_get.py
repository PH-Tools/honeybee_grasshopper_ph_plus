# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - PH-Nav Get Table."""

import json

try:
    from typing import Any  # noqa: F401
except ImportError:
    pass  # IronPython 2.7

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io. {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection import CustomCollection
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1.client import PHNavV1Client
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1.table_names import VALID_TABLE_NAMES
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1.table_schema import FieldDef, TableRecord
except ImportError as e:
    raise ImportError("\nFailed to import from honeybee_ph_plus_rhino {}".format(e))


class GHCompo_PHNavV1GetTable(object):
    """Download one PH-Navigator element table as raw rows + field definitions.

    Route 5 (`GET /tables/{table_name}`) of the V1 read API - the single generic
    downloader for all 12 row-based element types (`rooms`, `ventilators`, ... see
    `VALID_TABLE_NAMES`). Transport lives in `PHNavV1Client`; this component only
    validates the table name, then wraps each row / field-def in a dict-like
    `TableRecord` / `FieldDef` (so GH can display the contents instead of the bare
    `PythonDictionary` type name) and passes them through otherwise unchanged.
    Reshaping rows into Honeybee/PH objects is the job of the separate `Organize
    Table` component, keyed on the `table_name_` echoed here.

    The same records are also emitted as a `CustomCollection` (`record_collection_`)
    keyed by the `_key` field - the common GH pattern for matching a downloaded record
    to a Rhino geometry element via `Get From Custom Collection`. With no `_key` the
    collection is keyed by each record's `id`; duplicate keys are warned (not silently
    dropped) since the caller almost certainly wants a unique key.

    `_table_name` is validated against `VALID_TABLE_NAMES` before any network call, so
    a typo fails fast on the canvas instead of round-tripping to a 422. Everything past
    that (transport / envelope / HTTP errors) is handled by `PHNavV1Client`, which
    returns `None` after logging via `IGH.error`.
    """

    def __init__(self, _IGH, _project_number, _table_name, _key, _version, _url_base, _token, _download, *args, **kwargs):
        # type: (gh_io.IGH, str, str | None, str | None, str | None, str | None, str | None, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.project_number = _project_number
        self.table_name = _table_name
        self.key = _key
        self.version = _version
        self.url_base = _url_base
        self.token = _token
        self.download = _download

    @property
    def ready(self):
        # type: () -> bool
        return bool(self.download and self.project_number and self.table_name)

    def _empty_result(self):
        # type: () -> tuple[list, CustomCollection, list, str | None, str | None, str | None]
        """The 'nothing downloaded' result - matches the run() arity with empty values."""
        return [], CustomCollection(), [], None, None, None

    def run(self):
        # type: () -> tuple[list, CustomCollection, list, str | None, str | None, str | None]
        """Download one element table; wrap its rows + field defs for readable GH display."""
        if not self.ready:
            return self._empty_result()

        if self.table_name not in VALID_TABLE_NAMES:
            self.IGH.error(
                "Unknown table name '{}'. Valid names are:\n{}".format(
                    self.table_name, "\n".join(VALID_TABLE_NAMES)
                )
            )
            return self._empty_result()

        client = PHNavV1Client(self.IGH, self.project_number, self.url_base, self.token, self.version)
        records, field_defs = client.get_table(self.table_name)
        if records is None:
            # -- The client already surfaced the failure via IGH.error.
            return self._empty_result()

        if not records:
            # -- Empty table is a valid state (not a 404) - warn, do not error.
            self.IGH.warning("Table '{}' returned no records (it is empty).".format(self.table_name))

        # -- Build the raw preview from the payload dicts BEFORE wrapping, so `json_`
        # -- stays faithful JSON. The wrappers are dict-like, so the values are
        # -- unchanged for downstream consumers - only their GH display improves.
        json_preview = json.dumps({"records": records, "field_defs": field_defs}, indent=2, ensure_ascii=False)
        records = [TableRecord(r) for r in records]
        field_defs = [FieldDef(f) for f in field_defs]
        record_collection = self._build_collection(records)
        return records, record_collection, field_defs, self.table_name, json_preview, client.last_modified

    def _build_collection(self, _records):
        # type: (list[TableRecord]) -> CustomCollection
        """Index the wrapped records into a `CustomCollection` keyed by `_key` (or `id`)."""
        collection = CustomCollection(self.table_name or "")
        for record in _records:
            key = self._record_key(record)
            if key in collection:
                self.IGH.warning(
                    "Duplicate collection key '{}' in table '{}'; the later record overwrites the "
                    "earlier one. Pick a '_key' field with unique values.".format(key, self.table_name)
                )
            collection[key] = record
        return collection

    def _record_key(self, _record):
        # type: (TableRecord) -> str
        """The collection key for one record: the `_key` field value (built-in column
        first, then the `custom_values` bag), else the record's own `id`. Single-select
        values (`{"id", "label"}`) key on their label. Always stringified so the key is
        hashable and matches a text key supplied on the canvas."""
        if not self.key:
            return str(_record.id)
        value = _record.get(self.key)
        if value is None:
            value = (_record.get("custom_values") or {}).get(self.key)
        if isinstance(value, dict) and "id" in value and "label" in value:
            value = value["label"]
        return str(value)
