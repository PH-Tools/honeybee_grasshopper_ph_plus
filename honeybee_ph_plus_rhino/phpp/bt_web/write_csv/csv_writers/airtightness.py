# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Airtightness CSV data from the Main PHPP DataFrame"""

import pathlib

import pandas as pd

from honeybee_ph_plus_rhino.phpp.bt_web._variants_data_schema import VARIANTS


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

    start_row = VARIANTS.airtightness.start_row()
    end_row = VARIANTS.airtightness.end_row()
    airflow_df = _df_main.loc[start_row:end_row]

    # drop the 'SYSTEMS' row
    airflow_df_2 = airflow_df.drop(
        airflow_df[airflow_df["Datatype"] == "AIRTIGHTNESS"].index
    )

    airflow_df_2.to_csv(_output_path, index=False)
