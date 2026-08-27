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

## Two layers of Passive-House data: construction vs. aperture

A recurring modelling rule, easy to get wrong because both layers are reachable
from the same component:

- The **WindowConstruction** carries the window *product* — frame elements,
  glazing, and their type-default psi-values. It is **shared** across every window
  that uses it.
- The **Aperture** carries where that window actually *sits* — notably the
  per-edge Psi-Install "Install Types" on `properties.ph.install_types`. This is
  **instance** data.

Never write instance data into a construction, and never duplicate a construction
per window to make instance data fit: that is the defect `honeybee_grasshopper_ph`
issue #59 closed. When a calculation legitimately needs both (the ISO 10077-1 U-w
includes the install psi), resolve them into a **transient** frame duplicate, use
it, and discard it — `honeybee_ph_utils.aperture_psi_install.resolve_effective_frame`
upstream and `ph_navigator/v1/install_types_build.create_effective_frames` here are
both that pattern.

Two consequences worth knowing before debugging: a construction-level probe
(`const.properties.ph.ph_frame.top.psi_install`) legitimately reports the type
default even when the model is correct, and a construction's EnergyPlus U-factor
can legitimately differ from its own `ph_frame` for the same reason.

## Registry & naming

`_component_info_.py` styles each component and is mandatory for any new/renamed one. The display name `"HBPH+ - <Name>"` must match exactly across the `src/` filename, `ghenv.Component.Name`, and the registry key.

## Deployment

fsdeploy (VS Code, `deployOnSave`) copies the package to Rhino's runtime paths and the sibling `PHX/.venv/` on every save — so saving a logic file updates the live Rhino install with no build step. Only the `.ghuser` facade needs a real rebuild, and only when the facade changes. See the deep doc and `TECH_STACK.md`.
