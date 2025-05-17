# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Building-Data Tabel CSV file from the Main PHPP DataFrme"""

import pathlib

import pandas as pd

from honeybee_ph_plus_rhino.phpp.bt_web._variants_data_schema import VARIANTS

pd.options.mode.chained_assignment = None  # default='warn'


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
    # bldg_df = _df_main.loc[279:287]
    start_row = VARIANTS.geometry.start_row()
    end_row = VARIANTS.geometry.end_row()
    bldg_df = _df_main.loc[start_row:end_row]

    # --------------------------------------------------------------------------
    # TFA
    tfa_1 = bldg_df.loc[VARIANTS.geometry["TFA"].row]
    """
        Datatype                 TFA
        Units                    NaN
        Code Minimum      558.313778
        Insulation        558.313778
        Airtight + ERV    558.313778
        PH Windows        558.313778
        Passive House     558.313778
    """
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
    tfa = pd.Series(tfa_2, index=[bldg_df.columns])

    # --------------------------------------------------------------------------
    # Vn50 Volume
    # vol_1 = bldg_df.loc[281]
    vn50_vol_1 = bldg_df.loc[VARIANTS.geometry["Vn50"].row]
    vn50_vol_2 = []
    for each in vn50_vol_1:
        try:
            vn50_vol_2.append(each * 35.31466672)
        except:
            if each == "m3":
                vn50_vol_2.append("ft3")
            elif each == "Vn50":
                vn50_vol_2.append("Interior Net Volume")
            else:
                vn50_vol_2.append(each)
    vn50_volume = pd.Series(vn50_vol_2, index=[bldg_df.columns])

    # --------------------------------------------------------------------------
    # Gross Volume
    gross_vol_1 = bldg_df.loc[VARIANTS.geometry["Gross Volume"].row]
    gross_vol_2 = []
    for each in gross_vol_1:
        try:
            gross_vol_2.append(each * 35.31466672)
        except:
            if each == "m3":
                gross_vol_2.append("ft3")
            elif each == "Vn50":
                gross_vol_2.append("Interior Net Volume")
            else:
                gross_vol_2.append(each)
    gross_volume = pd.Series(gross_vol_2, index=[bldg_df.columns])

    # --------------------------------------------------------------------------
    # Total Exterior Surface
    # extSrfc_1 = bldg_df.loc[282]
    ext_surface_area_1 = bldg_df.loc[VARIANTS.geometry["Building Envelope Area"].row]
    ext_surface_area_2 = []
    for each in ext_surface_area_1:
        try:
            ext_surface_area_2.append(each * 10.76391042)
        except:
            if each == "m2":
                ext_surface_area_2.append("ft2")
            else:
                ext_surface_area_2.append(each)
    ext_surface_area = pd.Series(ext_surface_area_2, index=[bldg_df.columns])

    # --------------------------------------------------------------------------
    # Exterior Surface / Floor-Area Ratio
    srfc_to_floor_area_ratio = []
    for i, each in enumerate(ext_surface_area_2):
        try:
            srfc_to_floor_area_ratio.append(each / tfa_2[i])
        except:
            if each == "ft2":
                srfc_to_floor_area_ratio.append("-")
            else:
                srfc_to_floor_area_ratio.append("Ext. Surface Area / Floor Area")
    ext_srfc_floor_area_ratio_2 = pd.Series(
        srfc_to_floor_area_ratio, index=[bldg_df.columns]
    )

    # --------------------------------------------------------------------------
    # Exterior Surface / Gross-Volume Ratio
    srfc_to_volume_ratio = []
    for i, each in enumerate(ext_surface_area_2):
        try:
            srfc_to_volume_ratio.append(each / gross_vol_2[i])
        except:
            if each == "ft2":
                srfc_to_volume_ratio.append("-")
            else:
                srfc_to_volume_ratio.append("Ext. Surface Area / Gross Volume")
    ext_srfc_to_gross_volume_ratio_2 = pd.Series(
        srfc_to_volume_ratio, index=[bldg_df.columns]
    )

    # --------------------------------------------------------------------------
    # Floor-Area / Gross-Volume Ratio
    floor_area_to_volume_ratio = []
    for i, each in enumerate(tfa_2):
        try:
            floor_area_to_volume_ratio.append(each / gross_vol_2[i])
        except:
            if each == "ft2":
                floor_area_to_volume_ratio.append("-")
            else:
                floor_area_to_volume_ratio.append("Floor Area / Gross Volume")
    floor_area_to_gross_volume_ratio_2 = pd.Series(
        floor_area_to_volume_ratio, index=[bldg_df.columns]
    )

    # --------------------------------------------------------------------------
    # Window Areas by Orientation
    # window_areas_df = bldg_df.loc[283:287].T
    start_row = VARIANTS.geometry["Window Area (North)"].row
    end_row = VARIANTS.geometry["Window Area (Horiz)"].row
    window_areas_df = bldg_df.loc[start_row:end_row].T
    temp = []
    for col_name in window_areas_df:
        orientation = []
        for item in window_areas_df[col_name].values:
            try:
                orientation.append(item * 10.76391042)
            except:
                if item == "m2":
                    orientation.append("ft2")
                else:
                    orientation.append(item)
        newSeries = pd.Series(orientation, index=[window_areas_df.index])
        temp.append(newSeries)

    window_areas_df2 = pd.DataFrame(temp)

    # --------------------------------------------------------------------------
    # Combine together into a single DF
    demand_results_df1 = pd.concat(
        [
            tfa,
            ext_surface_area,
            vn50_volume,
            gross_volume,
            ext_srfc_floor_area_ratio_2,
            ext_srfc_to_gross_volume_ratio_2,
            floor_area_to_gross_volume_ratio_2,
        ],
        axis=1,
    )
    demand_results_df2 = pd.concat([demand_results_df1.T, window_areas_df2])
    demand_results_df3 = demand_results_df2.reset_index(drop=True)

    # --------------------------------------------------------------------------
    # Export to csv
    demand_results_df3.to_csv(_file_path, index=False)
