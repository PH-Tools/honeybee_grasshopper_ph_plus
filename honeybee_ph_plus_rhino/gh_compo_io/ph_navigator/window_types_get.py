# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH-Navigator Get Window Types."""

import json

from honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection import CustomCollection
from honeybee_ph_plus_rhino.gh_compo_io.hb_tools.win_create_types import WindowElement

# Import the new schema classes
from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.window_types_schema import (
    ApertureTypeData,
    ElementData,
    FrameData,
    GlazingData
)

try:
    from typing import Any, Dict, List
except ImportError:
    pass  # IronPython 2.7

try:
    import System.Net  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee_energy.construction.window import WindowConstruction
    from honeybee_energy.material.glazing import EnergyWindowMaterialSimpleGlazSys
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy. {}".format(e))

try:
    from honeybee_energy_ph.construction.window import (
        PhWindowFrame,
        PhWindowFrameElement,
        PhWindowGlazing,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_utils import iso_10077_1
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino. {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools.win_create_types import WindowUnitType 
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_plus_rhino. {}".format(e))


def create_hbph_glazing_types(aperture_types):
    # type: (List[ApertureTypeData]) -> Dict[str, PhWindowGlazing]
    """Create a collection of the HoneybeePH Glazing-Types from the PH-Navigator Aperture Types."""

    glazing_types = {}  # type: Dict[str, PhWindowGlazing]
    
    for aperture_type in aperture_types:
        for element in aperture_type.get_valid_elements():
            if element.glazing is None:
                continue

            glazing_data = element.glazing
            hbph_glazing = PhWindowGlazing(glazing_data.name)
            hbph_glazing.display_name = glazing_data.display_name
            hbph_glazing.u_factor = glazing_data.u_value_w_m2k
            hbph_glazing.g_value = glazing_data.g_value

            glazing_types[hbph_glazing.display_name] = hbph_glazing
    
    return glazing_types


def create_new_hbph_frame_element(aperture_types):
    # type: (List[ApertureTypeData]) -> Dict[str, PhWindowFrameElement]
    """Create a collection of the HoneybeePH Frame-Element-Types from the PH-Navigator Aperture Types."""

    frame_element_types = {}  # type: Dict[str, PhWindowFrameElement]
    
    for aperture_type in aperture_types:
        for element in aperture_type.get_valid_elements():
            for frame_data in element.frames.get_all_frames():
                if frame_data.name in frame_element_types:
                    continue  # Already created this frame element

                hbph_frame_element = PhWindowFrameElement(frame_data.name)
                hbph_frame_element.display_name = frame_data.display_name
                hbph_frame_element.width = frame_data.width_m
                hbph_frame_element.u_factor = frame_data.u_value_w_m2k
                hbph_frame_element.psi_glazing = frame_data.psi_glazing
                hbph_frame_element.psi_install = frame_data.psi_install
                hbph_frame_element.chi_value = frame_data.chi_value

                frame_element_types[hbph_frame_element.display_name] = hbph_frame_element
    
    return frame_element_types


def create_new_hbph_frames(aperture_types, frame_elements_types):
    # type: (List[ApertureTypeData], Dict[str, PhWindowFrameElement]) -> Dict[str, PhWindowFrame]
    """Create a collection of the HoneybeePH Frame-Types from the PH-Navigator Aperture Types."""

    frame_types = {}  # type: Dict[str, PhWindowFrame]
    
    for aperture_type in aperture_types:
        for element in aperture_type.get_valid_elements():
            # Create a new PhWindowFrame for this Element
            frame_id = "{}_{}".format(aperture_type.name, element.element_id_suffix)
            hbph_frame = PhWindowFrame(frame_id)
            hbph_frame.display_name = frame_id

            # Set all of the frame-elements for this Element
            for side in ["left", "right", "top", "bottom"]:
                frame_data = element.frames.get_frame_by_side(side)
                if frame_data is not None:
                    frame_element = frame_elements_types.get(frame_data.name)
                    if frame_element is not None:
                        setattr(hbph_frame, side, frame_element)
            
            frame_types[frame_id] = hbph_frame

    return frame_types


def create_hbph_window_unit_types(aperture_types, frame_types, IGH):
    # type: (List[ApertureTypeData], Dict[str, PhWindowFrame], gh_io.IGH) -> Dict[str, WindowUnitType]
    """Create a collection of the HoneybeePH WindowUnitTypes from the PH-Navigator Aperture Types."""

    window_types = {}  # type: Dict[str, WindowUnitType]
    
    for aperture_type in aperture_types:
        new_window_unit_type = WindowUnitType(IGH, aperture_type.name)
        
        for element in aperture_type.get_valid_elements():
            # -- Calculate the total width considering column span
            element_width_m = 0.0
            for col in range(element.column_number, element.column_number + element.column_span):
                element_width_m += aperture_type.get_column_width_m(col)
            
            # -- Calculate the total height considering row span
            # Note: The get_row_height_m method now handles the row reversal internally
            element_height_m = 0.0
            for row in range(element.row_number, element.row_number + element.row_span):
                element_height_m += aperture_type.get_row_height_m(row)

            window_element = WindowElement(
                element_width_m,
                element_height_m,
                element.column_number,
                element.row_number
            )
            new_window_unit_type.elements.append(window_element)

        window_types[new_window_unit_type.type_name] = new_window_unit_type
    
    return window_types


def create_new_hbph_window_material(display_name, hbph_frame, hbph_glazing):
    # type: (str, PhWindowFrame, PhWindowGlazing) -> EnergyWindowMaterialSimpleGlazSys
    """Create a new HB Simple Window Material and set the NFRC/HBmaterial properties"""
    
    nfrc_u_factor = iso_10077_1.calculate_window_uw(hbph_frame, hbph_glazing)
    nfrc_shgc = hbph_glazing.g_value
    t_vis = 0.6
    window_mat = EnergyWindowMaterialSimpleGlazSys(
        display_name, nfrc_u_factor, nfrc_shgc, t_vis
    )
    window_mat.display_name = display_name
    return window_mat


def create_hbph_ep_constructions(aperture_types, glazing_types, frame_types):
    # type: (List[ApertureTypeData], Dict[str, PhWindowGlazing], Dict[str, PhWindowFrame]) -> Dict[str, WindowConstruction]
    """Create the HoneybeePH EP-Constructions for the Window Types."""
    
    constructions = {}  # type: Dict[str, WindowConstruction]
    
    for aperture_type in aperture_types:
        for element in aperture_type.get_valid_elements():
            element_id = "{}_{}".format(aperture_type.name, element.element_id_suffix)

            # Get the frame and glazing for this element
            hbph_frame = frame_types.get(element_id)
            if hbph_frame is None:
                continue

            hbph_glazing = None
            if element.glazing is not None:
                hbph_glazing = glazing_types.get(element.glazing.name)
            
            if hbph_glazing is None:
                continue

            # Build the HB Window Material and Construction
            hbph_mat = create_new_hbph_window_material(element_id, hbph_frame, hbph_glazing)
            hb_win_construction = WindowConstruction(element_id, [hbph_mat])

            # Set the PH Properties on the WindowConstructionProperties
            prop_ph = hb_win_construction.properties.ph  # type: ignore
            prop_ph.ph_frame = hbph_frame
            prop_ph.ph_glazing = hbph_glazing

            constructions[hb_win_construction.display_name] = hb_win_construction

    return constructions


class GHCompo_PHNavGetWindowTypes(object):
    """A class for downloading PH-Navigator Window Types for a specific Project Number."""

    URL_BASE = "https://ph-dash-0cye.onrender.com"

    def __init__(self, IGH, project_number, url_base, get_aperture_types, *args, **kwargs):
        # type: (gh_io.IGH, str, str | None, bool, *Any, **Any) -> None
        self.IGH = IGH
        self.PROJECT_NUMBER = project_number
        self._url_base = url_base
        self.get_aperture_types = get_aperture_types

    @property
    def ready(self):
        # type: () -> bool
        if not self.PROJECT_NUMBER:
            return False
        if not self.get_aperture_types:
            return False
        return True

    @property
    def url(self):
        # type: () -> str
        """Get the URL for the PH-Navigator API."""
        _url = "{}/aperture/get-apertures-as-json/{}".format(
            self._url_base or self.URL_BASE, self.PROJECT_NUMBER
        )

        try:
            System.Net.ServicePointManager.SecurityProtocol = (
                System.Net.SecurityProtocolType.Tls12
            )
        except AttributeError:
            if _url.lower().startswith("https"):
                self.IGH.error(
                    "This system lacks the necessary security"
                    " libraries to download over https."
                )

        print("PH-Navigator URL: {}".format(_url))
        return _url

    def get_web_client(self, offset="0"):
        # type: (str) -> System.Net.WebClient
        """Get a web client with Header and Query configuration for downloading data from PH-Navigator."""

        client = System.Net.WebClient()
        client.Headers.Add("Authorization", "Bearer {}".format(None))
        client.Headers.Add("Content-type", "application/json")
        client.QueryString.Add("offset", offset)
        return client

    def download_aperture_types_json(self):
        # type: () -> List[ApertureTypeData]
        """Download and parse aperture types from PH-Navigator."""
        
        apertures_dict = {}  # type: Dict[str, Dict]
        offset = "0"

        while offset is not None:
            client = self.get_web_client(offset)
            response = client.DownloadString(self.url)
            data = json.loads(response)

            # Ensure 'apertures' is properly deserialized
            d = data.get("apertures", {})
            if isinstance(d, str):
                try:
                    d = json.loads(d)
                except Exception as e:
                    self.IGH.error("Failed to parse 'apertures': {}".format(e))
                    d = {}

            # Recursively deserialize all nested JSON strings
            apertures_dict.update(d)
            offset = data.get("offset", None)

        # Convert to schema objects
        aperture_types = []
        for aperture_data in apertures_dict.values():
            try:
                aperture_type = ApertureTypeData(aperture_data)
                aperture_types.append(aperture_type)
            except Exception as e:
                self.IGH.warning("Failed to parse aperture type: {}".format(e))
                continue

        return aperture_types

    def run(self):
        # type: () -> tuple[CustomCollection | None, CustomCollection | None]
        """Run the component."""
        if not self.ready:
            return None, None

        try:
            aperture_types = self.download_aperture_types_json()
        except Exception as e:
            msg = "Failed to download file from PH-Navigator.\n{}".format(e)
            self.IGH.error(msg)
            return None, None

        # Build all of the Types needed to create the HoneybeePH Window Types
        glazing_types_dict = create_hbph_glazing_types(aperture_types)
        print("Glazing Types: {}".format(glazing_types_dict.keys()))
        
        frame_element_types_dict = create_new_hbph_frame_element(aperture_types)
        print("Frame-Element Types: {}".format(frame_element_types_dict.keys()))
        
        frame_types_dict = create_new_hbph_frames(aperture_types, frame_element_types_dict)
        print("Frame-Types: {}".format(frame_types_dict.keys()))

        # Build all of the WindowUnitTypes
        window_unit_types_dict = create_hbph_window_unit_types(aperture_types, frame_types_dict, self.IGH)
        window_unit_types_collection = CustomCollection()
        for k, v in window_unit_types_dict.items():
            window_unit_types_collection[k] = v
        
        # Build the EP-Constructions for each of the Elements
        window_ep_construction_dict = create_hbph_ep_constructions(aperture_types, glazing_types_dict, frame_types_dict)
        window_ep_construction_collection = CustomCollection()
        for k, v in window_ep_construction_dict.items():
           window_ep_construction_collection[k] = v

        return window_unit_types_collection, window_ep_construction_collection