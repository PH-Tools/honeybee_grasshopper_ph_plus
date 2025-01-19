# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Run a Python Subprocess."""


import os
import subprocess


def run_subprocess(commands, _input=None):
    # type: (list[str], str | None) -> tuple[bytes, bytes]
    """Run a python subprocess.Popen, using the supplied commands.

    Args:
        commands: A list of the commands to pass to Popen
        _input: (Optional) A string to pass to the 'input' of the Popen process

    Returns:
        tuple:
            * [0] (bytes): stdout
            * [1] (bytes): stderr
    """
    # -- Create a new PYTHONHOME to avoid the Rhino-8 issues
    CUSTOM_ENV = os.environ.copy()
    CUSTOM_ENV["PYTHONHOME"] = ""

    use_shell = True if os.name == "nt" else False

    process = subprocess.Popen(
        commands,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=use_shell,
        env=CUSTOM_ENV,
    )

    if _input:
        stdout, stderr = process.communicate(input=_input)
    else:
        stdout, stderr = process.communicate()

    if stderr:
        if "Defaulting to Windows directory." in str(stderr):
            print("WARNING: {}".format(stderr))
        else:
            print(stderr)
            raise Exception(stderr)

    for _ in str(stdout).split("\\n"):
        print(_)

    return stdout, stderr
