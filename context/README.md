# context/ — canonical repo documentation

Stable, ground-truth documentation for HBPH+. Distinct from `planning/` (in-flight work). This repo has no `docs/` folder.

`CLAUDE.md` at the repo root is the dispatcher; this folder holds the docs it routes to. The deepest architecture doc — the two-layer/fsdeploy "why" and `GHCompo_*` anatomy — lives at `honeybee_ph_plus_rhino/gh_compo_io/.index.md`; the docs here point to it rather than duplicate it.

## Index

| Doc | Read when you need… |
|-----|---------------------|
| [`PRD.md`](PRD.md) | What HBPH+ is for and how it relates to the base HBPH package |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Orientation on the two-layer design + subpackage map (deep "why" is in `gh_compo_io/.index.md`) |
| [`TECH_STACK.md`](TECH_STACK.md) | Dependencies, the fsdeploy dev loop, release |
| [`CODING_STANDARDS.md`](CODING_STANDARDS.md) | IronPython 2.7 rules, imports, type comments, formatting, naming |

## Maintenance rule

When a decision changes how components are built, deployed, or released, fold it into the relevant doc here (or the `gh_compo_io/.index.md` "why" doc). Keep them true.
