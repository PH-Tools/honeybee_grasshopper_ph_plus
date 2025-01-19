# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH+ - Check Shade Mesh."""

from collections import defaultdict

try:
    from typing import Any, Iterable, List
except ImportError:
    pass  # IronPython 2.7

try:
    from ladybug_geometry.geometry3d import Mesh3D, Point3D
except ImportError as e:
    raise ImportError("Failed to import ladybug_rhino: {}".format(e))

try:
    from ladybug_rhino.fromgeometry import from_mesh3d
except ImportError as e:
    raise ImportError("Failed to import ladybug_rhino: {}".format(e))

try:
    from honeybee import shade
except ImportError as e:
    raise ImportError("Failed to import honeybee: {}".format(e))

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino: {}".format(e))


def find_vertix_index(vertix_list, vertix):
    # type: (List[Point3D], Point3D) -> int
    """Find the index of a vertix in a list of vertices."""

    TOL = 0.0000001
    for i, other_vert in enumerate(vertix_list):
        if vertix.is_equivalent(other_vert, TOL):
            return i
    raise ValueError()


def interpret_input_from_face_vertices(mesh_faces):
    # type: (Iterable[tuple[Point3D, Point3D, Point3D]]) -> tuple[list[Point3D], list[tuple[int, ...]]]
    """Custom version of the native LBT Mesh3D.from_face_vertices() method with custom `find_vertix_index` used."""

    vertices = []
    face_collector = []

    # -- Create a list of vertices and faces from the input mesh_faces
    for mesh_face in mesh_faces:
        index_list = []
        for mesh_vertix in mesh_face:
            try:  # try and use an existing vertix
                index_list.append(find_vertix_index(vertices, mesh_vertix))
            except ValueError:  # add new point
                vertices.append(mesh_vertix)
                index_list.append(len(vertices) - 1)

        # -- Add the new mesh-face
        face_collector.append(tuple(index_list))

    return vertices, face_collector


class GHCompo_CheckShadeMesh(object):
    def __init__(self, _IGH, _shades, _face_to_vertix_threshold, *args, **kwargs):
        # type: (gh_io.IGH, List[shade.Shade], float, *Any, **Any) -> None
        self.IGH = _IGH
        self.shades = _shades
        self.face_to_vertix_threshold = _face_to_vertix_threshold or 1.5

    def shades_grouped_by_name(self):
        # type: () -> dict[str, List[shade.Shade]]
        """Group shades by their display name."""
        shade_groups = defaultdict(list)  # type: dict[str, List[shade.Shade]]
        for shd in self.shades:
            shade_groups[shd.display_name].append(shd)

        return shade_groups

    def run(self):
        # type: () -> List[shade.Shade]
        """Check the shade meshes and return the ones that seem suspect."""
        shade_groups = self.shades_grouped_by_name()
        check_shades_ = []
        for shade_group in shade_groups.values():
            face_vertices = (
                v
                for shd in shade_group
                for v in shd.geometry.triangulated_mesh3d.face_vertices
            )
            vertices, face_collector = interpret_input_from_face_vertices(face_vertices)
            joined_mesh = Mesh3D(tuple(vertices), tuple(face_collector))
            face_to_vert_ratio = float(len(joined_mesh.faces)) / float(
                len(joined_mesh.vertices)
            )

            # -- Add any problem-Meshes to the check_shades_ list
            if face_to_vert_ratio > self.face_to_vertix_threshold:
                check_shades_.append(from_mesh3d(joined_mesh))

        if len(check_shades_) > 0:
            msg = (
                "Warning: {} shade meshes should be checked. They may have "
                "some issues with their geometry. Use the 'check_shades_' output to "
                "see the suspect meshes".format(len(check_shades_))
            )
            self.IGH.warning(msg)
            print(msg)

        return check_shades_
