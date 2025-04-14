# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Export Combined Heating/Cooling Energy Demand and Phius Certification CSV files from the Main PHPP DataFrme"""

import pathlib

import pandas as pd

from honeybee_ph_plus_rhino.phpp.bt_web._variants_data_schema import VARIANTS


def create_csv_heating_and_cooling_demand(
    _df_main: pd.DataFrame,
    _tfa_df: pd.DataFrame,
    _cert_limits_abs: pd.DataFrame,
    _output_path: pathlib.Path,
) -> None:
    # ---------------------------------------------------------------------------
    # Get the Cooling Demand results
    cooling_dem_df = _df_main.loc[
        VARIANTS.certification_results["Total Cooling Demand"].row
    ]
    cooling_dem_limit_df = _cert_limits_abs.loc[
        VARIANTS.certification_limits["Total Cooling Demand Limit"].row
    ]

    # Get the Heating Demand results
    heating_dem_df = _df_main.loc[VARIANTS.certification_results["Heat Demand"].row]
    heating_dem_limit_df = _cert_limits_abs.loc[
        VARIANTS.certification_limits["Heat Demand Limit"].row
    ]

    output_csv(
        [heating_dem_df, cooling_dem_df], _tfa_df, _output_path, heating_dem_limit_df
    )


def create_csv_heating_demand(
    _df_main: pd.DataFrame,
    _tfa_df: pd.DataFrame,
    _cert_limits_abs: pd.DataFrame,
    _output_path: pathlib.Path,
) -> None:
    # Get the Heating Demand results
    heating_dem_df = _df_main.loc[VARIANTS.certification_results["Heat Demand"].row]
    heating_dem_limit_df = _cert_limits_abs.loc[
        VARIANTS.certification_limits["Heat Demand Limit"].row
    ]

    output_csv([heating_dem_df], _tfa_df, _output_path, heating_dem_limit_df)


def create_csv_cooling_demand(
    _df_main: pd.DataFrame,
    _tfa_df: pd.DataFrame,
    _cert_limits_abs: pd.DataFrame,
    _output_path: pathlib.Path,
) -> None:
    # Get the Cooling Demand results
    cooling_dem_df = _df_main.loc[
        VARIANTS.certification_results["Total Cooling Demand"].row
    ]
    cooling_dem_limit_df = _cert_limits_abs.loc[
        VARIANTS.certification_limits["Total Cooling Demand Limit"].row
    ]

    output_csv([cooling_dem_df], _tfa_df, _output_path, cooling_dem_limit_df)


def create_csv_heating_load(
    _df_main: pd.DataFrame,
    _tfa_df: pd.DataFrame,
    _cert_limits_abs: pd.DataFrame,
    _output_path: pathlib.Path,
) -> None:
    # Get the  Heating Load results
    heating_load_df = _df_main.loc[
        VARIANTS.certification_results["Total Cooling Demand"].row
    ]
    heating_load_limit_df = _cert_limits_abs.loc[
        VARIANTS.certification_limits["Peak Heat Load Limit"].row
    ]

    output_csv([heating_load_df], _tfa_df, _output_path, heating_load_limit_df)


def create_csv_cooling_load(
    _df_main: pd.DataFrame,
    _tfa_df: pd.DataFrame,
    _cert_limits_abs: pd.DataFrame,
    _output_path: pathlib.Path,
) -> None:
    # Get the Cooling Load results
    cooling_load_df = _df_main.loc[
        VARIANTS.certification_results["Peak Cooling Load "].row
    ]
    cooling_load_limit_df = _cert_limits_abs.loc[
        VARIANTS.certification_limits["Peak Cooling Load Limit"].row
    ]

    output_csv([cooling_load_df], _tfa_df, _output_path, cooling_load_limit_df)


def output_csv(
    _data: list[pd.Series | pd.DataFrame],
    _tfa_df: pd.DataFrame,
    _output_path: pathlib.Path,
    _limit_df: pd.Series | pd.DataFrame,
) -> None:
    """Builds the CSV file based on the Heating/Cooling data given."""

    # ---------------------------------------------------------------------------
    # Construct a DataFrame from the input Series
    data_df = pd.concat(_data, axis=1).T

    # ---------------------------------------------------------------------------
    # --- Create the Header DF, join the data+header into a new DataFrame
    header_df = pd.DataFrame()

    for variant in data_df.columns[:2]:
        header_df[variant] = data_df[variant]

    header_df["Units"] = header_df["Units"].str.replace("/m2", "")  # 'm2' strings

    for variant in data_df.columns[2:]:
        # Convert to total kWh instead of kWh/m2
        header_df[variant] = data_df[variant].mul(_tfa_df[variant])

    # ---------------------------------------------------------------------------
    # ---- Output final data to CSV
    if isinstance(_limit_df, pd.Series):
        _limit_df = _limit_df.to_frame().T
    output_df = pd.concat([header_df, _limit_df])
    output_df.to_csv(_output_path, index=False)
