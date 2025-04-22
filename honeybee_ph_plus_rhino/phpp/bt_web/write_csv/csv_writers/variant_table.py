# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Variant Data Table CSV files from the Main PHPP DataFrme"""

import pathlib

import numpy as np
import pandas as pd

from honeybee_ph_plus_rhino.phpp.bt_web._variants_data_schema import VARIANTS

pd.options.mode.chained_assignment = None  # default='warn'


def split_table_into_sections(_variants_data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    _variants_data = 
                                            Datatype  ...            EnerPHit (by Component)
        break                               ENVELOPE  ...                                   
        329                                     Wall  ...                               15.0
        330                        Wall (Crawlspace)  ...                                5.0
        331                                     Roof  ...                               38.0
        332                       Floor (Crawlspace)  ...                               22.0
        333                       Floor (Bay Window)  ...                               22.0
        339    Thermal Bridge Allowance (% increase)  ...                                0.2
        340        Volumetric Air Leakage Rate (n50)  ...                                1.0
        341          Envelope Air Leakage Rate (q50)  ...                           0.030093
        342               Window U-value (Installed)  ...                           0.232476
        343                              Window SHGC  ...                               0.23
        break                                SYSTEMS  ...                                   
        0                         Ventilation System  ...  1-Balanced PH ventilation with HR
        1             Ventilation Unit HR Efficiency  ...                           0.727491
        2             Ventilation Unit ER Efficiency  ...                               0.68
        3                       System HR Efficiency  ...                           0.727491
        4                  Cold Air Duct Length (ea)  ...                          16.404199
        5         Cold Air Duct Insulation Thickness  ...                           2.047244
        6                             Heating System  ...                       Heat pump(s)
        7                             Cooling System  ...                    Elec. Heat Pump
        8                                 DHW System  ...                       Heat pump(s)
        9                                             ...                                   
        10                                            ...                                   
        11                                            ...                                   
        break                                RESULTS  ...                                   
        0                   Certification Compliant?  ...                                 No
        1                       Total Primary Energy  ...                       21846.612257
        2                          Total Site Energy  ...                        8402.543176
        3                                Heat Demand  ...                        1140.901369
        4                                Heat Demand  ...                           9.732269
        5                             Cooling Demand  ...                          1608.3779
        6                       Total Cooling Demand  ...                              13.72
        7                                 PEAK LOADS  ...                                   
        8                             Peak Heat Load  ...                        7075.533373
        9                 Peak Sensible Cooling Load  ...                        5814.733993
        10                  Peak Latent Cooling Load  ...                         975.231978
        11                                            ...                                   
        [37 rows x 7 columns]
    """

    # Look for the 'break' in the index, use that to delineate the 'section' of the DataFrame
    sections: dict[str, pd.DataFrame] = {}
    current_section = ""
    for index, row in _variants_data.iterrows():
        if row["Datatype"] == "":
            continue
        
        if index == "break":
            current_section = str(row["Datatype"]).upper().strip().replace(" ", "_")
            if current_section not in sections:
                sections[current_section] = pd.DataFrame()
        else:
            # --  If the row is a header, skip it
            if row["Datatype"].isupper():
                continue
            
            # --  Add the row to the current section
            sections[current_section] = pd.concat(
                [sections[current_section], row.to_frame().T], ignore_index=True
            )
            sections[current_section].reset_index(drop=True, inplace=True)

    return sections

def clean_variant_table_data(_df_main: pd.DataFrame, _variant_names: pd.Series) -> pd.DataFrame:
    # Certification Yes/No
    cert_df1 = _df_main.loc[
        VARIANTS.certification_compliant["Certification Compliant?"].row
    ]

    # Energy and Load values
    # --------------------------------------------------------------------------
    # Total Primary Energy
    pe_start_row = VARIANTS.primary_energy.start_row()
    pe_end_row = VARIANTS.primary_energy.end_row()
    pe_df1 = _df_main.loc[pe_start_row:pe_end_row]
    pe_df2 = pe_df1[_variant_names].sum()
    pe_df3 = pd.Series(["Total Primary Energy", "kWh/yr"], index=["Datatype", "Units"])
    pe_df4 = pd.concat([pe_df3, pe_df2])

    # Total Site Energy
    se_start_row = VARIANTS.site_energy.start_row()
    se_end_row = VARIANTS.site_energy.end_row()
    se_df1 = _df_main.loc[se_start_row:se_end_row]
    se_df2 = se_df1[_variant_names].sum()
    se_df3 = pd.Series(["Total Site Energy", "kWh/yr"], index=["Datatype", "Units"])
    se_df4 = pd.concat([se_df3, se_df2])

    # TFA
    tfa_df = _df_main.loc[VARIANTS.geometry["TFA"].row]

    # Heating and Cooling Demand
    hd_df1 = _df_main.loc[VARIANTS.certification_results["Heat Demand"].row]
    hd_df2 = pd.concat([tfa_df, hd_df1], axis=1).T[_variant_names].prod()
    hd_df3 = pd.Series(["Heat Demand", "kWh/yr"], index=["Datatype", "Units"])
    hd_df4 = pd.concat([hd_df3, hd_df2])

    cd_df1 = _df_main.loc[VARIANTS.certification_results["Total Cooling Demand"].row]
    cd_df2 = pd.concat([tfa_df, cd_df1], axis=1).T[_variant_names].prod()
    cd_df3 = pd.Series(["Cooling Demand", "kWh/yr"], index=["Datatype", "Units"])
    cd_df4 = pd.concat([cd_df3, cd_df2])

    demand_results_df1 = pd.concat(
        [cert_df1, pe_df4, se_df4, hd_df4, hd_df1, cd_df4, cd_df1], axis=1
    )
    demand_results_df2 = demand_results_df1.T

    # Peak Loads
    ld_start_row = VARIANTS.peak_loads.start_row()
    ld_end_row = VARIANTS.peak_loads.end_row()
    ld_df1 = _df_main.loc[ld_start_row:ld_end_row]

    # Combine it all together
    key_results_df = pd.concat([demand_results_df2, ld_df1])
    key_results_df = key_results_df.reset_index(drop=True)

    # Envelope R-Values and Airtightness
    # --------------------------------------------------------------------------
    env_start_row = VARIANTS.envelope.start_row()
    env_end_row = VARIANTS.envelope.end_row()
    env_df1 = _df_main.loc[env_start_row:env_end_row]
    env_df1a = pd.DataFrame(env_df1)
    new_datatype_column = (
        env_df1["Datatype"].str.replace("_", " ").str.replace("Generic ", "")
    )
    env_df1a["Datatype"] = new_datatype_column

    # Convert in the envelope leakage rate
    q50_ip1 = (
        env_df1.loc[VARIANTS.envelope["Envelope Air Leakage Rate (q50)"].row][
            _variant_names
        ]
        * 0.054680665
    )
    q50_ip2 = pd.Series(
        ["Envelope Air Leakage Rate (q50)", "cfm/ft2"], index=["Datatype", "Units"]
    )
    q50_ip3 = pd.concat([q50_ip2, q50_ip1])
    env_df1.loc[VARIANTS.envelope["Envelope Air Leakage Rate (q50)"].row] = q50_ip3
    env_results_df2 = env_df1.dropna(how="any")

    # Systems
    # --------------------------------------------------------------------------
    # Mech System info
    sys_start_row = VARIANTS.systems.start_row()
    sys_end_row = VARIANTS.systems.end_row()
    sys_df1 = _df_main.loc[sys_start_row:sys_end_row]

    # drop the 'SYSTEMS' row
    sys_df2 = sys_df1.drop(sys_df1[sys_df1["Datatype"] == "SYSTEMS"].index)

    # Re-set the units for duct
    duct_len_s1 = (
        sys_df2.loc[VARIANTS.systems["Cold Air Duct Length (ea)"].row][_variant_names]
        * 3.280839895
    )
    duct_len_s2 = pd.Series(
        ["Cold Air Duct Length (ea)", "ft"], index=["Datatype", "Units"]
    )
    duct_len_s3 = pd.concat([duct_len_s2, duct_len_s1])

    sys_df3 = sys_df2.copy(deep=True)
    sys_df3.loc[VARIANTS.systems["Cold Air Duct Length (ea)"].row] = duct_len_s3

    # Insulation
    duct_insul_s1 = (
        sys_df3.loc[VARIANTS.systems["Cold Air Duct Insulation Thickness"].row][
            _variant_names
        ]
        * 0.039370079
    )
    ductInsul_s2 = pd.Series(
        ["Cold Air Duct Insulation Thickness", "inches"], index=["Datatype", "Units"]
    )
    ductInsul_s3 = pd.concat([ductInsul_s2, duct_insul_s1])

    sys_df4 = sys_df3.copy(deep=True)
    sys_df4.loc[VARIANTS.systems["Cold Air Duct Insulation Thickness"].row] = ductInsul_s3
    sys_df5 = sys_df4.reset_index(drop=True)

    # Add the breaks
    brk_env = pd.DataFrame(np.nan, index=["break"], columns=_df_main.columns.tolist())
    brk_env["Datatype"] = "ENVELOPE"

    brk_sys = pd.DataFrame(np.nan, index=["break"], columns=_df_main.columns.tolist())
    brk_sys["Datatype"] = "SYSTEMS"

    brk_results = pd.DataFrame(np.nan, index=["break"], columns=_df_main.columns.tolist())
    brk_results["Datatype"] = "RESULTS"

    # --------------------------------------------------------------------------
    # -- Build the final df in the right order
    variants_data_df1 = pd.concat(
        [brk_env, env_results_df2, brk_sys, sys_df5, brk_results, key_results_df]
    )
    variants_data_df2 = variants_data_df1.fillna("")
    return variants_data_df2

def create_csv_variant_table(
    _df_main: pd.DataFrame,
    _variant_names: pd.Series,
    _file_path: pathlib.Path,
) -> None:
    """Create the comprehensive Variant Data Table with bits from all over the place.

    Arguments:
    ----------
        * _df_vent (pd.DataFrame): The PHPP Ventilation DataFrame.
        * _variant_names (pd.Series): A Series with all the Variant Names.
        * _output_path (pathlib.Path): The CSV output file path.

    Returns:
    --------
        * None
    """

    # --------------------------------------------------------------------------
    # Export the full table to csv
    variants_data_complete = clean_variant_table_data(_df_main,_variant_names)
    variants_data_complete.to_csv(_file_path, index=False)

    # --------------------------------------------------------------------------
    # Break up the Table into 'sections'
    for section_name, section_df in split_table_into_sections(variants_data_complete).items():
        section_file_path = _file_path.parent / f"{_file_path.stem}_{section_name}.csv"
        section_df.to_csv(section_file_path, index=False)