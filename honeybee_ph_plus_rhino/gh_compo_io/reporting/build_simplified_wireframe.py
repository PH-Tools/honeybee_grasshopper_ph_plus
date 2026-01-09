# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Create a simplified wireframe from a Honeybee Model."""


try:
    from System import Object # type: ignore
    from System.Drawing import Color # type: ignore
    import Rhino # type: ignore
    from Grasshopper import DataTree # type: ignore
    from Grasshopper.Kernel.Data import GH_Path # type: ignore
except ImportError as e:
    raise ImportError("\nFailed to import from Rhino:\n\t{}".format(e))

try:
    from ladybug_rhino.fromgeometry import from_face3d
except ImportError as e:
    raise ImportError("\nFailed to import ladybug_rhino:\n\t{}".format(e))

try:
    from honeybee.boundarycondition import Surface
    from honeybee.model import Model
    from honeybee.face import Face
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph_utils.face_tools import sort_hb_faces_by_co_planar, group_hb_faces
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError as e:
    raise ImportError("\nFailed to import ph_gh_component_io:\n\t{}".format(e))


class GHCompo_BuildHbModelSimplifiedWireframe(object):
    def __init__(self, _IGH, _hb_model, _color):
        # type: (gh_io.IGH, Model, Color | None) -> None
        self.IGH = _IGH
        self.hb_model = _hb_model
        self.color = _color

    @property
    def ready(self):
        if not self.hb_model:
            return False
        return True

    def run(self):
        # type: () -> tuple[list[Face], list, DataTree[Object], DataTree[Object], DataTree[Object], DataTree[Object], None]

        if not self.ready:
            return [], [], DataTree[Object](), DataTree[Object](), DataTree[Object](), [], None
        
        # -------------------------------------------------------------------------------
        # -- Get all the HB Envelope Faces
        faces_ = []
        for room in self.hb_model.rooms:
            for face in room.faces:
                if isinstance(face.boundary_condition, Surface):
                    continue
                dup_face = face.duplicate()
                dup_face.remove_sub_faces()
                faces_.append(dup_face)


        # -------------------------------------------------------------------------------
        # -- Find the CoPlanar Face Groups
        coplanar_face_groups_ = DataTree[Object]()
        for i, group in enumerate(
            sort_hb_faces_by_co_planar(
                faces_, self.IGH.ghdoc.ModelAbsoluteTolerance, self.IGH.ghdoc.ModelAngleToleranceDegrees
            )
        ):
            coplanar_face_groups_.AddRange(group, GH_Path(i))


        # -------------------------------------------------------------------------------
        # -- Merge the FaceGroups
        merged_hb_faces_ = DataTree[Object]()
        for i, b in enumerate(coplanar_face_groups_.Branches):
            for j, group in enumerate(
                group_hb_faces(b, self.IGH.ghdoc.ModelAbsoluteTolerance, self.IGH.ghdoc.ModelAngleToleranceDegrees)
            ):
                merged_hb_faces_.AddRange(group, GH_Path(i, j))  # type: ignore


        # -------------------------------------------------------------------------------
        # -- Create Rhino Surface Geometry
        construction_names_ = DataTree[Object]()
        rh_surfaces_ = DataTree[Object]()
        for i, branch in enumerate(merged_hb_faces_.Branches):
            faces = []
            for lb_face in branch:
                construction_name = lb_face.properties.energy.construction.display_name
                rh_face = from_face3d(lb_face.geometry)
                faces.append(rh_face)
                construction_names_.Add(construction_name, GH_Path(i))

            faces = self.IGH.ghc.MergeFaces(self.IGH.ghc.BrepJoin(faces).breps).breps
            if isinstance(faces, list):
                rh_surfaces_.AddRange(faces, GH_Path(i))
            else:
                rh_surfaces_.Add(faces, GH_Path(i))


        # -------------------------------------------------------------------------------
        # -- Create Rhino Wireframe Geometry
        wireframe_ = []
        all_rh_surfaces = self.IGH.ghc.FlattenTree(rh_surfaces_, GH_Path(0))
        joined_breps = self.IGH.ghc.BrepJoin(all_rh_surfaces).breps
        if not isinstance(joined_breps, list):
            joined_breps = [joined_breps]

        outline_layer = self.IGH.ghc.ModelLayer(layer="Outline", name="Outline").layer
        for brep in joined_breps:
            # -- Build the actual Model Object
            curves = self.IGH.ghc.JoinCurves(self.IGH.ghc.BrepWireframe(brep, -1), False)
            model_obj = self.IGH.ghc.ModelObject(
                object=curves,
                geometry=curves,
                layer=outline_layer,
            ).object
            if not isinstance(model_obj, list):
                model_obj = [model_obj]
            wireframe_.extend(model_obj)

        # -------------------------------------------------------------------------------
        # -- Setup the Wireframe Render Material
        material_name = "_wireframe_outline__"
        rh_material = self.IGH.create_rhino_render_material(material_name, self.color)
        gh_material = self.IGH.gh_type.GH_Material(rh_material.Id)

        # -------------------------------------------------------------------------------
        # -- Outputs
        return (
            faces_,
            coplanar_face_groups_,
            merged_hb_faces_,
            rh_surfaces_,
            construction_names_,
            wireframe_,
            gh_material,
        )
