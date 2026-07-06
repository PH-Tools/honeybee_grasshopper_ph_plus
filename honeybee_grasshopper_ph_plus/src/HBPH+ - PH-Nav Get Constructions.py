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
Download all of the opaque Constructions (assemblies) from a PH-Navigator project and
rebuild them as Honeybee-Energy 'OpaqueConstruction' objects. Optionally pin a specific
saved version using the '_version' input (see the 'PH-Nav Get Versions' component); if
no version is pinned, the project's latest saved version is used.
-
EM July 5, 2026
    Args:
        _project_number: (str) The PH-Navigator project number (ie: '2524').

        _version: (str) Optional. A specific saved 'version_id' to download. Leave
            empty to use the project's latest saved version.

        _token: (str) Optional. A PH-Navigator bearer token. Leave empty for
            anonymous read access.

        _download: (bool) Set True to download the assemblies from the project.

    Returns:
        constructions_: (CustomCollection[OpaqueConstruction]) The Honeybee-Energy
            Constructions built from the assemblies on the PH-Navigator project, keyed
            by assembly name. (Same output type as 'PH-Nav Get Apertures'.)

        last_modified_: (str) The save-timestamp of the downloaded version (for
            freshness / change-detection).

        json_: (str) The raw downloaded assembly data, as a formatted JSON string
            (handy for debugging).
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
ghenv.Component.Name = "HBPH+ - PH-Nav Get Constructions"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1 import constructions_get as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_PHNavV1GetConstructions(
    IGH,
    _project_number,
    _version,
    "http://localhost:8000/api/v1/gh" if DEV else "",
    _token,
    _download,
    )
constructions_, last_modified_, json_ = gh_compo_interface.run()
