# Feature: Per-edge Ψ-Install into Rhino / Grasshopper (GH client)

```
DATE:    2026-08-26
TIME:    17:45
STATUS:  COMPLETE — merged (HBPH+ #10, base #71), confirmed via METr
AUTHOR:  Ed May + Claude
SCOPE:   Make PH-Navigator's per-edge Ψ-install values reach the Honeybee model
         built by `HBPH+ - PH-Nav Get Apertures`. All work is in this repo.
RELATED: research.md (the 2026-08-13 scoping doc this supersedes);
         cross-repo: ph-navigator-v2/planning/features_v1.1/aperture-psi-install/
         — the PHN-side packet, whose phase-07 doc this supersedes
```

## Read order

0. **`research.md`** — the original 2026-08-13 scoping doc. Its §1 record of
   current behavior still holds; its §2 direction is superseded by `decisions.md`
   D-1 and D-5.
1. **`PRD.md`** — the trace (where the values stop today, verified live against
   project `Psi-Install-Test` / BT 1234) and the design that fixes it.
2. **`decisions.md`** — D-1…D-5, the choices the trace forced, including the
   one that reverses the older spec (D-1) and the one revised after code
   review (D-2).
3. **`PLAN.md`** — implementation sequence, three phases, all in this repo.
4. **`STATUS.md`** — current state, gates, next step.

## One-paragraph summary

Route 3 (`GET /api/v1/gh/projects/{bt}/aperture-types`) has emitted a complete
per-edge `installs` block since PHN phase 02, and it is correct on Ed's local
test project right now, mulled edges and all. The Grasshopper client never reads
it: `v1/window_types_schema.py` has no `installs` parsing, so the only Ψ-install
that reaches Rhino is the uniform project default carried in the legacy
`frames.{side}.frame_type.psi_install_w_mk` field. That is why every edge in
Ed's canvas reads 0.04 — three of those four edges are right by luck and the
mulled edge is wrong by 0.04 W/mK. Nothing in PH-Navigator needs to change. The
whole fix is one repo downstream.

## Where the work happens

| Repo | Change |
| --- | --- |
| **`honeybee_grasshopper_ph_plus`** (here) | Schema, build pipeline, and a new `install_types_` output on `PH-Nav Get Apertures`. No new component. |
| `ph-navigator-v2` | **None to product code.** Its v1.1 packet's phase-07 row points here. |
| `honeybee_grasshopper_ph` | **One change:** `HBPH - Set Aperture Psi-Installs` gains a keyed-collection input alongside its DataTree (D-2). Needs its own release. |
| `honeybee_ph` / `PHX` | **None.** Already shipped (v1.33.33 / v1.56.73) and verified in the trace. |
