# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Annual Heating Energy Demand CSV files for each Variant from the Main PHPP DataFrme"""

import pathlib

import pandas as pd

from honeybee_ph_plus_rhino.phpp.bt_web._variants_data_schema import VARIANTS


def clean_file_name(_filename: str) -> str:
    """Clean an input file name and remove disallowed characters ("/", etc..)"""
    return str(_filename).replace("/", "_").replace("\\", "_")


def create_csv_detailed_heating_demand(
    _df_main: pd.DataFrame, _cert_limits_abs: pd.DataFrame, _output_path: pathlib.Path
):
    """Creates the Annual Heating Demand data CSV files for each Variant based on the PHPP Climate DataFrame.

    Arguments:
    ----------
        * _df_climate (pd.DataFrame): The Main PHPP DataFrame to get the data from.
        * _cert_limits_abs (pd.DataFrame): The Certification Limits DataFrame.
        * _output_path (pathlib.Path): The full output file path for the CSV.

    Returns:
    --------
        * None
    """

    # Create the Detailed Heating Demand CSV
    demand_heat_losses_df = _df_main.loc[
        VARIANTS.heating_demand["Walls (AG)"]
        .row : VARIANTS.heating_demand["Ventilation"]
        .row
    ]
    demand_heat_gains_df = _df_main.loc[
        VARIANTS.heating_demand["Heating Demand"]
        .row : VARIANTS.heating_demand["Internal Gains"]
        .row
    ]

    # Get the variant column names (ignore the first two items 'Datatype' and 'Units')
    cols = demand_heat_losses_df.columns[2:].tolist()

    # Get the datatype and units values for both losses and gains
    dTtpes = pd.concat(
        [demand_heat_losses_df["Datatype"], demand_heat_gains_df["Datatype"]], sort=True
    )
    units = pd.concat(
        [demand_heat_losses_df["Units"], demand_heat_gains_df["Units"]], sort=True
    )

    # Create the 'Demand Limit' items in a way that matches the format of the main DF
    tempLimits = {}
    for colName in cols:
        index_temp = ["Datatype", "Units", "Losses", "Gains"]
        vals = [
            "Heating Demand Limit",
            "kWh",
            _cert_limits_abs.loc[VARIANTS.certification_limits["Heat Demand Limit"].row][
                colName
            ],
            _cert_limits_abs.loc[VARIANTS.certification_limits["Heat Demand Limit"].row][
                colName
            ],
        ]
        newSeries = pd.Series(vals, index=index_temp)
        tempLimits[colName] = newSeries

    # Create the main DF for outputting
    def create_new_DF(_colHead, _colName, _df):
        frame = {_colHead: _df[_colName]}
        r = pd.DataFrame(frame)
        return r

    losses = {}
    gains = {}
    for colName in cols:
        losses[colName] = create_new_DF("Losses", colName, demand_heat_losses_df)
        gains[colName] = create_new_DF("Gains", colName, demand_heat_gains_df)

    output = {}
    for k, v in losses.items():
        r1 = pd.concat([losses[k], gains[k]], sort=True)
        r2 = pd.concat([dTtpes, units, r1["Losses"], r1["Gains"]], axis=1)
        output[k] = r2.map(lambda x: 0 if pd.isna(x) else x)

    # Add the Demand Limits to the main DFs
    for k, v in output.items():
        output[k] = v._append(tempLimits[k], ignore_index=True)

    # Write out to CSV
    for k, v in output.items():
        new_filename = clean_file_name("{}_{}.csv".format(_output_path.stem, k))
        output_path = pathlib.Path(_output_path.parents[0], new_filename)
        v.to_csv(output_path, index=False)
