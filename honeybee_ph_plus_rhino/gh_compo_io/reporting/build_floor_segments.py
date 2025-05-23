# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Functions for getting / sorting all the Honeybee-Model TFA Floor Surfaces. """

from collections import OrderedDict, defaultdict

try:
    from typing import Any, Callable, Dict, List, Optional, Tuple
except ImportError:
    pass  # Python 2.7

try:
    from System.Drawing import Color  # type: ignore
except ImportError:
    pass  # Outside .NET

try:
    from Rhino import DocObjects as rdo  # type: ignore
    from Rhino import Geometry as rg  # type: ignore
    from Rhino.DocObjects import ObjectAttributes  # type: ignore
    from Rhino.Geometry import Brep, Line, Point3d  # type: ignore
except ImportError:
    pass  # Outside Rhino

try:
    from honeybee import facetype, model, room
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from ladybug_rhino.fromgeometry import from_face3d, from_point3d
except ImportError as e:
    raise ImportError("\nFailed to import honeybee:\n\t{}".format(e))

try:
    from honeybee_ph import space
    from honeybee_ph.properties.room import RoomPhProperties
    from honeybee_ph.properties.space import SpacePhProperties
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph:\n\t{}".format(e))

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")

try:
    from honeybee_ph_utils.input_tools import input_to_int
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_utils:\n\t{}".format(e))

try:
    from ph_units.converter import convert
except ImportError as e:
    raise ImportError("\nFailed to import ph_units:\n\t{}".format(e))

try:
    from honeybee_ph_plus_rhino.gh_compo_io.reporting.annotations import (
        TextAnnotation,
        TextAnnotationMaskAttributes,
    )
    from honeybee_ph_plus_rhino.gh_compo_io.reporting.create_clipping_plane_set import (
        ClippingPlaneLocation,
    )
except ImportError as e:
    raise ImportError("\nFailed to import honeybee_ph_rhino:\n\t{}".format(e))


# -----------------------------------------------------------------------------
# -- Styles
def color_by_TFA(_flr_seg, _space):
    # type: (space.SpaceFloorSegment, space.Space) -> Color
    """Return a System.Drawing.Color based on the TFA Weighting factor of the SpaceFloorSegment."""

    if _flr_seg.weighting_factor > 0.6:
        return Color.FromArgb(255, 252, 252, 139)  # Yellow
    elif 0.5 < _flr_seg.weighting_factor <= 0.6:
        return Color.FromArgb(255, 227, 201, 168)  # Brown
    elif 0.3 < _flr_seg.weighting_factor <= 0.5:
        return Color.FromArgb(255, 213, 247, 143)  # Green
    elif 0.0 < _flr_seg.weighting_factor <= 0.3:
        return Color.FromArgb(255, 173, 247, 223)  # Blue
    else:
        return Color.FromArgb(255, 252, 182, 252)  # Purple


def color_by_Vent(_flr_seg, _space):
    # type: (space.SpaceFloorSegment, space.Space) -> Color
    """Return a System.Drawing.Color based on the Ventilation Air Flow Rate of the Space"""
    space_prop_ph = getattr(_space.properties, "ph")  # type: SpacePhProperties
    if (space_prop_ph._v_sup or 0 > 0) and (space_prop_ph._v_eta or 0 > 0):
        return Color.FromArgb(255, 234, 192, 240)  # Balanced
    elif space_prop_ph._v_sup or 0 > 0:
        return Color.FromArgb(255, 183, 227, 238)  # Supply Only
    elif space_prop_ph._v_eta or 0 > 0:
        return Color.FromArgb(255, 246, 170, 154)  # Extract Only
    else:
        return Color.FromArgb(255, 235, 235, 235)  # No Vent Flow


def text_by_TFA(_space, _IGH, _units="SI"):
    # type: (space.Space, gh_io.IGH, str) -> str
    """Return the space data in a formatted block."""

    rhdoc_len_units = _IGH.get_rhino_unit_system_name()
    rhdoc_area_units = _IGH.get_rhino_areas_unit_name()
    rhdoc_vol_units = _IGH.get_rhino_volume_unit_name()

    if str(_units).upper().strip() == "IP":
        txt = [
            "ZONE: {}".format(_space.host.display_name),
            "NAME: {}".format(_space.full_name),
            "GROSS AREA: {:.01f} ft2".format(
                convert(_space.floor_area, rhdoc_area_units, "FT2")
            ),
            "WEIGHTED AREA: {:.01f} ft2".format(
                convert(_space.weighted_floor_area, rhdoc_area_units, "FT2")
            ),
            "Vn50: {:.01f} ft3".format(
                convert(_space.net_volume, rhdoc_vol_units, "FT3")
            ),
            "CLG HEIGHT: {:.01f} ft".format(
                convert(_space.avg_clear_height, rhdoc_len_units, "FT")
            ),
        ]
    else:
        txt = [
            "ZONE: {}".format(_space.host.display_name),
            "NAME: {}".format(_space.full_name),
            "GROSS AREA: {:.01f} m2".format(
                convert(_space.floor_area, rhdoc_area_units, "M2")
            ),
            "WEIGHTED AREA: {:.01f} m2".format(
                convert(_space.weighted_floor_area, rhdoc_area_units, "M2")
            ),
            "Vn50: {:.01f} m3".format(convert(_space.net_volume, rhdoc_vol_units, "M3")),
            "CLG HEIGHT: {:.01f} m".format(
                convert(_space.avg_clear_height, rhdoc_len_units, "M")
            ),
        ]

    return "\n".join(txt)


def text_by_Vent(_space, _IGH, _units="SI"):
    # type: (space.Space, gh_io.IGH, str) -> str
    """Return the space data in a formatted block."""
    space_prop_ph = getattr(_space.properties, "ph")  # type: SpacePhProperties

    def format_vent_rate(_rate, _target_unit="M3/HR"):
        # type (float | str | None) -> str
        # -- get the data cleanly, in case None
        try:
            return "{:.0f}".format(convert(_rate * 3600, "M3/HR", _target_unit))
        except:
            return "-"

    rhdoc_len_units = _IGH.get_rhino_unit_system_name()
    rhdoc_area_units = _IGH.get_rhino_areas_unit_name()
    rhdoc_vol_units = _IGH.get_rhino_volume_unit_name()

    if str(_units).upper().strip() == "IP":
        txt = [
            "ZONE: {}".format(_space.host.display_name),
            "NAME: {}".format(_space.full_name),
            "GROSS AREA: {:.01f} ft2".format(
                convert(_space.floor_area, rhdoc_area_units, "FT2")
            ),
            "NET AREA: {:.01f} ft2".format(
                convert(_space.net_floor_area, rhdoc_area_units, "FT2")
            ),
            "SUP: {} cfm".format(format_vent_rate(space_prop_ph._v_sup or 0.0, "CFM")),
            "ETA: {} cfm".format(format_vent_rate(space_prop_ph._v_eta or 0.0, "CFM")),
            "TRAN: {} cfm".format(format_vent_rate(space_prop_ph._v_tran or 0.0, "CFM")),
        ]
    else:
        txt = [
            "ZONE: {}".format(_space.host.display_name),
            "NAME: {}".format(_space.full_name),
            "GROSS AREA: {:.01f} m2".format(
                convert(_space.floor_area, rhdoc_area_units, "M2")
            ),
            "NET AREA: {:.01f} m2".format(
                convert(_space.net_floor_area, rhdoc_area_units, "M2")
            ),
            "SUP: {} m3/hr".format(
                format_vent_rate(space_prop_ph._v_sup or 0.0, "M3/HR")
            ),
            "ETA: {} m3/hr".format(
                format_vent_rate(space_prop_ph._v_eta or 0.0, "M3/HR")
            ),
            "TRAN: {} m3/hr".format(
                format_vent_rate(space_prop_ph._v_tran or 0.0, "M3/HR")
            ),
        ]

    return "\n".join(txt)


# -----------------------------------------------------------------------------


def _get_hbph_spaces(_hb_room_group):
    # type: (List[room.Room]) -> List[space.Space]
    """Return a sorted list of all the HBPH-Spaces in a list of HB-Rooms."""

    spaces = {}
    for room in _hb_room_group:
        room_prop_ph = getattr(room.properties, "ph")  # type: RoomPhProperties
        for space in room_prop_ph.spaces:
            spaces[space.display_name] = space

    return sorted(list(spaces.values()), key=lambda sp: sp.display_name)


def _sort_rooms_by_z_location(_hb_model):
    # type: (model.Model) -> Dict[str, List[room.Room]]
    """Return a Dict with the HB-Rooms grouped by their floor's Z-height."""

    rooms_by_z_height = defaultdict(list)
    for hb_room in _hb_model.rooms:
        flr_srfcs = [f for f in hb_room.faces if (isinstance(f.type, facetype.Floor))]
        floor_srfcs_min_z = round(min(hb_face.min.z for hb_face in flr_srfcs), 3)
        rooms_by_z_height[str(floor_srfcs_min_z)].append(hb_room)

    # -- Sort the room groups by their Key (which is their Z-dist)
    sorted_rooms_grouped_by_story = OrderedDict()
    for k in sorted(rooms_by_z_height.keys(), key=lambda k: float(k)):
        sorted_rooms_grouped_by_story[k] = rooms_by_z_height[k]

    return sorted_rooms_grouped_by_story


def _group_hb_rooms_by_story(_hb_model):
    # type: (model.Model) -> Dict[str, List[room.Room]]
    """Return a Dict with the HB-Rooms grouped by their 'Story'.

    If the HB-Story data is not applied, will attempt to sort the HB-Rooms based
    on their Z-height instead.
    """

    # -- If the model is missing 'Story' data, sort by floor Z-location
    if not all(hb_room.story for hb_room in _hb_model.rooms):
        return _sort_rooms_by_z_location(_hb_model)

    # -- If model has Story data, just use that instead.
    rooms_grouped_by_story = defaultdict(list)
    for hb_room in _hb_model.rooms:
        try:
            rooms_grouped_by_story["{:02d}".format(int(hb_room.story))].append(hb_room)
        except:
            rooms_grouped_by_story[hb_room.story].append(hb_room)

    # -- Sort the room groups by their Key (which is their Story name)
    sorted_rooms_grouped_by_story = OrderedDict()
    for k in sorted(rooms_grouped_by_story.keys()):
        sorted_rooms_grouped_by_story[k] = rooms_grouped_by_story[k]

    return sorted_rooms_grouped_by_story


def _build_rh_attrs(_IGH, _color, _weight=0.5, _draw_order=None):
    # type: (gh_io.IGH, Color, float, Optional[int]) -> ObjectAttributes

    new_attr_obj = rdo.ObjectAttributes()

    new_attr_obj.ObjectColor = _color
    new_attr_obj.PlotColor = _color
    new_attr_obj.ColorSource = rdo.ObjectColorSource.ColorFromObject
    new_attr_obj.PlotColorSource = rdo.ObjectPlotColorSource.PlotColorFromObject

    new_attr_obj.PlotWeight = _weight
    new_attr_obj.PlotWeightSource = rdo.ObjectPlotWeightSource.PlotWeightFromObject

    if _draw_order:
        new_attr_obj.DisplayOrder = _draw_order  # 1 = Front, -1 = Back

    return new_attr_obj


def _get_flr_seg_data(_IGH, _get_color, _space):
    # type: (gh_io.IGH, Callable, space.Space) -> Tuple[List, List]
    """Return a Tuple of Lists with the Geometry and the ObjectAttributes."""

    flr_seg_geom_ = []  # type: List[Optional[Brep]]
    flr_sef_attrs_ = []  # type: List[ObjectAttributes]

    # -- Build the outline curve attr
    crv_attr = _build_rh_attrs(_IGH, Color.FromArgb(255, 40, 40, 40), 0.4)

    for volume in _space.volumes:
        for flr_seg in volume.floor.floor_segments:
            # -- Object Attributes
            rh_attr = _build_rh_attrs(_IGH, _get_color(flr_seg, _space))

            # -- Geometry as Mesh
            brp = from_face3d(flr_seg.geometry)
            msh = _IGH.ghpythonlib_components.MeshColours(brp, rh_attr.ObjectColor)
            flr_seg_geom_.append(msh)
            flr_sef_attrs_.append(rh_attr)

            # -- Boundary Edges
            msh_edges = _IGH.ghpythonlib_components.MeshEdges(msh).naked_edges
            msh_boundary = _IGH.ghpythonlib_components.JoinCurves(
                msh_edges, preserve=False
            )

            # -- Sometimes Join Curves returns a list of items....
            if isinstance(msh_boundary, list):
                for crv in msh_boundary:
                    flr_seg_geom_.append(crv)
                    flr_sef_attrs_.append(crv_attr)
            else:
                flr_seg_geom_.append(msh_boundary)
                flr_sef_attrs_.append(crv_attr)

    return flr_seg_geom_, flr_sef_attrs_


def _get_clipping_plane_locations(_IGH, _room_group, _offset_up=0.25, _offset_down=0.25):
    # type: (gh_io.IGH, List[room.Room], float, float) -> Tuple[ClippingPlaneLocation, ClippingPlaneLocation]
    """Return a pair of ClippingPlaneLocation objects. One pointing 'up' and the other 'down'.

    These are used to clip the scene local to the floor-plan being printed.
    """

    # -- Get the offset distance in the Rhino-document units

    doc_units = _IGH.get_rhino_unit_system_name()
    offset_up_in_doc_units = convert(_offset_up, "M", doc_units)
    offset_down_in_doc_units = convert(_offset_down, "M", doc_units)

    # -- Find the Min Z-location of the Floor-Faces of the Room-Group
    # -- use both the space floor-segments and the Honeybee 'Floor' surfaces
    space_floor_segments = [
        face
        for rm in _room_group
        for sp in getattr(rm.properties, "ph").spaces
        for faces in sp.floor_segment_surfaces
        for face in faces
    ]
    hb_room_floor_srfcs = [
        face
        for rm in _room_group
        for face in rm.faces
        if (isinstance(face.type, facetype.Floor))
    ]
    flr_faces = space_floor_segments + hb_room_floor_srfcs
    flr_level_min_z = min(hb_face.min.z for hb_face in flr_faces)
    flr_level_max_z = max(hb_face.max.z for hb_face in flr_faces)

    # --Create the clipping plane location objects up/down from that level.
    upper_clipping_plane = ClippingPlaneLocation(
        rg.Point3d(0, 0, flr_level_max_z + offset_up_in_doc_units),
        rg.Vector3d(0, 0, -1),
    )
    lower_clipping_plane = ClippingPlaneLocation(
        rg.Point3d(0, 0, flr_level_min_z - offset_down_in_doc_units),
        rg.Vector3d(0, 0, 1),
    )

    return upper_clipping_plane, lower_clipping_plane


def _find_space_annotation_location(_IGH, _space):
    # type: (gh_io.IGH, space.Space) -> Point3d
    """Returns a single geometric center point of a Space's Volumes."""
    return _IGH.ghpythonlib_components.Average(
        [from_point3d(p) for p in _space.reference_points]
    )


def _get_all_space_floor_segment_center_points(_IGH, space):
    # type: (gh_io.IGH, space.Space) -> List[Point3d]
    """Return a list of all the SpaceFloorSegment center-points in the Space's Volumes."""

    return [
        from_point3d(flr_seg.geometry.center)
        for volume in space.volumes
        for flr_seg in volume.floor.floor_segments
    ]


def _build_annotation_leader_line(_IGH, _pt1, _pt2):
    # type: (gh_io.IGH, Point3d, Point3d) -> Tuple[Line, ObjectAttributes]
    """Return a new LeaderLine and ObjectAttributes"""

    rh_geom = rg.Line(_pt1, _pt2)
    rh_attr = _build_rh_attrs(_IGH, Color.FromArgb(255, 0, 0, 0), 0.05)

    return rh_geom, rh_attr


def _build_annotation_leader_marker(_IGH, _cp, _radius=0.0075):
    # type: (gh_io.IGH, Point3d, float) -> Tuple
    """Return a new 'dot' mesh and ObjectAttributes"""

    rh_attr = _build_rh_attrs(_IGH, Color.FromArgb(255, 0, 0, 0), 0.5, 1)

    c = _IGH.ghpythonlib_components.Circle(_cp, _radius)
    brp = _IGH.ghpythonlib_components.BoundarySurfaces(c)
    rh_geom = _IGH.ghpythonlib_components.MeshColours(brp, rh_attr.ObjectColor)

    return rh_geom, rh_attr


# -----------------------------------------------------------------------------


class GHCompo_CreateFloorSegmentPDFGeometry(object):
    def __init__(
        self, _IGH, _hb_model, _drawing_type, _units_, _flr_anno_txt_size, *args, **kwargs
    ):
        # type: (gh_io.IGH, model.Model, str, str, float, *Any, **Any) -> None
        self.IGH = _IGH
        self.hb_model = _hb_model
        self.units = _units_ or "SI"
        self.flr_anno_txt_size = _flr_anno_txt_size or 1.0

        drawing_type = input_to_int(_drawing_type, 1)
        if drawing_type == 1:  # TFA-Plans
            self.colors = color_by_TFA
            self.text = text_by_TFA
        elif drawing_type == 2:  # Ventilation Plans
            self.colors = color_by_Vent
            self.text = text_by_Vent
        else:
            self.IGH.error("Error: Plan type: {} is not supported?".format(_drawing_type))

    @property
    def mask(self):
        # type: () -> TextAnnotationMaskAttributes

        return TextAnnotationMaskAttributes(
            _show_mask=True,
            _mask_color=Color.FromArgb(0, 0, 0, 0),
            _mask_offset=self.flr_anno_txt_size * 2,
            _frame_type=1,
            _show_frame=True,
        )

    def run(self):
        # type: () -> Tuple

        # -- Output Trees
        floor_names_ = self.IGH.DataTree(str)
        clipping_plane_locations_ = self.IGH.DataTree()
        floor_geom_ = self.IGH.DataTree()
        floor_attributes_ = self.IGH.DataTree(ObjectAttributes)
        floor_annotations_ = self.IGH.DataTree(TextAnnotation)
        pth = self.IGH.GH_Path

        if not self.hb_model:
            return (
                floor_names_,
                clipping_plane_locations_,
                floor_geom_,
                floor_attributes_,
                floor_annotations_,
            )

        # -- Find the floor levels
        rooms_grouped_by_story = _group_hb_rooms_by_story(self.hb_model)

        # -- Build the TextAnnotation objects
        for i, item in enumerate(rooms_grouped_by_story.items()):
            level_name, hb_rm_group = item
            floor_names_.Add(level_name, pth(i))
            clipping_plane_locations_.AddRange(
                _get_clipping_plane_locations(self.IGH, hb_rm_group), pth(i)
            )

            # -- Create space floor Geometry and Annotation
            spaces = _get_hbph_spaces(hb_rm_group)
            for space in spaces:
                #  -- Add the Floor segment geometry
                flr_seg_geom, flr_seg_attrs = _get_flr_seg_data(
                    self.IGH, self.colors, space
                )
                floor_geom_.AddRange(flr_seg_geom, pth(i))
                floor_attributes_.AddRange(flr_seg_attrs, pth(i))

                # -- Add Leader Lines from Annotation to each FloorSegment CenterPoint
                anno_cp = _find_space_annotation_location(self.IGH, space)
                flr_seg_cps = _get_all_space_floor_segment_center_points(self.IGH, space)
                for flr_cp in flr_seg_cps:
                    # -- add the leader line itself
                    ldr, ldr_attr = _build_annotation_leader_line(
                        self.IGH, anno_cp, flr_cp
                    )
                    floor_geom_.Add(ldr, pth(i))
                    floor_attributes_.Add(ldr_attr, pth(i))

                    # -- add a dot marker at the leader line end point
                    marker_geom, marker_attrs = _build_annotation_leader_marker(
                        self.IGH, flr_cp, 0.05
                    )
                    floor_geom_.Add(marker_geom, pth(i))
                    floor_attributes_.Add(marker_attrs, pth(i))

                # -- Add the text Annotation object
                txt_annotation = TextAnnotation(
                    self.IGH,
                    _text=self.text(space, self.IGH, self.units),
                    _size=self.flr_anno_txt_size,
                    _location=anno_cp,
                    _format="{}",
                    _justification=4,
                    _mask=self.mask,
                    _align_to_layout_view=True,
                )
                floor_annotations_.Add(txt_annotation, pth(i))

        return (
            floor_names_,
            clipping_plane_locations_,
            floor_geom_,
            floor_attributes_,
            floor_annotations_,
        )
