# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to read all the active climate monthly data from a PHPP 'Climate' Worksheet.

This script is called from the command line with the following arguments:
    * [0] (str): The path to the Python script (this file)
    * [1] (str): The path to the CSV output file to write the data to.
"""

import sys
from pathlib import Path

import pandas as pd
import xlwings as xw
from PHX.PHPP import phpp_app
from PHX.xl import xl_app
from rich import print


def resolve_arguments(_args: list[str]) -> tuple[Path, Path | None]:
    """Get all the script arguments

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * Path: The path to the CSV output file to use.
        * Path | None: The path to the PHPP file to use
    """

    num_args = len(_args)
    assert num_args == 3, "Wrong number of arguments. Got {}.".format(num_args)

    csv_output_file_ = Path(str(_args[1]))
    if not csv_output_file_:
        raise Exception("Error: Missing CSV-output file path")

    if _args[2] == None or _args[2] == "None" or _args[2] == "":
        phpp_input_file_ = None
    else:
        phpp_input_file_ = Path(str(_args[2]))

    return csv_output_file_, phpp_input_file_


if __name__ == "__main__":
    print(f"Running script {__file__}")

    csv_output_file, phpp_input_file = resolve_arguments(sys.argv)

    # --- Connect to open instance of XL, Load the correct PHPP Shape file
    # -------------------------------------------------------------------------
    xl = xl_app.XLConnection(xl_framework=xw, output=print, xl_file_path=phpp_input_file)
    phpp_conn = phpp_app.PHPPConnection(xl)

    try:
        clr = "bold green"
        msg = f"[{clr}]> connected to Excel doc: {phpp_conn.xl.wb.name}[/{clr}]"
        xl.output(msg)
    except xl_app.NoActiveExcelRunningError as e:
        raise e

    # --- Read the Climate Data out and Write to a CSV file.
    # -------------------------------------------------------------------------
    climate_data = phpp_conn.climate.read_active_monthly_data()
    df = pd.DataFrame(climate_data).transpose().to_csv(csv_output_file)
    print(f"Wrote PHPP Climate data to: '{csv_output_file}'")
