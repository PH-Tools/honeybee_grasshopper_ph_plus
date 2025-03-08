# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Site Energy Data CSV files from the PHPP Main DataFrame"""


import pathlib

import pandas as pd


def get_site_energy_as_df(_df_main: pd.DataFrame) -> pd.DataFrame:
    """Return the building's site-energy consumption data in a DataFrame
                            Datatype	            Units	Code Minimum	As-Drawn	Improve Windows	Improve ERV	Improve Insulation
    Datatype
    Heating	                Heating	                kWh	18894.013298	11304.857062	7352.375323	6497.584214	3725.545278
    Cooling	                Cooling	                kWh	413.618352	454.330187	807.137649	608.668385	690.842606
    DHW	                    DHW	                    kWh	3114.843722	3059.251984	2986.819659	2974.217884	2941.724216
    Dishwashing	            Dishwashing	            kWh	178.75	178.75	178.75	178.75	178.75
    Clothes Washing	        Clothes Washing	        kWh	47.025	47.025	47.025	47.025	47.025
    Clothes Drying	        Clothes Drying	        kWh	972.5625	972.5625	972.5625	972.5625	972.5625
    Refrigerator	        Refrigerator	        kWh	445.3	445.3	445.3	445.3	445.3
    Cooking	                Cooking	                kWh	625	625	625	625	625
    PHI Lighting	        PHI Lighting	        kWh	0	0	0	0	0
    PHI Consumer Elec.	    PHI Consumer Elec.	    kWh	0	0	0	0	0
    PHI Small Appliances	PHI Small Appliances	kWh	0	0	0	0	0
    Phius MEL	            Phius MEL	            kWh	6991.1	6991.1	6991.1	6991.1	6991.1
    Phius Int Lighting	    Phius Int Lighting	    kWh	2417.5	2417.5	2417.5	2417.5	2417.5
    Phius Ext Lighting	    Phius Ext Lighting	    kWh	130.8	130.8	130.8	130.8	130.8
    Aux Elec	            Aux Elec	            kWh	0	0	0	0	0
    Solar PV                Solar PV                kWh 0   0   0   0   0
    """
    df1 = _df_main.loc[375:390]
    df2 = df1.dropna(axis=0, how="all")
    df3 = df2.set_index("Datatype", drop=False)

    return df3


def create_csv_SiteEnergy(
    _df_main: pd.DataFrame,
    _output_path: pathlib.Path,
) -> None:
    df_site_energy = get_site_energy_as_df(_df_main)

    # -- Export to csv
    df_site_energy.to_csv(_output_path, index=False)
