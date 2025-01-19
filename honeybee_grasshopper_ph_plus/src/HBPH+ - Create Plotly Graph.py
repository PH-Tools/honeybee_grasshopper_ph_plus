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
Use 'Plotly' to graph Ladybug Timeseries Data objects. This will create an HTML file with the 
data ploted in a simple line-graph. Note that all data supplied will be plotted on a single graph, 
and so all data must have the same type, unit, and time-period. 
-
EM January 18, 2025
    Args:
        _folder_: (str) The folder to save the HTML file.

        _name_: (str) The name of the HTML file to create.

        _title_: (str) The title of the Plot to display in the HTML

        _data: (list[HourlyContinuousCollection]) A list of Ladybug hourly-data to plot.

        _horiz_lines: (list[float]) A list of values to indicate with horizontal 
            annotation lines. This is useful if you want to add threshold markers or 
            similar to your plots.

        _run: (bool) Set to TRUE to create the HTML plot.

    Returns:
        html_: (str) The HTML output file with the new Plotly graph.
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
ghenv.Component.Name = "HBPH+ - Create Plotly Graph"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    reload(gh_io)
    from honeybee_ph_plus_rhino.gh_compo_io.reporting import create_plotly_graph as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )

# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreatePlotlyGraph(
    IGH, _folder_, _name_, _title_, _data, _horiz_lines, _run,
)
html_ = gh_compo_interface.run()
