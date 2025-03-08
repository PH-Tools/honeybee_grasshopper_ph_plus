# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Run a Python Subprocess."""

try:
    from typing import Any
except ImportError as e:
    pass  # IronPython 2.7

import os
import subprocess

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


def process_stdout(_IGH, _stdout):
    # type: (gh_io.IGH, bytes) -> None
    if not _stdout:
        return None
    for row in str(_stdout.decode("utf-8")).split("\\n"):
        print(row)
        _IGH.remark(row)


def process_stderr(_IGH, _stderr):
    # type: (gh_io.IGH, bytes) -> None
    if not _stderr:
        return
    for row in str(_stderr.decode("utf-8")).split("\\n"):
        print(row)
        _IGH.error(row)


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
    process.wait()  # Ensure the process is completely finished

    if _input:
        stdout, stderr = process.communicate(input=_input)  # type: ignore
    else:
        stdout, stderr = process.communicate()

    return stdout, stderr


def run_subprocess_from_shell(commands):
    # type: (list[str]) -> tuple[bytes, bytes]
    """Run a python subprocess.Popen THROUGH a MacOS terminal via a shell, using the supplied commands.

    When talking to Excel on MacOS it is necessary to run through a Terminal since Rhino
    cannot get the right 'permissions' to interact with Excel. This is a workaround and not
    required on Windows OS.

    Arguments:
    ----------
        * _commands: (List[str]): A list of the commands to pass to Popen

    Returns:
    --------
        * Tuple:
            - [0]: stdout
            - [1]: stderr
    """

    # -- Create a new PYTHONHOME to avoid the Rhino-8 issues
    CUSTOM_ENV = os.environ.copy()
    CUSTOM_ENV["PYTHONHOME"] = ""

    use_shell = True if os.name == "nt" else False

    # -- Make sure the files are executable
    shell_file = commands[0]
    try:
        subprocess.check_call(["chmod", "u+x", shell_file])
    except Exception as e:
        print("Failed to make the shell file executable: {}".format(e))
        raise e

    python_script_path = commands[3]
    try:
        subprocess.check_call(["chmod", "u+x", python_script_path])
    except Exception as e:
        print("Failed to make the python script executable: {}".format(e))
        raise e

    process = subprocess.Popen(
        commands,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=use_shell,
        env=CUSTOM_ENV,
    )
    process.wait()  # Ensure the process is completely finished
    stdout, stderr = process.communicate()

    return stdout, stderr
