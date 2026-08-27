# Decisions — Per-edge Ψ-Install into Rhino / Grasshopper

```
DATE:    2026-08-26
TIME:    17:45
STATUS:  Accepted — D-1 confirmed by Ed 2026-08-26; D-2 revised after code review
AUTHOR:  Ed May + Claude
SCOPE:   Accepted/rejected design choices for the GH client
RELATED: PRD.md, PLAN.md, research.md;
         cross-repo: ph-navigator-v2/planning/features_v1.1/aperture-psi-install/phases/phase-07-gh-client-per-edge.md
```

## D-1 — Per-edge Ψ rides on the **aperture**, not the construction

**Decision.** Build `PhApertureInstallType` objects and assign them to
`AperturePhProperties.install_types`. Leave `WindowConstructionPhProperties.ph_frame`
carrying the type default.

**This reverses two older specs**, both written before the upstream refactor
landed: this folder's own `research.md` §2 (2026-08-13) and the PHN packet's
`phases/phase-07-gh-client-per-edge.md` (2026-08-03). The latter's §3 specifies
duplicating the
shared `PhWindowFrameElement` per edge and writing the per-edge Ψ into the
construction's frame. That doc was written **nine days before** the upstream
refactor shipped (honeybee-ph v1.33.33, PHX v1.56.73, `honeybee_grasshopper_ph`
PR #60, 2026-08-12), which created the aperture-instance slots and explicitly
deleted the construction-duplication mechanism as issue #59. The PHN packet's `upstream-alignment.md`
(2026-08-12) already records the correction; this decision makes it binding and
retires both older §2/§3 directions.

**Why.** Install condition is a property of where a window sits, not of the window
product. The construction is shared; the placement is not. Writing instance data
into a shared construction is the exact defect #59 closed. It also loses the
Install Type's name and source, which PHX needs to synthesize WUFI/METr window-type
variants and which makes a model auditable.

**Cost, stated plainly.** Ed's current probe
(`const.properties.ph.ph_frame.top.psi_install`) will still print `0.04` after
this ships. That is the correct answer to the question that probe asks. The
aperture-level probe is in PRD.md §4.

**Known counter-precedent in this repo, not addressed here.**
`honeybee_ph_plus_rhino/gh_compo_io/airtable/create_window_constructions.py:219-224`
writes per-edge Ψ straight into the construction's frame elements
(`hbph_frame.top.psi_install = ...`) — the pattern this decision rejects. That
component is untouched by this feature, so after this lands HBPH+ carries two
contradictory conventions: the PH-Nav path puts install condition on the
aperture, the Airtable path puts it on the construction. Migrating the Airtable
path is its own piece of work and is deliberately not in scope. Recorded here so
the inconsistency is a known one rather than a discovery.

**Confirmed by Ed, 2026-08-26.** Phase 01 is unblocked.

## D-2 — One canonical aperture setter, taught to match by key

> **Revised twice.** (a) The original decision wired the collection through
> `HBPH+ - Get From Custom Collection` into the base setter and claimed that needed
> "no new matching logic and no new component" — untrue, see below. (b) The second
> version added `HBPH+ - PH-Nav Set Aperture Psi-Installs`. Ed then made the right
> call: that was a *third* component writing the same field as an existing one,
> differing only in matching strategy. This version folds the capability in and
> deletes the new component.

**Decision.** Two pieces:

1. A new `install_types_` output on `HBPH+ - PH-Nav Get Apertures`: a
   `CustomCollection` keyed by element type-name (`Test Aperture_C0_R0`), value =
   the ordered list `[top, right, bottom, left]` of `PhApertureInstallType`.
2. The base package's **`HBPH - Set Aperture Psi-Installs`** learns a second input
   shape. `_install_types` now accepts either its existing DataTree (matched by
   branch index, unchanged) **or** a keyed collection — anything dict-like — whose
   keys are Aperture display-names. HBPH+ ships **no setter of its own**.

**Why key matching is needed at all.** The base setter matches by **branch index**,
and every Aperture in a branch receives the *same* four Install Types:

```python
for branch_idx, apertures in enumerate(self._apertures.Branches):
    install_types_by_side = [...get_tree_item(self._install_types, branch_idx, side_idx)...]
    for ap in apertures:   # <- all four shared across the whole branch
```

That is right for its original use case: one install condition painted over a set of
windows. It cannot express per-window values against a **flat** list of Apertures —
and `srfc_names_` from `HBPH+ - Create Window Geometry` is exactly that, so every
Aperture lands in branch 0 and silently takes the first element's psi-installs. No
error, wrong model.

**Why one component rather than two.** A second component writing byte-for-byte the
same field (`aperture.properties.ph.install_types`), differing only in how it decides
which types go where, is duplication — that is a component with two input modes, not
two components. Folding it in keeps one answer to "set psi-installs on apertures."

**Why this does not invert the dependency.** The base repo does not learn that HBPH+
exists. `CustomCollection` already implements `.get(key, default)` and `.keys()`, so
the base component documents "a DataTree, or any dict-like keyed by Aperture name"
and duck-types on that pair. A plain dict works identically. Detection is by shape:
exactly one item in the tree, and that item dict-like — a `PhApertureInstallType`, a
number and a unit-string all fail the test, so the branch path is never taken by
surprise.

**Cost, stated plainly.** The change lands in a published package, so it needs a base
repo release. Existing DataTree wiring is untouched, and the component facade is
unchanged (unmatched Apertures are surfaced via `IGH.warning`, not a new output port),
so no `.ghuser` rebuild is required for it.

**Rejected:** an adapter that grafts the collection into the tree shape the base
setter already wants. It would have to emit *both* re-grafted apertures and a matching
tree, so the user wires two outputs that must stay in lockstep — more fragile than the
thing it replaces.

## D-3 — Mulled edges get a content-keyed synthetic identifier

**Decision.** Route 3 sends mulled edges as
`{install_type_id: null, name: null, psi_install_w_mk: 0.0, source: "mull"}`.
Build these as ordinary zero-Ψ Install Types with a **deterministic, content-keyed**
identifier and display name (follow `build_install_type` in
`honeybee_ph_rhino/gh_compo_io/apertures/win_create_install_type.py`, which already
does content-keying for anonymous types).

**Why not a uuid.** Every mulled edge in a project is the same condition. A uuid per
edge would produce hundreds of distinct Install Types that PHX would then have to
merge, and would make the HBJSON diff noisy on every re-download. Content-keying
makes re-downloads idempotent.

**Why not leave the slot `None`.** `None` means "inherit the construction default",
which is 0.04 — the wrong answer, and the whole bug.

## D-4 — `source = "default"` edges are assigned explicitly, not left to inherit

**Decision.** Assign the `apit_default` Install Type to those edges rather than
leaving the slot `None`.

**Why.** PHN is the authority on resolution; it already ran mull → assigned →
default and shipped the answer. Re-deriving it from a second resolver in
honeybee-ph invites the two to disagree. Explicit assignment also makes the HBJSON
self-describing: every edge names the condition it was modeled under.

**Cost.** Slightly larger HBJSON, and `install_types` is serialized on essentially
every PHN-sourced aperture rather than only the interesting ones. Acceptable —
`AperturePsiInstalls.to_dict()` writes four small objects at most.

## D-5 — The EP U-factor uses a transient effective frame

**Decision.** Resolve per-edge Ψ into a throwaway duplicate frame for the
`iso_10077_1` call inside `create_new_hbph_window_material`. Do not persist it.

**Why.** `calculate_window_uw` already includes `heat_loss_psi_install`, so the
EnergyPlus U-factor is Ψ-sensitive today and currently wrong on mulled edges.
Fixing it without violating D-1 requires exactly the transient-duplicate pattern
that `honeybee_ph_utils.aperture_psi_install.resolve_effective_frame()` uses
upstream for the same reason.

**Verified safe.** `PhWindowFrame.__copy__` (`honeybee_energy_ph/construction/window.py`)
deep-copies all four sides (`new_obj.top = self.top.duplicate()`, …), so
overwriting `psi_install` on the duplicate cannot reach back into the shared
`PhWindowFrameElement` pool built by `create_new_hbph_frame_elements`. That was
the one mechanism by which this decision could have quietly reintroduced #59;
it does not exist.

**Open, not decided here:** whether to also switch that call from the ISO Annex-F
standard-size window to the element's real dimensions. See PRD.md §5.1.
