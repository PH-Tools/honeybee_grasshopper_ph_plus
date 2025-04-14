# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Variant Data Table CSV files from the Main PHPP DataFrme"""

import pathlib

import numpy as np
import pandas as pd

from honeybee_ph_plus_rhino.phpp.bt_web._variants_data_schema import VARIANTS

pd.options.mode.chained_assignment = None  # default='warn'


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
    ductLen_s1 = (
        sys_df2.loc[VARIANTS.systems["Cold Air Duct Length (ea)"].row][_variant_names]
        * 3.280839895
    )
    ductLen_s2 = pd.Series(
        ["Cold Air Duct Length (ea)", "ft"], index=["Datatype", "Units"]
    )
    ductLen_s3 = pd.concat([ductLen_s2, ductLen_s1])

    sys_df3 = sys_df2.copy(deep=True)
    sys_df3.loc[VARIANTS.systems["Cold Air Duct Length (ea)"].row] = ductLen_s3

    # Insulation
    ductInsul_s1 = (
        sys_df3.loc[VARIANTS.systems["Cold Air Duct Insulation Thickness"].row][
            _variant_names
        ]
        * 0.039370079
    )
    ductInsul_s2 = pd.Series(
        ["Cold Air Duct Insulation Thickness", "inches"], index=["Datatype", "Units"]
    )
    ductInsul_s3 = pd.concat([ductInsul_s2, ductInsul_s1])

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
    variantsData_df = pd.concat(
        [brk_env, env_results_df2, brk_sys, sys_df5, brk_results, key_results_df]
    )
    variantsData_df2 = variantsData_df.fillna("")

    # --------------------------------------------------------------------------
    # Export to csv
    variantsData_df2.to_csv(_file_path, index=False)
