# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Get Face Polygon2Ds in Ref. Space."""

try:
    from typing import Any, Dict, List, Any, Optional, Tuple, Generator
except ImportError:
    pass  # IronPython 2.7

try:
    from System import Object  # type: ignore
    from Grasshopper import DataTree  # type: ignore
    from Grasshopper.Kernel.Data import GH_Path  # type: ignore
except:
    raise ImportError("Failed to import Grasshopper")

try:
    from Rhino.Geometry import Point3d, Brep  # type: ignore
except ImportError:
    raise ImportError("Failed to import Rhino")

try:
    from ladybug_geometry.geometry2d.polygon import Polygon2D
    from ladybug_geometry.geometry3d.plane import Plane
    from ladybug_geometry.geometry3d.face import Face3D
except ImportError as e:
    raise ImportError("Failed to import ladybug_geometry")

try:
    from honeybee import face
except ImportError as e:
    raise ImportError("Failed to import honeybee")

try:
    from honeybee_ph_utils import polygon2d_tools
except ImportError:
    raise ImportError("Failed to import honeybee_ph_utils")

try:
    from honeybee_ph_rhino import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")


class GHCompo_GeneratePolygon2DFromHBFaces(object):
    def __init__(self, _IGH, _hb_faces, _tolerance, *args, **kwargs):
        # type: (gh_io.IGH,List[face.Face], Optional[float], List[Any], Dict[str, Any]) -> None
        self.IGH = _IGH
        self.hb_faces = _hb_faces or []
        self.tolerance = _tolerance or self.IGH.ghdoc.ModelAbsoluteTolerance

    @property
    def lbt_face3Ds(self):
        # type: () -> List[Face3D]
        """Return the LBT-Face3Ds of all the HB-Faces."""
        return [f.geometry for f in self.hb_faces]

    @property
    def lbt_poly2Ds(self):
        # type: () -> List[Polygon2D]
        """Return the Polygon2Ds of all the LBT-Face3Ds."""
        return [f.geometry.polygon2d for f in self.hb_faces]

    @property
    def lbt_face3D_planes(self):
        # type: () -> List[Plane]
        """Return the Planes of all the HB-Faces."""
        return [f.geometry.plane for f in self.hb_faces]

    @property
    def reference_plane(self):
        # type: () -> Plane
        """Return the reference plane to be used for all the Polygon2Ds created.

        This is always the plane of the first face input.
        """

        return self.lbt_face3Ds[0].plane

    def generate_starting_breps(self):
        # type: () -> DataTree[Brep]
        """Generate the starting Rhino breps for the component (for preview)."""

        starting_polygons_ = DataTree[Brep]()
        for i, _face3D in enumerate(self.lbt_face3Ds):
            starting_polygons_.Add(
                self.IGH.ghc.BoundarySurfaces(
                    self.IGH.ghc.PolyLine(
                        (Point3d(v.x, v.y, v.z) for v in _face3D.vertices), True
                    )
                ),
                GH_Path(i),
            )
        return starting_polygons_

    def generate_result_breps(self, polygons_in_ref_space_):
        # type: (List[Polygon2D]) -> DataTree[Brep]
        """Generate the resulting (translated) Rhino breps for the component (for preview)."""

        rhino_breps_ = DataTree[Brep]()
        for i, p in enumerate(polygons_in_ref_space_):
            rhino_breps_.Add(
                self.IGH.ghc.BoundarySurfaces(
                    self.IGH.ghc.PolyLine(
                        (Point3d(v.x, v.y, 0) for v in p.vertices), True
                    )
                ),
                GH_Path(i),
            )

        return rhino_breps_

    def run(self):
        # type: () -> Tuple[List[Polygon2D], DataTree[Brep], DataTree[Brep]]
        """Run the component and return the results.

        Returns:
        --------
            * Tuple:
                * [0] - (List[Polygon2D]) List of generated LBT-Polygon2Ds in the reference plane
                * [1] - (DataTree[Brep]) Starting Rhino breps (*)for preview)
                * [2] - (DataTree[Brep]) Resulting Rhino breps (for preview)
        """
        # ---------------------------------------------------------------------
        # -- Get all the LBT-Face3D Polygon2Ds in the same Plane-space
        translated_polygon2Ds = []  # type: List[Polygon2D]
        for face3D_poly_2D, face3D_plane in zip(self.lbt_poly2Ds, self.lbt_face3D_planes):
            translated_polygon2Ds.append(
                polygon2d_tools.translate_polygon2D(
                    face3D_poly_2D, face3D_plane, self.reference_plane, self.tolerance
                )
            )

        # ---------------------------------------------------------------------
        # -- Generate the preview breps for troubleshooting
        starting_breps = self.generate_starting_breps()
        result_breps = self.generate_result_breps(translated_polygon2Ds)

        return (translated_polygon2Ds, starting_breps, result_breps)
