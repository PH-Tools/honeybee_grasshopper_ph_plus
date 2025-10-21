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
This component replicates the calculations found in the Phius Point Fastener Correction Calculator v25.1.0 (2025.04)
(https://www.phius.org/point-fastener-correction-calculator)

This component will adjust the thermal conductivity of the exterior insulation layer of the specified construction in
order to account for the effect of the fastener thermal bridges. This calculation is almost identical to the 
ISO 6946:2017 Appendix F, except that the Phius worksheet includes some rounding of the result values. This component
replicates this rounding behavior, even though it means it will not perfectly match calculations done following the ISO
standard. This choice was made in order to align the results here to the Phius worksheets as closely as possible.
-
EM Oct 21, 2025
    Args:
        _fastener_material: (str) Input either - 
"1-Aluminum"
"2-Mild Steel"
"3-Stanless Steel"
"4-Solid Plastic"

        _recessed_fasteners: (bool) Default=False. Choose 'True' if the fasteners start below the surface 
            of the exterior insulation if not, leave as 'False'.	

        _fastener_diameter: (float) Default=1/4". Diameter of one fastener.

        _fastener_length: (float) Default=insulation thickness. Length of fastener penetrating insulation layer. 
            Note that this can be greater than the thickness of the insulation layer if the fastener 
            passes through it at an angle.

        _reference_area: (float) The reference area for '_fastener_count'. (If a typical 4'x8' 
            section of material is being analyzed, input 32 sf)

        _fastener_count: (float) Number of fasteners used in the area being assessed within the '_reference_area'

        _layer_: (Optional[int]) An optional index for the insulation material. In none is provided, this 
            component will use the '0' (first) material in the Construction as the 'Insulation' layer being
            penetrated by the fasteners.

        _construction: (OpaqueConstruction) The Honeybee-Construction to set the adjusted thermal conductivity on.
            
    Returns:

        phius_worksheet_inputs_: (list[str]) Data to input into the Phius Point Fastener Correction Calculator v25.1.0 (2025.04)	
		
        construction_: (OpaqueConstsruction) The Honeybee-Construction with the thermal conductivity of the insulation
            layer adjusted to consider the effect of the fasteners. 
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
ghenv.Component.Name = "HBPH+ - Apply Fastener Correction"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import fastener_correction as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_AddFastenersToConstruction(
    IGH,
    _fastener_material,
    _recessed_fasteners,
    _fastener_diameter,
    _fastener_length,
    _reference_area,
    _fastener_count,
    _layer_,
    _construction,
)
construction_, phius_worksheet_inputs_ = gh_compo_interface.run()