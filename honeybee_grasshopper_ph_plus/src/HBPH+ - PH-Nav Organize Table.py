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
Reshape the raw data from 'PH-Nav Get Table' into named, table-specific output ports that
plug straight into the Honeybee-PH create-components. The output ports change automatically
based on the '_type' (table name): wire the 'table_name_' output of 'PH-Nav Get Table' into
'_type', and the ports below rename themselves for that table (rooms, ventilators, etc.).
-
Single-select fields (Type, Inside/Outside, ...) are emitted as their text label. All values
are passed through as raw SI units (see each port's tooltip); convert downstream as needed.
The 'report_' output lists any downloaded column that did not map to an output port, so no
data is ever silently dropped.
-
Note: The heat-pump tables are not yet supported. 'space_types' has no mapping yet and is
passed through unchanged on a 'records_' port.
-
EM July 5, 2026
    Args:
        _records: (list) The 'records_' output from the 'PH-Nav Get Table' component.

        _field_defs: (list) The 'field_defs_' output from the 'PH-Nav Get Table' component
            (used to label unmapped columns in the 'report_').

        _type: (str) The table name. Wire the 'table_name_' output of 'PH-Nav Get Table'
            here. This selects which set of output ports to show.

    Returns:
        report_: (list[str]) Notes about the reshape: record / port counts, ports that
            resolved to no data, and any downloaded columns not mapped to an output port.

        (dynamic): The remaining output ports are named automatically based on '_type'.
            For example, for 'ventilators': name_, heat_recovery_pct_, energy_recovery_pct_,
            elec_efficiency_, frost_protection_, frost_temp_limit_, inside_outside_.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    # -- Import the module directly (not via the `gh_compo_io` package): the
    # -- wrapper needs the module-level `get_component_outputs` function, which the
    # -- package only wildcard-re-exports classes from, not free functions.
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1 import table_organize
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_plus_rhino:\n\t{}'.format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))


# ------------------------------------------------------------------------------
import honeybee_ph_plus_rhino._component_info_
reload(honeybee_ph_plus_rhino._component_info_)
ghenv.Component.Name = "HBPH+ - PH-Nav Organize Table"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(table_organize)
    reload(gh_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
# -- Rewrite the dynamic output ports for the current '_type' BEFORE running, so
# -- the (renamed) ports line up with the value-lists produced below. Port 0 is
# -- GH's reserved 'out' stream; port 1 is the fixed 'report_'; data ports start
# -- at DATA_PORT_START_INDEX.
output_spec = table_organize.get_component_outputs(_type)
gh_io.setup_component_outputs(IGH, output_spec, _start_i=table_organize.DATA_PORT_START_INDEX)

# ------------------------------------------------------------------------------
gh_compo_interface = table_organize.GHCompo_PHNavV1OrganizeTable(
    IGH,
    _records,
    _field_defs,
    _type,
    )
result_dict = gh_compo_interface.run()

# ------------------------------------------------------------------------------
# -- Surface the results. GHPython reads each output from the script global whose
# -- name matches the (now-renamed) port, so assign the dynamic ports by name.
report_ = result_dict.get("report_", [])
for _output_node in output_spec.values():
    globals()[_output_node.name] = result_dict.get(_output_node.name, [])
