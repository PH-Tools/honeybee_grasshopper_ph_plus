# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - SQL Get Column Names."""

import json
import os
from collections import namedtuple

try:
    from typing import Any
except ImportError as e:
    pass  # IronPython 2.7

try:
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError("\nFailed to import ladybug:\n\t{}".format(e))

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")

try:
    from honeybee_ph_plus_rhino.gh_compo_io.run_subprocess import run_subprocess
except ImportError as e:
    raise ImportError("\nFailed to import run_subprocess:\n\t{}".format(e))


class GHCompo_CreatePlotlyGraph(object):

    def __init__(
        self, _IGH, _folder, _name, _title, _data, _horiz_lines, _run, *args, **kwargs
    ):
        # type: (gh_io.IGH, str | None, str | None, str | None, list[HourlyContinuousCollection], list[float], bool, *Any, **Any) -> None
        self.IGH = _IGH
        self.folder = _folder or hb_folders.default_simulation_folder
        self.name = _name or "unnamed_plot"
        self.title = _title or "Un-titled Plot"
        self.data = _data
        self.horiz_lines = _horiz_lines or []
        self._run = _run or False

    def get_dataset_unit_type(self):
        # type: () -> str | None
        unit_types = {dataset.header.unit for dataset in self.data}
        if not unit_types:
            return None
        if len(unit_types) > 1:
            msg = "All datasets must have the same unit type. Found: {}".format(
                ", ".join(unit_types)
            )
            print(msg)
            self.IGH.error(msg)
        return unit_types.pop()

    def get_dataset_datatype(self):
        # type: () -> str | None
        _types_ = {str(dataset.header.data_type) for dataset in self.data}
        if not _types_:
            return None
        if len(_types_) > 1:
            msg = "All datasets must have the same data-type. Found: {}".format(
                ", ".join(_types_)
            )
            print(msg)
            self.IGH.error(msg)
        return _types_.pop()

    @property
    def y_axis_label(self):
        # type: () -> str
        return "{} [{}]".format(self.get_dataset_datatype(), self.get_dataset_unit_type())

    def validate_data(self):
        # type: () -> bool
        for dataset in self.data:
            if not dataset:
                return False
            if not isinstance(dataset, HourlyContinuousCollection):
                print(
                    "Error: All datasets must be of type HourlyContinuousCollection. Got: {}".format(
                        type(dataset)
                    )
                )
                return False

        unit_types = {dataset.header.unit for dataset in self.data}
        if len(unit_types) > 1:
            msg = "All datasets must have the same unit type. Found: {}".format(
                ", ".join(unit_types)
            )
            print(msg)
            self.IGH.error(msg)
            return False

        analysis_period_lengths = {
            len(dataset.header.analysis_period.datetimes) for dataset in self.data
        }
        if len(analysis_period_lengths) > 1:
            msg = "All datasets must have the same analysis period length. Found: {}".format(
                ", ".join(str(analysis_period_lengths))
            )
            print(msg)
            self.IGH.error(msg)
            return False

        return True

    @property
    def ready(self):
        # type: () -> bool
        """Return True if the component is ready to run."""
        if not self._run or not self.data:
            return False
        if not self.validate_data():
            return False
        return True

    @property
    def py3_script_file(self):
        # type: () -> str
        """The path to the Python3 Script to run in the Subprocess."""
        return os.path.join(
            hb_folders.python_package_path,
            "honeybee_ph_plus_rhino",
            "plotly",
            "plot_ladybug_data.py",
        )

    @property
    def html_file_path(self):
        # type: () -> str
        """The path to the HTML file that will be created."""
        return os.path.join(self.folder, self.name + ".html")

    def process_stderr(self, stderr):
        # type: (bytes) -> None
        if not stderr:
            return
        for row in str(stderr.decode("utf-8")).split("\\n"):
            print("Error: {}".format(row))
            self.IGH.error(row)

    def process_stdout(self, stdout):
        # type: (bytes) -> None
        if not stdout:
            return None
        for row in str(stdout.decode("utf-8")).split("\\n"):
            print("Error: {}".format(row))
            self.IGH.remark(row)

    def data_as_json(self):
        # type: () -> str
        """Return the Ladybug Timeseries data as a JSON dictionary."""
        data_ = []
        for d in self.data:
            data_.append(d.to_dict())
        return json.dumps(data_)

    def run(self):
        # type: () -> Any
        if not self.ready:
            print("Not ready to run.")
            return None

        # -- Run as a Subprocess since sqlite3 doesn't work in Rhino on MacOS
        commands = [
            hb_folders.python_exe_path,  # --- The python3-interpreter to use
            self.py3_script_file,  # --------- The python3-script to run
            self.html_file_path,  # ---------- The HTML file path (to save)
            self.get_dataset_unit_type(),  # -- The unit type of the dataset
            self.y_axis_label,
            self.title,
            str(self.horiz_lines),
        ]
        stdout, stderr = run_subprocess(commands, _input=self.data_as_json())
        self.process_stderr(stderr)
        self.process_stdout(stdout)

        return self.html_file_path
