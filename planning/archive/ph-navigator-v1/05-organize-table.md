# 05 — `HBPH+ - PH-Nav Organize Table` (dynamic-output reshape)

**Status:** ✅ DONE (code) — `gh_compo_io/ph_navigator/v1/table_organize.py` +
`src/HBPH+ - PH-Nav Organize Table.py` + `_component_info_.py` entry + re-exports.
Depends on the Phase 06 `setup_component_outputs` helper (already in
`ph_gh_component_io`). Ed still builds the binary `.ghuser` (a **generous fixed
port set**: index 0 = `out`, index 1 = `report_`, indices 2-12 = 11 generic data
ports the wrapper renames per `_type`) and the icon. **Not yet run against a live
route-5 payload** — but the `source_field_key`s below are **no longer guesses**:
they were resolved against the `ph-navigator-v2` backend document row models
(`backend/features/project_document/tables/*.py`), so `OUTPUT_SPECS` in
`table_organize.py` carries the **real built-in column keys**. Notably, almost every
field this doc marked "PENDING server field" (rooms `ceiling_height_m`, TB/pump/tank
`quantity`, pump `inside_outside` / `annual_energy_kwh` / IHG factor, ventilator
`frost_protection*`, tank `inside_outside` / `location_temp_c` / `water_temp_c`) now
**exists server-side** and is mapped. `OUTPUT_SPECS` in the code is the source of
truth; the embedded spec block below is the original sketch, kept for provenance.

**Decisions made during implementation:**
- **Units:** values pass through as **raw SI** (each port's description names the
  unit); no `ph_units` conversion in the component. Convert downstream where a
  consumer needs non-SI. (Chose the plan's "leave SI" option for a clean first cut.)
- **`space_types` (O-E):** no mapping → warn + pass records through on a single
  `records_` port.
- **Heat pumps:** `_type` in the two heat-pump tables → `IGH.error` (not a raw
  `NotImplementedError` traceback) and blank all data ports.
- **Single-select** `{id,label}` → emit `label` (O-C); no port currently needs the id.
- **Table taxonomy** (mapped / passthrough / deferred / unknown) lives in one
  `_classify_table` classifier that both the port-setup phase and the value phase
  dispatch off, so they can't drift.

**File:** `gh_compo_io/ph_navigator/v1/table_organize.py`
**Class:** `GHCompo_PHNavV1OrganizeTable`
**Route:** none (consumes Get Table output).
**Purpose:** turn the generic `records_` + `field_defs_` from Get Table into
**named, ordered, correctly-typed output ports** that plug straight into the
existing `honeybee_ph` create-components — with the output ports **reshaping
dynamically based on `_type` (table name)**. This is the "clean workflow" piece:
PH-Nav → HBPH consumers with no manual field wrangling.

This is the hardest component and the one that needs **Ed's per-table mapping**.

## The pattern (output-side twin of `create_elec_equip.py`)

`HBPH - Create PH Equipment` reshapes its **input** nodes by `_type` using:

```python
input_dict = create_elec_equip.get_component_inputs(_type)   # {index: ComponentInput}
gh_io.setup_component_inputs(IGH, input_dict, _start_i=2)     # rewrites Params.Input[i]
input_values_dict = gh_io.get_component_input_values(ghenv)
```

We do the same on the **output** side: a per-table spec `{index: ComponentOutput}`
drives a new helper `setup_component_outputs(IGH, output_dict, _start_i=1)` that
rewrites `ghenv.Component.Params.Output[i]` (`Name`/`NickName`/`Description`/`Access`).

> **New shared helper required.** `ph_gh_component_io.gh_io` has
> `setup_component_inputs` but **no** output twin. Add `setup_component_outputs`
> (and a `ComponentOutput` dataclass: `name`, `description`, `access`). GH output
> params have no `TypeHint` (outputs are generic), so the helper is simpler than
> the input one — just Name/NickName/Description/Access on `Params.Output[i]`.
> **Decision:** add it to `ph_gh_component_io` (reusable) — see README infra §2.
> Fallback: a private `_gh_output_io.py` in this repo if we can't touch that pkg.

## Component shape

Inputs:

| Port          | Type       | Notes |
|---------------|------------|-------|
| `_records`    | list[dict] | From Get Table `records_`. |
| `_field_defs` | list[dict] | From Get Table `field_defs_`. |
| `_type`       | str        | Table name (from Get Table `table_name_`); selects the output spec. |

Outputs: **dynamic**, defined per-table by the mapping (see below). Port 0 may be a
constant `report_` (unmapped columns / warnings) so nothing is silently dropped
(README no-silent-caps principle).

## Per-table output mapping (from `outputs.md`)

Ed's desired **output ports per table** are the source of truth in
`planning/ph-navigator-v1/outputs.md`. The spec below is the port list (in order)
the Organize component reshapes to. Each row = one output port:
`(out_name, source_field_key, access, note)`.

> **Two known-unknowns per row:**
> 1. **`source_field_key`** — the actual column / `custom_values` key in the route-5
>    payload. Resolve against a live response + `field_defs` (map `display_name` ↔
>    `field_key`; **never hardcode** — O5). Marked `?` below where unconfirmed.
> 2. **"to be added to PH-Navigator"** fields don't exist server-side yet → the
>    resolver emits `None` (downstream defaults). This is expected, not an error.
>    Log a one-line `report_` note listing which requested ports were unresolved.

```python
# OUTPUT_SPECS[table_name] = [(out_name, source_field_key, access, note), ...]
ITEM = 0  # GH item access
OUTPUT_SPECS = {
    "rooms": [                                # 6 ports
        ("weighting_factor_", "icfa_weighting?", ITEM, "ICFA weighting factor"),
        ("ceiling_height_",   "ceiling_height?", ITEM, "PENDING server field"),
        ("room_name_",        "display_name?",   ITEM, ""),
        ("room_number_",      "room_number?",    ITEM, ""),
        ("supply_air_rate_",  "supply_air?",     ITEM, ""),
        ("extract_air_rate_", "extract_air?",    ITEM, ""),
    ],
    "thermal_bridges": [                      # 5 ports
        ("name_",     "display_name?", ITEM, ""),
        ("psi_value_","psi_value?",    ITEM, "W/mk"),
        ("f_rsi_",    "f_rsi?",        ITEM, ""),
        ("type_",     "tb_type?",      ITEM, "single-select -> label"),
        ("quantity_", "quantity?",     ITEM, "PENDING server field"),
    ],
    "ventilators": [                          # 7 ports
        ("name_",              "display_name?",        ITEM, ""),
        ("heat_recovery_pct_", "heat_recovery?",       ITEM, ""),
        ("energy_recovery_pct_","energy_recovery?",    ITEM, ""),
        ("elec_efficiency_",   "electrical_efficiency?",ITEM, "Wh/m3"),
        ("frost_protection_",  "frost_protection?",    ITEM, "PENDING server field"),
        ("frost_temp_limit_",  "frost_temp_limit?",    ITEM, "PENDING server field"),
        ("inside_outside_",    "location?",            ITEM, "inside/outside"),
    ],
    "pumps": [                                # 7 ports
        ("name_",            "display_name?",  ITEM, ""),
        ("type_",            "pump_type?",     ITEM, "single-select -> label"),
        ("quantity_",        "quantity?",      ITEM, "PENDING server field"),
        ("inside_outside_",  "location?",      ITEM, "PENDING server field"),
        ("annual_energy_",   "annual_energy?", ITEM, "PENDING server field, kWh/yr"),
        ("annual_runtime_",  "annual_runtime?",ITEM, ""),
        ("ihg_util_factor_", "ihg_factor?",    ITEM, "PENDING server field"),
    ],
    "fans": [                                 # 4 ports
        ("name_",           "display_name?",   ITEM, ""),
        ("type_",           "fan_type?",       ITEM, "single-select -> label"),
        ("airflow_rate_",   "airflow?",        ITEM, "m3/h"),
        ("annual_runtime_", "annual_runtime?", ITEM, ""),
    ],
    "hot_water_heaters": [                     # 2 ports
        ("name_", "display_name?", ITEM, ""),
        ("type_", "heater_type?",  ITEM, "single-select -> label"),
    ],
    "hot_water_tanks": [                       # 8 ports
        ("name_",           "display_name?", ITEM, ""),
        ("type_",           "tank_type?",    ITEM, "single-select -> label"),
        ("quantity_",       "quantity?",     ITEM, ""),
        ("heat_loss_rate_", "heat_loss?",    ITEM, "W/K"),
        ("volume_",         "volume?",       ITEM, "liters"),
        ("inside_outside_", "location?",     ITEM, "PENDING server field"),
        ("location_temp_",  "location_temp?",ITEM, "PENDING server field"),
        ("water_temp_",     "water_temp?",   ITEM, "PENDING server field"),
    ],
    "electric_heaters": [                      # 2 ports
        ("name_",    "display_name?", ITEM, ""),
        ("wattage_", "wattage?",      ITEM, "W"),
    ],
    "appliances": [                            # 11 ports (widest)
        ("name_",         "display_name?",  ITEM, ""),
        ("type_",         "appliance_type?",ITEM, "single-select -> label"),
        ("quantity_",     "quantity?",      ITEM, ""),
        ("model_",        "model?",         ITEM, ""),
        ("manufacturer_", "manufacturer?",  ITEM, ""),
        ("energy_star_",  "energy_star?",   ITEM, "yes/no"),
        ("capacity_",     "capacity?",      ITEM, ""),
        ("cef_",          "cef?",           ITEM, ""),
        ("imef_",         "imef?",          ITEM, ""),
        ("mef_",          "mef?",           ITEM, ""),
        ("annual_energy_","annual_energy?", ITEM, "kWh/yr"),
    ],
    # heat_pump_indoor_units / heat_pump_outdoor_units: DEFERRED.
    # -> raise NotImplementedError("Heat-pump organize not implemented yet") (Ed).
}
```

### Coverage vs. the 12 allowlisted tables

| Table                      | Ports | Status |
|----------------------------|-------|--------|
| `rooms`                    | 6     | mapped |
| `space_types`              | —     | **GAP** — not in `outputs.md`. Decide (see O-E). |
| `thermal_bridges`          | 5     | mapped |
| `pumps`                    | 7     | mapped |
| `fans`                     | 4     | mapped |
| `ventilators`              | 7     | mapped |
| `hot_water_heaters`        | 2     | mapped |
| `hot_water_tanks`          | 8     | mapped |
| `electric_heaters`         | 2     | mapped |
| `appliances`               | 11    | mapped (widest) |
| `heat_pump_indoor_units`   | —     | **deferred** → `NotImplementedError` |
| `heat_pump_outdoor_units`  | —     | **deferred** → `NotImplementedError` |

**ghuser output-port ceiling = 11** (Appliances) + 1 reserved `report_` port =
build the Organize ghuser with **~12 output ports**; the wrapper renames/activates
only what the current `_type` needs and blanks the rest to `-`.

### Consumer components (where these ports get wired downstream, FYI)

Not required to build Organize (Ed wires these on-canvas), but the intended targets:

| Table              | HB consumer (`honeybee_grasshopper_ph`) |
|--------------------|------------------------------------------|
| `ventilators`      | `hvac/create_ventilator.py` |
| `hot_water_heaters`| `shw/create_heater.py` |
| `hot_water_tanks`  | `shw/create_tank.py` |
| `appliances`       | `program/create_elec_equip.py` |
| `rooms`            | `space_create_from_hb_rooms.py`, `space_create_vent_rates.py` |
| `thermal_bridges` / `pumps` / `fans` / `electric_heaters` | HVAC / TB builders (confirm) |

## Logic outline

1. `output_spec = OUTPUT_SPECS.get(_type)`; if none → `IGH.warning` "unmapped table"
   and pass records through on a single `records_` output.
2. Build `{index: ComponentOutput}` from the spec; `setup_component_outputs(IGH, ...)`.
   (This runs in the `src/` wrapper, same place `setup_component_inputs` runs.)
3. For each record, pull each mapped `source_key` from the row. Resolution rules:
   - built-in typed column → direct.
   - inside `custom_values` bag → look up by `field_key` (use `_field_defs` to map
     `display_name`↔`field_key`; **don't hardcode field names**, O5).
   - **single-select** `{id,label}` → emit `label` (O-C); expose `id` only where a
     mapping row explicitly asks (joins).
   - missing/`null` → emit `None` (let downstream default).
4. Transpose row-values into per-output lists (GH `list` access) and assign to the
   dynamic output variables in the `src/` wrapper.
5. Anything in a record **not** covered by the spec → collect into `report_` so
   nothing is silently dropped.

## Units

Backend emits **SI with unit-suffixed field names** (`_w_m2k`, `_mm`, `_m`, `_pct`,
…). Convert to whatever the HB consumer expects using `ph_units` (as elsewhere in
this repo) inside the mapping/resolution step, or leave SI if the consumer takes SI.
Decide per mapping row; record the target unit in the spec `note`.

## `src/` wrapper responsibility

Like `HBPH - Create PH Equipment`, the dynamic-node call lives in the **wrapper**,
not the logic class:

```python
output_spec = table_organize.get_component_outputs(_type)
gh_io.setup_component_outputs(IGH, output_spec, _start_i=1)   # <-- new helper
compo = table_organize.GHCompo_PHNavV1OrganizeTable(IGH, _records, _field_defs, _type)
result_dict = compo.run()      # {out_name: [values...]}
# then assign result_dict values onto the (now-renamed) output variables
```

Ed builds the ghuser with a **generous fixed number of output ports** (e.g. 12–16),
initially blank; the wrapper renames/activates only the ones the current `_type`
needs (extra ports get a `-` name, as `setup_component_inputs` does for inputs).

## Open questions

- ~~**O-E `space_types`**~~ **RESOLVED**: `_type == "space_types"` → `IGH.warning`
  "no organize mapping" + pass-through on a single `records_` port. Can grow its own
  port list later if needed.
- **Heat pumps deferred**: `heat_pump_indoor_units` / `heat_pump_outdoor_units` →
  `IGH.error` "not implemented yet" + blank ports (chose a clean error over a raw
  `NotImplementedError` traceback). Joins on `outdoor_unit_id` revisited when built.
- ~~**`source_field_key` confirmation**~~ **RESOLVED (statically)**: instead of a
  live-payload fixture, the keys were read straight from the backend row models
  (`ph-navigator-v2/backend/features/project_document/tables/*.py`) and encoded in
  `OUTPUT_SPECS`. Still worth **one live smoke-test** per table shape to confirm the
  serialized payload matches (single-select `{id,label}` denormalization, empty
  table, custom_values bag) — the resolver already handles all three, but it hasn't
  run against a real route-5 response yet.
- ~~**Units**~~ **RESOLVED**: pass **raw SI** through (unit named in each port's
  description); convert downstream. No `ph_units` in the component for now.

*(Resolved: `setup_component_outputs` goes into `ph_gh_component_io` — see `06-…`.)*
