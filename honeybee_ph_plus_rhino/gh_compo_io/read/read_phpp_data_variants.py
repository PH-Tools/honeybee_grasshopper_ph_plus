# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Read Variants Data from PHPP."""

import os
from datetime import datetime

try:
    from typing import Any
except ImportError as e:
    pass  # IronPython 2.7

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.read import read_phpp_data
except ImportError as e:
    raise ImportError("\nFailed to import read_phpp_data:\n\t{}".format(e))


class GHCompo_ReadPHPPVariantsData(object):

    def __init__(self, _IGH, _folder, _filename, _phpp_file, _run, *args, **kwargs):
        # type: (gh_io.IGH, str | None, str | None, str | None, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.folder = _folder
        self.filename = _filename
        self.phpp_file = _phpp_file
        self._run = _run or False

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not self._run:
            self.IGH.warning("Set '_run' to True to read the data from PHPP.")
            return False
        return True

    @property
    def py3_script_file(self):
        # type: () -> str
        """The path to the Python3 Script to run in the Subprocess."""
        return os.path.join(
            hb_folders.python_package_path,
            "honeybee_ph_plus_rhino",
            "phpp",
            "read_phpp_data_variants.py",
        )

    @property
    def py3_shell_file(self):
        # type: () -> str
        """The path to the Shell Script to run in the Subprocess."""
        return os.path.join(
            hb_folders.python_package_path,
            "honeybee_ph_plus_rhino",
            "phpp",
            "read_phpp_data.sh",
        )

    def get_csv_output_file_path(self):
        # type: () -> str
        """The path to the CSV file to write the data to."""
        if self.folder is not None and self.filename is not None:
            if not os.path.exists(self.folder):
                os.makedirs(self.folder)
            if not self.filename.endswith(".csv"):
                self.filename = "{}.csv".format(self.filename)
            return os.path.join(self.folder, self.filename)
        else:
            file_name = "phpp_data_variants_{}.csv".format(
                datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            )
            return os.path.join(hb_folders.default_simulation_folder, file_name)

    def run(self):
        # type: () -> Any
        if not self.ready:
            print("Set '_run' to True to read the data from PHPP.")
            return None

        output_file = self.get_csv_output_file_path()
        read_phpp_data.run(
            self.IGH,
            self.py3_shell_file,
            self.py3_script_file,
            output_file,
        )

        return output_file
