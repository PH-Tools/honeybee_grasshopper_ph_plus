# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""A script to read all the Table names from a specified SQL file.

This script is called from the command line with the following arguments:
    * [0] (str): The path to the Python script (this file).
    * [1] (str): The folder path to save the HTML file.
    * [2] (str): The name of the HTML file to save.
"""

import json
import os
import sys
from collections import namedtuple
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

try:
    from ladybug.datacollection import HourlyContinuousCollection
except ImportError as e:
    raise ImportError("\nFailed to import ladybug:\n\t{}".format(e))


def resolve_arguments(_args: list[str]) -> tuple[Path, str, str, str, list[float]]:
    """Get out the file input table name.

    Arguments:
    ----------
        * _args (list[str]): sys.args list of input arguments.

    Returns:
    --------
        * Path: The HTML save file path.
        * str: The unit type of the data.
    """
    
    num_args = len(_args)
    assert num_args == 6, "Wrong number of arguments. Got {}.".format(num_args)

    html_file_path = Path(str(_args[1]))
    if not html_file_path:
        raise Exception("Error: missing save filename")

    unit_type = str(_args[2])
    if not unit_type:
        raise Exception("Error: Missing unit-type")

    y_axis = str(_args[3])
    if not y_axis:
        raise Exception("Error: Missing y-axis title")

    plot_title = str(_args[4])
    if not plot_title:
        raise Exception("Error: Missing plot title")

    horizontal_lines = eval(_args[5])

    return html_file_path, unit_type, y_axis, plot_title, horizontal_lines


def create_line_plot_figure(
    _df: pd.DataFrame,
    _title: str,
    _y_axis_title: str,
    _horizontal_lines: list[float] | None = None,
    _stack: bool = False,
) -> go.Figure:
    """Create a line plot figure from the DataFrame."""

    fig = go.Figure()

    if _df.empty:
        return fig

    for zone_name in _df["Zone"].unique():
        zone_data = _df[_df["Zone"] == zone_name]
        if _stack:
            fig.add_trace(
                go.Scatter(
                    x=zone_data["Date"],
                    y=zone_data["Value"],
                    mode="lines",
                    stackgroup="one",
                    name=zone_name,
                )
            )
        else:
            fig.add_trace(
                go.Scatter(
                    x=zone_data["Date"],
                    y=zone_data["Value"],
                    mode="lines",
                    name=zone_name,
                )
            )

    if _horizontal_lines:
        for line in _horizontal_lines:
            fig.add_shape(
                type="line",
                x0=_df["Date"].min(),  # Start of the line (minimum date)
                x1=_df["Date"].max(),  # End of the line (maximum date)
                y0=line,  # Y-coordinate of the line
                y1=line,  # Y-coordinate of the line
                line=dict(color="Red", width=2, dash="dash"),  # Line style
            )

    # Configure the legend to be at the bottom
    fig.update_layout(
        title=_title,
        legend=dict(
            orientation="v",  # Vertical layout
            x=0,  # Align to the left
            y=-0.2,  # Move it below the plot (adjust as needed)
        ),
        yaxis_title=_y_axis_title,
    )

    return fig


def build_df(hourly_collections: list[HourlyContinuousCollection]) -> pd.DataFrame:
    df = pd.DataFrame()

    for hourly_collection in hourly_collections:
        values = hourly_collection.values
        dates = hourly_collection.header.analysis_period.datetimes
        zone_name = hourly_collection.header.metadata.get("Zone", "Unknown")
        df = pd.concat([df, pd.DataFrame({"Date": dates, zone_name: values})], axis=1)
    return df


def get_plot_element_name(hourly_collection: HourlyContinuousCollection) -> str:
    _zone = hourly_collection.header.metadata.get("Zone", "Unknown Zone")
    _type = hourly_collection.header.metadata.get("type", "Unknown Type")
    return f"{_type} | {_zone}"


Record = namedtuple("Record", ["Date", "Value", "Zone", "DataType", "DataUnit"])


if __name__ == "__main__":
    # -- Get the Ladybug Hourly Data as a list of JSON Objects
    save_filer_path, unit_type, y_axis_label, plot_title, horizontal_lines = (
        resolve_arguments(sys.argv)
    )
    input_data = sys.stdin.read()
    data = json.loads(input_data)

    # -- Build up a list of data Records from the Ladybug Hourly Data
    hourly_collections: list[Record] = []
    for data_object in data:
        hourly_collection = HourlyContinuousCollection.from_dict(data_object)

        hourly_collections.extend(
            [
                Record(
                    d,
                    v,
                    get_plot_element_name(hourly_collection),
                    str(hourly_collection.header.data_type),
                    str(hourly_collection.header.unit),
                )
                for d, v in zip(
                    hourly_collection.header.analysis_period.datetimes,
                    hourly_collection.values,
                )
            ]
        )

    # -- Create the Plotly Line Plot
    with open(save_filer_path, "w") as f:
        f.write(
            pio.to_html(
                create_line_plot_figure(
                    pd.DataFrame(hourly_collections),
                    plot_title,
                    y_axis_label,
                    horizontal_lines,
                ),
                full_html=False,
                include_plotlyjs="cdn",
            )
        )
