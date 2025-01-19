# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to read all the Table names from a specified SQL file.

This script is called from the command line with the following arguments:
    * [0] (str): The path to the Python script (this file).
    * [1] (str): The path to the SQL file to read in.
"""

import sqlite3
import sys
from collections import namedtuple
from pathlib import Path


class InputFileError(Exception):
    def __init__(self, path) -> None:
        self.msg = f"\nCannot locate the specified file:'{path}'"
        super().__init__(self.msg)


Filepaths = namedtuple("Filepaths", ["sql"])


def resolve_paths(_args: list[str]) -> Filepaths:
    """Get out the file input path.

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * (Filepaths): The Filepaths object.
    """

    assert len(_args) == 2, "Error: Incorrect number of arguments."

    # -----------------------------------------------------------------------------------
    # -- The EnergyPlus SQL input file.
    results_sql_file = Path(_args[1])
    if not results_sql_file.exists():
        raise InputFileError(results_sql_file)

    return Filepaths(results_sql_file)


def get_table_names(source_file_path: Path) -> list[str]:
    """Get the table names from the SQLite file."""

    conn = sqlite3.connect(source_file_path)
    data_ = []  # defaultdict(list)
    try:
        c = conn.cursor()
        c.execute(
            "SELECT DISTINCT name FROM sqlite_master WHERE type='table' ORDER BY name;"
        )
        for row in c.fetchall():
            data_.append(str(row[0]))
    except Exception as e:
        conn.close()
        raise Exception(str(e))
    finally:
        conn.close()

    return data_


if __name__ == "__main__":
    file_paths = resolve_paths(sys.argv)
    table_names = get_table_names(file_paths.sql)
    print(f"{table_names=}")
