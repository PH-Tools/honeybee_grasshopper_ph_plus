#
# Honeybee-PH: A Plugin for adding Passive-House data to LadybugTools Honeybee-Energy Models
# 
# This component is part of the PH-Tools toolkit <https://github.com/PH-Tools>.
# 
# Copyright (c) 2025, PH-Tools and bldgtyp, llc <phtools@bldgtyp.com> 
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
Group Honeybee-Faces by whethere they are 'coplanar' with one another. This will use the 
ladybug `Plane.is_coplanar_tolerance()` method to assess whether two faces are coplanar with
one another.
-
EM June 4, 2025
    Args:
        _tolerance: (float) Optional tolerance (model-units) value to use when
            grouping the faces. If none is supplied, will use the Rhino-document's
            tolerance value.

        _angle_tolerance_deg: (float) Optional tolerance (degrees) value to use when
            grouping the faces. If none is supplied, will use the Rhino-document's
            angle-tolerance value.

        _faces: (list[Face]) The honeybe Faces to group by coplanarity.

    Returns:

        coplanar_face_groups_: The Honeybee-Faces grouped by coplanarity.
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


#-------------------------------------------------------------------------------
import honeybee_ph_plus_rhino._component_info_
reload(honeybee_ph_plus_rhino._component_info_)
ghenv.Component.Name = "HBPH+ - Get Coplanar Face Groups"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import get_coplanar_face_groups as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_GetCoPlanarFaceGroups(
    IGH,
    _tolerance,
    _angle_tolerance_deg,
    _faces,
)

coplanar_face_groups_ = gh_compo_interface.run()