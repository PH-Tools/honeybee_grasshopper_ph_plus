# Research — original scoping doc (2026-08-13)

> **Superseded in part, 2026-08-26.** This was the first pass at scoping the work,
> written before the live trace in `PRD.md`. Keep it for history and for §1, which
> still holds. Two things have changed:
>
> - **The deploy gate is closed.** Route 3's `installs` block was confirmed live on
>   `localhost:8000` against BT 1234 on 2026-08-26.
> - **§2 item 2's direction is superseded** by `decisions.md` D-1 / D-5. The mapping
>   table in §2 is still correct *except* its `source` row — see below; what changed
>   is where the values land and the addition of the EP U-factor fix.
> - **§2 item 3's "prefer the extra output" is half right**, per `decisions.md` D-2:
>   the extra output ships, but the base repo's `HBPH - Set Aperture Psi-Installs`
>   had to learn key matching to consume it — the output alone could not be wired
>   correctly against a flat aperture list.
> - **§2's `source` description is wrong.** It reads
>   "`assigned`/`default`/`mull` + type source". The actual value is one of
>   `"mull"` / `"assigned"` / `"default"` only
>   (`ResolvedInstallPsi.source: Literal[...]`); the library row's own Source field
>   (`opt_apit_src_*`) is never merged in. `PRD.md` §3.2 has it right.
>
> Read `README.md` → `PRD.md` → `decisions.md` → `PLAN.md` for the current spec.

**Original status:** Deferred — gated on Ed deploying the PH-Navigator
`feature/aperture-psi-install` branch to production (route-3 `installs` block; PHN packet
phase-02 deploy gate). UI polish in progress on the PHN side as of 2026-08-13. Everything
upstream is shipped and waiting.
**Date:** 2026-08-13
**Author:** Ed May + Claude
**Kind:** Client-side completion of the cross-repo `aperture-psi-install` refactor
(honeybee_ph v1.33.33 / PHX v1.56.73 / honeybee_grasshopper_ph PR #60 — all merged).

**Companion docs:**
- `ph-navigator-v2/planning/features_v1.1/aperture-psi-install/phases/phase-07-gh-client-per-edge.md` — the PHN-side spec for this work (its §3 is likewise superseded by `decisions.md` D-1)
- `ph-navigator-v2/planning/features_v1.1/aperture-psi-install/upstream-alignment.md` — field mapping (authoritative)
- `honeybee_grasshopper_ph/planning/refactor/aperture-psi-install.md` — the base-repo components this feeds

---

## 1. Current behavior (verified 2026-08-13)

`HBPH+ - PH-Nav Get Apertures` (`gh_compo_io/ph_navigator/v1/apertures_get.py`) consumes
PHN route 3 (`GET /aperture-types`) and gets psi-install at **uniform-default fidelity only**:

- **Parsed:** the legacy `frames.{side}.frame_type.psi_install_w_mk` field — PHN writes the
  *project default* Ψ into every side (never per-edge, by PHN decision D-5 so old clients
  keep working). Null-safe parse at `v1/window_types_schema.py:165` (0.04 fallback); applied
  to the construction frame elements at `v0/window_types_get.py:104`. This is the
  type-default layer of the new scheme — correct, and unchanged by this feature.
- **Dropped:** the per-edge `elements[n].installs.{side}` block —
  `{install_type_id, name, psi_install_w_mk, source}`, including `0.0 / "mull"` on interior
  (mulled) edges. Zero references to `installs` in the v1 schema or client. Mulled edges,
  party walls, and Install Types painted in PHN's Installs modal do not reach Grasshopper.

## 2. Design (agreed direction, 2026-08-13)

**No new base-repo work and no new data model** — the upstream chain is complete. Update the
existing component (plus, at most, a small companion output):

1. **Schema:** extend `v1/window_types_schema.py` to parse `elements[n].installs.{side}`
   (null-safe like everything else in the V1 fork; absent block ⇒ legacy-only payload,
   behavior unchanged).
2. **Build:** map each distinct `install_type_id` to ONE `PhApertureInstallType`
   (`honeybee_energy_ph.construction.window`), per `upstream-alignment.md`:

   | Route-3 field | PhApertureInstallType |
   |---|---|
   | `install_type_id` (`apit_*`) | `identifier` (verbatim — preserves PHN round-trip identity) |
   | `name` | `display_name` |
   | `psi_install_w_mk` | `psi_install` |
   | `source` (`assigned`/`default`/`mull` + type source) | `source` (free text) |

   Mulled edges arrive as zero-Ψ types (source `"mull"`) — no special handling needed;
   honeybee-ph deliberately has no mull concept.
3. **Output:** emit per-aperture-type, per-element Install Type trees in **top/right/bottom/left
   order**, shaped to wire directly into the base repo's `HBPH - Set Aperture Psi-Installs`
   component (which accepts exactly that: up to 4 Install Types per branch, t/r/b/l).
   Design decision at implementation: extra output(s) on `HBPH+ - PH-Nav Get Apertures` vs. a
   small companion `HBPH+ - PH-Nav Get Install Types` component — prefer the extra output
   unless canvas ergonomics argue otherwise.
4. The per-edge data is aperture-**instance** data: it applies when apertures are placed in
   the model, via the base component — this repo only delivers the parsed types/trees.

## 3. Verification targets

- PHN packet regression case: project 2524 — 196 `psi_install_w_mk: null` frames via route 3
  (named as the phase-07 verification target in the PHN packet STATUS).
- A PHN project with painted Installs (assigned + mulled edges) round-trips: PHN modal →
  route 3 → GH → HBJSON aperture `install_types` → PHX → per-row PHPP psi / WUFI variant
  types. Zero window-construction duplication at every step.
- Legacy payload (no `installs` block) ⇒ byte-identical behavior to today.

## 4. Repo mechanics (when implementing)

- IronPython 2.7 rules; V1 schema fork stays null-safe; component pattern per
  `context/ARCHITECTURE.md` (wrapper + `GHCompo_*` + `_component_info_.py` + icon + .ghuser).
- Requires base `honeybee_grasshopper_ph` release carrying the Install-Type components
  (post-PR #60) in `requirements.txt`.
