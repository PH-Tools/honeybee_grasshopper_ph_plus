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
Download all of the Window-Types from the PH-Navigator website. This will download the data and attempt 
to build a new Honeybee Construction and WindowUnitType for each Aperture in the project.
-
EM Aug 05, 2025
    Args:

        _project_number: (int) The project number (ie: '2305') to get the Window Types for.
         
        _download: (bool) Set True to download the data from the specified project.
            
    Returns:

        window_types_: dict[str, WindowUnitType] A collection with all the WindowUnitTypes. Pass
            this into the "HBPH+ - Create Window Geometry" to create window geometry.
        
        constructions_: (dict[str, WindowUnitType]) A collection with all of the Honeybee-PH Window Constructions.

        json_: (str) A preview of the JSON data downloaded from PH-Navigator.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_plus_rhino import gh_compo_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_rhino:\n\t{}'.format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))


# ------------------------------------------------------------------------------
import honeybee_ph_plus_rhino._component_info_
reload(honeybee_ph_plus_rhino._component_info_)
ghenv.Component.Name = "HBPH+ - PH-Navigator Get Window Types"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import win_create_types
    reload(win_create_types)
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator import window_types_schema
    reload(window_types_schema)
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator import window_types_get as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.ph_navigator.GHCompo_PHNavGetWindowTypes(
    IGH,
    _project_number,
    "http://127.0.0.1:8000" if DEV else "",
    _download,
)
window_types_, constructions_, json_ = gh_compo_interface.run()