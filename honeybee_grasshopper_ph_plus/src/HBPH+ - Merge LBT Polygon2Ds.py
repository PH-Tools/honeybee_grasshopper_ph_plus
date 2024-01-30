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
Merge together a group of Ladybug Polygon2D objects. Note that the groups of 
Polygon2D objects should be touching or overlapping in order to merge properly.
-
EM January 29, 2024
    Args:
        _tolerance: (float) The Optional tolerance value to use when translating
            the faces into reference space. If none is supplied, 
            will use the Rhino document's tolerance. 

        _lbt_polygon_2ds: (List[Polygon2D]) A group of Polygon2D objects to merge together into
            a single new Polygon2D.
        
    Returns:
        lbt_polygon_2ds_: (List[Polygon2D]) All the HB-face's Ladybug Polygon2Ds, translated into 
            the reference space of the reference-face (the first face in the '_hb_faces')
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
ghenv.Component.Name = "HBPH+ - Merge LBT Polygon2Ds"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_utils import vector3d_tools
    reload(vector3d_tools)
    from honeybee_ph_utils import polygon2d_tools
    reload(polygon2d_tools)
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import merge_lbt_polygon2ds as gh_compo_io
    reload(gh_compo_io)

    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_MergeLBTPolygon2Ds(
        IGH,
        _tolerance,
        _lbt_polygon_2ds,
)
lbt_polygon_2ds_ = gh_compo_interface.run()