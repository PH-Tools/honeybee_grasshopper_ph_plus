---
DATE: 2026-07-15
STATUS: CANONICAL PRD
---

# honeybee_grasshopper_ph_plus (HBPH+) — Product Requirements

## 1. Goal

Provide the **advanced / utility** Grasshopper components for the Honeybee-PH toolchain — the ones beyond the base modeling set: Airtable integration, reporting and PDF generation, PHPP readers, EnergyPlus SQL readers, Plotly plotting, PH-Navigator hooks, and other power-user tools.

## 2. Who uses it

Passive House consultants already using the base `honeybee_grasshopper_ph` package who need more advanced model configuration, data integration, and reporting on the Grasshopper canvas. HBPH+ requires the base HBPH package to be installed.

## 3. What belongs here

- Utility/advanced GH components (thin wrappers in `honeybee_grasshopper_ph_plus/src/` + logic classes in `honeybee_ph_plus_rhino/gh_compo_io/`).
- The backend integration libraries these components use: `phpp/` (PHPP readers), `plotly/` (plotting), `sql/` (E+ SQLite readers).
- The component registry, icons, and compiled `.ghuser` user objects.

## 4. Non-goals

- **Not the base modeling components** — those are `honeybee_grasshopper_ph`.
- **Not the core data model / serialization** — `honeybee_ph` / `PHX`.
- **No test suite of its own** — logic is verified against the sibling backend repos or by loading in Rhino/GH.

## 5. Success criteria

- Every component loads and runs inside Rhino's IronPython 2.7 with the base HBPH package present.
- Names stay consistent across wrapper filename, `ghenv.Component.Name`, and the registry key.
- fsdeploy keeps the live Rhino install in sync with the repo during development.

## 6. Direction

- Active/related planning in `planning/STATUS.md`. Archived design material (PH-Navigator v1 integration) in `planning/archive/`.
