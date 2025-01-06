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
Convert any arbitrary unit. To use, input the value, starting-unit and 'target-unit' as a 
string such as: 
    - '23.4 M to INCHES'
    - '14.5 W/M2K as HR-FT2-F/BTU'

us the 'as' or 'to' key word to deliniate the starting unit from the target-unit. To see a 
listing of all valid unit-types, check the 'out_' node before proceeding.
-
EM January 6, 2025
    Args:
        _in: (str) The path (or paths) to the Flixo .csv files you would like 
            to import as Honeybee-Energy Materials.
            
    Returns:
        out_: The new Honeybee-Energy materials which were created from the 
            Flixo .csv files.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from honeybee_ph_rhino import gh_io
from honeybee_ph_plus_rhino import gh_compo_io

# ------------------------------------------------------------------------------
import honeybee_ph_plus_rhino._component_info_
reload(honeybee_ph_plus_rhino._component_info_)
ghenv.Component.Name = "HBPH+ - Unit Converter"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from ph_units import converter
    reload(converter)
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import convert_unit as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_ConvertValueToUnit(
    IGH,
    _in
)
out_ = gh_compo_interface.run()