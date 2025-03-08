# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to convert raw PHPP CSV data into clean CSV files ready for the BLDGTYP standard web-dashboard.

This script is called from the command line with the following arguments:
    * [0] (str): The path to the Python script (this file)
    * [1] (str): The path to the Variant Data CSV File
    * [2] (str): The path to the Climate Data CSV File
    * [3] (str): The path to the Room-Ventilation Data CSV File
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from rich import print

from honeybee_ph_plus_rhino.phpp.bt_web._types import PHPPData
from honeybee_ph_plus_rhino.phpp.bt_web.write_csv import generate_csv_files


def convert_to_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Converts all columns in a DataFrame to numeric values where possible."""
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").combine_first(df[col])
    return df


def clean_climate_df(_climate_df: pd.DataFrame) -> pd.DataFrame:
    # -- Drop the first column
    climate_df_ = _climate_df.drop(_climate_df.columns[0], axis=1)

    # -- Get only the Monthly Data (columns 1-13)
    climate_df_ = climate_df_.iloc[:, 0:13]

    # -- Reset the index to be the values from column-0
    climate_df_.index = climate_df_[climate_df_.columns[0]]
    #
    # -- Convert to numeric where possible
    climate_df_ = convert_to_numeric(climate_df_)

    return climate_df_


def clean_room_vent_df(_room_vent_df: pd.DataFrame) -> pd.DataFrame:
    # -- convert to numeric where possible
    room_vent_df_ = convert_to_numeric(_room_vent_df)

    # -- Drop the first column
    room_vent_df_ = room_vent_df_.drop(room_vent_df_.columns[0], axis=1)

    # -- Drop the first 3 rows (headers)
    room_vent_df_ = room_vent_df_[3:]

    # -- Keep only the first 19 columns
    room_vent_df_ = room_vent_df_.iloc[:, 1:20]

    return room_vent_df_


def clean_variants_df(_variant_df: pd.DataFrame) -> pd.DataFrame:
    """Cleans up the 'Main' Variant Results DataFrame of PHPP Data."""

    # -- Reset the Column Names (Row 2 has the column names)
    _variant_df.columns = _variant_df.iloc[0]

    # -- Drop the first two rows
    clean_df = _variant_df[2:].reset_index(drop=True)

    # -- Cleanup the Columns
    clean_df = clean_df.drop(clean_df.columns[0], axis=1)
    clean_df = clean_df.drop(clean_df.columns[3], axis=1)
    clean_df.rename(columns={clean_df.columns[0]: "Datatype"}, inplace=True)
    clean_df.rename(columns={clean_df.columns[1]: "Units"}, inplace=True)
    clean_df.reset_index(drop=True, inplace=True)

    # -- Change the index start so it aligns with Excel
    clean_df.index = np.arange(11, len(clean_df) + 11)  # type: ignore

    # -- Remove any columns without active variant data
    clean_df.dropna(axis=1, thresh=2, inplace=True)

    # -- clean up trailing white-space in datatype names...
    clean_df["Datatype"] = clean_df["Datatype"].str.strip()
    clean_df["Datatype"] = clean_df["Datatype"].str.replace(",", " ")

    # Convert columns to numeric where possible
    clean_df = convert_to_numeric(clean_df)

    return clean_df


def get_tfa_as_df(_df_main: pd.DataFrame) -> pd.Series:
    """Return the Treated Floor Area (TFA) for each Variant as a pandas.Series

    Arguments:
    ----------
        * _df_main (pd.DataFrame): The Main DataFrame with data from the Variants Worksheet.

    Returns:
    --------
        * (pd.Series): The TFA of each Variant.
    """
    return _df_main.loc[279]


def get_absolute_certification_limits_as_df(
    _df_main: pd.DataFrame,
) -> pd.DataFrame:
    """Return a DataFrame with all the PH/Phius Certification limits found in the PHPP.

    Arguments:
    ----------
        * _df_main (pd.DataFrame): The Main DataFrame with data from the Variants Worksheet.

    Returns:
    --------
        * (pd.DataFrame): A new DataFrame with the Certification Limits
    """

    # Get all the certification LIMITS in ../m2 values
    cert_limits_specific = _df_main.loc[318:326]

    tfa_df = get_tfa_as_df(_df_main)

    # Calc the total limits (not .../m2 results for certification values)
    cert_limits_abs = pd.DataFrame()
    for variant in cert_limits_specific.columns[:2]:  # Data ID cols
        cert_limits_abs[variant] = cert_limits_specific[variant]

    cert_limits_abs["Units"] = cert_limits_specific["Units"].str.replace(
        "/m2", ""
    )  # 'm2' strings

    for variant in cert_limits_specific.columns[2:]:  # The data cols
        cert_limits_abs[variant] = cert_limits_specific[variant].mul(tfa_df[variant])

    return cert_limits_abs


def get_variant_names_as_series(_df_main: pd.DataFrame) -> pd.Series:
    """Return the Variants Names for each Variant as a pandas.Series

    Arguments:
    ----------
        * _df_main (pd.DataFrame): The Main DataFrame with data from the Variants Worksheet.

    Returns:
    --------
        * (pd.Series): The Variant Name of each Variant.
    """
    return _df_main.columns[2::]


def resolve_arguments(_args: list[str]) -> tuple[Path, Path, Path, Path]:
    """Get all the script arguments

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * tuple[Path, Path, Path]:
            * [0]: The path to the Variant Data CSV File
            * [1]: The path to the Climate Data CSV File
            * [2]: The path to the Room-Ventilation Data CSV File
    """

    num_args = len(_args)
    assert num_args == 5, "Wrong number of arguments. Got {}.".format(num_args)

    variant_data_csv = Path(str(_args[1]))
    if not variant_data_csv:
        raise Exception("Error: Missing Variant Data CSV?")

    climate_data_csv = Path(str(_args[2]))
    if not climate_data_csv:
        raise Exception("Error: Missing Climate Data CSV?")

    room_vent_data_csv = Path(str(_args[3]))
    if not room_vent_data_csv:
        raise Exception("Error: Missing Room-Ventilation Data CSV?")

    save_folder = Path(str(_args[4]))
    if not save_folder:
        raise Exception("Error: Missing Save Folder?")

    return variant_data_csv, climate_data_csv, room_vent_data_csv, save_folder


if __name__ == "__main__":
    print(f"Running script {__file__}")

    variant_data_csv, climate_data_csv, room_vent_data_csv, save_folder = (
        resolve_arguments(sys.argv)
    )

    # variant_data_csv = Path("/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_grasshopper_ph_plus/honeybee_ph_plus_rhino/phpp/bt_web/test/phpp_data_variants.csv")
    # climate_data_csv = Path("/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_grasshopper_ph_plus/honeybee_ph_plus_rhino/phpp/bt_web/test/phpp_data_climate.csv")
    # room_vent_data_csv = Path("/Users/em/Dropbox/bldgtyp-00/00_PH_Tools/honeybee_grasshopper_ph_plus/honeybee_ph_plus_rhino/phpp/bt_web/test/phpp_data_room_ventilation.csv")

    print(f"Reading Data from: {variant_data_csv}")
    variant_df = clean_variants_df(pd.read_csv(variant_data_csv))

    print(f"Reading Data from: {climate_data_csv}")
    climate_df = clean_climate_df(pd.read_csv(climate_data_csv))

    print(f"Reading Data from: {room_vent_data_csv}")
    room_vent_df = clean_room_vent_df(pd.read_csv(room_vent_data_csv))

    abs_cert_limits_df = get_absolute_certification_limits_as_df(variant_df)
    tfa_df = get_tfa_as_df(variant_df)
    variant_names = get_variant_names_as_series(variant_df)

    phpp_data = PHPPData(
        variant_df, climate_df, room_vent_df, abs_cert_limits_df, tfa_df, variant_names
    )

    generate_csv_files.create_csv_files(save_folder, phpp_data)
