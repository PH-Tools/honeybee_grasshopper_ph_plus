# 06 — Shared helper: `setup_component_outputs` in `ph_gh_component_io`

**Repo:** `PH_GH_Component_IO` (sibling package `ph_gh_component_io`), file
`ph_gh_component_io/gh_io.py`.
**Decision (Ed, confirmed):** add the output-side helper to the shared package —
NOT a private copy in HBPH+. Reusable by any future dynamic-output component.

> **STATUS: DONE (uncommitted).** `ComponentOutput` + `setup_component_outputs`
> added to `gh_io.py` (beside `ComponentInput` / `setup_component_inputs`), py_compile
> clean. No version bump / commit yet (per repo convention — bump-my-version tags on
> release; do when ready). No unit test added — the repo has no test harness and
> `gh_io.py` can't import under CPython (System/GhPython/Grasshopper load at module
> top), so a test needs those mocked; deferred as out-of-scope for this change.

## Why

`gh_io.py` already has the input-side twin:
- `class ComponentInput` (name, description, access, type_hint, target_unit)
- `def setup_component_inputs(IGH, _input_dict, _start_i=1, _end_i=20)` — rewrites
  `IGH.ghenv.Component.Params.Input[i]` (`Name`/`NickName`/`Description`/`Access`/`TypeHint`).

There is **no** output equivalent. The Organize Table component (`05-…`) needs to
rename/activate output ports dynamically by `_type`. GH output params are generic
(no `TypeHint`), so the helper is a strict simplification of the input one.

## What to add

```python
class ComponentOutput:
    """GH-Component Output Node data class."""
    def __init__(self, _name="-", _description="", _access=0):
        # type: (str, str, int) -> None
        self.name = _name
        self.description = _description
        self.access = _access  # 0='item', 1='list', 2='tree'
    # __str__/__repr__/ToString mirroring ComponentInput


def setup_component_outputs(IGH, _output_dict, _start_i=1, _end_i=20):
    # type: (IGH, Dict[int, ComponentOutput], int, int) -> None
    """Dynamic GH component OUTPUT node configuration (twin of setup_component_inputs).

    Rewrites Params.Output[i].Name/NickName/Description/Access from _output_dict.
    Ports not present in _output_dict are reset to a blank '-' node so stale names
    from a previous _type don't linger.
    """
    for output_num in range(_start_i, _end_i):
        item = _output_dict.get(output_num, ComponentOutput("-", "-"))
        try:
            node = IGH.ghenv.Component.Params.Output[output_num]
            node.NickName = item.name
            node.Name = item.name
            node.Description = item.description
            node.Access = IGH.Grasshopper.Kernel.GH_ParamAccess(item.access)
        except ValueError:
            pass  # past end of component outputs
    return None
```

## Notes / constraints

- **IronPython 2.7 + Py2/3 dual-target.** Match the file's existing style (that repo
  targets both). No f-strings; keep `# type:` comments.
- **`_start_i` for outputs is usually `0` or `1`.** GHPython's first output is often
  a reserved `out` (runtime messages) at index 0; confirm the base index on the
  Organize ghuser and pass `_start_i` accordingly (inputs start at 1 there; outputs
  likely start at 1 as well if index 0 is the `out` stream).
- **Re-entrancy.** Because GH re-solves on every change, `setup_component_outputs`
  must be idempotent and must reset unused ports to `-` (handled above) so switching
  `_type` from a wide table (Appliances, 11) to a narrow one (Electric Heaters, 2)
  clears the leftover ports.
- **No wire preservation guarantee.** Renaming a port that has a downstream wire
  keeps the wire but changes the label — acceptable and matches how
  `setup_component_inputs` already behaves.

## Version / release

- Bump `ph_gh_component_io` (its own release process) and note the new minimum
  version in HBPH+ where the Organize component imports it.
- Sequencing: land this helper **before** `table_organize.py`'s `src/` wrapper (the
  wrapper calls it at solve time).

## Test

- Add a small unit/spec in `PH_GH_Component_IO` mirroring any existing
  `setup_component_inputs` test (mock `IGH.ghenv.Component.Params.Output`).
