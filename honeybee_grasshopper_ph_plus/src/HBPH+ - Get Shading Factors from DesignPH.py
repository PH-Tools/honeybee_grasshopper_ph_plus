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
Pull out the shading factors from a text blob copied from DesignPH. After running DesignPH
to generate the shading factors, go to 'AREAS | SHADING' and simply select and copy all the    
text from this section. Paste this copied text into a Multiline Panel in GH, and then input 
this panel text into the the component here. 
-
Once all the shading factors are extracted, pass them to a "HBPH - Apply Shading Factors"
component in order to apply these factors to actual HB-Apertures.
-
If you have deciduous trees, or other seasonal variation in shading, you should run DesignPH
twice, and copy/paste the data from both runs into GH-Panels. Use two of this component in 
order to extract the seasonal shading factors separately for each of the runs.
-
EM February 15, 2024
    Args:
        _hb_apertures: (List[Aperture]) A list of Honeybee-Apertures to which are 
            used to sort and order the shading-factors.
    
        _design_ph_text: (List[str]) The text copied from DesignPH's Areasl/Shading section.
            It is expected that the text blob looks like -
[
    <empty>, 
    <empty>,
    1,
    C.0.1,
    4 - South Windows,
    0.91,
    2.03,
    Wall_002_S,
    0.22,
    0.23,
    <empty>,
    <empty>,
    2,
    N.0.z,
    ...
]
 
    Returns:
        winter_shading_factors_: (List[float]) A list of the winter-shading-factors extracted from the DesignPH
            text blob. The shading factors will be ordered to match the input Honeybee-Apertures.

        summer_shading_factors_: (List[float]) A list of the winter-shading-factors extracted from the DesignPH
            text blob. The shading factors will be ordered to match the input Honeybee-Apertures.
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
ghenv.Component.Name =  "HBPH+ - Get Shading Factors from DesignPH"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import win_get_design_ph_shading_factors as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_GetDesignPHShadingFactors(
    IGH,
    _hb_apertures,
    _design_ph_text,
    )
winter_shading_factors_, summer_shading_factors_ = gh_compo_interface.run()