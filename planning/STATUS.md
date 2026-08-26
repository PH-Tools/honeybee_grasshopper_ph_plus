# Planning Status

Master index of tracked planning work in HBPH+.

_Last updated: 2026-08-26_

## Active / current work

| Item | Kind | Status | Pointer |
|------|------|--------|---------|
| Consume PHN per-edge Psi-Install data (`PH-Nav Get Apertures`) | Feature | **In progress** — all gates closed (D-1 confirmed, D-2 revised to add `HBPH+ - PH-Nav Set Apertures`); building on `feat/phn-psi-install-per-edge`. Remaining manual gate: `.ghuser` rebuild by Ed | [`features/phn-psi-install-per-edge/`](features/phn-psi-install-per-edge/README.md) |
| `Infiltration from ACH` — 50Pa output unit mismatch | Bug fix | **Implemented** — automated verification passed | [`bug-fixes/infiltration-from-ach-units.md`](bug-fixes/infiltration-from-ach-units.md) |

## Archived

| Item | Kind | Summary | Folder |
|------|------|---------|--------|
| PH-Navigator v1 integration | Feature | Design docs for the v1 PH-Navigator GH components (shared client, get-versions/constructions/apertures, table build/organize) | [`archive/ph-navigator-v1/`](archive/ph-navigator-v1/) |

## Update rule

When an item reaches `Complete`, fold its outcome into the relevant `context/` doc, then move it to `archive/<slug>/` and add a row to `archive/README.md`.
