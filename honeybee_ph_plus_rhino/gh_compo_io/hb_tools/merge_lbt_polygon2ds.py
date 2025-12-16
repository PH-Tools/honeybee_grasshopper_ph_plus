# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Merge LBT Polygon2Ds."""

try:
    from typing import Any, Dict, List, Optional
except ImportError:
    pass  # IronPython 2.7

try:
    from ladybug_geometry.geometry2d.polygon import Polygon2D
except ImportError as e:
    raise ImportError("Failed to import ladybug_geometry")

try:
    from honeybee_ph_utils import polygon2d_tools
except ImportError:
    raise ImportError("Failed to import honeybee_ph_utils")

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")


class GHCompo_MergeLBTPolygon2Ds(object):
    def __init__(self, _IGH, _tolerance, _lbt_polygon2ds, *args, **kwargs):
        # type: (gh_io.IGH, Optional[float], List[Polygon2D],  List[Any], Dict[str, Any]) -> None
        self.IGH = _IGH
        self.tolerance = _tolerance or self.IGH.ghdoc.ModelAbsoluteTolerance
        self.lbt_polygon2ds = _lbt_polygon2ds or []

    def run(self):
        # type: () -> List[Polygon2D]
        """Merge the LBT-Polygon2Ds.

        Returns:
        --------
            List[Polygon2D]: A list of the merged LBT-Polygon2Ds
        """
        merged_polygon_2d = polygon2d_tools.merge_polygon_2ds(self.lbt_polygon2ds, self.tolerance)

        if len(merged_polygon_2d) > 1:
            self.IGH.warning("Warning: Merge resulted in more than one polygon.")

        return merged_polygon_2d
