# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - PH-Nav Organize Table.

Reshape the generic `records` + `field_defs` from `Get Table` (route 5) into
**named, per-table output ports** that plug straight into the existing
`honeybee_ph` create-components. The output ports are *dynamic*: they rename /
activate based on `_type` (the table name), driven by `OUTPUT_SPECS` below.

This is the output-side twin of the dynamic-*input* pattern used by
`honeybee_grasshopper_ph`'s `HBPH - Create PH Equipment` (which rewrites its input
ports by `_type`). Split of responsibilities:
- `get_component_outputs(_type)` -> `{index: ComponentOutput}` is called by the
  `src/` wrapper to rewrite the component's output ports BEFORE this class runs
  (via `gh_io.setup_component_outputs`).
- This class only maps values: for each output port it pulls the mapped
  `field_key` out of every record and returns one list per port. The `src/`
  wrapper then surfaces those lists on the (now-renamed) ports.

Both phases dispatch off one classifier (`_classify_table`) so the table taxonomy
lives in exactly one place. Field keys are the **backend built-in column keys**
(verified against the `ph-navigator-v2` document row models), not guesses.
Resolution falls back to the record's `custom_values` bag by key, so a custom
field can be mapped later without code changes. Single-select values arrive as
`{"id", "label"}` and are flattened to their `label` (O-C). Missing / unset fields
resolve to `None` so the downstream create-component applies its own default.
"""

try:
    from typing import Any, Dict, List  # noqa: F401
except ImportError:
    pass  # IronPython 2.7

try:
    from ph_gh_component_io import gh_io
    from ph_gh_component_io.gh_io import ComponentOutput
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io. {}".format(e))


# -- Output port index 0 is GHPython's reserved `out` runtime-message stream;
# -- index 1 is the fixed `report_` port (unmapped columns / gaps). The dynamic
# -- per-table data ports therefore start at index 2.
REPORT_PORT_NAME = "report_"
DATA_PORT_START_INDEX = 2

# -- Table kinds (the four ways `_type` can resolve). See `_classify_table`.
_MAPPED = "mapped"
_PASSTHROUGH = "passthrough"
_DEFERRED = "deferred"
_UNKNOWN = "unknown"

# -- Heat pumps are deferred (cross-table `outdoor_unit_id` joins not designed yet).
DEFERRED_TABLES = ("heat_pump_indoor_units", "heat_pump_outdoor_units")

# -- Allowlisted tables with no organize mapping (see outputs.md gap O-E). These
# -- pass their raw records straight through on a single `records_` port.
PASSTHROUGH_TABLES = ("space_types",)


class _Port(ComponentOutput):
    """One dynamic output port: a `ComponentOutput` (name / description, item
    access) plus the record `field_key` its value is pulled from."""

    def __init__(self, _name, _field_key, _description=""):
        # type: (str, str, str) -> None
        ComponentOutput.__init__(self, _name, _description)
        self.field_key = _field_key


# -- The single `records_` port used when an allowlisted table has no mapping. A
# -- shared constant so the structure phase (`get_component_outputs`) and the data
# -- phase (`run`) agree on the port name.
PASSTHROUGH_PORT = ComponentOutput(
    "records_", "(list) Raw records, passed through (no organize mapping for this table)."
)


# -----------------------------------------------------------------------------
# -- Per-table output mapping. `field_key` values are the backend built-in column
# -- keys (from the ph-navigator-v2 document row models). Order == port order.
# -- Values are passed through as raw SI (unit noted in the description); convert
# -- downstream where a consumer expects non-SI.

OUTPUT_SPECS = {
    "rooms": [
        _Port("weighting_factor_", "icfa_factor", "(float) iCFA weighting factor (0-1)."),
        _Port("ceiling_height_", "ceiling_height_m", "(float) Ceiling height [m] (SI)."),
        _Port("room_name_", "name", "(str) Room name."),
        _Port("room_number_", "number", "(str) Room number."),
        _Port("supply_air_rate_", "supply_airflow_m3h", "(float) Supply airflow rate [m3/h] (SI)."),
        _Port("extract_air_rate_", "extract_airflow_m3h", "(float) Extract airflow rate [m3/h] (SI)."),
    ],
    "thermal_bridges": [
        _Port("name_", "name", "(str) Thermal-bridge name."),
        _Port("psi_value_", "psi_value_w_mk", "(float) Psi-value [W/mk] (SI)."),
        _Port("f_rsi_", "frsi_value", "(float) fRsi value (0-1)."),
        _Port("type_", "thermal_bridge_type", "(str) Type (single-select label)."),
        _Port("quantity_", "quantity", "(int) Quantity."),
    ],
    "ventilators": [
        _Port("name_", "name", "(str) Ventilator name."),
        _Port("heat_recovery_pct_", "heat_recovery_percent", "(float) Heat-recovery efficiency [%]."),
        _Port("energy_recovery_pct_", "moisture_recovery_percent", "(float) Moisture/enthalpy-recovery efficiency [%]."),
        _Port("elec_efficiency_", "electrical_efficiency_wh_m3", "(float) Electrical efficiency [Wh/m3] (SI)."),
        _Port("frost_protection_", "frost_protection", "(str) Frost protection (single-select label)."),
        _Port("frost_temp_limit_", "frost_protection_limit_temp_c", "(float) Frost-protection limit temp [deg C] (SI)."),
        _Port("inside_outside_", "inside_outside", "(str) Inside / Outside (single-select label)."),
    ],
    "pumps": [
        _Port("name_", "name", "(str) Pump name."),
        _Port("type_", "device_type", "(str) Type (single-select label)."),
        _Port("quantity_", "quantity", "(int) Quantity."),
        _Port("inside_outside_", "inside_outside", "(str) Inside / Outside (single-select label)."),
        _Port("annual_energy_", "annual_energy_kwh", "(float) Annual energy demand [kWh/yr]."),
        _Port("annual_runtime_", "runtime_khr_yr", "(float) Annual runtime [thousand-hr/yr]."),
        _Port("ihg_util_factor_", "internal_heat_gains_utilization_factor", "(float) Internal-heat-gains utilization factor."),
    ],
    "fans": [
        _Port("name_", "name", "(str) Fan name."),
        _Port("type_", "fan_type", "(str) Type (single-select label)."),
        _Port("airflow_rate_", "airflow_m3h", "(float) Airflow rate [m3/h] (SI)."),
        _Port("annual_runtime_", "annual_runtime_min_yr", "(float) Annual runtime [min/yr]."),
    ],
    "hot_water_heaters": [
        _Port("name_", "name", "(str) Heater name."),
        _Port("type_", "heater_type", "(str) Type (single-select label)."),
    ],
    "hot_water_tanks": [
        _Port("name_", "name", "(str) Tank name."),
        _Port("type_", "tank_type", "(str) Type (single-select label)."),
        _Port("quantity_", "quantity", "(int) Quantity."),
        _Port("heat_loss_rate_", "heat_loss_rate_w_k", "(float) Heat-loss rate [W/K] (SI)."),
        _Port("volume_", "size_l", "(float) Volume / size [liters]."),
        _Port("inside_outside_", "inside_outside", "(str) Inside / Outside (single-select label)."),
        _Port("location_temp_", "location_temp_c", "(float) Location temp [deg C] (SI)."),
        _Port("water_temp_", "water_temp_c", "(float) Water temp [deg C] (SI)."),
    ],
    "electric_heaters": [
        _Port("name_", "name", "(str) Heater name."),
        _Port("wattage_", "watt", "(float) Wattage [W] (SI)."),
    ],
    "appliances": [
        _Port("name_", "name", "(str) Appliance name."),
        _Port("type_", "appliance_type", "(str) Type (single-select label)."),
        _Port("quantity_", "quantity", "(int) Quantity."),
        _Port("model_", "model", "(str) Model."),
        _Port("manufacturer_", "manufacturer", "(str) Manufacturer."),
        _Port("energy_star_", "energy_star", "(str) EnergyStar (single-select label)."),
        _Port("capacity_", "capacity_m3", "(float) Capacity [m3] (SI)."),
        _Port("cef_", "cef", "(float) Combined Energy Factor."),
        _Port("imef_", "imef", "(float) Integrated Modified Energy Factor."),
        _Port("mef_", "mef", "(float) Modified Energy Factor."),
        _Port("annual_energy_", "annual_energy_kwh", "(float) Annual energy use [kWh/yr]."),
    ],
}


def _classify_table(_type):
    # type: (str | None) -> str
    """The one place the table taxonomy lives; both phases dispatch off it."""
    if not _type:
        return _UNKNOWN
    if _type in DEFERRED_TABLES:
        return _DEFERRED
    if _type in OUTPUT_SPECS:
        return _MAPPED
    if _type in PASSTHROUGH_TABLES:
        return _PASSTHROUGH
    return _UNKNOWN


def get_component_outputs(_type):
    # type: (str | None) -> Dict[int, ComponentOutput]
    """Build the `{index: ComponentOutput}` map the `src/` wrapper feeds to
    `gh_io.setup_component_outputs` to (re)name the dynamic output ports.

    Index 1 (`report_`) is a fixed port the ghuser owns, so it is not returned
    here; the data ports start at `DATA_PORT_START_INDEX`. Deferred / unknown
    tables return `{}` so every data port blanks to `-`.
    """
    kind = _classify_table(_type)
    if kind == _MAPPED:
        return {DATA_PORT_START_INDEX + i: port for i, port in enumerate(OUTPUT_SPECS[_type])}
    if kind == _PASSTHROUGH:
        return {DATA_PORT_START_INDEX: PASSTHROUGH_PORT}
    return {}  # deferred / unknown -> no data ports


def _flatten_option(_value):
    # type: (Any) -> Any
    """Single-select values arrive as `{"id", "label"}` (O6) - emit the label."""
    if isinstance(_value, dict) and "id" in _value and "label" in _value:
        return _value.get("label")
    return _value


class GHCompo_PHNavV1OrganizeTable(object):
    """Reshape one downloaded element table into per-table, named output lists.

    Consumes the `records_` + `field_defs_` + `table_name_` from `Get Table`. The
    dynamic output ports are configured in the `src/` wrapper (see
    `get_component_outputs`); this class only produces `{port_name: [values]}`
    plus a `report_` list flagging any downloaded column that no port consumed
    (so nothing is silently dropped).
    """

    def __init__(self, _IGH, _records, _field_defs, _type, *args, **kwargs):
        # type: (gh_io.IGH, List | None, List | None, str | None, *Any, **Any) -> None
        self.IGH = _IGH
        self.records = _records or []
        self.field_defs = _field_defs or []
        self.type = _type

    @property
    def ready(self):
        # type: () -> bool
        return bool(self.type)

    def run(self):
        # type: () -> Dict[str, list]
        """Map each output port across all records. Keyed by port name (+ `report_`)."""
        if not self.ready:
            return {}

        kind = _classify_table(self.type)
        if kind == _DEFERRED:
            self.IGH.error(
                "Organize for '{}' is not implemented yet (heat-pump joins are deferred).".format(self.type)
            )
            return {}
        if kind == _UNKNOWN:
            self.IGH.error(
                "Unknown table type '{}'. It has no organize mapping and is not an allowlisted table.".format(self.type)
            )
            return {}
        if kind == _PASSTHROUGH:
            self.IGH.warning(
                "No organize mapping for '{}'; passing the raw records through unchanged.".format(self.type)
            )
            return {PASSTHROUGH_PORT.name: list(self.records), REPORT_PORT_NAME: self._report([], {})}

        spec = OUTPUT_SPECS[self.type]
        result = {port.name: [self._resolve(r, port.field_key) for r in self.records] for port in spec}
        result[REPORT_PORT_NAME] = self._report(spec, result)
        return result

    def _resolve(self, _record, _field_key):
        # type: (Any, str) -> Any
        """Pull one field from a record: built-in column first, then `custom_values`."""
        if _field_key in _record:
            return _flatten_option(_record[_field_key])
        custom_values = _record.get("custom_values") or {}
        return _flatten_option(custom_values.get(_field_key))

    def _present_field_keys(self):
        # type: () -> List[str]
        """Every data column that actually appears in the records, in first-seen
        order (built-in columns + `custom_values` keys; structural keys skipped)."""
        structural = ("id", "custom_values", "custom_links")
        seen = set()
        keys = []
        for record in self.records:
            for key in list(record.keys()) + list((record.get("custom_values") or {}).keys()):
                if key in structural or key in seen:
                    continue
                seen.add(key)
                keys.append(key)
        return keys

    def _display_names(self):
        # type: () -> Dict[str, str]
        """`{field_key: display_name}` from `field_defs`, for a readable report."""
        names = {}
        for field_def in self.field_defs:
            key = field_def.get("field_key")
            if key:
                names[key] = field_def.get("display_name") or key
        return names

    def _report(self, spec, result):
        # type: (List[_Port], Dict[str, list]) -> List[str]
        """Flag gaps: ports that resolved to nothing, and downloaded columns that
        no port consumed - so nothing is silently dropped (README no-silent-caps).
        Reads the already-resolved `result` rather than re-resolving every field."""
        notes = ["{} record(s), {} output port(s).".format(len(self.records), len(spec))]

        empty_ports = [port.name for port in spec if all(value is None for value in result[port.name])]
        if self.records and empty_ports:
            notes.append("Ports with no data (field unset or missing server-side): " + ", ".join(empty_ports))

        mapped_keys = set(port.field_key for port in spec)
        unmapped = [key for key in self._present_field_keys() if key not in mapped_keys]
        if unmapped:
            display_names = self._display_names()
            pretty = ["{} ({})".format(display_names.get(key, key), key) for key in unmapped]
            notes.append("Downloaded columns not mapped to an output port: " + ", ".join(pretty))

        notes.append("Values are raw SI (units in each port's description); convert downstream as needed.")
        return notes
