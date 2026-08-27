# PRD — Per-edge Ψ-Install into Rhino / Grasshopper

```
DATE:    2026-08-26
TIME:    17:45
STATUS:  Accepted — trace re-verified against the code and the live API 2026-08-26
AUTHOR:  Ed May + Claude
SCOPE:   Trace + design contract for the GH-client half of aperture-psi-install
RELATED: README.md, decisions.md, PLAN.md, research.md;
         cross-repo: ph-navigator-v2/planning/features_v1.1/aperture-psi-install/upstream-alignment.md
```

> **Review note, 2026-08-26.** Every claim below was re-checked against the
> working tree and against a live `GET /api/v1/gh/projects/1234/aperture-types`.
> The trace held; §4.6's `1.3011` → `1.2686` and §5.1's ~7% gap were reproduced
> against the real `ISO100771Data`. Two things changed: §3.3's delivery mechanism
> (see decisions.md D-2) and the cited line numbers, which had drifted 2-6 lines.

## 1. The observed symptom

Canvas: `/Users/em/Desktop/psi-install-test.ghx`, project `Psi-Install-Test`
(BT `1234`, id `8e19b467-35f5-44c1-9d01-6606c8c46402`), one aperture type
"Test Aperture", two elements side by side, so one interior mulled joint.

The canvas prints, for every construction:

```
Psi-Install Values (W/mk)
Top: 0.04   Right: 0.04   Bottom: 0.04   Left: 0.04
```

Expected, from PHN's own Installs sub-tab: element `C0_R0` should read
`right = 0.0` (mull) and element `C1_R0` should read `left = 0.0` (mull).

## 2. The trace — six links, one break

Verified 2026-08-26 by reading each link and calling the live local API, and
re-verified the same day during code review. Line numbers below are as of
that second pass.

### 2.1 PHN document → route 3 — ✅ correct

`backend/features/gh_api/aperture_types_export.py:_element()` emits, per glazed
element, both a `frames` block and an additive `installs` block. Live response
for BT 1234 (abridged, element `A` at column 0):

```json
"frames": { "top": { "frame_type": { "psi_install_w_mk": 0.04, ... } }, ... },
"installs": {
  "top":    { "install_type_id": "apit_default", "name": "Default", "psi_install_w_mk": 0.04, "source": "default" },
  "right":  { "install_type_id": null,           "name": null,      "psi_install_w_mk": 0.0,  "source": "mull"    },
  "bottom": { "install_type_id": "apit_default", "name": "Default", "psi_install_w_mk": 0.04, "source": "default" },
  "left":   { "install_type_id": "apit_default", "name": "Default", "psi_install_w_mk": 0.04, "source": "default" }
}
```

Element `B` at column 1 is the mirror: `left` is the mull, `right` is default.
The data is complete and correct, mull included. **PH-Navigator is done.**

Note the deliberate asymmetry, documented in that module's docstring as decision
D-5 of the PHN packet: `frames.{side}.frame_type.psi_install_w_mk` always
carries the **uniform project default**, never a per-edge value, precisely so
that an old GH client which shares one frame element across edges cannot
misapply it. `0.04` in the canvas is that uniform default arriving intact. The
client is reading exactly the field it was designed to read; it is just the
wrong field now.

### 2.2 Route 3 → GH schema — ❌ **this is the break**

`honeybee_ph_plus_rhino/gh_compo_io/ph_navigator/v1/window_types_schema.py`

`ElementData.from_dict` (`:349-363`) parses `name`, `row_number`,
`column_number`, `col_span`, `row_span`, `glazing`, `frames`. It does not parse
`installs`. There is no `InstallData` class in the file and no reference to the
payload key anywhere in the repo. The block is silently discarded at parse time.

(The only `psi_install` writes elsewhere in HBPH+ are in the unrelated Airtable
path, `gh_compo_io/airtable/create_window_constructions.py:219-224` — see
decisions.md D-1.)

The only Ψ-install the schema carries is `FrameType.psi_install_w_mk`
(`:165`), read from the legacy uniform field with a `0.04` fallback.

### 2.3 GH schema → HBPH frame elements — ⚠️ correct but load-bearing

`v0/window_types_get.py:create_new_hbph_frame_elements()` (`:85-109`) builds one
`PhWindowFrameElement` per **frame-product name** and shares that single
instance across every edge of every element that uses the product. With one
uniform Ψ per product that is right and efficient. It is also the reason D-5
exists: writing a per-edge value into this pool would leak one edge's Ψ onto
every other edge using the same frame product.

`create_new_hbph_frames()` (`:112-135`) then builds one `PhWindowFrame` per
element, keyed `"{type}_C{col}_R{row}"` — so `Test Aperture_C0_R0`,
`Test Aperture_C1_R0`, matching Ed's panel. The same format is the
`NAME_FORMAT` of `hb_tools/win_create_geom.py:36`, which is why the
`srfc_names_` keys line up.

### 2.4 Construction → EnergyPlus U-factor — ⚠️ carries the default Ψ

`create_new_hbph_window_material()` (`:182-191`) computes the
`EnergyWindowMaterialSimpleGlazSys` U-factor with
`iso_10077_1.calculate_window_uw(frame, glazing)`. That function **includes**
`heat_loss_psi_install` (`honeybee_ph_utils/iso_10077_1.py`,
`ISO100771Data.uw`), evaluated on the ISO 10077-2 Annex F standard-size window
(1.23 m × 1.48 m), using whatever `psi_install` the frame elements carry — today
the uniform default. So the number EnergyPlus actually simulates already depends
on Ψ-install, and today it is the wrong one on mulled edges.

Two consequences worth separating:

- **Wrong Ψ.** Fixable, and in scope (see §3.3).
- **Standard size, not element size.** PHN computes its own installed U-value at
  the element's real dimensions (`backend/features/aperture_u_value/service.py`,
  `_calculate_element_detail`, `_edge_breakdown`), while the GH client uses the
  1.23 × 1.48 reference window. These will not agree even after the Ψ fix. Out
  of scope, raised as an open question in §5.

### 2.5 HB Aperture → HBJSON — ✅ landing zone exists and is empty

`honeybee_ph/properties/aperture.py` has `AperturePsiInstalls` with four
optional `PhApertureInstallType` slots (`top`/`right`/`bottom`/`left`),
serialized under `install_types` only when at least one side is assigned, with a
`.get()` guard for older HBJSON. Nothing writes to those slots in the PH-Nav
path today, so they stay empty and every edge inherits the construction default.

### 2.6 HBJSON → PHX → PHPP / WUFI — ✅ ready and waiting

- `honeybee_ph_utils/aperture_psi_install.py` — `resolve_psi_install_values()`
  and `resolve_effective_frame()`: assigned Install Type wins, otherwise inherit
  the construction frame element. No hidden defaults.
- `PHX/from_HBJSON/create_building.py:221` calls
  `aperture_psi_install.resolve_psi_install_values(_hb_aperture)`, so per-row
  PHPP Ψ-install and WUFI/METr window-type variant synthesis both key off the
  aperture slots.
- `honeybee_grasshopper_ph/src/HBPH - Set Aperture Psi-Installs.py` +
  `HBPH - Create Aperture Install Type.py` exist and are merged. The setter takes
  a DataTree of up to four items per branch in **top / right / bottom / left**
  order, accepts either `PhApertureInstallType` objects or bare numbers, matches
  branches to the aperture branches, duplicates the apertures, and never touches
  the construction.

**Conclusion:** every link is built except §2.2. The entire fix is parsing the
`installs` block and delivering it in the shape the merged setter already wants.

## 3. Design

### 3.1 Parse the block (schema)

Add to `v1/window_types_schema.py`:

- `InstallData` — `install_type_id` (str or `None`), `name` (str or `None`),
  `psi_install_w_mk` (float, via the existing `_as_float`), `source` (str).
- `InstallsData` — the four-sided container, parallel to `FramesData`
  (`:258-316`), with `get_install_by_side(side)` and `get_all_installs()`.
- `ElementData.installs` — populated from `_data_dict.get("installs")`, and
  `None` when the key is absent so an older server keeps today's behavior
  byte for byte.

Side names need no row flipping. `reverse_elements_row_order` (`:458-472`)
changes an element's **row index** for Rhino's bottom-to-top build order; the
grid is re-indexed, not mirrored, so an element's own top edge is still its top
edge. Left/right are likewise unmoved. The existing `frames` path already relies
on this — `create_new_hbph_frames` `setattr`s side names straight through — so
`installs` inherits proven behavior. Stated explicitly because the row reversal
is the standing trap in this file, and a test should pin it (§4).

### 3.2 Build one `PhApertureInstallType` per distinct library row

Mapping is fixed by the PHN packet's `upstream-alignment.md` and is 1:1:

| Route-3 field | `PhApertureInstallType` |
| --- | --- |
| `install_type_id` (`apit_*`) | `identifier`, verbatim — preserves PHN round-trip identity |
| `name` | `display_name` |
| `psi_install_w_mk` | `psi_install` |
| `source` | `source` (free text) |

Mulled edges arrive with `install_type_id: null` and `name: null`, so they need
a synthetic, **content-keyed** identifier rather than a uuid — see D-3. They are
otherwise ordinary zero-Ψ Install Types; honeybee-ph deliberately has no mull
concept and edge adjacency stays PHN's business.

Build the types into a pool keyed by identifier so a project with one Install
Type across 200 windows produces one object, not 200.

### 3.3 Deliver them — one new output, one new component, plus an honest U-factor

> Revised 2026-08-26. The original plan routed the collection through
> `HBPH+ - Get From Custom Collection` into `HBPH - Set Aperture Psi-Installs`.
> That does not work; decisions.md D-2 carries the full reasoning. The short
> version: the setter matches by **branch index** and gives every aperture in a
> branch the same four Install Types, while `srfc_names_` is a flat list — so
> the whole model would take element A's values, silently.

**New output on `HBPH+ - PH-Nav Get Apertures`: `install_types_`.**

A `CustomCollection` keyed by the **same** element type-name as
`constructions_` (`Test Aperture_C0_R0`, …), whose value is the ordered list
`[top, right, bottom, left]` of `PhApertureInstallType`.

**New component: `HBPH+ - PH-Nav Set Apertures`.**

Inputs `_apertures` (a DataTree of Honeybee Apertures) and `_install_types`
(that collection). For each aperture it looks the key up from the aperture's own
`display_name`, duplicates the aperture, and writes the four slots on
`properties.ph.install_types`. Output is the duplicated apertures in the input
tree structure, plus a `report_` of any aperture whose name found no key.

Key-based lookup is immune to tree topology, which is the whole point: the
aperture already carries the key that `HBPH+ - Create Window Geometry` stamped
on its geometry (`NAME_FORMAT = "{}_C{}_R{}"`), so no grafting, flattening, or
branch bookkeeping is required of the user, and a mismatch is reported rather
than silently mis-applied.

`HBPH - Set Aperture Psi-Installs` in the base repo remains the right tool for
hand-painting an install condition across a branch of windows. This is the bulk
PH-Nav path, not a replacement for it.

**And: compute the EP U-factor from the resolved per-edge Ψ.**

In `create_new_hbph_window_material`, build a **transient** effective frame —
duplicate the element's `PhWindowFrame`, overwrite each side's `psi_install`
from the `installs` block, use it for the ISO 10077-1 call, and throw it away.
The persisted `prop_ph.ph_frame` keeps the type-default values.

This mirrors `resolve_effective_frame()` upstream, which does exactly this for
the same reason. It means the EnergyPlus-visible U-factor reflects the real
install condition without the construction ever carrying instance data — the
thing `honeybee_grasshopper_ph` issue #59 forbids.

### 3.4 What this deliberately does not do

It does not write per-edge Ψ into `prop_ph.ph_frame`. So Ed's current probe —

```python
print "Top:", const.properties.ph.ph_frame.top.psi_install
```

— will keep printing the type default `0.04` after this work, **by design**. The
construction is the default layer; the aperture is the instance layer. The
revised probe is on the aperture, and the canvas verification in §4 uses it.

**A second, related divergence to expect.** After §3.3's U-factor fix, the
construction's `prop_ph.ph_frame` (uniform `0.04`) and the EP material's
U-factor (mull-aware) describe different windows. Anything that recomputes Uw
from the construction alone reads `1.3011`, while EnergyPlus simulates `1.2686`.
That is correct: aperture-aware consumers go through
`aperture_psi_install.resolve_effective_frame()` and get the same answer
EnergyPlus does. Noted so it is not mistaken for a bug later.

## 4. Acceptance

> **Result, 2026-08-26.** Items 1, 2, 6 and 7 are **verified** — run against the
> live route-3 response for BT 1234 on `localhost:8000`, driving the real build
> pipeline with the real `honeybee_energy_ph` / `honeybee_ph_utils` (not stubs).
> Items 3 and 4 were **confirmed by Ed on the canvas** the same day (DEV-mode
> GHPython, before the user-object rebuild), and item 8 was confirmed as a
> PHX → **WUFI** write placing Ψ=0 on the mulled edge. Item 5 (explicit HBJSON
> round-trip) has not been exercised on its own. Evidence:
>
> ```
> Test Aperture_C0_R0   t/r/b/l = [0.04, 0.0, 0.04, 0.04]
>                       ids     = [apit_default, PhApertureInstallType_0.0000, apit_default, apit_default]
>                       sources = [default, mull, default, default]
> Test Aperture_C1_R0   t/r/b/l = [0.04, 0.04, 0.04, 0.0]
> distinct PhApertureInstallType instances: 2   (8 edges, pooled)
>
> EP U-factor   before = 1.3011   after = 1.2686   (both constructions)
> persisted ph_frame keeps the 0.04 type default on every edge: True
> shared PhWindowFrameElement pool untouched:                    True
> ```
>
> 35 unit tests cover the same ground against stubs, including the flat-list
> regression that pins D-2 and the shared-frame-element leak that would re-open #59.

Against BT `1234` on `http://localhost:8000`, both elements 1.0 m × 1.0 m,
50 mm frame, U-f 1.5, U-g 1.0, Ψ-g 0.04:

1. `install_types_` contains two keys. `Test Aperture_C0_R0` →
   `[0.04, 0.0, 0.04, 0.04]` (t/r/b/l). `Test Aperture_C1_R0` →
   `[0.04, 0.04, 0.04, 0.0]`.
2. Mulled entries carry `psi_install == 0.0` and `source == "mull"`.
   Default entries carry `identifier == "apit_default"` and
   `display_name == "Default"`.
3. After `HBPH+ - PH-Nav Set Apertures`,
   `ap.properties.ph.install_types.right.psi_install == 0.0` on the C0 aperture
   and `.left.psi_install == 0.0` on the C1 aperture — with the apertures on a
   **flat** input list, the topology that would have broken the old §3.3 plan.
4. `honeybee_ph_utils.aperture_psi_install.resolve_psi_install_values(ap)`
   returns `{top: 0.04, right: 0.0, bottom: 0.04, left: 0.04}` for C0.
5. HBJSON round-trip: the aperture dict carries an `install_types` key;
   reloading reproduces the four values.
6. EP U-factor: both constructions read **1.3011 W/m²K** today. With §3.3 both
   should read **1.2686 W/m²K** (one edge of the Annex-F reference window drops
   from 0.04 to 0.0). **Confirmed 2026-08-26** by running the real
   `iso_10077_1.calculate_standard_window_uw` against a 50 mm / U-f 1.5 /
   U-g 1.0 / Ψ-g 0.04 frame: `1.3011` with four 0.04 edges, `1.2686` with the
   right edge at 0.0.
7. Legacy payload with no `installs` key produces objects identical to today's,
   `install_types_` comes back empty rather than raising, and
   `HBPH+ - PH-Nav Set Apertures` passes the apertures through untouched.
8. PHX export of the resulting HBJSON writes distinct per-row Ψ-install to PHPP,
   with `0.0` on the mulled rows.

## 5. Open questions for Ed

1. **Standard-size vs element-size U-value (§2.4).** Still open. The GH client
   characterizes every element on the ISO Annex-F 1.23 × 1.48 reference window;
   PHN's U-Values page uses each element's real dimensions. **Both numbers
   confirmed 2026-08-26** against `ISO100771Data`: the BT 1234 mulled element
   reads `1.2686` at Annex-F size (GH, after this fix) and `1.3590` at its real
   1.0 × 1.0 (PHN) — a 7.1% gap that has nothing to do with Ψ-install and
   predates this work. The client already knows the real width and height
   (`create_hbph_window_unit_types` computes `element_width_m` /
   `element_height_m`), so aligning is a small change and would make the two
   screens agree, but it moves the U-factor of every existing model. Worth
   doing, and it should be its own decision, not a side effect of this one.
2. ~~**Auto-apply, or leave the wiring to the user?**~~ **Resolved 2026-08-26
   (Ed): ship both.** Not ergonomics after all — the collection-only route is
   incorrect, not merely inconvenient. See decisions.md D-2.
3. **When does the legacy `0.04` fallback (`v1/window_types_schema.py:165`) come
   out?** It is dead against any current PHN server. Removing it is safe only
   once every server Ed points at emits the new contract; production carries
   route 3's `installs` block already, so this is close to collectable.
