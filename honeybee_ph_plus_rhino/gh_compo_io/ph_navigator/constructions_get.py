# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - PH-Navigator Get Constructions."""

import json

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
    from honeybee_energy.construction.opaque import OpaqueConstruction
except ImportError as e:
    raise ImportError("Failed to import honeybee_energy. {}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino. {}".format(e))


class GHCompo_PHNavGetConstructions(object):
    """A class for downloading PH-Navigator Constructions for a specific Project Number."""

    URL_BASE = "https://ph-dash-0cye.onrender.com"

    def __init__(
        self, _IGH, _project_number, _url_base, _get_constructions, *args, **kwargs
    ):
        # type: (gh_io.IGH, str, str | None, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.PROJECT_NUMBER = _project_number
        self._url_base = _url_base
        self.get_constructions = _get_constructions

    @property
    def ready(self):
        # type: () -> bool
        if not self.PROJECT_NUMBER:
            return False
        if not self.get_constructions:
            return False
        return True

    @property
    def url(self):
        # type: () -> str
        """Get the URL for the PH-Navigator API."""
        # URL for the PH-Navigator API
        _url = "{}/assembly/get-assemblies-as-hbjson/{}".format(
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

    def download_hb_constructions_json(self):
        # type: () -> dict[str, dict]
        """Download HB-Constructions from PH-Navigator.

        Since PH-Navigator limits the number of records that can be downloaded
        in a single request, this method will download all records in the table
        by making multiple requests using the 'offset' query parameter.
        """
        hb_constructions = {}  # type: dict[str, dict]
        offset = "0"

        while offset != None:
            client = self.get_web_client(offset)
            response = client.DownloadString(self.url)
            data = json.loads(response)  # type: dict
            print(type(data), data)
            """
            data.hb_constructions = {
                "Assembly 1: {....},
                "Assembly 2: {....},
                ...
            }
            """

            # Ensure 'hb_constructions' is properly deserialized
            d = data.get("hb_constructions", {})
            print(d)
            if isinstance(d, str):  # If it's a string, deserialize it
                try:
                    d = json.loads(d)
                except json.JSONDecodeError as e:
                    self.IGH.error("Failed to parse 'hb_constructions': {}".format(e))
                    d = []

            hb_constructions.update(d)
            offset = data.get("offset", None)

        return hb_constructions

    def run(self):
        # type: () -> None | list[OpaqueConstruction]
        """Run the component."""
        if not self.ready:
            return None

        try:
            hb_constructions_json_ = self.download_hb_constructions_json()
        except Exception as e:
            msg = "Failed to download file from PH-Navigator.\n{}".format(e)
            self.IGH.error(msg)
            return None

        return [OpaqueConstruction.from_dict(_) for _ in hb_constructions_json_.values()]
