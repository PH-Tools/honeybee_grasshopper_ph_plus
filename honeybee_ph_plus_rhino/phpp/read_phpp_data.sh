#!/usr/bin/env bash
# Used to run the python script in a new terminal window. 
# This is needed for MacOS in order to get around the permissions issues with Rhino and Excel.

exe_path=$1
python_exe_path=$2
python_script_path=$3
csv_output_file=$4
phpp_input_file=$5

PYTHONHOME=""
export PYTHONHOME
echo Using:
echo - Path: ${exe_path}
echo - Python: ${python_exe_path}
echo - Script: ${python_script_path}
echo - CSV-File: ${csv_output_file}
echo - PHPP-File: ${phpp_input_file}
cd "$exe_path"
osascript -e "tell app \"Terminal\"
    do script \"\\\"${python_exe_path}\\\" \\\"${python_script_path}\\\" \\\"${csv_output_file}\\\" \\\"${phpp_input_file}\\\" \"
end tell"