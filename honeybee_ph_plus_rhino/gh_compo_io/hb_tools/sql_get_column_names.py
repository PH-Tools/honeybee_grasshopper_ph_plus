# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - SQL Get Column Names."""

import os
from collections import namedtuple

try:
    from typing import Any
except ImportError as e:
    pass  # IronPython 2.7

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.run_subprocess import run_subprocess
except ImportError as e:
    pass  # raise ImportError("\nFailed to import run_subprocess:\n\t{}".format(e))


ColumnData = namedtuple("ColumnData", ["index", "name", "type", "not_null", "default", "primary_key"])


class GHCompo_SQLGetColumnNames(object):

    def __init__(self, _IGH, _sql_file, _table_name, *args, **kwargs):
        # type: (gh_io.IGH, str | None, str | None, *Any, **Any) -> None
        self.IGH = _IGH
        self._sql_file = _sql_file
        self._table_name = _table_name

    @property
    def py3_script_file(self):
        # type: () -> str
        """The path to the Python3 Script to run in the Subprocess."""
        return os.path.join(
            hb_folders.python_package_path,
            "honeybee_ph_plus_rhino",
            "sql",
            "get_column_names.py",
        )

    @property
    def sql_file(self):
        # type: () -> bool | str
        """The SQL file to read."""
        if not self._sql_file:
            return False
        if not os.path.exists(self._sql_file):
            return False
        if not self._sql_file.endswith(".sql"):
            return False
        return self._sql_file

    @property
    def table_name(self):
        # type: () -> bool | str
        if not self._table_name:
            return False
        return str(self._table_name).strip()

    def process_stderr(self, stderr):
        # type: (bytes) -> None
        """Subprocess stderr, if not empty, will include the error messages."""
        if not stderr:
            return
        for row in str(stderr.decode("utf-8")).split("\\n"):
            print("Error: {}".format(row))
            self.IGH.error(row)

    def process_stdout(self, stdout):
        # type: (bytes) -> tuple[list[str], list[str]]
        """Subprocess stdout, if successful, will include the column data."""
        column_names = []
        column_types = []
        if not stdout:
            return column_names, column_types

        for row in str(stdout.decode("utf-8")).split("\\n"):
            if "column_data=" in row:
                for item in eval(row.replace("column_data=", "").strip()):
                    column_names.append(getattr(item, "name", ""))
                    column_types.append(getattr(item, "type", ""))
        return column_names, column_types

    def run(self):
        # type: () -> tuple[list[str], list[str]]
        if not self.sql_file or not self.table_name:
            return [], []

        # -- Run as a Subprocess since sqlite3 doesn't work in Rhino on MacOS
        commands = [
            hb_folders.python_exe_path,  # --- The python3-interpreter to use
            self.py3_script_file,  # --------- The python3-script to run
            self.sql_file,  # ---------------- The SQL file to use
            self.table_name,  # -------------- The table name to get the columns from
        ]
        stdout, stderr = run_subprocess(commands)
        self.process_stderr(stderr)
        return self.process_stdout(stdout)
