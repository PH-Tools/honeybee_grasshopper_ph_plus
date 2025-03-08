# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Airtightness CSV data from the Main PHPP DataFrme"""

import pathlib

import pandas as pd


def create_csv_airtightness(_df_main: pd.DataFrame, _output_path: pathlib.Path) -> None:
    """Creates the Airtightness (HR%, Vv, Vn50, etc.) CSV file based on the PHPP DataFrame.

    Arguments:
    ----------
        * _df_main (pd.DataFrame): The Main PHPP DataFrame to get the data from.
        * _output_path (pathlib.Path): The full output file path for the CSV.

    Returns:
    --------
        * None
    """

    airflow_df = _df_main.loc[437:443]
    airflow_df.to_csv(_output_path, index=False)
