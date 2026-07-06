> **Status (Phase 05 implemented):** these desired outputs are now mapped in
> `OUTPUT_SPECS` (`gh_compo_io/ph_navigator/v1/table_organize.py`), which is the
> source of truth for port order + backend `field_key`s. The "(Note: to be added to
> PH-Navigator)" annotations below were assumptions at authoring time — **most of
> those fields already exist server-side** (verified against the backend row models)
> and are wired up. See `05-organize-table.md` for the resolved mapping and the few
> genuine gaps. This file is kept as the original requirements record.

The following outputs should be yielded by components after reading and interpreting the download data from PH-Navigator-V2

## Rooms

1. weighting factors (ICFA)
2. ceiling height (Note: to be added to PH-Navigator)
3. room-name
4. room-number
5. supply-air-rate
6. extract-air-rate

## Thermal Bridges

1. name
2. Psi-Value
3. fRsi value
4. Type
5. Quantity (Note: to be added to PH-Navigator)

## Ventilators

1. name
2. heat-recovery %
3. energy-recovery %
4. electrical-efficiency
5. frost protection (Note: to be added to PH-Navigator)
6. frost protection limit temp (Note: to be added to PH-Navigator)
7. Inside / Outside

## Pumps

1. name
2. type
3. quantity (Note: to be added to PH-Navigator)
4. Inside/Outside (Note: to be added to PH-Navigator)
5. annual energy-demand (Note: to be added to PH-Navigator)
6. annual runtime
7. Internal Heat Gains Utilization Factor (Note: to be added to PH-Navigator)

## Fans

1. Name
2. Type
3. Airflow Rate
4. annual runtime

## Hot Water Heater

1. Name
2. Type

## Hot Water Tank

1. Name
2. Type
3. quantity
4. heat-loss-rate
5. volume (size)
6. inside/outside (Note: to be added to PH-Navigator)
7. Location temp (Note: to be added to PH-Navigator)
8. water temp (Note: to be added to PH-Navigator)

## Electric Heaters

1. Name
2. Wattage

## Appliances

1. Name
2. Type
3. Quantity
4. Model
5. Manufacturer
6. EnergyStar (yes/no)
7. Capacity
8. CEF
9. IMEF
10. MEF
11. annual-energy-use

## Heat Pumps

Note: Ommit for now. Rais NotImplementedError