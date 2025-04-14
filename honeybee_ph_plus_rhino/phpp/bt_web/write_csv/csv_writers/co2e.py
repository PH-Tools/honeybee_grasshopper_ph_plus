# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export CO2e Data CSV files from the PHPP Main DataFrame"""

import pathlib

import pandas as pd

from honeybee_ph_plus_rhino.phpp.bt_web._variants_data_schema import VARIANTS


def get_co2e_as_df(
    _df_main: pd.DataFrame,
) -> pd.DataFrame:
    """Return the building's CO2-equiv data in a DataFrame

                            Datatype	            Units	Code Minimum	As-Drawn	Improve Windows	Improve ERV	Improve Insulation
    Datatype
    Heating	                Heating	                kgCO2e	18894.013298	11304.857062	7352.375323	6497.584214	3725.545278
    Cooling	                Cooling	                kgCO2e	413.618352	454.330187	807.137649	608.668385	690.842606
    DHW	                    DHW	                    kgCO2e	3114.843722	3059.251984	2986.819659	2974.217884	2941.724216
    Dishwashing	            Dishwashing	            kgCO2e	178.75	178.75	178.75	178.75	178.75
    Clothes Washing	        Clothes Washing	        kgCO2e	47.025	47.025	47.025	47.025	47.025
    Clothes Drying	        Clothes Drying	        kgCO2e	972.5625	972.5625	972.5625	972.5625	972.5625
    Refrigerator	        Refrigerator	        kgCO2e	445.3	445.3	445.3	445.3	445.3
    Cooking	                Cooking	                kgCO2e	625	625	625	625	625
    PHI Lighting	        PHI Lighting	        kgCO2e	0	0	0	0	0
    PHI Consumer Elec.	    PHI Consumer Elec.	    kgCO2e	0	0	0	0	0
    PHI Small Appliances	PHI Small Appliances	kgCO2e	0	0	0	0	0
    Phius MEL	            Phius MEL	            kgCO2e	6991.1	6991.1	6991.1	6991.1	6991.1
    Phius Int Lighting	    Phius Int Lighting	    kgCO2e	2417.5	2417.5	2417.5	2417.5	2417.5
    Phius Ext Lighting	    Phius Ext Lighting	    kgCO2e	130.8	130.8	130.8	130.8	130.8
    Aux Elec	            Aux Elec	            kgCO2e	0	0	0	0	0
    IPCC Limit               IPCC Limit             kgCO2e  0   0   0   0   0
    """

    start_row = VARIANTS.co2e.start_row()
    end_row = VARIANTS.co2e.end_row()
    df1 = _df_main.loc[start_row:end_row]

    # drop the 'CO2E' row
    df2 = df1.drop(df1[df1["Datatype"] == "CO2E"].index)

    df3 = df2.dropna(axis=0, how="all")
    df4 = df3.set_index("Datatype", drop=False)

    return df4


def create_csv_CO2E(
    _df_main: pd.DataFrame,
    _output_path: pathlib.Path,
) -> None:
    """Get the CO2 Dataframe and export to CSV file."""
    df_co2e = get_co2e_as_df(_df_main)
    df_co2e.to_csv(_output_path, index=False)
