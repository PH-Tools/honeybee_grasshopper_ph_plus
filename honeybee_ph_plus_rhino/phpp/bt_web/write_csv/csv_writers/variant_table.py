# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Variant Data Table CSV files from the Main PHPP DataFrme"""

import pathlib

import numpy as np
import pandas as pd

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
    #  START = 202 # PHPP-9
    START = 270  # PHPP-10

    # Certification?
    cert_df1 = _df_main.loc[190 + START]

    # Energy and Load values
    # --------------------------------------------------------------------------
    # Total Primary Energy
    pe_df1 = _df_main.loc[122 + START : 136 + START]
    pe_df2 = pe_df1[_variant_names].sum()
    pe_df3 = pd.Series(["Total Primary Energy", "kWh/yr"], index=["Datatype", "Units"])
    pe_df4 = pe_df3._append(pe_df2)

    # Total Primary Energy Renewable
    per_df1 = _df_main.loc[138 + START : 153 + START]
    per_df2 = per_df1[_variant_names].sum()
    per_df3 = pd.Series(
        ["Total Primary Energy Renewable", "kWh/yr"], index=["Datatype", "Units"]
    )
    per_df4 = per_df3._append(per_df2)

    # Total Site Energy
    se_df1 = _df_main.loc[105 + START : 119 + START]
    se_df2 = se_df1[_variant_names].sum()
    se_df3 = pd.Series(["Total Site Energy", "kWh/yr"], index=["Datatype", "Units"])
    se_df4 = se_df3._append(se_df2)

    # TFA
    tfa_df = _df_main.loc[210]

    # Heating and Cooling Demand
    hd_df1 = _df_main.loc[156 + START]
    hd_df2 = pd.concat([tfa_df, hd_df1], axis=1).T[_variant_names].prod()
    hd_df3 = pd.Series(["Heat Demand", "kWh/yr"], index=["Datatype", "Units"])
    hd_df4 = hd_df3._append(hd_df2)

    cd_df1 = _df_main.loc[159 + START]
    cd_df2 = pd.concat([tfa_df, cd_df1], axis=1).T[_variant_names].prod()
    cd_df3 = pd.Series(["Cooling Demand", "kWh/yr"], index=["Datatype", "Units"])
    cd_df4 = cd_df3._append(cd_df2)

    demand_results_df1 = pd.concat(
        [cert_df1, pe_df4, per_df4, se_df4, hd_df4, hd_df1, cd_df4, cd_df1], axis=1
    )
    demand_results_df2 = demand_results_df1.T

    # Peak Loads
    ld_df1 = _df_main.loc[194 + START : 196 + START]

    # Combine it all together
    key_results_df = demand_results_df2._append(ld_df1).reset_index(drop=True)

    # Envelope R-Values and Airtightness
    # --------------------------------------------------------------------------
    env_df1 = _df_main.loc[20 + START : 32 + START]
    env_df1a = pd.DataFrame(env_df1)
    new_datatype_column = (
        env_df1["Datatype"].str.replace("_", " ").str.replace("Generic ", "")
    )
    env_df1a["Datatype"] = new_datatype_column

    # Convert in the envelope leakage rate
    q50_ip1 = env_df1.loc[START + 32][_variant_names] * 0.054680665
    q50_ip2 = pd.Series(
        ["Envelope Air Leakage Rate (q50)", "cfm/ft2"], index=["Datatype", "Units"]
    )
    q50_ip3 = q50_ip2._append(q50_ip1)
    env_df1.loc[START + 32] = q50_ip3
    env_results_df2 = env_df1.dropna(how="any")

    # Systems
    # --------------------------------------------------------------------------
    # Mech System info
    sys_df1 = _df_main.loc[35 + START : 43 + START]

    # Re-set the units for duct
    ductLen_s1 = sys_df1.loc[309][_variant_names] * 3.280839895
    ductLen_s2 = pd.Series(
        ["Cold Air Duct Length (ea)", "ft"], index=["Datatype", "Units"]
    )
    ductLen_s3 = ductLen_s2._append(ductLen_s1)

    sys_df2 = sys_df1.copy(deep=True)
    sys_df2.loc[START + 39] = ductLen_s3

    # Insulation
    ductInsul_s1 = sys_df2.loc[START + 40][_variant_names] * 0.039370079
    ductInsul_s2 = pd.Series(
        ["Cold Air Duct Insulation Thickness", "inches"], index=["Datatype", "Units"]
    )
    ductInsul_s3 = ductInsul_s2._append(ductInsul_s1)

    sys_df3 = sys_df2.copy(deep=True)
    sys_df3.loc[START + 40] = ductInsul_s3
    sys_df4 = sys_df3.reset_index(drop=True)

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
        [brk_env, env_results_df2, brk_sys, sys_df4, brk_results, key_results_df]
    )
    variantsData_df2 = variantsData_df.fillna("")

    # --------------------------------------------------------------------------
    # Export to csv
    variantsData_df2.to_csv(_file_path, index=False)
