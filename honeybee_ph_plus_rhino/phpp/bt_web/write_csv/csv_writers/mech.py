# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Mechanical System Data CSV files from the PHPP Ventilation DataFrme"""

import pathlib

import numpy as np
import pandas as pd


def create_csv_fresh_air_flowrates(
    _df_vent: pd.DataFrame, _output_path: pathlib.Path
) -> None:
    """Create the Room-by-Room Fresh air flow rate CSV data file.

    Arguments:
    ----------
        * _df_vent (pd.DataFrame): The PHPP Ventilation DataFrame.
        * _output_path (pathlib.Path): The CSV output file path.

    Returns:
    --------
        * None
    """

    # -- The Actual column headings
    colNames = [
        "Amount",
        "Room name",
        "Allocation to Vent Unit",
        "Area",
        "Clear height",
        "Room Vol.",
        "V_Supply",
        "V_Extract",
        "V_Transmission",
        "Room ACH",
        "Utilisation h/d",
        "Utilisation d/wk",
        "Holidays d/yr",
        "Reduction Factor 1",
        "Operation Factor 1",
        "Reduction Factor 2",
        "Operation Factor 2",
        "Reduction Factor 3",
        "Operation Factor 3",
    ]
    rm_vent_df1 = _df_vent.reset_index(drop=True)
    rm_vent_df1.columns = colNames

    # -- Drop any rows with no room name
    rm_vent_df2 = rm_vent_df1.dropna(axis=0, subset=["Room name"])

    # Calc the flow rates for high, med and low for each room
    unitFactor_flow = 0.588577779  # m3/h---> cfm
    unitFactor_vol = 35.31466672  # m3 --> ft3
    unitFactor_area = 10.76391042  # m3 --> ft3
    unitFactor_length = 3.280839895  # m --> ft

    flowRate_Sup_High = (
        rm_vent_df2["V_Supply"].values
        * rm_vent_df2["Reduction Factor 1"].values
        * unitFactor_flow
    )
    flowRate_Eta_High = (
        rm_vent_df2["V_Extract"].values
        * rm_vent_df2["Reduction Factor 1"].values
        * unitFactor_flow
    )
    flowRate_Trans_High = (
        rm_vent_df2["V_Transmission"].values
        * rm_vent_df2["Reduction Factor 1"].values
        * unitFactor_flow
    )
    cols = ["V_Sup_High", "V_Eta_High", "V_Trans_High"]
    flows_high_df = pd.DataFrame(
        [flowRate_Sup_High, flowRate_Eta_High, flowRate_Trans_High], index=cols
    ).T

    flowRate_Sup_Med = (
        rm_vent_df2["V_Supply"].values
        * rm_vent_df2["Reduction Factor 2"].values
        * unitFactor_flow
    )
    flowRate_Eta_Med = (
        rm_vent_df2["V_Extract"].values
        * rm_vent_df2["Reduction Factor 2"].values
        * unitFactor_flow
    )
    flowRate_Trans_Med = (
        rm_vent_df2["V_Transmission"].values
        * rm_vent_df2["Reduction Factor 2"].values
        * unitFactor_flow
    )
    cols = ["V_Sup_Med", "V_Eta_Med", "V_Trans_Med"]
    flows_med_df = pd.DataFrame(
        [flowRate_Sup_Med, flowRate_Eta_Med, flowRate_Trans_Med], index=cols
    ).T

    flowRate_Sup_Low = (
        rm_vent_df2["V_Supply"].values
        * rm_vent_df2["Reduction Factor 3"].values
        * unitFactor_flow
    )
    flowRate_Eta_Low = (
        rm_vent_df2["V_Extract"].values
        * rm_vent_df2["Reduction Factor 3"].values
        * unitFactor_flow
    )
    flowRate_Trans_Low = (
        rm_vent_df2["V_Transmission"].values
        * rm_vent_df2["Reduction Factor 3"].values
        * unitFactor_flow
    )
    cols = ["V_Sup_Low", "V_Eta_Low", "V_Trans_Low"]
    flows_low_df = pd.DataFrame(
        [flowRate_Sup_Low, flowRate_Eta_Low, flowRate_Trans_Low], index=cols
    ).T

    # Create the air flows DF
    roomAirFlows = pd.concat(
        [flows_high_df, flows_med_df, flows_low_df], axis=1, sort=False
    )

    # Convert the units for vol, areas...
    roomNames = pd.DataFrame(rm_vent_df2["Room name"].values, columns=["Room Name"])
    roomVol = pd.DataFrame(
        rm_vent_df2["Room Vol."].values * unitFactor_vol, columns=["Room Vol. (ft3)"]
    )
    roomArea = pd.DataFrame(
        rm_vent_df2["Area"].values * unitFactor_area, columns=["Room Area (ft2)"]
    )
    roomHeight = pd.DataFrame(
        rm_vent_df2["Clear height"].values * unitFactor_length,
        columns=["Room Height (ft)"],
    )

    rm_vent_df5 = pd.concat(
        [roomNames, roomVol, roomArea, roomHeight, roomAirFlows], axis=1, sort=True
    )
    rm_vent_df6 = rm_vent_df5.replace(to_replace=0, value="-")

    # Sort by Room Number and Name
    rm_vent_df7 = rm_vent_df6.sort_values(by=["Room Name"])

    # Calc the Totals for each column
    rm_vent_df8 = rm_vent_df7.map(lambda x: np.nan if x == "-" else x)
    columnNames = list(rm_vent_df8.columns.values)

    totals = rm_vent_df8[columnNames].sum()
    totals["Room Name"] = "Totals"
    totals["Room Height (ft)"] = " "
    newSeries = pd.Series(totals)
    newSeries.name = "Totals"

    # Add in the totals to the main DF
    rm_vent_df9 = rm_vent_df7._append(newSeries)

    # Export to csv
    rm_vent_df9.to_csv(_output_path, index=False)
