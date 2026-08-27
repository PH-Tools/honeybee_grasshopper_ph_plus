# Planning Status

Master index of tracked planning work in HBPH+.

_Last updated: 2026-08-28_

## Active / current work

| Item | Kind | Status | Pointer |
|------|------|--------|---------|
| `Infiltration from ACH` — 50Pa output unit mismatch | Bug fix | **Implemented** — automated verification passed | [`bug-fixes/infiltration-from-ach-units.md`](bug-fixes/infiltration-from-ach-units.md) |

## Archived

| Item | Kind | Summary | Folder |
|------|------|---------|--------|
| Per-edge Psi-Install into Rhino / Grasshopper | Feature | PHN route-3 `installs` now reaches the HB model; base setter gained a keyed-collection input. Merged HBPH+ #10 / honeybee_grasshopper_ph #71, confirmed via METr | [`archive/phn-psi-install-per-edge/`](archive/phn-psi-install-per-edge/) |
| PH-Navigator v1 integration | Feature | Design docs for the v1 PH-Navigator GH components (shared client, get-versions/constructions/apertures, table build/organize) | [`archive/ph-navigator-v1/`](archive/ph-navigator-v1/) |

## Update rule

When an item reaches `Complete`, fold its outcome into the relevant `context/` doc, then move it to `archive/<slug>/` and add a row to `archive/README.md`.
