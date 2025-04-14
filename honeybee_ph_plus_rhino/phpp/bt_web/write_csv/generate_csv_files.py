# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""Run the functions to generate CSV files from PHPP Data."""

from pathlib import Path

from honeybee_ph_plus_rhino.phpp.bt_web._types import PHPPData
from honeybee_ph_plus_rhino.phpp.bt_web.write_csv.csv_writers import (
    create_csv_airtightness,
    create_csv_bldg_basic_data_table,
    create_csv_CO2E,
    create_csv_detailed_cooling_demand,
    create_csv_detailed_heating_demand,
    create_csv_fresh_air_flowrates,
    create_csv_Phius_net_source_energy,
    create_csv_radiation,
    create_csv_SiteEnergy,
    create_csv_temperatures,
    create_csv_variant_table,
)
from honeybee_ph_plus_rhino.phpp.bt_web.write_csv.csv_writers.heating_and_cooling import (
    create_csv_cooling_demand,
    create_csv_cooling_load,
    create_csv_heating_and_cooling_demand,
    create_csv_heating_demand,
    create_csv_heating_load,
)


def create_csv_files(_csv_file_path: Path, _phpp_data: PHPPData) -> None:
    """Generate all the .CSV files based on the input PHPPData object.

    Arguments:
    ----------
        * config (Config): The Config object with the input / output paths.
        * phpp_data (PHPPData): A PHPPData object with all the data pulled from the Excel file.

    Returns:
    --------
        * None
    """

    print(f'> Writing out CSV files to: "{_csv_file_path}/..."')

    # --- Heating and Cooling Data
    create_csv_heating_and_cooling_demand(
        _phpp_data.df_variants,
        _phpp_data.df_tfa,
        _phpp_data.df_certification_limits,
        _csv_file_path / "demand_HeatAndCool.csv",
    )
    create_csv_heating_demand(
        _phpp_data.df_variants,
        _phpp_data.df_tfa,
        _phpp_data.df_certification_limits,
        _csv_file_path / "demand_Phius_heating.csv",
    )
    create_csv_cooling_demand(
        _phpp_data.df_variants,
        _phpp_data.df_tfa,
        _phpp_data.df_certification_limits,
        _csv_file_path / "demand_Phius_cooling.csv",
    )
    create_csv_heating_load(
        _phpp_data.df_variants,
        _phpp_data.df_tfa,
        _phpp_data.df_certification_limits,
        _csv_file_path / "load_Phius_heating.csv",
    )
    create_csv_cooling_load(
        _phpp_data.df_variants,
        _phpp_data.df_tfa,
        _phpp_data.df_certification_limits,
        _csv_file_path / "load_Phius_cooling.csv",
    )
    create_csv_Phius_net_source_energy(
        _phpp_data.df_variants,
        _phpp_data.df_certification_limits,
        _csv_file_path / "Phius_net_source_energy.csv",
    )
    create_csv_SiteEnergy(
        _phpp_data.df_variants,
        _csv_file_path / "energy_Site.csv",
    )

    # --- CO2 Emissions
    create_csv_CO2E(
        _phpp_data.df_variants,
        _csv_file_path / "energy_TonsCO2.csv",
    )

    # --- Get the Model Variants info
    create_csv_variant_table(
        _phpp_data.df_variants,
        _phpp_data.variant_names,
        _csv_file_path / "variant_inputs.csv",
    )
    create_csv_bldg_basic_data_table(
        _phpp_data.df_variants, _csv_file_path / "bldg_data.csv"
    )

    # --- Create Detailed Heating, Cooling Demand
    create_csv_detailed_heating_demand(
        _phpp_data.df_variants,
        _phpp_data.df_certification_limits,
        _csv_file_path / "heating_demand.csv",
    )
    create_csv_detailed_cooling_demand(
        _phpp_data.df_variants,
        _phpp_data.df_certification_limits,
        _csv_file_path / "cooling_demand.csv",
    )

    # --- Airtightness
    create_csv_airtightness(
        _phpp_data.df_variants, _csv_file_path / "envelope_airflow.csv"
    )

    # --- Climate
    create_csv_radiation(_phpp_data.df_climate, _csv_file_path / "climate_radiation.csv")
    create_csv_temperatures(_phpp_data.df_climate, _csv_file_path / "climate_temps.csv")

    # --- Mechanical
    create_csv_fresh_air_flowrates(
        _phpp_data.df_room_vent, _csv_file_path / "room_airflows.csv"
    )

    print(f"> Done writing CSV files.")
