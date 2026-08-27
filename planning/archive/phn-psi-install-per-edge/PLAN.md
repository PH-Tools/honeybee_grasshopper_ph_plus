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

## Phase 02 — Build Install Types, the `install_types_` output, and key matching

**Files (HBPH+):** a new `v1/install_types_build.py`; `v1/apertures_get.py`;
`honeybee_grasshopper_ph_plus/src/HBPH+ - PH-Nav Get Apertures.py`.

**Files (base repo, `honeybee_grasshopper_ph`):**
`honeybee_ph_rhino/gh_compo_io/apertures/win_set_psi_install_values.py`;
`honeybee_grasshopper_ph/src/HBPH - Set Aperture Psi-Installs.py` (docstring only).

- **New builder** (`install_types_build.py`): walk the parsed aperture types,
  pool one `PhApertureInstallType` per distinct identifier (D-3 content-keying
  for mulls, D-4 explicit assignment for defaults), and return
  `{element_type_name: [top, right, bottom, left]}`.
- **Getter output:** `GHCompo_PHNavV1GetApertures.run()` returns a fifth value,
  `install_types_`, as a `CustomCollection.from_dict(...)`. Empty collection when
  no element carried an `installs` block. Facade gains the output, its docstring
  entry, and the unpack line.
- **Base setter learns key matching (D-2):** `as_keyed_lookup` detects a single
  dict-like item in `_install_types` and switches from branch-index matching to
  per-Aperture matching on `display_name`. Preserves input tree paths on that path;
  warns via `IGH` for unmatched or short entries and passes those Apertures through
  untouched. The DataTree path is unchanged, and the component facade is unchanged,
  so no `.ghuser` rebuild is needed for it.
- **`.ghuser` rebuild — Ed's manual step, HBPH+ only.** `PH-Nav Get Apertures`
  gained an output. fsdeploy does not touch user-objects. This is the one gate an
  agent cannot close.

**Tests** (HBPH+, stubbing the Rhino deps via `sys.modules`):

- the BT 1234 fixture payload produces the two expected four-item lists;
- one `PhApertureInstallType` instance is shared across every `apit_default` edge;
- mull identifiers are stable across two runs of the same payload;
- **contract tests against the base setter** — loaded from the sibling repo, skipped
  if it is not checked out, because the base repo hosts no tests by policy (its
  `CONTRIBUTING.md`). These pin: the collection is recognised as a keyed lookup, a
  **flat** aperture list gets per-element values (the regression for D-2), tree
  topology does not change the answer, input paths survive, unmatched and short
  entries warn rather than half-apply, and the branch-index path still works.

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
- `honeybee_ph_plus_rhino/gh_compo_io/ph_navigator/.index.md` — the new
  `v1/install_types_build.py` module and the `install_types_` output, plus a
  pointer to the base repo's setter as its consumer.
- `context/` — fold the accepted outcome in, per `planning/README.md` rule 1.
- `planning/STATUS.md` — update the row.
- On completion, move this folder to `planning/archive/phn-psi-install-per-edge/`
  unchanged and add a row to `planning/archive/README.md` (flat by slug, never
  nested by date).

In `ph-navigator-v2`:
- `planning/features_v1.1/aperture-psi-install/STATUS.md` — phase 07 row already
  points here; mark it closed. Its `phases/phase-07-gh-client-per-edge.md` §3 is
  superseded by D-1, recorded in that row rather than by editing a dated doc.
