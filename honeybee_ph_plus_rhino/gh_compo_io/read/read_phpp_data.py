# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Functions to read PHPP data using a specified Shell-script."""

import os

try:
    from typing import Any
except ImportError as e:
    pass  # IronPython 2.7

try:
    from honeybee.config import folders as hb_folders
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.run_subprocess import (
        process_stderr,
        process_stdout,
        run_subprocess_from_shell,
    )
except ImportError as e:
    raise ImportError("\nFailed to import run_subprocess:\n\t{}".format(e))


def run(_IGH, _py3_shell_file, _py3_script_file, _output_file, _phpp_file):
    # type: (gh_io.IGH, str, str, str, str | None) -> Any

    # # -- Run as a Subprocess so we can use Python3, pandas, etc.
    if os.name == "nt":
        raise NotImplementedError("This component is not yet implemented for Windows.")
    else:
        # -- If on MacOS, run the subprocess through a shell-script
        # -- and another terminal window in order to connect to Excel.
        # -- This is a workaround for the permissions issue on MacOS.
        # -- See:
        # -- https://discourse.mcneel.com/t/python-subprocess-permissions-error-on-mac-os-1743/142830/6

        execution_root = os.path.join(
            hb_folders.python_package_path, "honeybee_ph_plus_rhino"
        )
        # -- Build up the commands to run
        commands = [
            _py3_shell_file,  # -------------- The shell script to run
            execution_root,
            hb_folders.python_exe_path,  # --- The python3-interpreter to use
            _py3_script_file,  # ------------- The python3-script to run
            _output_file,  # ----------------- The output CSV filepath
            str(_phpp_file),  # ------------------- The input PHPP file
        ]
        stdout, stderr = run_subprocess_from_shell(commands)

        process_stdout(_IGH, stdout)
        process_stderr(_IGH, stderr)

    return _output_file
