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
Calculate an envelope infiltration rate (m3/s-m2) base on a specified ACH (Air Change Rate) value. This
is typical for PHI Passive House projects which use an ACH limiting value for Certification. Note that
this component will use the NET interior volume of the Spaces, so ensure that all of your Honeybee-Rooms
have Spaces added BEFORE using this component. The exterior envelope area will include all faces exposed
to the Ouotdoor air, or Ground, but not faces expose to Adiabatic or Surface conditions.
-
EM December 16, 2025
    Args:
        _ach_at_50Pa: The Air Change Rate (ACH) at 50Pa. Typical Values:
- PHI New Construction: 0.6 ACH@50Pa
- PHI EnerPHit: 1.0 ACH@50Pa
- PHI Low Energy Building: 1.0 ACH@50PA

        _hb_rooms: The Honeybee-Rooms to use as the reference volume and envelope area.
    
    Returns:
        infilt_per_exterior_at_4Pa_: The envelope air infiltration rate (m3/s-m2)
            ---
            This value can be passed directly into the Honeybee 'Apply Load Values' component 
            as the 'infilt_per_area' value. Note that this value is calculated at 4Pa of pressure, 
            which is an approximate for the 'resting' normal pressure difference.

        infilt_per_exterior_at_50Pa_: The envelope air infiltration rate (m3/s-m2)
            --- 
            This value can be  passed into the Honeybee 'Blower Pressure Converter' in order 
            to determine the infiltration rate at a specific resting pressure. Note that this 
            value should NOT be passed directly into the Honeybee 'Apply Load Values' component as 
            the 'infilt_per_area'. For this, use the 'infilt_per_exterior_at_4Pa_' value instead.
"""


import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

from ph_gh_component_io import gh_io
from honeybee_ph_plus_rhino import gh_compo_io

# ------------------------------------------------------------------------------
import honeybee_ph_plus_rhino._component_info_
reload(honeybee_ph_plus_rhino._component_info_)
ghenv.Component.Name = "HBPH+ - Infiltration from ACH"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import infiltration_from_ach as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


#-------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CalculateInfiltrationFromACH(
        IGH,
        _ach_at_50Pa,
        _hb_rooms,
    )
infilt_per_exterior_at_4Pa_, infilt_per_exterior_at_50Pa_ = gh_compo_interface.run()