# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Building-Data Tabel CSV file from the Main PHPP DataFrme"""

import pandas as pd

pd.options.mode.chained_assignment = None  # default='warn'
import pathlib


def create_csv_bldg_basic_data_table(
    _df_main: pd.DataFrame, _file_path: pathlib.Path
) -> None:
    """Creates the Building Data Table CSV file based on the PHPP DataFrame.

    Arguments:
    ----------
        * _df_main (pd.DataFrame): The Main PHPP DataFrame to get the data from.
        * _output_path (pathlib.Path): The full output file path for the CSV.

    Returns:
    --------
        * None
    """

    # Building Data Basics from Main PHPP DataFrame
    bldg_df = _df_main.loc[279:287]

    # --------------------------------------------------------------------------
    # TFA
    tfa_1 = bldg_df.loc[279]
    tfa_2 = []
    for each in tfa_1:
        try:
            tfa_2.append(each * 10.76391042)
        except:
            if each == "m2":
                tfa_2.append("ft2")
            elif each == "TFA":
                tfa_2.append("Floor Area*")
            else:
                tfa_2.append(each)
    tfa_3 = pd.Series(tfa_2, index=[bldg_df.columns])

    # --------------------------------------------------------------------------
    # Vn50 Volume
    vol_1 = bldg_df.loc[281]
    vol_2 = []
    for each in vol_1:
        try:
            vol_2.append(each * 35.31466672)
        except:
            if each == "m3":
                vol_2.append("ft3")
            elif each == "Vn50":
                vol_2.append("Interior Net Volume")
            else:
                vol_2.append(each)
    vol_3 = pd.Series(vol_2, index=[bldg_df.columns])

    # --------------------------------------------------------------------------
    # Total Exterior Surface
    extSrfc_1 = bldg_df.loc[282]
    extSrfc_2 = []
    for each in extSrfc_1:
        try:
            extSrfc_2.append(each * 10.76391042)
        except:
            if each == "m2":
                extSrfc_2.append("ft2")
            else:
                extSrfc_2.append(each)
    extSrfc_3 = pd.Series(extSrfc_2, index=[bldg_df.columns])

    # --------------------------------------------------------------------------
    # Srfc / Vol Ratio
    srfc_vol_ratio = []
    for i, each in enumerate(extSrfc_2):
        try:
            srfc_vol_ratio.append(each / tfa_2[i])
        except:
            if each == "ft2":
                srfc_vol_ratio.append("-")
            else:
                srfc_vol_ratio.append("Ext. Surface Area / Floor Area Ratio")
    srfc_vol_ratio2 = pd.Series(srfc_vol_ratio, index=[bldg_df.columns])

    # --------------------------------------------------------------------------
    # A/V Ratio
    av_ratio = []
    for i, each in enumerate(tfa_2):
        try:
            av_ratio.append(each / vol_2[i])
        except:
            if each == "ft2":
                av_ratio.append("-")
            else:
                av_ratio.append("Floor Area / Volume Ratio")
    av_ratio2 = pd.Series(av_ratio, index=[bldg_df.columns])

    # --------------------------------------------------------------------------
    # Window Areas by Orientation
    windowAeas_df = bldg_df.loc[283:287].T
    temp = []
    for colName in windowAeas_df:
        orientation = []
        for item in windowAeas_df[colName].values:
            try:
                orientation.append(item * 10.76391042)
            except:
                if item == "m2":
                    orientation.append("ft2")
                else:
                    orientation.append(item)
        newSeries = pd.Series(orientation, index=[windowAeas_df.index])
        temp.append(newSeries)

    windowAeas_df2 = pd.DataFrame(temp)

    # --------------------------------------------------------------------------
    # Combine together into a single DF
    demand_results_df1 = pd.concat(
        [tfa_3, vol_3, extSrfc_3, srfc_vol_ratio2, av_ratio2], axis=1
    )
    demand_results_df2 = pd.concat([demand_results_df1.T, windowAeas_df2])
    demand_results_df3 = demand_results_df2.reset_index(drop=True)

    # --------------------------------------------------------------------------
    # Export to csv
    demand_results_df3.to_csv(_file_path, index=False)
