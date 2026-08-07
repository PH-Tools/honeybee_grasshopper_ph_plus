# infiltration-from-ach-units

**Status:** Implemented — automated verification passed
**Opened:** 2026-08-06
**Component:** `HBPH+ - Infiltration from ACH`
**File:** `honeybee_ph_plus_rhino/gh_compo_io/hb_tools/infiltration_from_ach.py`

## Summary

The component's second output is declared as a flow **per exterior area** but returns a
**total** volumetric flow. It is wrong by a factor of the building's exposed envelope area —
roughly 260x on a small house, and it scales with building size.

Found while investigating an unrelated ACH bug in PHX. See "Not the same bug" below.

## The defect

The GH component unpacks two outputs, both named `infilt_per_exterior_…`, so both should be
`M3/S-M2`:

```python
# honeybee_grasshopper_ph_plus/src/HBPH+ - Infiltration from ACH.py:85
infilt_per_exterior_at_4Pa_, infilt_per_exterior_at_50Pa_ = gh_compo_interface.run()
```

`run()` returns `(infiltration_rate_at_4Pa, infiltration_rate_at_50Pa)`, but the second value
comes from `calculate_infiltration_rate_at_test_pressure()`, which **prints** the normalized
rate and **returns** the un-normalized total:

```python
q50 = n_50 * volume_m3 / 3600.0        # m3/s -- TOTAL, not per-area
print(... q50 / envelope_area_m2 ...)  # prints the correct M3/S-M2 value
return q50                             # <-- returns the TOTAL
```

The printout is right, which is what makes this hard to catch by eye: the Grasshopper output
panel shows the correct number while the socket carries a different one.

### Measured

`1 ACH50`, net volume `300 m³`, exposed envelope `260 m²`:

| output | value | unit | correct? |
|---|---|---|---|
| `infilt_per_exterior_at_4Pa_` | `0.00006207` | M3/S-M2 | ✓ |
| `infilt_per_exterior_at_50Pa_` | `0.08333` | **M3/S (total)** | ✗ — should be `0.00032051` |

Returned ratio between the two outputs is **1343x**. The correct ratio is
`1 / (4/50)^0.65 = 5.16x`. Any ratio far from 5.16 is the signature of this bug.

Sanity anchor for the correct values: `0.00032051 M3/S-M2` = `0.063 CFM/ft²@50Pa`, dropping to
`0.0122 CFM/ft²@4Pa`.

## Impact

The `4Pa` output — the one wired into `Infiltration.flow_per_exterior_area` for the energy
model — is **correct**. Only the `50Pa` output is affected.

That output is the natural one to use for an airtightness compliance check against a Phius
limit expressed in CFM/ft². Anyone doing so gets a number several hundred times too large,
which is obvious enough to catch immediately rather than ship — but it should not be wrong.

## Fix

`calculate_infiltration_rate_at_test_pressure()` must keep returning the total, because
`calculate_infiltration_rate_at_resting_pressure()` normalizes by envelope area internally.
Normalize at the return site instead, and rename the local so the units are legible where it
is used:

```python
# run()
q50_total_m3s = self.calculate_infiltration_rate_at_test_pressure(
    self.ach_at_50Pa, vn50_m3, exposed_area_m2,
)
infiltration_rate_at_4Pa = self.calculate_infiltration_rate_at_resting_pressure(
    q50_total_m3s, exposed_area_m2, ...
)
return infiltration_rate_at_4Pa, q50_total_m3s / exposed_area_m2
```

### Two secondary cleanups in the same file

1. **Mislabelled print** in `calculate_infiltration_rate_at_resting_pressure()`. It prints
   `q_rest_area` (a per-area rate) as *"Total Leakage Airflow … M3/S [CFM]"* and converts it
   to CFM as though it were a total. Doubly wrong, and it is the line someone would read while
   verifying exactly this calculation. The second print, labelled `M3/S-M2`, is correct.
2. **The density round-trip is a no-op.** `run()` passes `air_density_kg_m3=1.0` against the
   function's `1.2041` default, but `rho` cancels algebraically — verified, both give
   `0.00006207`. The whole mass-flow derivation reduces to:

   ```
   q_rest_area = (q50 / A) * (P_rest / P_50) ** n
   ```

   Harmless today, but it is ~15 lines implying a precision that is not there, and the
   mismatched argument invites someone to "correct" it and assume the result changed. Either
   collapse it to the closed form or drop the density parameter.

## Test

```python
def test_output_pressure_ratio():
    """The two outputs differ ONLY by the power-law pressure correction."""
    at_4Pa, at_50Pa = component.run()
    assert at_50Pa / at_4Pa == pytest.approx((50.0 / 4.0) ** 0.65, rel=1e-6)
```

This is the assertion that fails today (it returns ~1343 instead of ~5.16) and it stays valid
regardless of how the internals are refactored. Worth a second test pinning the absolute
`M3/S-M2` value for a known volume/area, so a future change to the normalization is caught.

## Not the same bug

Do not conflate this with the ACH defect in PHX `from_HBJSON/create_rooms.py:63`, which
understates **ventilation** (outdoor-air supply) by 3600x. Different load, different repo,
different mechanism:

| | this | PHX `create_rooms.py:63` |
|---|---|---|
| Honeybee load | `Infiltration` (envelope leakage) | `Ventilation` (outdoor air) |
| Error | returns total instead of per-area | double `/3600` conversion |
| Magnitude | x envelope area (~260x) | 3600x |
| Real-project exposure | 50Pa output only | none — 0 of 37 projects |

They do share a root cause worth noting: **a function returning bare numbers whose units live
only in a docstring, assigned to a local whose name contradicts them.** Here,
`q50` (a total) becomes `infiltration_rate_at_50Pa` and reaches a socket named
`per_exterior`. In PHX, a flow becomes `air_changes_per_hour` and gets divided by 3600 again.
Same failure twice, in two repos.

Mitigation worth considering across both: return `NamedTuple`s with unit-bearing field names
(`flow_by_ach_m3s`, `q50_total_m3s`) rather than positional tuples of floats. Makes this class
of bug unwritable instead of merely findable.

## Implementation

Implemented 2026-08-06 in `infiltration_from_ach.py`:

- `run()` now keeps the blower-door flow in `q50_total_m3s` and divides by exposed envelope
  area only for the 50 Pa per-area output.
- The 4 Pa calculation uses the equivalent closed-form pressure law. The density argument is
  retained as a documented no-op for compatibility with callers of the published component.
- The incorrect 4 Pa total-flow diagnostic was removed; the remaining diagnostic is labelled
  and converted as `M3/S-M2` / `CFM/FT2`.
- `tests/test_infiltration_from_ach.py` covers the pressure ratio and the absolute 300 m3 /
  260 m2 normalization anchor using dependency stubs.

Verification:

- `.venv/bin/python -m pytest tests/test_infiltration_from_ach.py -q` — `2 passed`.
- `.venv/bin/python -m pytest -q` — `3 passed` across the full repository test suite.
- `git diff --check` — passed.
- Black formatted the maintained Python code after `honeybee_grasshopper_ph_plus/` was
  excluded as Grasshopper-scraped source. Ruff was skipped at user direction.
