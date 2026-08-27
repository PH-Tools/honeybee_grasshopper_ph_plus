# STATUS — Per-edge Ψ-Install into Rhino / Grasshopper

```
DATE:    2026-08-26
TIME:    21:10
STATUS:  COMPLETE — shipped, merged, and confirmed end-to-end via METr
AUTHOR:  Ed May + Claude
SCOPE:   State, gates, next step
RELATED: README.md, PRD.md, decisions.md, PLAN.md, research.md
```

**State:** **Complete.** All three phases shipped and merged:
`honeybee_grasshopper_ph_plus` PR #10 and `honeybee_grasshopper_ph` PR #71. Ed
regenerated both user-objects in Grasshopper, ran the full chain on a real project,
and confirmed a **METr** export places Psi=0 on the mulled edges. 36 tests pass.

## Phase ledger

| Phase | State |
| --- | --- |
| 01 Parse `installs` | **Complete** — `InstallData` / `InstallsData` / `ElementData.installs`, 15 tests |
| 02 Build Install Types + `install_types_` output + base-setter key matching | **Complete** — builder + `HBPH - Set Aperture Psi-Installs` keyed input; verified live against BT 1234 |
| 03 EP U-factor from resolved Ψ + verification | **Complete** — transient effective frames; 1.3011 → 1.2686 verified live |

## Gates — all closed

1. ~~**D-1 confirmation (Ed).**~~ Closed 2026-08-26. Per-edge Ψ rides on the aperture.
2. ~~**D-2 delivery mechanism.**~~ Closed, then revised twice. Final: the base
   package's `HBPH - Set Aperture Psi-Installs` learned key matching; HBPH+ ships no
   setter. See `decisions.md` D-2.
3. ~~**`requirements.txt` pin.**~~ Void — no such file in HBPH+. Verified against the
   deployed Rhino install instead.
4. ~~**`.ghuser` rebuild.**~~ Done by Ed 2026-08-28; both user-objects regenerated and
   committed. No icon needed — D-2's revision removed the new component.
5. ~~**Base repo release.**~~ Merged to `main` (PR #71); Ed cuts the installer release.

**Not gates any more.** The v1.1 packet listed phase 07 as blocked on deploying
route 3. Route 3's `installs` block is live on `localhost:8000`, confirmed
2026-08-26 against BT 1234 by direct request. The production API serves the same
merged code; re-confirm there before pointing a non-DEV component at it.

## Verified facts (2026-08-26, re-checked during code review)

- Route 3 emits a complete, correct `installs` block including
  `source: "mull"` / `psi_install_w_mk: 0.0` on both interior edges of BT 1234.
  Confirmed against the live response, not only the source.
- The GH V1 schema has zero references to the `installs` payload key; the block
  is dropped at parse.
- `PhApertureInstallType`, `AperturePsiInstalls`, the resolver, the PHX consumer
  (`PHX/from_HBJSON/create_building.py:221`), and both Grasshopper Install-Type
  components all exist and are merged. Upstream released as honeybee-ph
  v1.33.33 / PHX v1.56.73 / `honeybee_grasshopper_ph` PR #60, all 2026-08-12.
- `PhWindowFrame.__copy__` deep-copies its four elements, so D-5's transient
  frame cannot leak a per-edge Ψ back into the shared frame-element pool.
- Acceptance §4.6's `1.3011` → `1.2686` W/m²K reproduced against the real
  `ISO100771Data`; §5.1's element-size figure is `1.3590` (7.1% gap).
- Nothing in `ph-navigator-v2` needs a product change.

## Known, out of scope

`gh_compo_io/airtable/create_window_constructions.py:219-224` still writes
per-edge Ψ into construction frame elements — the pattern D-1 rejects. Untouched
here; see `decisions.md` D-1.
