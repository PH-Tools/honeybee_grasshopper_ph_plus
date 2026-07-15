---
DATE: 2026-07-15
STATUS: CANONICAL
---

# HBPH+ — Tech Stack

## Runtime

- **IronPython 2.7** (Rhino/Grasshopper) for all deployed code.
- **CPython** for repo tooling only (black, ruff, bump-my-version) — never installed into Rhino.

## Dependencies

Imports resolve against sibling PH-Tools packages installed in the Rhino Python path (not via pip):

- `honeybee_ph`, `honeybee_ph_rhino` (the base `honeybee_grasshopper_ph` package — **required**), `ph_units`.
- Ladybug/Honeybee core.
- `.NET` APIs (`Rhino`, `Grasshopper`, `System`).

`typings/` holds `.NET`/GH API stubs (`Grasshopper/`, `System/`) for static checking only.

Backend integration libraries in `honeybee_ph_plus_rhino/`: `phpp/` (PHPP readers — climate, room ventilation, variants), `plotly/` (Ladybug data plotting), `sql/` (EnergyPlus SQLite readers).

## Packaging

- Not a pip package — `pyproject.toml` carries tooling + bump-my-version config only. Distribution is the `.ghuser` user objects (regenerated on release).

## Dev loop (fsdeploy)

`.vscode/settings.json` `fsdeploy` (`deployOnSave: true`) copies the package on every save to: the `ladybug_tools/.../site-packages/` path Grasshopper imports at runtime, and the sibling `PHX/.venv/`. Saving a `gh_compo_io/` logic file updates the live Rhino install with no build step. Only the `.ghuser` facade needs a rebuild, and only when the facade changes.

## Testing

- **No tests in this repo** (the `.pytest_cache` is incidental). Verify against the sibling backend repos or in Rhino/GH.

## Versioning & release

- `bump-my-version` rewrites `RELEASE_VERSION` in `_component_info_.py`, commits (`bump: … [skip ci]`), tags `v{version}`.
- `.github/workflows/release.yml` handles the release (manual dispatch or `repository_dispatch` from the base repo's orchestrator).
- Do not hand-edit versions.

## Docs

- No `docs/` folder / docs-hub spoke in this repo.
