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
Check the mesh-geometry for Honeybee-Shades. This will provide a warning if the ratio of 
mesh-faces / mesh-vertices is above the threshold (default=1.5), which is a marker of suspect geometry. 
Use the 'check_shades_' output to visualize the suspect shades. Often is is easiest to 
simplty re-drawn the shade geometry in Rhino more cleanly to resolve these meshing issues.
- 
Note that not all shades flagged here will cause a failure or problem. This merely means that the 
meshes have many faces, and may increase the computation time and file sizes in later operations. 
This is especially true if you are visualizing these meshes outside Rhino. Try to keep your shade 
geometry as simple as can be and keep the meshes as clean as possible to improve performance.
-
EM May 29, 2024
    Args:
        _shades: (List[Shade]) A list of the Honeybee Shades to check the meshes of. 

        _threshold: (float) default=1.5 | The ratio of faces::vertices of the resultant
            mesh which indicates that it should be checked and could probably be cleaned up.
            
    Returns:
        check_shades_: A list of the suspect shade meshes. Visualize these to see which 
            elements can likely be cleaned up or improved in your Rhino-scene. 
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
ghenv.Component.Name = "HBPH+ - Check Shade Mesh"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import check_shade_mesh as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CheckShadeMesh(
    IGH,
    _shades,
    _threshold,
)
check_shades_ = gh_compo_interface.run()
