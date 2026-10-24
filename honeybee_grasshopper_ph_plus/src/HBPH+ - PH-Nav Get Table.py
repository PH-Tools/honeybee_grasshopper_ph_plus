#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
#
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
#
# Copyright (c) 2022, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com>
# Honeybee-PH is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 3 of the License,
# or (at your option) any later version.
#
# Honeybee-PH is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For a copy of the GNU General Public License
# see <https://github.com/PH-Tools/honeybee_ph/blob/main/LICENSE>.
#
# @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>
#
"""
Download one element table (rooms, ventilators, thermal-bridges, ...) from a PH-Navigator
project as raw rows plus their field definitions. This is a generic downloader for all of
the row-based element types; wire the outputs into 'PH-Nav Organize Table' to reshape the
rows into Honeybee-PH objects. Optionally pin a specific saved version using the '_version'
input (see the 'PH-Nav Get Versions' component); if no version is pinned, the project's
latest saved version is used.
-
Note: Only raw stored fields are returned. Computed / formula rollups (e.g. a room's total
airflow) are not included yet.
-
EM July 5, 2026
    Args:
        _project_number: (str) The PH-Navigator project number (ie: '2524').

        _table_name: (str) The element table to download. Must be one of the 12 valid
            names (rooms, space_types, thermal_bridges, pumps, fans, ventilators,
            hot_water_heaters, hot_water_tanks, electric_heaters, appliances,
            heat_pump_indoor_units, heat_pump_outdoor_units).

        _key: (str) Optional. The record field to key the 'record_collection_' output
            by (ie: 'number' for rooms, to match records against Rhino geometry). Looks
            in the built-in columns first, then the record's custom fields. Leave empty
            to key the collection by each record's unique 'id'.

        _version: (str) Optional. A specific saved 'version_id' to download. Leave
            empty to use the project's latest saved version.

        _token: (str) Optional. A PH-Navigator bearer token. Leave empty for
            anonymous read access.

        _download: (bool) Set True to download the table from the project.

    Returns:
        records_: (list[TableRecord]) One 'TableRecord' per row: 'id' + the typed
            built-in columns + a 'custom_values' bag + a 'custom_links' bag. Dict-like
            (record.get('name'), record['id']) but displays its contents in a panel.

        record_collection_: (CustomCollection) The same records as a keyed collection
            (keyed by '_key', or by record 'id' if no '_key' is given). Feed this into
            'HBPH - Get From Custom Collection' to look up a record by its key - eg. to
            match a downloaded room to a Rhino geometry element by room number.

        field_defs_: (list[FieldDef]) The field definitions (built-in + custom) for the
            table: 'field_key', 'display_name', 'field_type', 'config', 'origin', etc.
            Dict-like, and displays its contents in a panel.

        table_name_: (str) The resolved table name (feeds 'PH-Nav Organize Table').

        json_: (str) The raw downloaded table data, as a formatted JSON string
            (handy for debugging).

        last_modified_: (str) The save-timestamp of the downloaded version (for
            freshness / change-detection).
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_plus_rhino import gh_compo_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_plus_rhino:\n\t{}'.format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))


# ------------------------------------------------------------------------------
import honeybee_ph_plus_rhino._component_info_
reload(honeybee_ph_plus_rhino._component_info_)
ghenv.Component.Name = "HBPH+ - PH-Nav Get Table"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1 import table_get as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_PHNavV1GetTable(
    IGH,
    _project_number,
    _table_name,
    _key,
    _version,
    "http://localhost:8000/api/v1/gh" if DEV else "",
    _token,
    _download,
    )
records_, record_collection_, field_defs_, table_name_, json_, last_modified_ = gh_compo_interface.run()
