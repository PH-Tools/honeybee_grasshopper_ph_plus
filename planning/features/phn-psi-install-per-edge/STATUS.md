# STATUS — Per-edge Ψ-Install into Rhino / Grasshopper

```
DATE:    2026-08-26
TIME:    17:45
STATUS:  In progress — gates closed, implementation started
AUTHOR:  Ed May + Claude
SCOPE:   State, gates, next step
RELATED: README.md, PRD.md, decisions.md, PLAN.md, research.md
```

**State:** Trace complete and verified live, then independently re-verified
against the working tree. Design accepted, with D-2 revised. Implementation
under way on branch `feat/phn-psi-install-per-edge`.

**Next step:** Phase 02 — build the Install Types, the `install_types_` output,
and `HBPH+ - PH-Nav Set Apertures`.

## Phase ledger

| Phase | State |
| --- | --- |
| 01 Parse `installs` | **Complete** — `InstallData` / `InstallsData` / `ElementData.installs`, 15 tests |
| 02 Build Install Types + `install_types_` output + `PH-Nav Set Apertures` | Not started |
| 03 EP U-factor from resolved Ψ + verification | Not started |

## Gates

1. ~~**D-1 confirmation (Ed).**~~ **Closed 2026-08-26** — Ed confirmed. Per-edge Ψ
   rides on the aperture, not the construction. Consequence stands: Ed's current
   canvas probe keeps printing `0.04`. See `decisions.md` D-1 and `PRD.md` §3.4.
2. ~~**D-2 delivery mechanism.**~~ **Closed 2026-08-26** — Ed chose "output +
   set component" after review showed the collection-only wiring can silently
   apply one element's values to the whole model. See `decisions.md` D-2.
3. ~~**`requirements.txt` pin.**~~ **Void — no such file.** HBPH+ is not a pip
   package; deps resolve against sibling packages on the Rhino Python path
   (`context/TECH_STACK.md`). Verified directly instead: the base Install-Type
   modules and the `HBPH - Set Aperture Psi-Installs.ghuser` are present in Ed's
   live Rhino 8 install, and PR #60 shipped in `honeybee_grasshopper_ph` v1.33.0.
4. **`.ghuser` rebuild (Ed, Grasshopper).** *Open — the one gate an agent cannot
   close.* Phase 02 adds an output to `PH-Nav Get Apertures` and introduces
   `PH-Nav Set Apertures`; fsdeploy does not regenerate user-objects.

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
