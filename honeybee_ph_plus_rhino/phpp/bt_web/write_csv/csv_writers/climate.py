# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Climate Data CSV files from the PHPP Climate DataFrme"""

import pathlib

import pandas as pd


def create_csv_radiation(_df_climate: pd.DataFrame, _output_path: pathlib.Path) -> None:
    """Creates the Radiation data CSV file based on the PHPP Climate DataFrame.

    Arguments:
    ----------
        * _df_climate (pd.DataFrame): The Main PHPP DataFrame to get the data from.
        * _output_path (pathlib.Path): The full output file path for the CSV.

    Returns:
    --------
        * None
    """

    # --------------------------------------------------------------------------
    # Climate: Radiation
    climate_col_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "June",
        "July",
        "Aug",
        "Sept",
        "Oct",
        "Nov",
        "Dec",
    ]
    _df_climate.columns = ["Units"] + climate_col_names

    # --------------------------------------------------------------------------
    # Pull out the Radiation Data
    rad_df1 = _df_climate.loc[
        [
            "Radiation North",
            "Radiation East",
            "Radiation South",
            "Radiation West",
            "Horizontal radiation",
        ]
    ]
    rad_df2 = rad_df1.T

    rad_df3 = rad_df2.drop("Units")

    rad_series_converted = []
    for each_col_name in rad_df3.columns:
        newSeries = pd.Series(
            rad_df3[each_col_name].values / 10.76391042
        )  # kWh/m2---> kWh/ft2
        rad_series_converted.append(newSeries)

    rad_df4 = pd.DataFrame(rad_series_converted).T
    rad_df4.columns = ["North", "East", "South", "West", "Horizontal"]
    rad_df4.insert(loc=0, column="Month", value=climate_col_names)

    # --------------------------------------------------------------------------
    # Export to csv
    rad_df4.to_csv(_output_path, index=False)


def create_csv_temperatures(
    _df_climate: pd.DataFrame, _output_path: pathlib.Path
) -> None:
    """Creates the Temperature data CSV file based on the PHPP Climate DataFrame.

    Arguments:
    ----------
        * _df_climate (pd.DataFrame): The Main PHPP DataFrame to get the data from.
        * _output_path (pathlib.Path): The full output file path for the CSV.

    Returns:
    --------
        * None
    """

    # --------------------------------------------------------------------------
    # Climate: Temps
    climate_col_names = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "June",
        "July",
        "Aug",
        "Sept",
        "Oct",
        "Nov",
        "Dec",
    ]

    # --------------------------------------------------------------------------
    # Pull out the Temperature Data
    temps_df1 = _df_climate.loc[
        ["Exterior temperature", "Dew point temperature", "Sky temperature"]
    ]
    temps_df2 = temps_df1.T
    temps_df3 = temps_df2.drop("Units")

    temps_series_converted = []
    for each_col_name in temps_df3.columns:
        newSeries = pd.Series(temps_df3[each_col_name].values * (9 / 5) + 32)  # C-->F
        temps_series_converted.append(newSeries)

    temps_df4 = pd.DataFrame(temps_series_converted).T
    temps_df4.columns = temps_df3.columns
    temps_df4.insert(loc=0, column="Month", value=climate_col_names)

    # --------------------------------------------------------------------------
    # Export to csv
    temps_df4.to_csv(_output_path, index=False)
