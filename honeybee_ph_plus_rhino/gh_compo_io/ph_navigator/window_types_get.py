# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH-Navigator Get Window Types."""

import json

try:
    from typing import Any
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
    from honeybee_energy_ph.properties.construction.window import (
        WindowConstructionPhProperties,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_energy_ph:\n\t{}".format(e))

try:
    from honeybee_ph_utils import iso_10077_1
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io. {}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection import (
        CustomCollection,
    )
    from honeybee_ph_plus_rhino.gh_compo_io.hb_tools.win_create_types import (
        WindowElement,
        WindowUnitType,
    )
    from honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.window_types_schema import (
        ApertureTypeData,
        GlazingData,
        GlazingType,
    )
except ImportError as e:
    raise ImportError("\nFailed to import from honeybee_ph_plus_rhino {}".format(e))


def create_hbph_glazing_types(_aperture_types):
    # type: (list[ApertureTypeData]) -> dict[str, PhWindowGlazing]
    """Create a collection of the HoneybeePH Glazing-Types from the PH-Navigator Aperture Types."""

    glazing_types_ = {}  # type: dict[str, PhWindowGlazing]
    for aperture_type in _aperture_types:
        for element in aperture_type.elements:
            if element.glazing is None:
                continue

            glazing_data = element.glazing  # type: GlazingData
            glazing_type_data = glazing_data.glazing_type  # type: GlazingType
            hbph_glazing = PhWindowGlazing(glazing_type_data.name)
            hbph_glazing.display_name = glazing_type_data.name
            hbph_glazing.u_factor = glazing_type_data.u_value_w_m2k
            hbph_glazing.g_value = glazing_type_data.g_value

            glazing_types_[hbph_glazing.display_name] = hbph_glazing

    return glazing_types_


def create_new_hbph_frame_element(_aperture_types):
    # type: (list[ApertureTypeData]) -> dict[str, PhWindowFrameElement]
    """Create a collection of the HoneybeePH Frame-Element-Types from the PH-Navigator Aperture Types."""

    frame_element_types_ = {}  # type: dict[str, PhWindowFrameElement]
    for aperture_type in _aperture_types:
        for element in aperture_type.elements:
            for frame_data in element.frames.get_all_frames():
                if frame_data.name in frame_element_types_:
                    continue  # Already created this frame element

                if not frame_data.frame_type:
                    continue

                hbph_frame_element = PhWindowFrameElement(frame_data.frame_type.name)
                hbph_frame_element.display_name = frame_data.frame_type.name
                hbph_frame_element.width = frame_data.frame_type.width_m
                hbph_frame_element.u_factor = frame_data.frame_type.u_value_w_m2k
                hbph_frame_element.psi_glazing = frame_data.frame_type.psi_glazing
                hbph_frame_element.psi_install = frame_data.frame_type.psi_install
                hbph_frame_element.chi_value = frame_data.frame_type.chi_value

                frame_element_types_[hbph_frame_element.display_name] = hbph_frame_element

    return frame_element_types_


def create_new_hbph_frames(_aperture_types, _frame_elements_types):
    # type: (list[ApertureTypeData], dict[str, PhWindowFrameElement]) -> dict[str, PhWindowFrame]
    """Create a collection of the HoneybeePH Frame-Types from the PH-Navigator Aperture Types."""

    frame_types_ = {}  # type: dict[str, PhWindowFrame]

    for aperture_type in _aperture_types:
        for element in aperture_type.elements:
            # Create a new PhWindowFrame for this Element
            frame_id = "{}".format(element.type_name)
            hbph_frame = PhWindowFrame(frame_id)
            hbph_frame.display_name = frame_id

            # Set all of the frame-elements for this Element
            for side in ["left", "right", "top", "bottom"]:
                frame_data = element.frames.get_frame_by_side(side)
                if frame_data is not None and frame_data.frame_type is not None:
                    frame_element = _frame_elements_types.get(frame_data.frame_type.name)
                    if frame_element is not None:
                        setattr(hbph_frame, side, frame_element)

            frame_types_[frame_id] = hbph_frame

    return frame_types_


def create_hbph_window_unit_types(_IGH, _aperture_types):
    # type: (gh_io.IGH, list[ApertureTypeData]) -> dict[str, WindowUnitType]
    """Create a collection of the HoneybeePH WindowUnitTypes from the PH-Navigator Aperture Types."""

    window_types_ = {}  # type: dict[str, WindowUnitType]
    for aperture_type in _aperture_types:
        new_window_unit_type = WindowUnitType(_IGH, aperture_type.name)

        for element in aperture_type.elements:
            # -- Calculate the total width considering column span
            element_width_m = 0.0
            for col in range(
                element.column_number, element.column_number + element.column_span
            ):
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
                element.row_number,
            )
            new_window_unit_type.elements.append(window_element)

        window_types_[new_window_unit_type.type_name] = new_window_unit_type

    return window_types_


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


def create_hbph_ep_constructions(_aperture_types, _glazing_types, _frame_types):
    # type: (list[ApertureTypeData], dict[str, PhWindowGlazing], dict[str, PhWindowFrame]) -> dict[str, WindowConstruction]
    """Create the HoneybeePH EP-Constructions for the Window Types."""

    constructions_ = {}  # type: dict[str, WindowConstruction]
    for aperture_type in _aperture_types:
        for element in aperture_type.elements:
            # Get the frame-type and glazing-type for this element
            hbph_frame = _frame_types.get(element.type_name, None)
            if hbph_frame is None:
                continue

            hbph_glazing = _glazing_types.get(element.glazing.glazing_type.name, None)
            if hbph_glazing is None:
                continue

            # Build the HB Window Material and Construction
            hbph_mat = create_new_hbph_window_material(
                element.type_name, hbph_frame, hbph_glazing
            )
            hb_win_construction = WindowConstruction(element.type_name, [hbph_mat])

            # Set the PH Properties on the WindowConstructionProperties
            prop_ph = getattr(
                hb_win_construction.properties, "ph"
            )  # type: WindowConstructionPhProperties
            prop_ph.ph_frame = hbph_frame
            prop_ph.ph_glazing = hbph_glazing

            constructions_[hb_win_construction.display_name] = hb_win_construction

    return constructions_


class GHCompo_PHNavGetWindowTypes(object):
    """A class for downloading PH-Navigator Window Types for a specific Project Number."""

    URL_BASE = "https://ph-dash-0cye.onrender.com"

    def __init__(
        self, IGH, _project_number, _url_base, _get_aperture_types, *args, **kwargs
    ):
        # type: (gh_io.IGH, str, str | None, bool, *Any, **Any) -> None
        self.IGH = IGH
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
        """Download and parse aperture types from PH-Navigator."""

        apertures_dict = {}  # type: dict[str, dict]
        offset = "0"

        while offset is not None:
            client = self.get_web_client(offset)
            response = client.DownloadString(self.url)
            data = json.loads(response)  # type: dict[str, Any]

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

        return apertures_dict

    def convert_json_data_to_aperture_types(self, _apertures_dict):
        # type: (dict[str, dict]) -> list[ApertureTypeData]
        """Convert the downloaded JSON data to a list of ApertureTypeData objects."""

        aperture_types_ = []
        for aperture_data in _apertures_dict.values():
            try:
                aperture_type = ApertureTypeData.from_dict(aperture_data)
                aperture_types_.append(aperture_type)
            except Exception as e:
                self.IGH.warning("Failed to parse aperture type: {}".format(e))
                continue

        return aperture_types_

    def run(self):
        # type: () -> tuple[CustomCollection | None, CustomCollection | None, Any | None]
        """Run the component."""
        if not self.ready:
            return None, None, None

        try:
            download_data = self.download_aperture_types_json()
            aperture_types = self.convert_json_data_to_aperture_types(download_data)
        except Exception as e:
            msg = "Failed to download file from PH-Navigator.\n{}".format(e)
            self.IGH.error(msg)
            return None, None, None

        # Build all of the Types needed to create the HoneybeePH Window Types
        glazing_types_dict = create_hbph_glazing_types(aperture_types)
        frame_element_types_dict = create_new_hbph_frame_element(aperture_types)
        frame_types_dict = create_new_hbph_frames(
            aperture_types, frame_element_types_dict
        )

        # Build all of the WindowUnitTypes
        window_unit_types_dict = create_hbph_window_unit_types(self.IGH, aperture_types)
        window_unit_types_collection_ = CustomCollection()
        for k, v in window_unit_types_dict.items():
            window_unit_types_collection_[k] = v

        # Build the EP-Constructions for each of the Elements
        window_ep_construction_dict = create_hbph_ep_constructions(
            aperture_types, glazing_types_dict, frame_types_dict
        )
        window_ep_construction_collection_ = CustomCollection()
        for k, v in window_ep_construction_dict.items():
            window_ep_construction_collection_[k] = v

        return (
            window_unit_types_collection_,
            window_ep_construction_collection_,
            json.dumps(download_data, indent=2, ensure_ascii=False),
        )
