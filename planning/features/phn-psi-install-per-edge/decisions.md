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

## D-2 — Deliver an `install_types_` collection **plus** a component that applies it

> **Revised 2026-08-26** after verifying the original plan against the code. The
> first version of this decision routed the collection through
> `HBPH+ - Get From Custom Collection` into the merged
> `HBPH - Set Aperture Psi-Installs` and claimed that needed "no new matching
> logic and no new component." That claim does not survive reading the setter.

**Decision.** Two pieces:

1. A new `install_types_` output on `HBPH+ - PH-Nav Get Apertures`: a
   `CustomCollection` keyed by element type-name (`Test Aperture_C0_R0`), value =
   the ordered list `[top, right, bottom, left]` of `PhApertureInstallType`.
2. A new component, **`HBPH+ - PH-Nav Set Aperture Psi-Installs`**, taking `_apertures` and
   `_install_types` (that collection) and doing the key → element lookup
   internally, off each aperture's own `display_name`. It duplicates the
   apertures and writes the four slots directly, never touching the construction.

**Why the setter route fails.** `HBPH - Set Aperture Psi-Installs` matches by
**branch index**, and every aperture in a branch receives the *same* four Install
Types:

```python
for branch_idx, apertures in enumerate(self._apertures.Branches):
    install_types_by_side = [as_install_type(get_tree_item(self._install_types, branch_idx, side_idx)) ...]
    for ap in apertures:   # <- all four shared across the whole branch
```

That is the right contract for its own use case (one install condition painted
over a set of windows). It is the wrong one here, where every element differs.
And `srfc_names_` from `HBPH+ - Create Window Geometry` is a **flat list** of
every element surface, so the apertures land in a single branch. Two failure
modes, depending on how GhPython marshals a nested list on an output:

- flattened → the branch holds 4N items, the setter reads items 0-3, and the
  first element's four values are applied to **every** aperture. No error.
- wrapped → `as_install_type` receives a list and `parse_psi_install_w_mk`
  raises.

The first is silent and would ship a wrong model. Making the setter route work
needs grafting on both trees *plus* a resolved answer on nested-list
marshalling, which nothing in the repo currently exercises.

**Why the new component instead.** The key is already on the aperture. A
key-based lookup is immune to tree topology, cannot silently mis-align, and can
report unmatched apertures. It costs the full component pattern — `src/`
wrapper, `_component_info_.py` entry, icon, `.ghuser` — which is a known,
bounded cost, unlike an unverified wiring assumption.

**`HBPH - Set Aperture Psi-Installs` stays the right tool** for hand-painted
install conditions on a branch of windows. This is the bulk PH-Nav path, not a
replacement for it.

**Rejected:** a separate `HBPH+ - PH-Nav Get Install Types` component. It would
issue a second identical route-3 request or need the payload passed to it, for no
gain over an extra output on the getter.

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
