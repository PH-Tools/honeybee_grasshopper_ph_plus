# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Clean Variants Data CSV."""

import os
import time

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
    from honeybee_ph_plus_rhino.gh_compo_io.run_subprocess import (
        process_stderr,
        process_stdout,
        run_subprocess,
    )
except ImportError as e:
    raise ImportError("\nFailed to import run_subprocess:\n\t{}".format(e))


class GHCompo_ProcessPHPPCSVData(object):

    def __init__(
        self,
        _IGH,
        _folder,
        _variant_data,
        _climate_data,
        _room_ventilation_data,
        _run,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, str, str, str, str, bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.save_folder = _folder
        self.variant_data_csv = _variant_data
        self.climate_data_csv = _climate_data
        self.room_vent_data_csv = _room_ventilation_data
        self._run = _run or False

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not all([self.variant_data_csv, self.climate_data_csv, self.room_vent_data_csv]):
            self.IGH.warning(
                "Please provide the source-data CSV-files to process."
            )
            return False
        if not self.save_folder:
            self.IGH.warning(
                "Please provide a save-folder location."
            )
            return False
        if not self._run:
            self.IGH.warning(
                "Set '_run' to True to process the PHPP data into CSV files."
            )
            return False
        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
        return True

    @property
    def py3_script_file(self):
        # type: () -> str
        """The path to the Python3 Script to run in the Subprocess."""
        return os.path.join(
            hb_folders.python_package_path,
            "honeybee_ph_plus_rhino",
            "phpp",
            "bt_web",
            "process_phpp_csv_data.py",
        )

    @property
    def save_folder(self):
        return self._save_folder

    @save_folder.setter
    def save_folder(self, _folder):
        # type: (str) -> None
        if not _folder:
            self._save_folder = None
            return None
        if not os.path.exists(_folder):
            os.makedirs(_folder)
        self._save_folder = _folder

    @property
    def execution_root(self):
        # type: () -> str
        """The root folder for the execution of the subprocess."""
        return os.path.join(hb_folders.python_package_path, "honeybee_ph_plus_rhino")

    def check_csv_file_exists(self, _csv_file):
        # type: (str) -> None
        """Ensure that the input CSV file actually exists.

        Since the CSV writer executes in a subprocess, we need to check to see
        if the files exist, it not, lets pause and wait for them to be created.
        """
        while not os.path.exists(_csv_file):
            # Small delay to avoid excessive CPU usage
            time.sleep(0.25)

        # Wait until file writing is finished by checking file size stability
        previous_size = -1
        while True:
            current_size = os.path.getsize(_csv_file)
            if current_size == previous_size:
                break
            previous_size = current_size
            time.sleep(0.25)

    def run(self):
        # type: () -> Any
        if not self.ready:
            return None

        self.check_csv_file_exists(self.variant_data_csv)
        self.check_csv_file_exists(self.climate_data_csv)
        self.check_csv_file_exists(self.room_vent_data_csv)

        # -- Run as a Subprocess so we can use Pandas, etc..
        commands = [
            hb_folders.python_exe_path,  # -- The python3-interpreter to use
            self.py3_script_file,  # -------- The python3-script to run
            self.variant_data_csv,  # ------- Variant Data CSV Path
            self.climate_data_csv,  # ------- Climate Data CSV Path
            self.room_vent_data_csv,  # ----- Room Ventilation Data CSV Path
            self.save_folder,  # ------------ The folder to save the CSV files
        ]
        stdout, stderr = run_subprocess(commands)
        process_stderr(self.IGH, stderr)
        process_stdout(self.IGH, stdout)

        self.save_folder
