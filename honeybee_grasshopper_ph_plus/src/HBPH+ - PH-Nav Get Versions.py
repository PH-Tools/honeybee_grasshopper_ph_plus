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
List the saved Versions for a PH-Navigator project. Use the 'version_ids_' output to
pin a specific saved version on the other 'PH-Nav Get ...' components (for the
certification-archive use-case). If no version is pinned, those components will read
the project's latest saved version.
-
EM July 5, 2026
    Args:
        _project_number: (str) The PH-Navigator project number (ie: '2524').

        _url_base: (str) Optional. A dev-server base URL override. Leave empty to
            use the production PH-Navigator API.

        _token: (str) Optional. A PH-Navigator bearer token. Leave empty for
            anonymous read access.

        _get: (bool) Set True to download the saved-version list from the project.

    Returns:
        version_ids_: (list[str]) The 'version_id' for each saved version, newest
            first. Wire to a value-list to pin a version on the other components.

        versions_: (list[str]) A human-readable label for each saved version
            (its date, name, and kind).

        kinds_: (list[str]) The 'kind' of each saved version
            (working | submitted | closed | snapshot).

        project_: (str) The project identifier (its number and name).
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
ghenv.Component.Name = "HBPH+ - PH-Nav Get Versions"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1 import versions_get as gh_compo_io
    reload(gh_compo_io)

# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_PHNavV1GetVersions(
    IGH,
    _project_number,
    "http://localhost:8000/api/v1/gh" if DEV else "",
    _token,
    _get,
    )
version_ids_, versions_, kinds_, project_ = gh_compo_interface.run()
