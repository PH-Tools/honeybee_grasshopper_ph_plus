# PLAN — Per-edge Ψ-Install into Rhino / Grasshopper

```
DATE:    2026-08-26
TIME:    17:45
STATUS:  Accepted — D-1 confirmed, D-2 revised, preconditions all verified closed
AUTHOR:  Ed May + Claude
SCOPE:   Implementation sequence. All code lands in honeybee_grasshopper_ph_plus.
RELATED: PRD.md, decisions.md, research.md
```

All three phases are in this repo. IronPython 2.7 only (no f-strings, no
dataclasses, no `:=`), the V0 schema stays frozen, component pattern per
`context/ARCHITECTURE.md`.

Repo-level preconditions — **all verified closed 2026-08-26**:

- **Base-package components available.** HBPH+ is not a pip package and has no
  `requirements.txt` (`context/TECH_STACK.md`: imports resolve against sibling
  PH-Tools packages on the Rhino Python path). The check is therefore against the
  deployed install, not a pin. Verified present:
  `~/ladybug_tools/python/lib/python3.10/site-packages/honeybee_ph_rhino/gh_compo_io/apertures/`
  carries `win_create_install_type.py` and `win_set_psi_install_values.py`, and
  `.../Grasshopper (…)/UserObjects/honeybee_grasshopper_ph/HBPH - Set Aperture Psi-Installs.ghuser`
  exists. Upstream is released: PR #60 is contained in `honeybee_grasshopper_ph`
  v1.33.0.
- **Route-3 `installs` block is live** on `localhost:8000` (BT 1234, re-confirmed
  by direct request 2026-08-26). Re-confirm against `api.ph-nav.com` before a
  non-DEV component points at production.
- **Test harness.** The repo `.venv` carries only tooling and .NET stubs — no
  `honeybee_ph` / `honeybee_energy`. Phase 01's tests are pure-dict and run as
  is; Phase 02's need `honeybee_energy_ph.construction.window` stubbed following
  the `sys.modules` pattern in `tests/test_win_create_types.py`. Budgeted in
  Phase 02 below.

---

## Phase 01 — Parse `installs`

**Files:** `honeybee_ph_plus_rhino/gh_compo_io/ph_navigator/v1/window_types_schema.py`

- Add `InstallData` (`install_type_id`, `name`, `psi_install_w_mk` via `_as_float`,
  `source`) and `InstallsData` (four sides + `get_install_by_side` +
  `get_all_installs`), shaped like the existing `FrameData` / `FramesData` pair at
  `:212-316` — including `__copy__`, `__str__`, `__repr__`, `ToString`.
- `ElementData` gains `installs`, set to `None` when the key is absent so an old
  payload is unchanged. Thread it through `ElementData.__copy__` — the copy is
  load-bearing, `reverse_elements_row_order` runs every element through it.
- Docstring note on `FrameType.psi_install_w_mk` (`:151-167`): the `0.04` fallback
  is now legacy-only; a current server always sends the uniform project default
  here and the per-edge truth in `installs`.

**Tests:** payload with `installs` parses all four sides including the
`null`-id mull; payload without `installs` yields `installs is None`; a side-order
test that pins "row reversal does not touch side names" (PRD §3.1).

**Ships nothing user-visible.** Pure parse.

## Phase 02 — Build Install Types, the `install_types_` output, and the setter component

**Files:** a new `v1/install_types_build.py`; a new `v1/apertures_set.py`;
`v1/apertures_get.py`; `v1/__init__.py` (re-export the new `GHCompo_*`);
`gh_compo_io/ph_navigator/__init__.py` (same); a new
`honeybee_grasshopper_ph_plus/src/HBPH+ - PH-Nav Set Apertures.py`;
`honeybee_grasshopper_ph_plus/src/HBPH+ - PH-Nav Get Apertures.py`;
`honeybee_ph_plus_rhino/_component_info_.py` (new entry for the new component);
an icon in `icons/`.

- **New builder** (`install_types_build.py`): walk the parsed aperture types,
  pool one `PhApertureInstallType` per distinct identifier (D-3 content-keying
  for mulls, D-4 explicit assignment for defaults), and return
  `{element_type_name: [top, right, bottom, left]}`.
- **Getter output:** `GHCompo_PHNavV1GetApertures.run()` (`:78-98`) returns a
  fifth value, `install_types_`, as a `CustomCollection.from_dict(...)`. Empty
  collection when no element carried an `installs` block. Facade gains the
  output, its docstring entry, and the unpack line.
- **New component** (`apertures_set.py` → `GHCompo_PHNavV1SetApertures`, D-2):
  inputs `_apertures` (DataTree) + `_install_types` (CustomCollection). For each
  aperture, look up the collection by the aperture's `display_name`, duplicate
  the aperture, and set the four `properties.ph.install_types` slots. Preserve
  the input tree structure. Emit a `report_` listing apertures whose name matched
  no key; pass those through unchanged rather than raising. No key or an empty
  collection ⇒ apertures pass through untouched.
  Follow the `win_set_psi_install_values.py` shape for the DataTree handling, but
  match on key rather than branch index.
- **`.ghuser` rebuild — Ed's manual step in Grasshopper.** Two user-objects now:
  the regenerated `PH-Nav Get Apertures` facade (new output) and the brand-new
  `PH-Nav Set Apertures`. fsdeploy does not touch user-objects. This is the one
  gate an agent cannot close.

**Tests** (stub `honeybee_energy_ph` / `honeybee_ph` via `sys.modules` per
`tests/test_win_create_types.py`):

- the BT 1234 fixture payload produces the two expected four-item lists;
- one `PhApertureInstallType` instance is shared across every `apit_default` edge;
- mull identifiers are stable across two runs of the same payload;
- the setter assigns per-element values correctly from a **flat** aperture list
  (the topology that breaks the rejected branch-index route — this is the
  regression test for D-2);
- an aperture whose name is not in the collection lands in `report_` and comes
  out unmodified.

## Phase 03 — Honest EP U-factor + canvas verification

**Files:** `v0/window_types_get.py` (`create_new_hbph_window_material` `:182-191`,
`create_hbph_ep_constructions` `:194-221`) — or a V1 fork of those two functions if
the repo's V0-frozen rule applies; `ph_navigator/.index.md` marks `v0/` **frozen,
"do not change behavior"**, so the acceptable in-place edit is an *optional*
parameter defaulting to today's behavior. If that cannot be kept clean, fork to
`v1/`.

- Pass the element's `installs` into construction building; inside the material
  builder, duplicate the frame, overwrite each side's `psi_install` from the
  resolved value, call `iso_10077_1.calculate_standard_window_uw` on the
  duplicate, discard it. `prop_ph.ph_frame` keeps the type defaults (D-1, D-5).
  `PhWindowFrame.__copy__` deep-copies all four elements, so the overwrite cannot
  reach the shared `PhWindowFrameElement` pool — verified, see D-5.
- While in this function: `calculate_window_uw` is deprecated upstream in favor of
  `calculate_standard_window_uw`. Switching is a one-line, behavior-identical
  change and silences a `DeprecationWarning` on every Rhino run.
- Do **not** take up the standard-size-vs-element-size question here (PRD §5.1).

**Verification:** the full acceptance list in PRD §4, run live against BT 1234 on
`localhost:8000`, then once against a real project with painted Install Types.
Finish with the HBJSON round-trip and a PHX → PHPP write showing `0.0` on the
mulled rows.

---

## Docs to close out

Here:
- `honeybee_ph_plus_rhino/gh_compo_io/ph_navigator/.index.md` — two new modules
  (`v1/install_types_build.py`, `v1/apertures_set.py`), the new
  `install_types_` output, and the new component.
- `context/` — fold the accepted outcome in, per `planning/README.md` rule 1.
- `planning/STATUS.md` — update the row.
- On completion, move this folder to `planning/archive/phn-psi-install-per-edge/`
  unchanged and add a row to `planning/archive/README.md` (flat by slug, never
  nested by date).

In `ph-navigator-v2`:
- `planning/features_v1.1/aperture-psi-install/STATUS.md` — phase 07 row already
  points here; mark it closed. Its `phases/phase-07-gh-client-per-edge.md` §3 is
  superseded by D-1, recorded in that row rather than by editing a dated doc.
