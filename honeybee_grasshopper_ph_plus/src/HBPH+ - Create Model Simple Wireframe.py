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
This component will create a simplified wireframe ModelObject of the Honeybee-Mode which 
is useful as refernce geometry when exporting / printing / making diagrams, etc.
-
EM Nov 15, 2025
    Args:

        _hb_model: (Model) The Honeybee-Model object to pull the ERV Ducting out of.

    Returns:

        faces_: (list[Face]) The 'exterior' honeybee-faces of the Honeybee-Model

        coplanar_face_groups_: (DataTree[Face]) The honeybee-faces grouped onto branches based on 
            they co-planarity.

        merged_hb_faces_: (DataTree[Face]) The co-planar honeybee-faces merged together.

        rh_surfaces_: (DataTree[Brep]) The co-planar faces as Rhino surfaces.

        construction_names_: (DataTree[str]) The names of the constructions for each of the 
            co-planar face groups.

        wireframe_: (list[Model Curve]) The simplified wireframe ModelObjects which can be passed along
            for export or printing.
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
ghenv.Component.Name = "HBPH+ - Create Model Simple Wireframe"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.reporting import build_simplified_wireframe as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_BuildHbModelSimplifiedWireframe(
    IGH,
    _hb_model,
)

(
    faces_,
    coplanar_face_groups_,
    merged_hb_faces_,
    rh_surfaces_,
    construction_names_,
    wireframe_,
) = gh_compo_interface.run()