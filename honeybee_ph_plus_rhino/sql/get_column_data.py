# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to read all the Table names from a specified SQL file.

This script is called from the command line with the following arguments:
    * [0] (str): The path to the Python script (this file).
    * [1] (str): The path to the SQL file to read in.
    * [2] (str): The table name to read from.
    * [3] (str): The column name to read from.
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


def resolve_arguments(_args: list[str]) -> tuple[Filepaths, str, str]:
    """Get out the file input table name.

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * Filepaths: The Filepaths object.
        * str: The table name.
        * str: The column name.
    """

    assert len(_args) == 4, "Error: Incorrect number of arguments."

    # -----------------------------------------------------------------------------------
    # -- The EnergyPlus SQL input file.
    results_sql_file = Path(_args[1])
    if not results_sql_file.exists():
        raise InputFileError(results_sql_file)

    table_name = str(_args[2])
    if not table_name:
        raise InputFileError(table_name)

    column_name = str(_args[3])
    if not column_name:
        raise InputFileError(column_name)

    return (Filepaths(results_sql_file), table_name, column_name)


def get_column_data(source_file_path: Path, table_name: str, column_name: str) -> list:
    """Get the field data from the specified SQLite file | Table | Column."""

    conn = sqlite3.connect(source_file_path)
    data_ = []
    try:
        c = conn.cursor()
        c.execute(f"SELECT {column_name} FROM '{table_name}';")
        for d in c.fetchall():
            data_.append(d[0])
    except Exception as e:
        conn.close()
        raise Exception(str(e))
    finally:
        conn.close()

    return data_


if __name__ == "__main__":
    file_paths, table_name, column_name = resolve_arguments(sys.argv)
    column_data = get_column_data(file_paths.sql, table_name, column_name)
    print(f"{column_data=}")
