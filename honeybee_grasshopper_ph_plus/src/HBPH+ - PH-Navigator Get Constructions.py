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
Download Constructons from the PH-Navigator website. This will download the data and attempt 
to build a new Honeybee OpaqueConstruction for each Assembly in the project.
-
EM May 20, 2025
    Args:

        _project_numner: (int) The project numner (ie: '2305') to get the Construction of.
         
        _download: (bool) Set True to download the data from the specified project.
            
    Returns:
        
        constructions_: (list[OpaqueConstruction]) The Honeybee-Energy Constructions built from the 
            data on the PH-Navigator project site.
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
ghenv.Component.Name = "HBPH+ - PH-Navigator Get Constructions"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator import constructions_get as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_PHNavGetConstructions(
    IGH,
    _project_number,
    "http://127.0.0.1:8000" if DEV else "",
    _download,
    )
constructions_ = gh_compo_interface.run()