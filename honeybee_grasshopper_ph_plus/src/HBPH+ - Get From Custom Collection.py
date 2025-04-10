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
Get all of the Rhino Material Names for the subfaces of a closed Brep. This is 
useful wheh using Materials as the 'key' for assigning things like constructions, 
boundary-conditions or other sub-face specific values.
-
EM April 7, 2025
    Args:
        _collection: (List[Guid]) A CustomCollection to get items from.
        
        _keys: (List[str]) A list of the keys to 'get' from the collection

        _strict: (bool) Default=False. If 'strict' is set to true, will raise an
            error if the Key is not found in the collection. If false (default) 
            will simply outut 'None' if key is not found.
        
    Returns:
        values_: The items found, or None if not found.
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
ghenv.Component.Name = "HBPH+ - Get From Custom Collection"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev="250407")
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.collections import get_item_from_collection as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_GetFromCustomCollection(
    IGH,
    _collection,
    _keys,
    _strict,
    )
values_ = gh_compo_interface.run()