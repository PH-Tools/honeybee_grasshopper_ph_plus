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
Create 'steel-stud' constructions with effective thermal conductivity values determined according to the 
American Iron and Steel Institute (AISI) S250-21 | “North American Standard for Thermal Transmittance of Building 
Envelopes With Cold-Formed Steel Framing, 2021 Edition.” The method outlined in this guide roughly aligns with the 
ASHRAE 'modified zone method' for numerical calculations of steel-stud wall thermal performance. It should be noted that
the values here are approximate only, and if more exact values are required then 2- or 3-dimensional heat flow 
simulations should be used in lieu of these numerical calculations. 
- 
Note that the surrounding layers will affect the effective performance of the insulated steel stud layer, and as such the 
stud-layer thermal conductivity values from this calculator will vary depending on all of the layers input. 
- 
For more information on the calculation methodology used, see:
https://www.steel.org/2021/09/aisi-publishes-aisi-s250-21-north-american-standard-for-thermal-transmittance-of-building-envelopes-with-cold-formed-steel-framing-2021-edition/
-
EM May 16, 2025
    Args:
        _construction_name_: [Optional] A name for the new Honeybee-Energy Construction.

        _ext_claddings_: (list[EnergyMaterial]) [Optional] A list of Honeybee-Energy 
            OpaqueMaterials, ordered from outside-to-inside. These materials should represent
            any 'cladding' layers which occur outside of any continuous insulation.
        
        _ext_insulations_: (list[EnergyMaterial]) [Optional] A list of Honeybee-Energy 
            OpaqueMaterials, ordered from outside-to-inside. These materials should represent
            any continuous insulation layer which occur outside of the steel-stud framing 
            and sheathing, but underneath any 'cladding'.

        _ext_sheathings_: (list[EnergyMaterial]) [Optional] A list of Honeybee-Energy 
            OpaqueMaterials, ordered from outside-to-inside. These materials should represent
            any 'sheathing' layers which occur outside of the primary steel-stud framing layer.
        
        _stud_layer_insulation_: (EnergyMaterial) [Default=AirCavity] The insulation material
            to use for the steel-stud layer. If None is provided, and empty air-cavity will be used.

        _stud_depth_mm_: (float) [Optional | Default=88.9mm (3-1/2")] The depth of the steel-stud.
        
        _stud_spacing_mm_: (float) [Optional | Default=400mm (16")] The center-to-center spacing of the steel-studs.
Input either - 
- 152.5 mm (6 in. OC)
- 304.8 mm (12 in. OC)
- 406.4 mm (16 in. OC)
- 609.6 mm (24 in. OC)

        _stud_thickness_mm_: (float) [Optional | Default=1.0922mm (43 Mil)] The thickness of the steel-stud walls. 
Input either - 
- 0.8382 mm (33 mil) 
- 1.0922 mm (43 mil)
- 1.3716 mm (54 mil)
- 1.7272 mm (68 mil)
        
        _stud_flange_width_mm_: (float) [Optional | Default=41mm (1-5/8")] The flange face-width.
        
        _steel_conductivity_W_mk_: (float) [Default=857 W/mk (495 Btu/hr-ft-F)] The steel-stud  
            material thermal conductivity.
        
        _int_layers_: (list[EnergyMaterial]) [Optional] A list of Honeybee-Energy 
            OpaqueMaterials, ordered from outside-to-inside. These materials should represent
            any interior finish materials such as gypsum board which occur on the 'inside' of
            the primary steel-stud framing layer.

    Returns:
        construction_: (OpaqueConstruction) A New Honeybee-Energy OpaqueConstruction which will 
            include all of the layers, as well as a new hybrid 'Steel-stud' layer with a 
            conductivity calculated based on the AISI S250-21w protocol.
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
ghenv.Component.Name = "HBPH+ - Create Steel-Stud Construction"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_utils import aisi_s250_21
    reload(aisi_s250_21)
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools import steel_stud_construction as gh_compo_io
    reload(gh_compo_io)
    
# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateSteelStudConstruction(
    IGH,
    _construction_name_,
    _ext_claddings_,
    _ext_insulations_, 
    _ext_sheathings_,
    _stud_layer_insulation_,
    _stud_depth_mm_,
    _stud_spacing_mm_,
    _stud_thickness_mm_,
    _stud_flange_width_mm_,
    _steel_conductivity_W_mk_,
    _int_layers_,
)
construction_ = gh_compo_interface.run()