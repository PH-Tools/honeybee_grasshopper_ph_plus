# honeybee_grasshopper_ph_plus (HBPH+)

Open-source (`github.com/PH-Tools`) plugin adding **extra utility** Grasshopper components on top of the base `honeybee_grasshopper_ph` package (Airtable integration, reporting/PDF, PHPP readers, SQL/E+ readers, Plotly plotting, PH-Navigator, and more). Requires the base HBPH package.

> **Runtime constraint (critical):** deployed code runs inside **Rhino/Grasshopper's IronPython 2.7**, not CPython 3. Repo tooling (black/ruff/bumpversion, `.venv`) is CPython and is for linting/release only — never installed into Rhino. See `context/CODING_STANDARDS.md`.

## Where things live — read before working

| Working on… | Read |
|-------------|------|
| What this repo is/isn't, scope | `context/PRD.md` |
| The two-layer design, fsdeploy, `GHCompo_*` anatomy (the deep "why") | `honeybee_ph_plus_rhino/gh_compo_io/.index.md` |
| Component pattern + subpackage map (orientation) | `context/ARCHITECTURE.md` |
| IronPython 2.7 rules, imports, type comments, formatting | `context/CODING_STANDARDS.md` |
| Deps, fsdeploy dev loop, release | `context/TECH_STACK.md` |
| Current / in-flight work | `planning/STATUS.md` |
| File-level navigation | `.index.md` (root) + per-folder `.index.md` under `gh_compo_io/` |

Full context index: `context/README.md`.

## Hard rules

1. **IronPython 2.7 for deployed code.** No f-strings/`pathlib`/modern stdlib; type **comments** (`# type:`), not annotations. Do not "modernize" to Py3 idioms — match the surrounding Py2.7 style. `F401` is globally ignored (type-hint-in-comment imports); `__init__.py` may use wildcard imports.
2. **A component = thin GH wrapper + backend logic class.** Wrapper `honeybee_grasshopper_ph_plus/src/HBPH+ - <Name>.py` (no logic); logic `honeybee_ph_plus_rhino/gh_compo_io/<subcat>/<name>.py` (`GHCompo_*`). Adding one touches: (a) `src/` wrapper, (b) `gh_compo_io/` class, (c) `_component_info_.py` entry, (d) icon in `icons/`, (e) rebuilt `.ghuser`.
3. **Names must match exactly** across the `src/` filename, `ghenv.Component.Name`, and the `_component_info_.py` key — all `"HBPH+ - <Name>"`. Preserve the GPL header + Args/Returns docstring in wrappers (GH renders it as tooltips).
4. **fsdeploy makes saves live.** Saving a `gh_compo_io/` logic file silently updates the live Rhino install (`.vscode/settings.json` → `fsdeploy`). Never edit inside Rhino's folders directly — those copies are overwritten on next deploy. Leave the wrapper `DEV`/`reload` block at `dev=False` on commit.
5. **Do not hand-edit the version.** `bump-my-version` rewrites `RELEASE_VERSION` in `_component_info_.py`; `.github/workflows/release.yml` releases. Don't commit version bumps unless asked.
6. **No test suite here** (the `.pytest_cache` is incidental). Verify logic against the sibling backend repos where the tested code lives, or by loading in Rhino/GH.

## Related repos (all under `~/Dropbox/bldgtyp-00/00_PH_Tools/`)

`honeybee_grasshopper_ph` (base package — **required**) · `honeybee_ph` (data model) · `PHX` (serialization) · `PH_units` (units).
