---
DATE: 2026-07-15
STATUS: ORIENTATION (deep "why" is in gh_compo_io/.index.md)
---

# HBPH+ — Architecture (orientation)

The **authoritative deep dive** — why the two-layer facade exists, how fsdeploy works, and the anatomy of a `GHCompo_*` class — is in [`../honeybee_ph_plus_rhino/gh_compo_io/.index.md`](../honeybee_ph_plus_rhino/gh_compo_io/.index.md). Read that before adding or editing a component. This file is just the map.

## Two layers

```
honeybee_grasshopper_ph_plus/   ← GH-facing package (the deployed artifact)
  src/HBPH+ - <Name>.py         ← thin canvas wrapper (no logic), compiled into…
  user_objects/HBPH+ - <Name>.ghuser   ← the installable binary (build output)
  icons/  (AI/ source + PNG/ export)

honeybee_ph_plus_rhino/         ← backend library (the logic)
  gh_compo_io/<subcat>/<name>.py   ← GHCompo_* classes (all the real work)
  _component_info_.py              ← registry: RELEASE_VERSION, CATEGORY=HB-PH+, SUB_CATEGORIES, COMPONENT_PARAMS
  phpp/   plotly/   sql/           ← integration libs used by the components
```

The wrapper instantiates the `GHCompo_*` class and calls `.run()`; logic never lives in the wrapper.

## `gh_compo_io/` subcategories

`airtable/` · `collections/` · `ghpy/` · `hb_tools/` · `ph_navigator/` · `read/` · `reporting/` — each with its own `.index.md`. Backend integration packages `phpp/`, `plotly/`, `sql/` sit at the `honeybee_ph_plus_rhino/` root.

## Registry & naming

`_component_info_.py` styles each component and is mandatory for any new/renamed one. The display name `"HBPH+ - <Name>"` must match exactly across the `src/` filename, `ghenv.Component.Name`, and the registry key.

## Deployment

fsdeploy (VS Code, `deployOnSave`) copies the package to Rhino's runtime paths and the sibling `PHX/.venv/` on every save — so saving a logic file updates the live Rhino install with no build step. Only the `.ghuser` facade needs a real rebuild, and only when the facade changes. See the deep doc and `TECH_STACK.md`.
