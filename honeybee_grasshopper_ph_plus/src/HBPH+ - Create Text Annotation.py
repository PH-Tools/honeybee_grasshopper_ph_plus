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
Create a new Text Annotation object which can be used during PDF Export. These
annotations can be used to add titles or other data to Layouts, or to add notes or 
text directly into the Rhino-scene as well.
-
EM June 15, 2024
    Args:
        _text: (str) The Text for the annotation to show.
        
        _size: (float) The size of the Text to show. Default=0.25
        
        _location: (Rhino.Geometry.Point3d) The anchor point for the Text.
        
        _format: (str) Optional. A format string using the standard python
            'f-string' inputs. Incude the curly-braces. For example, if you 
            want to show the text "0.3456789" as "0.35 m3" you would pass 
            in "{:0.2f} m3" (inclding the curly braces).
            
        _justification: (int) Relative to the anchor point. Input either:
            0 [Bottom-Left]
            1 [Bottom-Center]
            2 [Bottom-Right]
            3 [Middle-Left]
            4 [Middle-Center]
            5 [Middle-Right]
            6 [Top-Left]
            7 [Top-Middle]
            8 [Top-Right]

        _mask: (TextAnnotationMaskAttributes | None): Mask Attributes, if any
            
    Returns:
        text_annotations_: The new TextAnnotations objects. These can be used by 
            the "HBPH - Export PDFs" component when exporting PDF documents.
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
ghenv.Component.Name = "HBPH+ - Create Text Annotation"
DEV = honeybee_ph_plus_rhino._component_info_.set_component_params(ghenv, dev=False)
if DEV:
    from honeybee_ph_plus_rhino.gh_compo_io.reporting import annotations as gh_compo_io
    reload(gh_compo_io)


# ------------------------------------------------------------------------------
# -- GH Interface
IGH = gh_io.IGH( ghdoc, ghenv, sc, rh, rs, ghc, gh )


# ------------------------------------------------------------------------------
gh_compo_interface = gh_compo_io.GHCompo_CreateTextAnnotations(    
    IGH,
    _text,
    _size,
    _location,
    _format,
    _justification,
    _mask,
)
text_annotations_ = gh_compo_interface.run()
