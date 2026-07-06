# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""The allowlisted PH-Navigator element-table names (route 5 - `GET /tables/{name}`).

Single source of truth for the 12 row-based element tables the V1 read API serves.
`Get Table` validates its `_table_name` input against this before making the network
call, and Ed populates the GH value-list dropdown from the same list - so the canvas
and the client agree on exactly what the backend allows.

Keep this identical to the backend allowlist. If a route-5 call 422s with a
`details.valid_names` that differs from this tuple, the plugin is stale relative to
the server (a new table was added or renamed) - update this constant to match.
"""

# -- Ordered so a value-list dropdown reads in a sensible grouping (envelope, then
# -- the mechanical / equipment tables). Kept identical to the backend allowlist.
VALID_TABLE_NAMES = (
    "rooms",
    "space_types",
    "thermal_bridges",
    "pumps",
    "fans",
    "ventilators",
    "hot_water_heaters",
    "hot_water_tanks",
    "electric_heaters",
    "appliances",
    "heat_pump_indoor_units",
    "heat_pump_outdoor_units",
)
