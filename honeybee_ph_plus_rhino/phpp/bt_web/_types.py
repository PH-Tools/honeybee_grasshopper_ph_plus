# -*- coding: utf-8 -*-
# -*- Python Version: 3.10 -*-

"""PHPP Data Classes."""

from dataclasses import dataclass

import pandas as pd


@dataclass
class PHPPData:
    """Collection of PHPP Data"""

    df_variants: pd.DataFrame
    df_climate: pd.DataFrame
    df_room_vent: pd.DataFrame
    df_certification_limits: pd.DataFrame
    df_tfa: pd.DataFrame
    variant_names: pd.Series
