# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Functions for exporting a PDF report page."""

import os

try:
    from itertools import izip_longest  # type: ignore
except:
    from itertools import zip_longest as izip_longest

try:
    from typing import Iterable, List, Optional, Tuple
except ImportError:
    pass  # IronPython 2.7

try:
    from System import Guid  # type: ignore
    from System.Drawing import Color, Size  # type: ignore
except ImportError:
    pass  # Outside .NET

try:
    from Rhino import Display as rdp  # type: ignore
    from Rhino import DocObjects as rdo  # type: ignore
    from Rhino import FileIO  # type: ignore
    from Rhino import Geometry as rg  # type: ignore
    from Rhino.DocObjects.DimensionStyle import MaskFrame  # type: ignore

    # from Rhino.Geometry import (
    #     Hatch,
    #     Mesh,
    #     Point3d,
    #     Rectangle3d,
    #     TextJustification,
    #     Transform,
    # )
except ImportError:
    pass  # Outside Rhino

try:
    from Grasshopper import DataTree  # type: ignore
except ImportError:
    pass  # Outside Grasshopper

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")

try:
    from honeybee_ph_utils.input_tools import clean_tree_get
except ImportError:
    raise ImportError("Failed to import honeybee_ph_utils")

try:
    from honeybee_ph_plus_rhino.gh_compo_io.reporting.annotations import TextAnnotation
    from honeybee_ph_plus_rhino.gh_compo_io.reporting.create_clipping_plane_set import (
        ClippingPlaneLocation,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


def create_default_solid_hatch_pattern(_IGH):
    # type: (gh_io.IGH) -> int
    """Create a new SOLID hatch pattern in the document and return its index."""
    hatch_pattern = rdo.HatchPattern()
    hatch_pattern.FillType = rdo.HatchPatternFillType.Solid  # type: ignore
    hatch_pattern.Name = "SOLID"
    try:
        new_index = _IGH.sc.doc.HatchPatterns.Add(hatch_pattern)
        return new_index
    except Exception as e:
        print(e)
        return 0


def get_default_solid_hatch_index(_IGH):
    # type: (gh_io.IGH) -> int
    """Return the index of the default SOLID hatch pattern.

    If the SOLID hatch pattern does not exist, create it first.
    """
    for hatch_pattern in _IGH.sc.doc.HatchPatterns:
        if str(hatch_pattern.Name).upper() == "SOLID":
            return hatch_pattern.Index
    try:
        return create_default_solid_hatch_pattern(_IGH)
    except Exception as e:
        print(e)
        return 0


def hatch_from_curve(_hatchCurve, _tolerance, _hatch_pattern_index=0):
    # type: (rg.Curve, float, int) -> rg.Hatch
    return rg.Hatch.Create(
        curve=_hatchCurve,
        hatchPatternIndex=_hatch_pattern_index,
        rotationRadians=0,
        scale=0,
        tolerance=_tolerance,
    )[0]


def _clean_filename(_input_str):
    # type: (str) -> str
    """Return a cleaned and validated filename string."""
    valid_filename = os.path.splitext(_input_str)[0]  # remove any extension
    valid_filename = valid_filename.replace(" ", "_").strip()
    valid_filename = "".join(_ if _.isalnum() else "_" for _ in valid_filename)
    return valid_filename


def gen_file_paths(_save_folder, _file_names, _target_length):
    # type: (str, DataTree, int) -> List[str]
    """Return a list of full paths for each PDF file to export. Will create save folder if needed.

    Arguments:
    ----------
        * _save_folder (str):
        * _file_names (DataTree):
        * _target_length (int):

    Returns:
    --------
        * List[str]
    """
    file_paths = []

    if not _save_folder:
        return file_paths

    if _file_names.BranchCount == 0:
        return file_paths

    if _target_length == 0:
        # save-file list len should match the target (geometry) len.
        return file_paths

    if _file_names.BranchCount != _target_length:
        raise Exception(
            "Error: The number of geometry branches ({}) does not"
            " match the number of file-names ({})?".format(
                _target_length, _file_names.BranchCount
            )
        )

    # --- Save folder
    if not os.path.exists(_save_folder):
        try:
            os.makedirs(_save_folder)
        except Exception as e:
            raise Exception("{}\nError creating save folder: {}".format(e, _save_folder))

    # -- Save filenames
    for branch in _file_names.Branches:
        file_name = _clean_filename(str(branch[0]))
        file_path = os.path.join(_save_folder, file_name + os.extsep + "pdf")
        file_paths.append(file_path)

    return file_paths


def gen_layout_names(_layout_names, _target_length):
    layout_names = []

    if not _layout_names:
        return layout_names

    if _layout_names.BranchCount == 0:
        return layout_names

    if _target_length == 0:
        # layout-name list len should match the target (geometry) len.
        return layout_names

    # -- Create the LayoutNames list
    for i in range(_target_length):
        try:
            layout_names.append(_layout_names.Branch(i)[0])
        except:
            try:
                layout_names.append(_layout_names.Branch(0)[0])
            except:
                raise Exception("Error: Shape of _layout_names does not match geometry?")

    return layout_names


def get_active_view_name(_IGH):
    return _IGH.scriptcontext.doc.Views.ActiveView.ActiveViewport.Name


def set_active_view_by_name(_IGH, _view_name):
    # type: (gh_io.IGH, str) -> None
    """Changes the Active View to the specified layout/view by name. Raises an error if the target view name does not exist.

    Arguments:
    ----------
        * _IGH (gh_io.IGH):
        * _view_name (str):

    Returns:
    --------
        * (None)
    """
    # https://developer.rhino3d.com/samples/rhinocommon/get-and-set-the-active-view/

    # active view and non-active view names
    active_view_name = get_active_view_name(_IGH)
    non_active_views = [
        (view.ActiveViewport.Name, view)
        for view in _IGH.scriptcontext.doc.Views
        if view.ActiveViewport.Name != active_view_name
    ]

    if _view_name != active_view_name:
        if _view_name in [seq[0] for seq in non_active_views]:
            _IGH.scriptcontext.doc.Views.ActiveView = [
                seq[1] for seq in non_active_views if seq[0] == _view_name
            ][0]
            # print("Setting Active View to: '{}'".format(_view_name))
        else:
            msg = '"{0}" is not a valid view name?'.format(_view_name)
            _IGH.error(msg)


def get_active_layer_name(_IGH):
    # type (gh_io.IGH) -> str
    """Return the name of the current active layer"""
    with _IGH.context_rh_doc():
        return _IGH.scriptcontext.doc.Layers.CurrentLayer.FullPath


def set_active_layer_by_name(_IGH, _layer_name):
    # type: (gh_io.IGH, str) -> None
    """Change the active layer by name"""
    with _IGH.context_rh_doc():
        if _layer_name not in _IGH.rhinoscriptsyntax.LayerNames():
            raise Exception(
                "Error: Cannot find the Layer with name: '{}'?".format(_layer_name)
            )
        _IGH.rhinoscriptsyntax.CurrentLayer(_layer_name)


def get_detail_views_for_active_view(_IGH):
    # type: (gh_io.IGH) -> List[rdo.DetailViewObject]
    """Return a List of the DetailViewObjects for the Active View."""

    with _IGH.context_rh_doc():
        active_view = _IGH.scriptcontext.doc.Views.ActiveView
        try:
            return active_view.GetDetailViews()
        except:
            # If its not a Layout View....
            return []


def get_layout_view_transform(_IGH, _dtl_view_objs, _layout_name):
    # type: (gh_io.IGH, List[rdo.DetailViewObject], str) -> rg.Transform
    """Return the Transform for the Layout View. Raises an error if there are multiple Detail-Views on the Layout-Page."""

    all_dtl_view_transforms = {vw.WorldToPageTransform for vw in _dtl_view_objs}
    if len(all_dtl_view_transforms) != 1:
        msg = (
            "Warning: There are {} Detail-Views found on Layout-Page: '{}'."
            "Model-Annotations may not align properly when multiple Detail-Views "
            "are present on a single Layout-Page. Try splitting up the Detail-Views "
            "onto multiple Layout-Pages, or make sure that the orientation of each "
            "Detail-View on the Layout-Page is the same.".format(
                len(_dtl_view_objs), _layout_name
            )
        )
        _IGH.warning(msg)
    return all_dtl_view_transforms.pop()


def find_layers_with_detail_views(_IGH):
    # type: (gh_io.IGH) -> List[str]
    """Goes to the Active View and looks to see if there are any 'DetailViews' present,
    If so, find the Layer the DetailViews are on and add the layerIndex to the list.
    This is used to ensure that the DetailViews will remain 'on' when exporting the PDF.

    Arguments:
    ----------
        * (gh_io.IGH):

    Returns:
    --------
        * (List[str]):
    """

    layer_names_ = []  # type: List[str]
    layer_IDs_ = []  # type: List[int]

    with _IGH.context_rh_doc():
        active_view = _IGH.scriptcontext.doc.Views.ActiveView
        detail_views = active_view.GetDetailViews()
        for detail_view in detail_views:
            layer_IDs_.append(detail_view.Attributes.LayerIndex)

        # Find the right Layer Names from the Index vals
        layer_IDs_ = list(set(layer_IDs_))  # Keep only one of each unique index val

        for i in range(len(layer_IDs_)):
            # Get the Layer and any parents
            layer_path = _IGH.scriptcontext.doc.Layers[layer_IDs_[i]].FullPath
            layer_names = list(layer_path.Split(":"))  # type: List[str]

            for layerName in layer_names:
                layer_names_.append(layer_path)
                layer_names_.append(layerName)

    return list(set(layer_names_))


def get_current_layer_visibilities(_IGH):
    # type: (gh_io.IGH) -> List[bool]
    """Return a list of current Layer visibilities"""
    with _IGH.context_rh_doc():
        return [
            _IGH.rhinoscriptsyntax.LayerVisible(layer)
            for layer in _IGH.rhinoscriptsyntax.LayerNames()
        ]


def turn_off_all_layers(_IGH, _except_layers):
    # type: (gh_io.IGH, List[str]) -> None
    """Turn all Layer Visibilities 'Off' except for the specified layers. Returns a list
        of the starting layer states before changing as a bool (True=On, False=Off).

    Arguments:
    ----------
        * _IGH (gh_io.IGH):
        * _except_layers (List[str]): A list of the Layers to leave 'on'

    Returns:
    --------
        * (None)
    """

    with _IGH.context_rh_doc():
        # Set layers 'off' if they aren't on the list to stay on
        for layer_name in _IGH.rhinoscriptsyntax.LayerNames():
            # if list(layer.Split(":"))[-1] not in allLayersOn:
            if layer_name in _except_layers:
                _IGH.rhinoscriptsyntax.LayerVisible(layer_name, True)
            else:
                _IGH.rhinoscriptsyntax.LayerVisible(layer_name, False)

        _IGH.Rhino.RhinoDoc.ActiveDoc.Views.RedrawEnabled = True
        _IGH.Rhino.RhinoDoc.ActiveDoc.Views.Redraw()


def reset_all_layer_visibility(_IGH, _layer_vis_settings):
    # type: (gh_io.IGH, List[bool]) -> None
    """Reset all the Layer Vis settings to the original State

    Arguments:
    ----------
        *
        *

    Returns:
    --------
        * (None)
    """

    with _IGH.context_rh_doc():
        layers = _IGH.rhinoscriptsyntax.LayerNames()

        for (
            layer,
            vis_setting,
        ) in izip_longest(layers, _layer_vis_settings):
            _IGH.rhinoscriptsyntax.LayerVisible(layer, vis_setting)

        _IGH.Rhino.RhinoDoc.ActiveDoc.Views.RedrawEnabled = True
        _IGH.Rhino.RhinoDoc.ActiveDoc.Views.Redraw()


def create_bake_layer(_IGH):
    # type: (gh_io.IGH) -> str
    """Creates a new layer which is used for bake objects. Returns the name of the new layer.

    Arguments:
    ----------
        *

    Returns:
    --------
        *
    """

    with _IGH.context_rh_doc():
        # Create an Unused Layer Name
        new_layer_name = _IGH.scriptcontext.doc.Layers.GetUnusedLayerName(False)

        # Add a new Layer to the Document
        _IGH.scriptcontext.doc.Layers.Add(new_layer_name, Color.Black)

    return new_layer_name


def remove_bake_layer(_IGH, _layer_name):
    # type: (gh_io.IGH, str) -> None
    """Remove a layer with the specified name. Will also delete all objects on the layer.

    Arguments:
    ----------
        *

    Returns:
    --------
        *
    """

    with _IGH.context_rh_doc():
        print("Removing Bake-Layer: {}".format(_layer_name))

        # Be sure the temp layer exists
        if _layer_name not in _IGH.rhinoscriptsyntax.LayerNames():
            return

        # Remove all the objects on the specified layer
        _IGH.rhinoscriptsyntax.DeleteObjects(
            _IGH.rhinoscriptsyntax.ObjectsByLayer(_layer_name)
        )

        # Remove the layer
        _IGH.scriptcontext.doc.Layers.Delete(
            _IGH.scriptcontext.doc.Layers.FindName(_layer_name)
        )


def mesh2Hatch(_IGH, mesh, _hatch_pattern_index=0):
    # type: (gh_io.IGH, rg.Mesh, int) -> Tuple[List[rg.Hatch], List[Color]]
    """Copied / Adapted from Ladybug Definition

    Arguments:
    ----------
        *

    Returns:
    --------
        *
    """

    # Make some lists to hold key parameters
    hatches = []  # type: List[rg.Hatch]
    colors = []  # type: List[Color]
    meshColors = mesh.VertexColors

    for faceCount, face in enumerate(mesh.Faces):
        faceColorList = []
        facePointList = []

        # Extract the points and colors.
        if face.IsQuad:
            faceColorList.append(meshColors[face.A])
            faceColorList.append(meshColors[face.B])
            faceColorList.append(meshColors[face.C])
            faceColorList.append(meshColors[face.D])

            facePointList.append(mesh.PointAt(faceCount, 1, 0, 0, 0))
            facePointList.append(mesh.PointAt(faceCount, 0, 1, 0, 0))
            facePointList.append(mesh.PointAt(faceCount, 0, 0, 1, 0))
            facePointList.append(mesh.PointAt(faceCount, 0, 0, 0, 1))
        else:
            faceColorList.append(meshColors[face.A])
            faceColorList.append(meshColors[face.B])
            faceColorList.append(meshColors[face.C])

            facePointList.append(mesh.PointAt(faceCount, 1, 0, 0, 0))
            facePointList.append(mesh.PointAt(faceCount, 0, 1, 0, 0))
            facePointList.append(mesh.PointAt(faceCount, 0, 0, 1, 0))

        # Calculate the average color of the face.
        if face.IsQuad:
            hatchColorR = (
                faceColorList[0].R
                + faceColorList[1].R
                + faceColorList[2].R
                + faceColorList[3].R
            ) / 4
            hatchColorG = (
                faceColorList[0].G
                + faceColorList[1].G
                + faceColorList[2].G
                + faceColorList[3].G
            ) / 4
            hatchColorB = (
                faceColorList[0].B
                + faceColorList[1].B
                + faceColorList[2].B
                + faceColorList[3].B
            ) / 4
        else:
            hatchColorR = (
                faceColorList[0].R + faceColorList[1].R + faceColorList[2].R
            ) / 3
            hatchColorG = (
                faceColorList[0].G + faceColorList[1].G + faceColorList[2].G
            ) / 3
            hatchColorB = (
                faceColorList[0].B + faceColorList[1].B + faceColorList[2].B
            ) / 3
        hatchColor = Color.FromArgb(255, hatchColorR, hatchColorG, hatchColorB)

        # Create the outline of a new hatch.
        hatchCurveInit = rg.PolylineCurve(facePointList)
        if face.IsQuad:
            hatchExtra = rg.LineCurve(facePointList[0], facePointList[3])
        else:
            hatchExtra = rg.LineCurve(facePointList[0], facePointList[2])
        hatchCurve = rg.Curve.JoinCurves([hatchCurveInit, hatchExtra], _IGH.tolerance)[0]

        # Create the Hatch
        if hatchCurve.IsPlanar():
            meshFaceHatch = hatch_from_curve(
                hatchCurve, _IGH.tolerance, _hatch_pattern_index
            )
            hatches.append(meshFaceHatch)
            colors.append(hatchColor)
        else:
            # We have to split the quad face into two triangles.
            hatchCurveInit1 = rg.PolylineCurve(
                [facePointList[0], facePointList[1], facePointList[2]]
            )
            hatchExtra1 = rg.LineCurve(facePointList[0], facePointList[2])
            hatchCurve1 = rg.Curve.JoinCurves(
                [hatchCurveInit1, hatchExtra1],
                _IGH.tolerance,
            )[0]
            meshFaceHatch1 = hatch_from_curve(
                hatchCurve1, _IGH.tolerance, _hatch_pattern_index
            )
            hatchCurveInit2 = rg.PolylineCurve(
                [facePointList[2], facePointList[3], facePointList[0]]
            )
            hatchExtra2 = rg.LineCurve(facePointList[2], facePointList[0])
            hatchCurve2 = rg.Curve.JoinCurves(
                [hatchCurveInit2, hatchExtra2],
                _IGH.tolerance,
            )[0]
            meshFaceHatch2 = hatch_from_curve(
                hatchCurve2, _IGH.tolerance, _hatch_pattern_index
            )

            hatches.extend([meshFaceHatch1, meshFaceHatch2])
            colors.extend([hatchColor, hatchColor])

    return hatches, colors


def create_geometry_attributes(parent_layer_index, _color, _display_order=0):
    # type: (int, Color, int) -> rdo.ObjectAttributes
    """Create a new ObjectAttributes object with the specified color and layer index."""
    attr = rdo.ObjectAttributes()
    attr.LayerIndex = parent_layer_index
    attr.ObjectColor = _color
    attr.PlotColor = _color
    attr.ColorSource = rdo.ObjectColorSource.ColorFromObject  # type: ignore
    attr.PlotColorSource = rdo.ObjectPlotColorSource.PlotColorFromObject  # type: ignore
    attr.DisplayOrder = _display_order
    return attr


def bake_mesh(_IGH, _layer_name, _geometry, _draw_order=0):
    # type: (gh_io.IGH, str, rg.Mesh, int) -> None
    """Bake a Mesh object into the Rhino Scene."""
    # --
    layer_table = _IGH.Rhino.RhinoDoc.ActiveDoc.Layers
    hatch_id = get_default_solid_hatch_index(_IGH)
    parent_layer_index = rdo.Tables.LayerTable.FindByFullPath(  # type: ignore
        layer_table, _layer_name, True
    )

    # -- Create the hatches, and Bake them into the Rhino Doc
    guids = []
    for hatch, color in zip(*mesh2Hatch(_IGH, _geometry, hatch_id)):
        attr = create_geometry_attributes(parent_layer_index, color, _draw_order)
        guids.append(_IGH.Rhino.RhinoDoc.ActiveDoc.Objects.AddHatch(hatch, attr))

    # -- Group the hatches so they are manageable
    group_ = _IGH.Rhino.RhinoDoc.ActiveDoc.Groups
    rdo.Tables.GroupTable.Add(group_, guids)  # type: ignore
    _IGH.scriptcontext.doc.Views.Redraw()

    return None


def bake_geometry_object(_IGH, _geom_obj, _attr_obj, _layer_name):
    # type: (gh_io.IGH, Guid, rdo.ObjectAttributes | None, str) -> None
    """Takes in a geom obj Guid and attributes, then bakes to a Layer

    If the Object is a Mesh, will bake that using the Mesh's Vertex Colors. To
    set these, use the Grasshopper MeshColor component (ghc.MeshColours() ) before
    inputting here.

    If its a Curve input, will try and look for Attribute information in the
    _geomAttributes input.

    If its some other type of geometry, will just use a default attribute for printing.

    Arguments:
    ----------
        * _IGH (gh_io.IGH):
        * _geom_obj (Guid):
        * _attr_obj (ObjectAttributes):
        * _layer_name (str):

    Returns:
    --------
        * (None)
    """
    doc_object = _IGH.rhinoscriptsyntax.coercerhinoobject(_geom_obj, True, True)
    geometry = doc_object.Geometry

    with _IGH.context_rh_doc():
        if _IGH.rhinoscriptsyntax.IsMesh(geometry):
            if _attr_obj and _attr_obj.DisplayOrder:
                draw_order = _attr_obj.DisplayOrder
            else:
                draw_order = -1  # +1 = Front, -1 = Back
            bake_mesh(_IGH, _layer_name, geometry, draw_order)

        elif isinstance(geometry, rg.Curve):
            rhino_geom = _IGH.scriptcontext.doc.Objects.Add(
                geometry, _attr_obj or doc_object.Attributes
            )

            # Set the new Object's Layer
            if not _IGH.rhinoscriptsyntax.IsLayer(_layer_name):
                _IGH.rhinoscriptsyntax.AddLayer(_layer_name)
            _IGH.rhinoscriptsyntax.ObjectLayer(rhino_geom, _layer_name)

        else:
            # Just bake the regular Geometry with default attributes
            rhino_geom = _IGH.scriptcontext.doc.Objects.Add(
                geometry, doc_object.Attributes
            )

            # Set the new Object's Layer
            if not _IGH.rhinoscriptsyntax.IsLayer(_layer_name):
                _IGH.rhinoscriptsyntax.AddLayer(_layer_name)
            _IGH.rhinoscriptsyntax.ObjectLayer(rhino_geom, _layer_name)


def bake_annotation_object(
    _IGH, _annotation, _target_layer, _avoid_collisions=False, _neighbors=None
):
    # type: (gh_io.IGH, TextAnnotation, str, bool, Optional[List[rg.Rectangle3d]]) -> Optional[rg.Rectangle3d]
    """Add a new Text element to the Rhino document.

    Arguments:
    ----------
        * _IGH (gh_io.IGH):
        * _annotation (TextAnnotation):
        * _target_layer (str):
        * _avoid_collisions (bool):
        * _neighbors (Optional[List[Rectangle3d]])

    Returns:
    --------
        * (Optional[Rhino.Geometry.Rectangle3d])
    """

    # https://developer.rhino3d.com/api/RhinoCommon/html/T_Rhino_Geometry_TextEntity.htm
    # https://discourse.mcneel.com/t/adding-text-to-instancedefinition-block/99346

    bounding_rect = None
    _neighbors = _neighbors or []
    with _IGH.context_rh_doc():
        # Create the txt object
        txt = rg.TextEntity()
        try:
            txt.Font = rdo.Font("Source Code Pro")  # type: ignore
        except:
            pass
        txt.Text = _annotation.text
        txt.Plane = _IGH.ghc.Move(
            _annotation.plane, _IGH.ghc.Amplitude(_annotation.plane.Normal, 0.1)
        ).geometry
        txt.TextHeight = _annotation.text_size
        txt.Justification = _annotation.justification
        txt.DrawForward = False
        if _annotation.mask:
            txt.MaskEnabled = _annotation.mask.show_mask
            txt.MaskColor = _annotation.mask.mask_color
            txt.MaskOffset = _annotation.mask.mask_offset
            txt.MaskFrame = _annotation.mask.frame_type
            txt.DrawTextFrame = _annotation.mask.show_frame

        if _avoid_collisions:
            raise NotImplementedError("Not yet....")
            #  Test against the other text items on the sheet
            # First, find / create the bounding box rectangle of the text note
            this_bounding_box = txt.GetBoundingBox(txt.Plane)
            box_x_dim = abs(this_bounding_box.Min.X - this_bounding_box.Max.X)
            box_y_dim = abs(this_bounding_box.Min.Y - this_bounding_box.Max.Y)
            domain_x = _IGH.ghpythonlib_components.ConstructDomain(
                (box_x_dim / 2) * -1, box_x_dim / 2
            )
            domain_y = _IGH.ghpythonlib_components.ConstructDomain(
                (box_y_dim / 2) * -1, box_y_dim / 2
            )
            bounding_rect = _IGH.ghpythonlib_components.Rectangle(
                txt.Plane, domain_x, domain_y, 0
            ).rectangle

            # Compare the current text note to the others already in the scene
            # Move the current tag if necessary
            for eachNeighbor in _neighbors:
                intersection = _IGH.ghpythonlib_components.CurveXCurve(
                    eachNeighbor, bounding_rect
                )
                if intersection.points != None:
                    neighbor = _IGH.ghpythonlib_components.DeconstuctRectangle(
                        eachNeighbor
                    )  # The overlapping textbox
                    neighborY = neighbor.Y  # Returns a domain
                    # neighborY = abs(neighborY[0] - neighborY[1]) # Total Y distance

                    neighborCP = neighbor.base_plane.Origin
                    thisCP = _IGH.ghpythonlib_components.DeconstuctRectangle(
                        bounding_rect
                    ).base_plane.Origin

                    if thisCP.Y > neighborCP.Y:
                        # Move the tag 'up'
                        neighborMaxY = neighborCP.Y + neighborY[1]
                        thisMinY = thisCP.Y - (box_y_dim / 2)
                        moveVector = rg.Vector3d(0, neighborMaxY - thisMinY, 0)
                        bounding_rect = _IGH.ghpythonlib_components.Move(
                            bounding_rect, moveVector
                        ).geometry
                    else:
                        # Move the tag 'down'
                        neighborMinY = neighborCP.Y - neighborY[1]
                        thisMaxY = thisCP.Y + (box_y_dim / 2)
                        moveVector = rg.Vector3d(0, neighborMinY - thisMaxY, 0)
                        bounding_rect = _IGH.ghpythonlib_components.Move(
                            bounding_rect, moveVector
                        ).geometry

                    # Re-Set the text tag's origin to the new location
                    txt.Plane = _IGH.ghpythonlib_components.DeconstuctRectangle(
                        bounding_rect
                    ).base_plane

        # Add the new text object to the Scene
        txtObj = _IGH.Rhino.RhinoDoc.ActiveDoc.Objects.AddText(txt)

        # Set the new Text's Layer
        if not _IGH.rhinoscriptsyntax.IsLayer(_target_layer):
            _IGH.rhinoscriptsyntax.AddLayer(_target_layer)
        _IGH.rhinoscriptsyntax.ObjectLayer(txtObj, _target_layer)

    return bounding_rect


def export_single_pdf(_IGH, _file_path, _dpi=300, _raster=True):
    # type: (gh_io.IGH,  str, float, bool) -> None
    """Export a single-page PDF document of the Active Layout View.

    Arguments:
    ----------
        * _IGH (gh_io.IGH): Grasshopper Interface
        * _file_path (str): The full path for the PDF file to create
        * _dpi (float): default=300
        * _raster (bool): Use raster output mode. default=False.

    Returns:
    --------
        * (None)
    """
    # Layout Page Size in Layout's Units
    page_height = _IGH.scriptcontext.doc.Views.ActiveView.PageHeight
    page_width = _IGH.scriptcontext.doc.Views.ActiveView.PageWidth

    # Layout Page Size in Inches
    # Ref: https://developer.rhino3d.com/api/RhinoScriptSyntax/#document-UnitScale
    # Ref: https://developer.rhino3d.com/api/RhinoCommon/html/P_Rhino_RhinoDoc_PageUnitSystem.htm
    page_unit_system_number = _IGH.rhinoscriptsyntax.UnitSystem(in_model_units=False)
    page_unit_scale = _IGH.rhinoscriptsyntax.UnitScale(
        8, page_unit_system_number
    )  # Type 8 = Inches

    page_height = page_height * page_unit_scale
    page_width = page_width * page_unit_scale
    page_height = round(page_height, 2)
    page_width = round(page_width, 2)

    pdf = FileIO.FilePdf.Create()  # type: ignore
    size = Size(page_width * _dpi, page_height * _dpi)
    settings = rdp.ViewCaptureSettings(
        _IGH.scriptcontext.doc.Views.ActiveView, size, _dpi
    )
    settings.RasterMode = _raster
    settings.OutputColor = rdp.ViewCaptureSettings.ColorMode.DisplayColor  # type: ignore
    pdf.AddPage(settings)

    try:
        os.remove(_file_path)
    except OSError as e:
        if not os.path.exists(_file_path):
            pass
        else:
            raise OSError("{}/nFile {} can not be removed?".format(e, _file_path))

    pdf.Write(_file_path)


def add_clipping_plane(_IGH, _cp_location, _cp_layer, _dtl_view_objs):
    # type: (gh_io.IGH, ClippingPlaneLocation, str, List[rdo.DetailViewObject]) -> None
    """Add a new ClippingPlane object into the Rhino Scene.

    Ref: https://developer.rhino3d.com/samples/rhinocommon/add-clipping-plane/

    Arguments:
    ----------
        * _IGH (gh_io.IGH):
        * _cp_location (ClippingPlaneLocation): The ClippingPlaneLocation object with an origin and normal.
        * _cp_layer(str): The name of the Clipping Plane layer to bake to.
        * _dtl_view_objs (List[DetailViewObject]): A list of DetailViewObjects to apply the ClippingPlane to.

    Returns:
    --------
        * (System.Guid)
    """

    pl = rg.Plane(_cp_location.origin, _cp_location.normal)

    with _IGH.context_rh_doc():
        cp_id = _IGH.scriptcontext.doc.Objects.AddClippingPlane(
            plane=pl,
            uMagnitude=1,
            vMagnitude=1,
            clippedViewportIds=[dv.Id for dv in _dtl_view_objs],
        )

        # Set the new ClippingPlane's Layer
        if not _IGH.rhinoscriptsyntax.IsLayer(_cp_layer):
            _IGH.rhinoscriptsyntax.AddLayer(_cp_layer)
        _IGH.rhinoscriptsyntax.ObjectLayer(cp_id, _cp_layer)

        if cp_id != Guid.Empty:
            _IGH.scriptcontext.doc.Views.Redraw()

    return cp_id


def align_to_detail_view(_model_annotations):
    # type: (Iterable[TextAnnotation]) -> bool
    """Check if all the model-annotations have the same 'Align to Layout View' attribute value."""

    all_values = {a.align_to_layout_view for a in _model_annotations}

    if all_values == {True}:  # All True
        return True
    elif all_values == {False}:  # All False
        return False
    else:
        msg = "Error: Model-Annotation 'Align to Layout View' attribute values are not all the same?"
        raise Exception(msg)


def export_pdfs(
    _IGH,
    _file_paths,
    _layout_names,
    _layers_on,
    _cp_loc,
    _geom,
    _geom_attrs,
    _model_annotations,
    _layout_annotations,
    _remove_baked_items,
    _raster,
):
    # type: (gh_io.IGH, List[str], List[str], List[str], DataTree[ClippingPlaneLocation],DataTree[Guid], DataTree[rdo.ObjectAttributes], DataTree[TextAnnotation], DataTree[TextAnnotation],bool,bool) -> None
    """

    Arguments:
    ----------
        * _IGH (gh_io.IGH): Grasshopper Interface.
        * _file_paths (List[str]): A list of the full file-paths to save out to.
        * _layout_name (str): The name of the Layout (View) to export as PDF
        * _layers_on (List[str]): A list of the layer-names to leave 'on' during export.
        * _cp_loc (DataTree[ClippingPlaneLocation]):
        * _geom (DataTree[Guid]):
        * _geom_attrs (DataTree[ObjectAttributes]):
        * _model_annotations (DataTree[LayoutPageLabel]):
        * _layout_annotations (DataTree[LayoutPageLabel]):
        * _raster (bool): Use raster output mode. default=False.

    Returns:
    --------
        * None
    """
    # -- Sort out the layers and views and transforms
    starting_active_view_name = get_active_view_name(_IGH)
    starting_active_layer_name = get_active_layer_name(_IGH)
    starting_layer_visibilities = get_current_layer_visibilities(_IGH)

    # -- Bake objects
    for branch_num, geom_list in enumerate(_geom.Branches):
        # --------------------------------------------------------------------------------------------------------------
        # -- Setup the right layers for the Layout View being printed
        layout_view_name = _layout_names[branch_num]
        set_active_view_by_name(_IGH, layout_view_name)
        layers_with_detail_views = find_layers_with_detail_views(_IGH)
        layers_on = _layers_on + layers_with_detail_views
        turn_off_all_layers(_IGH, _except_layers=layers_on)

        # --------------------------------------------------------------------------------------------------------------
        # -- Find the Layout's Detail-View objects and View-Transform
        dtl_view_objs = get_detail_views_for_active_view(_IGH)
        dtl_view_transform = get_layout_view_transform(
            _IGH, dtl_view_objs, layout_view_name
        )

        # --------------------------------------------------------------------------------------------------------------
        # -- Create new temporary output layers
        geom_bake_layer = create_bake_layer(_IGH)  # Geometry
        label_bake_layer = create_bake_layer(_IGH)  # Text Labels
        cp_layer = create_bake_layer(_IGH)  # Clipping Planes

        try:
            # ----------------------------------------------------------------------------------------------------------
            # -- Bake the Geometry into the Scene
            set_active_view_by_name(_IGH, "Top")  # Change to 'Top' View for Baking
            for i, geom_obj in enumerate(geom_list):
                # -- Object Attribute
                attr_obj = _geom_attrs.Branch(branch_num)[i]

                # -- Bake Geometry to the specified layer
                bake_geometry_object(_IGH, geom_obj, attr_obj, geom_bake_layer)

            # ----------------------------------------------------------------------------------------------------------
            # -- Add any ClippingPlanes into the scene
            try:
                for cp in clean_tree_get(_cp_loc, branch_num, []):
                    add_clipping_plane(_IGH, cp, cp_layer, dtl_view_objs)
            except ValueError as e:
                msg = "Error Adding Clipping Plane: {}".format(e)
                print(msg)
                raise Exception(msg)

            # ----------------------------------------------------------------------------------------------------------
            # -- Bake Model-Space Annotations (text in the RH model space)
            if _model_annotations.BranchCount != 0:
                # -- Set the right view for baking
                align_annotations = align_to_detail_view(
                    _model_annotations.Branch(branch_num)
                )
                if align_annotations == True:
                    set_active_view_by_name(_IGH, layout_view_name)
                else:
                    set_active_view_by_name(_IGH, "Perspective")

                # -- Bake the Annotations to the Rhino Scene
                text_bounding_boxes = []  # the annotations's bounding boxes
                for model_annotation in _model_annotations.Branch(branch_num):
                    # -- If the annotation needs to be rotated to match the view, execute the transform
                    if align_annotations == True:
                        # -- Transform (Rotate) the Annotation's Location to match the Detail-View
                        model_annotation = model_annotation.transform(dtl_view_transform)

                    # -- Bake the text to the Rhino view
                    text_bounding_box = bake_annotation_object(
                        _IGH=_IGH,
                        _annotation=model_annotation,
                        _target_layer=label_bake_layer,
                        _avoid_collisions=False,
                        _neighbors=text_bounding_boxes,
                    )

                    # -- Keep track of bounding boxes for collision detection later
                    text_bounding_boxes.append(text_bounding_box)

            # ----------------------------------------------------------------------------------------------------------
            # -- Bake Paper-Space Title-block Labels to the specified layer
            set_active_view_by_name(_IGH, layout_view_name)
            try:
                for layout_annotation in _layout_annotations.Branch(branch_num):
                    bake_annotation_object(_IGH, layout_annotation, label_bake_layer)
            except ValueError as e:
                # No Layout Annotations for this Branch-number
                pass

            # ----------------------------------------------------------------------------------------------------------
            # # -- Export PDF file
            set_active_view_by_name(_IGH, layout_view_name)
            export_single_pdf(_IGH, _file_paths[branch_num], _raster=_raster)
        finally:
            # ----------------------------------------------------------------------------------------------------------
            # -- Cleanup baked items
            if _remove_baked_items != False:
                print("Removing Bake-Layers")
                remove_bake_layer(_IGH, geom_bake_layer)
                remove_bake_layer(_IGH, label_bake_layer)
                remove_bake_layer(_IGH, cp_layer)

    # -- Cleanup layer vis and active view
    reset_all_layer_visibility(_IGH, starting_layer_visibilities)
    set_active_view_by_name(_IGH, starting_active_view_name)
    set_active_layer_by_name(_IGH, starting_active_layer_name)
