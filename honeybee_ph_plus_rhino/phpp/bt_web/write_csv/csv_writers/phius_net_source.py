# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Mechanical System Data CSV files from the Main PHPP DataFrame"""

import pathlib

import pandas as pd

from honeybee_ph_plus_rhino.phpp.bt_web._variants_data_schema import VARIANTS


def create_csv_Phius_net_source_energy(
    _df_main: pd.DataFrame, _cert_limits_abs: pd.DataFrame, _output_path: pathlib.Path
) -> None:
    """Outputs a formatted .CSV with the Net-Primary-Energy information as per Phius.

    Arguments:
    ----------
        * _df_main (pd.DataFrame): The Main Excel DF with all the Data.
        * _cert_limits_abs (pd.DataFrame): The PHPP Certification Limits DataFrame.
        * _output_path (pathlib.Path): The full path where to save out the file.

    Returns:
    --------
        * None
    """

    # Create the PE data csv
    start_row = VARIANTS.primary_energy.start_row()
    end_row = VARIANTS.primary_energy.end_row()
    PE_df1 = _df_main.loc[start_row:end_row]
    PE_df2 = reduce_energy_by_solar(_df_main, PE_df1)

    # -- Little bit of cleanup
    PE_df3 = PE_df2.dropna(axis=0, how="all")

    # -- add in the Target Row
    targets = _cert_limits_abs.loc[
        VARIANTS.certification_limits["PHIUS Net Source Energy Limit"].row
    ]
    if isinstance(targets, pd.Series):
        targets = targets.to_frame().T
    PE_df4 = pd.concat([PE_df3, targets], ignore_index=False)

    # -- Output the CSV
    PE_df4.to_csv(_output_path, index=False)


def reduce_energy_by_solar(_df_main: pd.DataFrame, _pe_df: pd.DataFrame) -> pd.DataFrame:
    """Reduces Energy consumption by %, based on Variant's Solar PV

    Arguments:
    ----------
        * _df_main (pd.DataFrame): The Main PHPP DataFrame with all the Data.
        * _pe_df (pd.DataFrame): The 'PE' dataframe.

    Returns:
    --------
        * (pd.DataFrame) A new DF with all the consumption values reduced by some
            amount, based on the Solar PV.

    """

    solar_row = VARIANTS.primary_energy["Solar PV"].row
    PE_solar_df = _df_main.loc[solar_row:solar_row]
    PE_solar_data_df = PE_solar_df.iloc[:, -5:]
    PE_solar_data_df = PE_solar_data_df.apply(pd.to_numeric)
    PE_solar_data_df = PE_solar_data_df * 1.8

    # --- Add 'totals' row to each column
    """ 
    _pe_df = 
        0                Datatype Units  ...    PH Windows Passive House
        436                    PE   NaN  ...           NaN           NaN
        437               Heating  kWh   ...  21259.503681  16103.553119
        438               Cooling  kWh   ...   6129.219363   5729.921122
        439                   DHW  kWh   ...   9019.073447   8970.247848
        440           Dishwashing  kWh   ...    312.405472    312.405472
        441       Clothes Washing  kWh   ...    178.866377    178.866377
        442        Clothes Drying  kWh   ...     851.54578     851.54578
        443          Refrigerator  kWh   ...       1157.78       1157.78
        444               Cooking  kWh   ...   1123.951978   1123.951978
        445          PHI Lighting  kWh   ...    543.812925    543.812925
        446    PHI Consumer Elec.  kWh   ...   1674.917838   1674.917838
        447  PHI Small Appliances  kWh   ...    176.952237    176.952237
        448   Phius Int. Lighting  kWh   ...           0.0           0.0
        449   Phius Ext. Lighting  kWh   ...           0.0           0.0
        450             Phius MEL  kWh   ...           0.0           0.0
        451              Aux Elec  kWh   ...   2854.750771   2854.750771
        452              Solar PV  kWh   ...           0.0           0.0
        453                   NaN   NaN  ...           NaN           NaN
    """
    # remove any row where 'Datatype' is NaN
    pe_df1 = _pe_df.dropna(subset=["Datatype"])

    # drop the 'PE' row
    pe_df2 = pe_df1.drop(pe_df1[pe_df1["Datatype"] == "PE"].index)

    # -- Sum up the totals for each column
    totals = pe_df2.sum(axis=0, numeric_only=False)
    totals["Datatype"] = "Totals"
    totals["Units"] = None
    """
    totals = 
        Datatype                Totals
        Units                     None
        Code Minimum       74307.85775
        Insulation        68476.059319
        Airtight + ERV    54316.624202
        PH Windows        45282.779867
        Passive House     39678.705466
        dtype: object
    """

    # -- Add the totals row to the end of the DataFrame
    PE_df3 = pd.concat([pe_df2, totals.to_frame().T], ignore_index=True)

    # --- Separate out the 'data' columns and the 'datatype' columns
    PE_datatype_cols_df = PE_df3.iloc[:, :2]
    PE_df_data = PE_df3.iloc[:, -5:]
    PE_df_data = PE_df_data.apply(pd.to_numeric).fillna(0)

    totals_data = PE_df_data.iloc[-1]

    # -- Compute the % of total for each of the consumption areas
    pe_percentage_values_df = pd.DataFrame(PE_df_data.values / totals_data.values)
    pe_percentage_values_df.columns = PE_df_data.columns

    # -- Compute a reduction from solar for each of the consumption areas based on %
    reduction_from_solar_df = pe_percentage_values_df.mul(
        PE_solar_data_df.iloc[-1]
    ).fillna(0)
    PE_NET_data_df = PE_df_data  # - reduction_from_solar_df

    # -- Recombine the final DF
    PE_NET_df = pd.concat([PE_datatype_cols_df, PE_NET_data_df], axis=1)
    PE_NET_df.drop(PE_NET_df.tail(1).index, inplace=True)

    return PE_NET_df
