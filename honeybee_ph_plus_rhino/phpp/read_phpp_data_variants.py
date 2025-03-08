# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to read all the result data from a PHPP 'Variants' Worksheet.

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


def resolve_arguments(_args: list[str]) -> Path:
    """Get all the script arguments

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * Path: The path to the CSV output file to use.
    """

    num_args = len(_args)
    assert num_args == 2, "Wrong number of arguments. Got {}.".format(num_args)

    csv_output_file = Path(str(_args[1]))
    if not csv_output_file:
        raise Exception("Error: Missing CSV-output file path")

    return csv_output_file


if __name__ == "__main__":
    print(f"Running script {__file__}")

    csv_output_file = resolve_arguments(sys.argv)

    # --- Connect to open instance of XL, Load the correct PHPP Shape file
    # -------------------------------------------------------------------------
    xl = xl_app.XLConnection(xl_framework=xw, output=print)
    phpp_conn = phpp_app.PHPPConnection(xl)

    try:
        clr = "bold green"
        msg = f"[{clr}]> connected to Excel doc: {phpp_conn.xl.wb.name}[/{clr}]"
        xl.output(msg)
    except xl_app.NoActiveExcelRunningError as e:
        raise e

    # --- Read the Variants Data out and Write to a CSV file.
    # -------------------------------------------------------------------------
    variants_data = phpp_conn.variants.get_variant_results_data()
    df = pd.DataFrame(variants_data).transpose().to_csv(csv_output_file)
    print(f"Wrote PHPP Variants data to: '{csv_output_file}'")
