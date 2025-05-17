# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export PER (Primary Energy Renewable) Data CSV files from the PHPP Main DataFrame"""

import pathlib

import pandas as pd

from honeybee_ph_plus_rhino.phpp.bt_web._variants_data_schema import VARIANTS


def get_per_as_df(
    _df_main: pd.DataFrame,
) -> pd.DataFrame:
    """Return the building's CO2-equiv data in a DataFrame

    Datatype	            Units	As-Drawn	Improve Windows	Improve ERV	Improve Insulation
    PER
    Heating	                kWh 	16286.79025	1430.906468	676.5609175	494.9069071	463.7467669
    Cooling	                kWh 	2380.885426	1657.507446	1466.63343	1426.324006	1418.086504
    DHW	                    kWh 	5622.978259	1242.170419	1238.788739	1238.47162	1238.128901
    Dishwashing	            kWh 	127.0511193	127.0511193	127.0511193	127.0511193	127.0511193
    Clothes Washing	        kWh 	73.314782	73.314782	73.314782	73.314782	73.314782
    Clothes Drying	        kWh 	345.3406855	345.3406855	345.3406855	345.3406855	345.3406855
    Refrigerator	        kWh 	556.625	556.625	556.625	556.625	556.625
    Cooking	                kWh 	452.2800048	452.2800048	452.2800048	452.2800048	452.2800048
    PHI Lighting	        kWh 	218.8311575	218.8311575	218.8311575	218.8311575	218.8311575
    PHI Consumer Elec.	    kWh 	688.8250343	688.8250343	688.8250343	688.8250343	688.8250343
    PHI Small Appliances	kWh 	76.83563061	76.83563061	76.83563061	76.83563061	76.83563061
    Phius Int. Lighting	    kWh     0	        0	        0	0	0
    Phius Ext. Lighting	    kWh 	0	        0	        0	0	0
    Phius MEL	            kWh 	0	        0	        0	0	0
    Aux Elec	            kWh 	897.254343	725.1749736	638.1539768	638.1539768	638.1539768
    Solar PV	            kWh 	0	        0	        0	0	0
    """

    start_row = VARIANTS.primary_energy_renewable.start_row()
    end_row = VARIANTS.primary_energy_renewable.end_row()
    df1 = _df_main.loc[start_row:end_row]

    # drop the 'CO2E' row
    df2 = df1.drop(df1[df1["Datatype"] == "PER"].index)

    df3 = df2.dropna(axis=0, how="all")
    df4 = df3.set_index("Datatype", drop=False)

    return df4


def create_csv_PER(
    _df_main: pd.DataFrame,
    _output_path: pathlib.Path,
) -> None:
    """Get the CO2 Dataframe and export to CSV file."""
    df_per = get_per_as_df(_df_main)
    df_per.to_csv(_output_path, index=False)
