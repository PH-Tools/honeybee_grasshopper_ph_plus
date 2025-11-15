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
Pull out the ERV Ducting objects as 'Model Objects' which can be exported. This is especially
useful when exporting to Sketchup or other 3D model formats outside of Rhino.
-
EM Nov 06, 2025
    Args:

        _hb_model: (Model) The Honeybee-Model object to pull the ERV Ducting out of.
         
        _duct_type: (str) Input either -
- "1-Supply" (default)
- "2-Exhaust"
            
    Returns:

        duct_objects_: (DataTree[]) The Duct Model-Objects for exporting.
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
ghenv.Component.Name = "HBPH+ - Create ERV Duct Model Objects"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.reporting import build_erv_duct_objects as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_BuildErvDucting(
    IGH,
    _hb_model,
    _duct_type,
)
duct_objects_ = gh_compo_interface.run()