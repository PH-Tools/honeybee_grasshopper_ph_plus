# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH-Navigator Get Window Types."""

import json

from honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection import CustomCollection
from honeybee_ph_plus_rhino.gh_compo_io.hb_tools.win_create_types import WindowElement

try:
    from typing import Any, TypeVar

    T = TypeVar("T")
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


def create_hbph_glazing_types(_aperture_types_dict):
    # type: (dict[str, dict]) -> dict[str, PhWindowGlazing]
    """Create a collection of the HoneybeePH Glazing-Types from the PH-Navigator Aperture Types."""

    glazing_types = {}  # type: dict[str, PhWindowGlazing]
    for ap_type_data_dict in _aperture_types_dict.values():
        for element_data in ap_type_data_dict["elements"]:
            glazing_data = element_data.get("glazing", None)
            if glazing_data is None:
                continue

            hbph_glazing = PhWindowGlazing(glazing_data["name"])
            hbph_glazing.display_name = glazing_data["name"]
            hbph_glazing.u_factor = float(glazing_data["u_value_w_m2k"])
            hbph_glazing.g_value = float(glazing_data["g_value"])

            glazing_types[hbph_glazing.display_name] = hbph_glazing
    
    return glazing_types


def create_new_hbph_frame_element(_frame_element_types_dict):
    # type: (dict[str, dict]) -> dict[str, PhWindowFrameElement]
    """Create a collection of the HoneybeePH Frame-Element-Types from the PH-Navigator Aperture Types."""

    frame_element_types_ = {}  # type: dict[str, PhWindowFrameElement]
    for frame_element_type_data_dict in _frame_element_types_dict.values():
        for element_data in frame_element_type_data_dict["elements"]:
            frames = element_data["frames"]
            for side in ["left", "right", "top", "bottom"]:
                frame_data = frames[side]
                if not frame_data:
                    continue

                hbph_frame_element = PhWindowFrameElement(frame_data["name"])
                hbph_frame_element.display_name = frame_data["name"]
                hbph_frame_element.width = float(frame_data["width_mm"] / 1000)
                hbph_frame_element.u_factor = float(frame_data["u_value_w_m2k"])
                # hbph_frame_element.psi_glazing = frame_data. TODO....
                hbph_frame_element.psi_install = 0.0
                hbph_frame_element.chi_value = 0.0

                frame_element_types_[hbph_frame_element.display_name] = hbph_frame_element
    
    return frame_element_types_


def create_new_hbph_frames(_aperture_types_dict, _frame_elements_types_dict):
    # type: (dict[str, dict], dict[str, PhWindowFrameElement]) -> dict[str, PhWindowFrame]
    """Create a collection of the HoneybeePH Frame-Types from the PH-Navigator Aperture Types."""

    frame_types_ = {}  # type: dict[str, PhWindowFrame]
    for ap_type_data_dict in _aperture_types_dict.values():
        for element_data in ap_type_data_dict["elements"]:
            if not element_data:
                continue
            
            # -- Create a new PhWindowFrame for this Element
            frame_id = "{}_C{}_R{}".format(ap_type_data_dict["name"], element_data["column_number"], element_data["row_number"]) # < TODO: Use ID ?
            hbph_frame = PhWindowFrame(frame_id)
            hbph_frame.display_name = frame_id

            # -- Set all of the frame-elements for this Element
            frames = element_data["frames"]
            for side in ["left", "right", "top", "bottom"]:
                frame_data = frames[side]
                if not frame_data:
                    continue
                setattr(hbph_frame, side, _frame_elements_types_dict[frame_data["name"]])
            
            # -- Add the new Frame to the collection
            frame_types_[frame_id] = hbph_frame

    return frame_types_


def create_hbph_window_unit_types(_aperture_types_dict, _frame_types_dict, _IGH):
    # type: (dict[str, dict], dict[str, PhWindowFrame], gh_io.IGH) -> dict[str, WindowUnitType]
    """Create a collection of the HoneybeePH WindowUnitTypes from the PH-Navigator Aperture Types."""

    window_types_ = {}  # type: dict[str, WindowUnitType]
    for ap_type_data_dict in _aperture_types_dict.values():
        new_window_unit_type = WindowUnitType(_IGH, ap_type_data_dict["name"])

        for element_data in ap_type_data_dict["elements"]:
            if not element_data:
                continue

            new_window_unit_type.elements.append(
                WindowElement(
                    ap_type_data_dict["column_widths_mm"][element_data["column_number"]] / 1000,
                    ap_type_data_dict["row_heights_mm"][element_data["row_number"]] / 1000,
                    element_data["column_number"],
                    element_data["row_number"]
                )
            )

        window_types_[new_window_unit_type.type_name] = new_window_unit_type
    
    return window_types_


def create_new_hbph_window_material(_display_name, _hbph_frame, _hbph_glazing):
    # type: (str, PhWindowFrame, PhWindowGlazing) -> EnergyWindowMaterialSimpleGlazSys
    """Create a new HB Simple Window Material and set the NFRC/HBmaterial properties"""
    
    nfrc_u_factor = iso_10077_1.calculate_window_uw(_hbph_frame, _hbph_glazing)
    nfrc_shgc = _hbph_glazing.g_value
    t_vis = 0.6
    window_mat = EnergyWindowMaterialSimpleGlazSys(
        _display_name, nfrc_u_factor, nfrc_shgc, t_vis
    )
    window_mat.display_name = _display_name
    return window_mat


def create_hbph_ep_constructions(_aperture_types_dict, _glazing_types_dict, _frame_types_dict):
    # type: (dict, dict, dict) -> dict
    """Create the HoneybeePH EP-Constructions for the Window Types."""
    constructions_ = {}
    for ap_type_data_dict in _aperture_types_dict.values():
        for element_data in ap_type_data_dict["elements"]:
            if not element_data:
                continue

            element_id = "{}_C{}_R{}".format(
                ap_type_data_dict["name"], element_data["column_number"], element_data["row_number"]
            )

            hbph_frame = _frame_types_dict[element_id]
            if element_data["glazing"]:
                hbph_glazing = _glazing_types_dict[element_data["glazing"]["name"]]

            # -----------------------------------------------------------------------------
            # -- Build the HB Window Material and Construction
            hbph_mat = create_new_hbph_window_material(
                element_id, hbph_frame, hbph_glazing
            )
            hb_win_construction = WindowConstruction(element_id, [hbph_mat])

            # -- Set the PH Properties on the WindowConstructionProperties
            prop_ph = hb_win_construction.properties.ph  # type: ignore
            prop_ph.ph_frame = hbph_frame
            prop_ph.ph_glazing = hbph_glazing

            constructions_[hb_win_construction.display_name] = hb_win_construction

    return constructions_


class GHCompo_PHNavGetWindowTypes(object):
    """A class for downloading PH-Navigator Window Types for a specific Project Number."""

    URL_BASE = "https://ph-dash-0cye.onrender.com"

    def __init__(
        self, _IGH, _project_number, _url_base, _get_aperture_types, *args, **kwargs
    ):
        # type: (gh_io.IGH, str, str | None, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.PROJECT_NUMBER = _project_number
        self._url_base = _url_base
        self.get_aperture_types = _get_aperture_types

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
        # URL for the PH-Navigator API
        _url = "{}/aperture/get-apertures-as-json/{}".format(
            self._url_base or self.URL_BASE, self.PROJECT_NUMBER
        )

        try:
            # TLS 1.2 is needed to download over https
            System.Net.ServicePointManager.SecurityProtocol = (
                System.Net.SecurityProtocolType.Tls12
            )
        except AttributeError:
            # TLS 1.2 is not provided by MacOS .NET in Rhino 5
            if _url.lower().startswith("https"):
                self.IGH.error(
                    "This system lacks the necessary security"
                    " libraries to download over https."
                )

        print("PH-Navigator URL: {}".format(_url))
        return _url

    def get_web_client(self, _offset="0"):
        # type: (str) -> System.Net.WebClient
        """Get a web client with Header and Query configuration for downloading data from PH-Navigator."""

        client = System.Net.WebClient()
        client.Headers.Add("Authorization", "Bearer {}".format(None))
        client.Headers.Add("Content-type", "application/json")
        client.QueryString.Add("offset", _offset)

        return client

    def download_aperture_types_json(self):
        # type: () -> dict[str, dict]
        """Download HB-Constructions from PH-Navigator.

        Since PH-Navigator limits the number of records that can be downloaded
        in a single request, this method will download all records in the table
        by making multiple requests using the 'offset' query parameter.
        """
        apertures = {}  # type: dict[str, dict]
        offset = "0"

        while offset != None:
            client = self.get_web_client(offset)
            response = client.DownloadString(self.url)
            data = json.loads(response)  # type: dict
            """
            data.apertures = {
                "Aperture 1": "....",
                "Aperture 2": "....",
                ...
            }
            """

            # Ensure 'apertures' is properly deserialized
            d = data.get("apertures", {})
            if isinstance(d, str):  # If it's a string, deserialize it
                try:
                    d = json.loads(d) # type: dict
                except json.JSONDecodeError as e:
                    self.IGH.error("Failed to parse 'apertures': {}".format(e))
                    d = {}

            apertures.update(d)
            offset = data.get("offset", None)

        return apertures

    def run(self):
        # type: () -> tuple[CustomCollection | None, CustomCollection | None]
        """Run the component."""
        if not self.ready:
            return None, None

        try:
            aperture_types_dict = self.download_aperture_types_json()
        except Exception as e:
            msg = "Failed to download file from PH-Navigator.\n{}".format(e)
            self.IGH.error(msg)
            return None, None

        # --------------------------------------------------------------------------------------------------------------
        # -- Window Types (Geometry)
        # -- Build all of the Types needed to create the HoneybeePH Window Types
        glazing_types_dict = create_hbph_glazing_types(aperture_types_dict)
        print("Glazing Types: {}".format(glazing_types_dict.keys()))
        frame_element_types_dict = create_new_hbph_frame_element(aperture_types_dict)
        print("Frame-Element Types: {}".format(frame_element_types_dict.keys()))
        frame_types_dict = create_new_hbph_frames(aperture_types_dict, frame_element_types_dict)
        print("Frame-Types Types: {}".format(frame_types_dict.keys()))

        # -- Build all of the WindowUnitTypes
        window_unit_types_dict = create_hbph_window_unit_types(aperture_types_dict, frame_types_dict, self.IGH)
        window_unit_types_collection_ = CustomCollection()
        for k, v in window_unit_types_dict.items():
            window_unit_types_collection_[k] = v
        
        # --------------------------------------------------------------------------------------------------------------
        # -- Build the EP-Constructions for each of the Elements
        window_ep_construction_dict = create_hbph_ep_constructions(aperture_types_dict, glazing_types_dict, frame_types_dict)
        window_ep_construction_collection_ = CustomCollection()
        for k, v in window_ep_construction_dict.items():
           window_ep_construction_collection_[k] = v

        # --------------------------------------------------------------------------------------------------------------
        return window_unit_types_collection_, window_ep_construction_collection_