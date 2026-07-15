---
DATE: 2026-07-15
STATUS: CANONICAL ENGINEERING STANDARD
---

# HBPH+ — Coding Standards

## 1. IronPython 2.7 for deployed code

Everything that runs on the Grasshopper canvas must be Python-2.7 / IronPython-2.7 safe. (`.venv` + black/ruff/bumpversion are CPython, for lint/release only — never installed into Rhino.)

- No f-strings, no `pathlib`, no modern stdlib.
- Type **comments** (`# type: (int) -> None`), never inline annotations.
- **Do not "modernize" to Python 3 idioms.** Match the surrounding Py2.7 style exactly.
- `F401` (unused import) is globally ignored — it collides with the type-hint-in-comment style. Wildcard imports allowed in `__init__.py`.
- Line length **120** (black + ruff).

## 2. The component contract

- Logic in `honeybee_ph_plus_rhino/gh_compo_io/<subcat>/<name>.py` (`GHCompo_*`).
- Thin wrapper in `honeybee_grasshopper_ph_plus/src/HBPH+ - <Name>.py` — preserve the GPL header and the Args/Returns docstring block (Grasshopper renders it as canvas tooltips). Keep the `DEV`/`reload` block at `dev=False` on commit.
- **Registry entry mandatory** in `_component_info_.py` for any new/renamed component.
- **Names match exactly** across the `src/` filename, `ghenv.Component.Name`, and the registry key — all `"HBPH+ - <Name>"`.
- Adding a component touches all of: `src/` wrapper, `gh_compo_io/` class, `_component_info_.py`, icon in `icons/`, rebuilt `.ghuser`.

Deep rationale and `GHCompo_*` anatomy: `../honeybee_ph_plus_rhino/gh_compo_io/.index.md`.

## 3. Deployment discipline

fsdeploy copies the package to Rhino on save — **never edit inside Rhino's folders directly**; those copies are overwritten on the next deploy. Edit here.

## 4. Versions — hands off

`bump-my-version` rewrites `RELEASE_VERSION` in `_component_info_.py` and tags `v{version}`. Do not hand-edit the version; do not commit version bumps unless asked.

## 5. Verification

No test suite in this repo. Verify logic changes against the sibling backend repos where the tested code lives (`honeybee_ph`, `PHX`), or by loading the component in Rhino/Grasshopper.

## Closeout checklist

- [ ] Deployed code is IronPython-2.7-safe (no f-strings/pathlib; type comments; no Py3 modernization).
- [ ] Wrapper preserves GPL header + Args/Returns docstring; `DEV` left at `dev=False`.
- [ ] Registry entry added/updated; names match across wrapper / `ghenv.Component.Name` / registry.
- [ ] Icon added and `.ghuser` rebuilt if a new/changed component.
- [ ] black + ruff clean; version not hand-edited.
