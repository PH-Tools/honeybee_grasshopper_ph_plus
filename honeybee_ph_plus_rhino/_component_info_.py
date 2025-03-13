# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Names and meta-data for all the Honeybee-PH-PLUS Grasshopper Components.
These are called when the component is instantiated within the Grasshopper canvas.
"""

RELEASE_VERSION = "Honeybee-PH+ v1.01.23"
CATEGORY = "HB-PH+"
SUB_CATEGORIES = {
    0: "00 | Utils",
    1: "01 | Collections",
    2: "02 | GH-PY",
    3: "03 | HB-Tools",
    4: "04 | AirTable",
    5: "05 | Reporting",
}
COMPONENT_PARAMS = {
    # -- Collections
    "HBPH+ - Create Objects From CSV": {
        "NickName": "Create Objs from CSV",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH+ - Create Custom Collection": {
        "NickName": "Create Collection",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    "HBPH+ - Get From Custom Collection": {
        "NickName": "Get From Collection",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 1,
    },
    # -- GH-PY
    "HBPH+ - Get Object Attributes": {
        "NickName": "Get Attributes",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HBPH+ - Set Object Attributes": {
        "NickName": "Set Attributes",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    "HBPH+ - Create Objects from Key-Values": {
        "NickName": "Create Object",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 2,
    },
    # -- HB-Tools
    "HBPH+ - Get Brep Subface Materials": {
        "NickName": "Get Subface Mats",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Sort Geom by Level": {
        "NickName": "Sort Geom by Level",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Sort HB Objects by Level": {
        "NickName": "Sort HB-Objs by Level",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Diagnose HB Rooms": {
        "NickName": "Diagnose HB Rooms",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Clean Input Breps": {
        "NickName": "Clean Input Breps",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Check Shade Mesh": {
        "NickName": "Check Shade Mesh",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Create Window Types": {
        "NickName": "Create Win Types",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Create Window Geometry": {
        "NickName": "Create Geom",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Get Shading Factors from DesignPH": {
        "NickName": "Create Shading from DesignPH",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Import Flixo Materials": {
        "NickName": "Import Flixo Mats.",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Rebuild Window Surfaces": {
        "NickName": "Rebuild Win. Surfaces",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Get Rooms by Name": {
        "NickName": "Get Rooms by Name",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Get Faces by Name": {
        "NickName": "Get Faces by Name",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Group Connected Faces": {
        "NickName": "Group Connected Faces",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Get Face Polygon2Ds in Ref. Space": {
        "NickName": "Poly2Ds in Ref. Space",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Merge LBT Polygon2Ds": {
        "NickName": "Merge LBT Polygon2Ds",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Convert Unit": {
        "NickName": "Convert Unit",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - SQL Get Table Names": {
        "NickName": "SQL Get Table Names",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - SQL Get Column Names": {
        "NickName": "SQL Get Column Names",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - SQL Get Report Variable Names": {
        "NickName": "SQL Get Report Variable Names",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - SQL Get Column Data": {
        "NickName": "SQL Get Column Data",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    "HBPH+ - Infiltration from ACH": {
        "NickName": "Infiltration from ACH",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 3,
    },
    # -- AirTable
    "HBPH+ - Airtable Download Table Data": {
        "NickName": "Download Table Data",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH+ - Airtable Create Material Layers": {
        "NickName": "Airtable Material Layers",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH+ - Airtable Create Constructions": {
        "NickName": "Airtable Opaque Constructions",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    "HBPH+ - Airtable Create Window Constructions": {
        "NickName": "Airtable Window Constructions",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 4,
    },
    # -- Reporting / PDF
    "HBPH+ - Report Envelope Data": {
        "NickName": "Report Envelope",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 5,
    },
    "HBPH+ - Report Thermal Bridge Data": {
        "NickName": "Report TB",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 5,
    },
    "HBPH+ - Report Space Floor Segments": {
        "NickName": "Report Floor Segments",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 5,
    },
    "HBPH+ - Create Text Annotation": {
        "NickName": "Create Text Annotation",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 5,
    },
    "HBPH+ - Create Text Annotation Mask": {
        "NickName": "Create Text Annotation Mask",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 5,
    },
    "HBPH+ - Create PDF Geometry": {
        "NickName": "Create PDF Geometry",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 5,
    },
    "HBPH+ - Create Elevation PDF Geometry": {
        "NickName": "Report Elevations",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 5,
    },
    "HBPH+ - Export PDFs": {
        "NickName": "Export PDFs",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 5,
    },
    "HBPH+ - Create Plotly Graph": {
        "NickName": "Create Plotly Graph",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 5,
    },
    # -- Read PHPP
    "HBPH+ - Read Variants Data from PHPP": {
        "NickName": "Read PHPP Variants Data",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 6,
    },
    "HBPH+ - Read Climate Data from PHPP": {
        "NickName": "Read PHPP Climate Data",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 6,
    },
    "HBPH+ - Read Room Ventilation Data from PHPP": {
        "NickName": "Read PHPP Room Ventilation",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 6,
    },
    "HBPH+ - Clean Variants Data CSV": {
        "NickName": "Clean PHPP Variants Data",
        "Message": RELEASE_VERSION,
        "Category": CATEGORY,
        "SubCategory": 6,
    },
}


class ComponentNameError(Exception):
    def __init__(self, _name, error):
        self.message = 'Error: Cannot get Component Params for: "{}"'.format(_name)
        print(error)
        super(ComponentNameError, self).__init__(self.message)


def turn_off_old_tag(ghenv):
    """Turn off the old tag that displays on GHPython components.
    Copied from 'ladybug-rhino.grasshopper.turn_off_old_tag()'

    Arguments:
    __________
        * ghenv: The Grasshopper Component 'ghenv' variable.

    Returns:
    --------
        * None:
    """
    try:  # try to turn off the OLD tag on the component
        ghenv.Component.ToggleObsolete(False)
    except Exception:
        pass  # older version of Rhino that does not have the Obsolete method


def set_component_params(ghenv, dev=False):
    # type (ghenv, Optional[str | bool]) -> bool
    """
    Sets the visible attributes of the Grasshopper Component (Name, Date, etc..)

    Arguments:
    __________
        * ghenv: The Grasshopper Component 'ghenv' variable.
        * dev: (str | bool) Default=False. If False, will use the RELEASE_VERSION value as the
            'message' shown on the bottom of the component in the Grasshopper scene.
            If a string is passed in, will use that for the 'message' shown instead.

    Returns:
    --------
        * None:
    """

    compo_name = ghenv.Component.Name
    try:
        sub_cat_num = COMPONENT_PARAMS.get(compo_name, {}).get("SubCategory", 1)
        sub_cat_name = SUB_CATEGORIES.get(sub_cat_num)
    except Exception as e:
        raise ComponentNameError(compo_name, e)

    # ------ Set the visible message
    if dev:
        msg = "DEV | {}".format(str(dev))
    else:
        msg = COMPONENT_PARAMS.get(compo_name, {}).get("Message")

    ghenv.Component.Message = msg

    # ------ Set the other stuff
    ghenv.Component.NickName = COMPONENT_PARAMS.get(compo_name, {}).get("NickName")
    ghenv.Component.Category = CATEGORY
    ghenv.Component.SubCategory = sub_cat_name
    ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
    turn_off_old_tag(ghenv)  # For Rhino 8

    return dev
