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
Apply the per-edge Psi-Install 'Install Types' downloaded from PH-Navigator onto the
Honeybee Apertures in the model. Use the 'install_types_' output of the
'HBPH+ - PH-Nav Get Apertures' component as the '_install_types' input here.
-
Each Aperture is matched to the collection by its name, which should be the name
given to the window surface by 'HBPH+ - Create Window Geometry' (ie: 'Type-A_C0_R0').
Matching is by name, NOT by tree-position, so the Aperture tree can be grafted or
flattened however you like. Any Aperture whose name is not found in the collection is
passed through unchanged and listed in the 'report_' output.
-
Only the Apertures are modified. The window constructions are never touched or
duplicated: the install condition is a property of WHERE the window sits, not of the
window product, so it is stored on the Aperture and resolved against the
construction's frame-element defaults when the model is exported to PHPP / WUFI.
-
EM August 26, 2026
    Args:
        _apertures: (List[Aperture]) The Honeybee Apertures to apply the
            Install-Types to.

        _install_types: (CustomCollection[List[PhApertureInstallType]]) The collection
            of per-edge Install Types from the 'HBPH+ - PH-Nav Get Apertures'
            component's 'install_types_' output.

    Returns:
        report_: (List[str]) A summary of the Apertures matched, and the names of any
            which were not found in the collection.

        apertures_: (List[Aperture]) The Apertures with their per-edge Install Types
            assigned.
"""

import scriptcontext as sc
import Rhino as rh
import rhinoscriptsyntax as rs
import ghpythonlib.components as ghc
import Grasshopper as gh

try:
    from honeybee_ph_plus_rhino import gh_compo_io
except ImportError as e:
    raise ImportError('\nFailed to import honeybee_ph_plus_rhino:\n\t{}'.format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError('\nFailed to import ph_gh_component_io:\n\t{}'.format(e))


# ------------------------------------------------------------------------------
import honeybee_ph_plus_rhino._component_info_
reload(honeybee_ph_plus_rhino._component_info_)
ghenv.Component.Name = "HBPH+ - PH-Nav Set Aperture Psi-Installs"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1 import aperture_psi_installs_set as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_PHNavV1SetAperturePsiInstalls(
    IGH,
    _apertures,
    _install_types,
    )
apertures_, report_ = gh_compo_interface.run()
