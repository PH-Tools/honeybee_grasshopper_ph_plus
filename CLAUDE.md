# CLAUDE.md — honeybee_grasshopper_ph_plus (HBPH+)

Open-source (`github.com/PH-Tools`) plugin adding extra utility Grasshopper components to the Honeybee-PH toolchain. See `.index.md` for the file-level navigation map, and `honeybee_ph_plus_rhino/gh_compo_io/.index.md` for the "why" behind the facade/deploy/IronPython design plus the anatomy of a `GHCompo_*` class (each `gh_compo_io/` subfolder has its own `.index.md` too).

## Runtime target — IronPython 2.7

The deployed code runs inside **Rhino/Grasshopper's IronPython 2.7**, NOT CPython 3.

- Write Py2.7-compatible code: no f-strings, no `pathlib`, use `# type:` comment annotations (not inline `def f(x: int)`), `print` is fine but rarely used.
- `.venv/` and repo tooling (black, ruff, bumpversion) ARE CPython — that's only for linting/release, never installed into Rhino.
- ruff/black line-length is **120**. `F401` is globally ignored (type-hint-in-comment imports); `__init__.py` may use wildcard imports.
- Do NOT "modernize" to Python 3 idioms. Match the surrounding Py2.7 style exactly.

## Two-layer architecture

A component = a thin GH wrapper + a backend logic class. Keep the two in sync.

1. **`honeybee_grasshopper_ph_plus/src/HBPH+ - <Name>.py`** — thin GH-canvas wrapper. Boilerplate GPL header + docstring (Args/Returns block that GH renders as tooltips), sets `ghenv.Component.Name`, builds an `IGH` interface, instantiates a `GHCompo_*` class from `gh_compo_io`, calls `.run()`. Logic does NOT live here.
2. **`honeybee_ph_plus_rhino/gh_compo_io/<subcat>/<name>.py`** — the actual `GHCompo_*` class doing the work. Subcategory folders: `airtable/ collections/ ghpy/ hb_tools/ ph_navigator/ read/ reporting/`; also `phpp/`, `plotly/`, `sql/` at package root.
3. **`honeybee_ph_plus_rhino/_component_info_.py`** — registry: `RELEASE_VERSION`, `CATEGORY` = `HB-PH+`, `SUB_CATEGORIES` map, per-component `COMPONENT_PARAMS` (NickName / Category / SubCategory).
4. **`honeybee_grasshopper_ph_plus/user_objects/HBPH+ - <Name>.ghuser`** — compiled binary user object (build artifact, regenerated on release — do not hand-edit).
5. **`honeybee_grasshopper_ph_plus/icons/`** — `AI/` source + `PNG/` export per component.

## Adding / editing a component

To add one, touch all of: (a) `src/` wrapper, (b) `gh_compo_io/` logic class, (c) `_component_info_.py` entry, (d) icon in `icons/`, (e) rebuild the `.ghuser`. Editing behavior usually means editing the `gh_compo_io/` class only — the `src/` wrapper rarely changes.

The `DEV` block in each wrapper (`reload(...)` calls guarded by `dev=False`) is a hot-reload aid for canvas development; leave `dev=False` on commit.

## Deployment — fsdeploy (why this repo lives outside Rhino)

We keep the source in this git repo instead of inside Rhino's application folders (where `.ghuser` code normally lives and can't be diffed/reviewed/type-checked). A VS Code extension, **fsdeploy**, bridges the gap: on every save (`fsdeploy.deployOnSave: true` in `.vscode/settings.json`) it copies the package to Rhino's runtime paths.

- Targets (`fsdeploy.nodes` in `.vscode/settings.json`): the `ladybug_tools/python/.../site-packages/` path Grasshopper imports at runtime, and the sibling `PHX/.venv/` so PHX-side dev/tests resolve the same package.
- Consequence: **saving a `gh_compo_io/` logic file silently updates the live Rhino install** — no build step for logic changes. Only the `.ghuser` facade needs a real rebuild, and only when the facade itself changes.
- Never edit inside the Rhino folders directly; those copies are overwritten on the next deploy.

## Dependencies (external, IronPython import namespace)

Imports resolve against sibling PH-Tools packages installed in the Rhino Python path, not via pip: `honeybee_ph`, `honeybee_ph_rhino` (base `honeybee_grasshopper_ph` — required), `ph_units`, plus Ladybug/Honeybee core and `.NET` (`Rhino`, `Grasshopper`, `System`). `typings/` holds stubs for the .NET/GH API for static checking only.

## Versioning & release

`bump-my-version` drives releases: it rewrites `RELEASE_VERSION` in `_component_info_.py`, commits (`bump: ... [skip ci]`), and tags `v{version}`. `.github/workflows/release.yml` handles the release. Do not hand-edit the version string; do not commit version bumps unless asked.

## Conventions

- Preserve the GPL-3.0 header block and the Args/Returns docstring format in `src/` wrappers — GH parses the docstring for the canvas UI.
- Component display names are the exact `"HBPH+ - <Name>"` strings; they must match across `src/` filename, `ghenv.Component.Name`, and the `_component_info_.py` key.
- No test suite in this repo (the `.pytest_cache` is incidental). Verify logic changes against the sibling backend repos where the tested code lives, or by loading in Rhino/GH.
