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
Description....
-
EM June 15, 2024
    Args:
        _show_mask: (bool) default=True

        _color: (System.Color)

        _offset: (float) default=0.0

        _frame_type: (MaskFrame) Input Either -
"0" No Frame
"1" Rectangular Frame (default)
"2" Capsule Frame

        _show_frame: (bool) default=True

    Returns:
        mask_: The mask to apply to the Text Annotation
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
ghenv.Component.Name = "HBPH+ - Create Text Annotation Mask"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.reporting import annotation_mask as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateTextAnnotationMask(    
    IGH,
    _show_mask,
    _color,
    _offset,
    _frame_type,
    _show_frame,
)
mask_ = gh_compo_interface.run()
