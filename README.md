# honeybee-grasshopper-ph+:

Additional HBPH components for Rhino / Grasshopper.

![Screenshot 2024-01-25 at 6 48 52 PM](https://github.com/PH-Tools/honeybee_grasshopper_ph_plus/assets/69652712/9c9261f7-52b3-4174-aa98-5d41b9231316)

This repository contains the HBPH+ Grasshopper components for the Honeybee-PH plugin. These are additional utility components for more advanced HBPH model configurations. The basic HBPH Grasshopper pacakge is required in addition to these extra components. 

More information, examples, and tutorials can be found on the [Honeybee-PH](https://ph-tools.github.io/honeybee_grasshopper_ph/) page.

## Development

HBPH+ uses a two-layer design: thin canvas wrappers in `honeybee_grasshopper_ph_plus/src/` and the actual `GHCompo_*` logic classes in `honeybee_ph_plus_rhino/gh_compo_io/`. All deployed code targets **IronPython 2.7**; the base `honeybee_grasshopper_ph` package is required.

For contributor/agent orientation see [`CLAUDE.md`](CLAUDE.md) and the [`context/`](context/) folder. The deep architecture rationale (two-layer facade, fsdeploy, `GHCompo_*` anatomy) is in [`honeybee_ph_plus_rhino/gh_compo_io/.index.md`](honeybee_ph_plus_rhino/gh_compo_io/.index.md).

[![IronPython](https://img.shields.io/badge/ironpython-2.7-red.svg)](https://github.com/IronLanguages/ironpython2/releases/tag/ipy-2.7.8/)
