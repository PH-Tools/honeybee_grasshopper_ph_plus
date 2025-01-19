# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - SQL Get Table Names."""

import os

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


class GHCompo_SQLGetTableNames(object):

    def __init__(self, _IGH, _sql_file, *args, **kwargs):
        # type: (gh_io.IGH, str | None, *Any, **Any) -> None
        self.IGH = _IGH
        self._sql_file = _sql_file

    @property
    def py3_script_file(self):
        # type: () -> str
        """The path to the Python3 Script to run in the Subprocess."""
        return os.path.join(
            hb_folders.python_package_path,
            "honeybee_ph_plus_rhino",
            "sql",
            "get_table_names.py",
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

    @staticmethod
    def clean_table_name(_str):
        # type: (str) -> str
        """Clean the table name."""
        return (
            _str.strip()
            .replace("'", "")
            .replace('"', "")
            .replace("[", "")
            .replace("]", "")
        )

    def process_stderr(self, stderr):
        # type: (bytes) -> None
        """Subprocess stderr, if not empty, will include the error messages."""
        if not stderr:
            return
        for row in str(stderr.decode("utf-8")).split("\\n"):
            print("Error: {}".format(row))
            self.IGH.error(row)

    def process_stdout(self, stdout):
        # type: (bytes) -> list[str]
        """Subprocess stdout, if successful, will include the table names."""
        table_names = []
        if not stdout:
            return table_names

        for row in str(stdout.decode("utf-8")).split("\\n"):
            if "table_names=" in row:
                table_names_string = row.replace("table_names=", "").strip()
                for table_name in table_names_string.split(","):
                    if table_name:
                        table_names.append(self.clean_table_name(table_name))
        return table_names

    def run(self):
        # type: () -> list[str]
        if not self.sql_file:
            return []

        # -- Run as a Subprocess since sqlite3 doesn't work in Rhino on MacOS
        commands = [
            hb_folders.python_exe_path,  # -- The python3-interpreter to use
            self.py3_script_file,  # --------- The python3-script to run
            self.sql_file,  # --------------- The SQL file to use
        ]
        stdout, stderr = run_subprocess(commands)
        self.process_stderr(stderr)
        return self.process_stdout(stdout)