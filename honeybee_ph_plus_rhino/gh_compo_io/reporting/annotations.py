# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""TextAnnotations class used for writing to PDF."""

from copy import copy

try:
    from typing import Any, List, Optional, TypeVar, Union

    T = TypeVar("T")
except ImportError:
    pass  # IronPython 2.7

try:
    from Grasshopper import DataTree  # type: ignore
    from Rhino import Geometry as rg  # type:ignore
except ImportError:
    pass  # Outside Rhino

try:
    from ph_gh_component_io import gh_io
except ImportError:
    raise ImportError("Failed to import ph_gh_component_io")
    
try:
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")

try:
    from honeybee_ph_utils.input_tools import clean_tree_get, cleaner_get
except ImportError as e:
    raise ImportError("{}\nFailed to import honeybee_ph_utils".format(e))

from honeybee_ph_plus_rhino.gh_compo_io.reporting.annotation_mask import (
    TextAnnotationMaskAttributes,
)


class RHTextJustify(ghio_validators.Validated):
    """Validator for Integer user-input conversion into Rhino.Geometry.TextJustification Enum."""

    def validate(self, name, new_value, old_value):
        if new_value is None:
            return old_value

        if isinstance(new_value, rg.TextJustification):
            return new_value

        # if it's an integer input, convert to a TextJustification
        mapping = {
            0: rg.TextJustification.BottomLeft,
            1: rg.TextJustification.BottomCenter,
            2: rg.TextJustification.BottomRight,
            3: rg.TextJustification.MiddleLeft,
            4: rg.TextJustification.MiddleCenter,
            5: rg.TextJustification.MiddleRight,
            6: rg.TextJustification.TopLeft,
            7: rg.TextJustification.TopCenter,
            8: rg.TextJustification.TopRight,
        }

        try:
            return mapping[int(new_value)]
        except KeyError as e:
            msg = "Error: {} is not a valid Text Justification?".format(new_value)
            raise KeyError("{}\n{}".format(e, msg))


class TextAnnotation(object):
    """Dataclass for Layout-Page Labels."""

    justification = RHTextJustify("justification")

    def __init__(
        self,
        _IGH,
        _text,
        _size,
        _location,
        _format="{}",
        _justification=3,
        _align_to_layout_view=False,
        _mask=None,
    ):
        # type: (gh_io.IGH, str, float, Union[rg.Point3d, rg.Plane], str, int, bool, Optional[TextAnnotationMaskAttributes]) -> None
        self.IGH = _IGH
        self._text = _text
        self.text_size = _size
        self._location = _location
        self.format = _format
        self.justification = _justification  # type: TextJustification # type: ignore
        self.align_to_layout_view = _align_to_layout_view
        self.mask = _mask

    @property
    def anchor_point(self):
        # type: () -> rg.Point3d
        """Return the 3D anchor point for the Text Annotation"""

        if isinstance(self._location, rg.Plane):
            return self._location.Origin
        if isinstance(self._location, rg.Point3d):
            return self._location
        else:
            raise ValueError(
                "Location input must be a Point3d or Plane? Got: {}".format(
                    type(self._location)
                )
            )

    @property
    def plane(self):
        # type: () -> rg.Plane
        """Return the 3D Plane for the Text Annotation."""

        if isinstance(self._location, rg.Plane):
            return self._location
        elif isinstance(self._location, rg.Point3d):
            default_normal = rg.Vector3d(0, 0, 1)  # Assumes Top View
            default_plane = rg.Plane(origin=self._location, normal=default_normal)
            return default_plane
        else:
            raise ValueError(
                "Location input must be a Point3d or Plane? Got: {}".format(
                    type(self._location)
                )
            )

    @property
    def text(self):
        fmt = "{}".format(self.format)
        try:
            return fmt.format(self._text)
        except ValueError:
            try:
                return fmt.format(float(self._text))
            except Exception:
                return self._text

    def transform(self, _transform):
        # type: (rg.Transform) -> TextAnnotation
        """Applies a Rhino-Transform to a TextAnnotation object. Returns a copy of the TextAnnotation.

        Arguments:
        ----------
            * _transform (Transform): The Rhino Transform to apply to the TextAnnotation.

        Returns:
        --------
            * (TextAnnotation): The new TextAnnotation with the transform applied.
        """

        if not _transform:
            return self

        new_obj = self.duplicate()
        try:
            new_obj._location = self.IGH.ghc.Transform(new_obj._location, _transform)
        except Exception as e:
            raise Exception(e)

        return new_obj

    def duplicate(self):
        # type: () -> TextAnnotation
        return self.__copy__()

    def __copy__(self):
        # type: () -> TextAnnotation
        return TextAnnotation(
            self.IGH,
            copy(self._text),
            self.text_size,
            self._location,
            self.format,
            self.justification,
            self.align_to_layout_view,
            copy(self.mask),
        )

    def _truncate(self, txt):
        # type: (str) -> str
        limit = 20
        if len(txt) > limit:
            return "{}...".format(txt.replace("\n", "")[:limit])
        else:
            return txt

    def __str__(self):
        return "{}(text={}, text_size={}, anchor_point={}, format={}, justification={})".format(
            self.__class__.__name__,
            self._truncate(self.text),
            self.text_size,
            self.anchor_point,
            self._truncate(self.format),
            self.justification,
        )

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)


class GHCompo_CreateTextAnnotations(object):
    default_size = 0.25
    default_location = rg.Point3d(0, 0, 0)
    default_format = "{}"
    default_justification = 4  # 4=Middle-Center

    def __init__(
        self,
        _IGH,
        _text,
        _size,
        _location,
        _format,
        _justification,
        _mask,
        *args,
        **kwargs
    ):
        # type: (gh_io.IGH, DataTree, DataTree, DataTree, DataTree, DataTree, DataTree, *Any, **Any) -> None
        self.IGH = _IGH
        self.text = _text
        self.size = _size
        self.location = _location
        self.format = _format
        self.justification = _justification
        self.mask = _mask

    def get_size_branch(self, i):
        # type: (int) -> List[float]
        return clean_tree_get(self.size, i, _default=[self.default_size])

    def get_location_branch(self, i):
        # type: (int) -> List[rg.Point3d]
        return clean_tree_get(self.location, i, _default=[rg.Point3d(0, 0, 0)])

    def get_format_branch(self, i):
        # type: (int) -> List[str]
        return clean_tree_get(self.format, i, _default=[self.default_format])

    def get_justification_branch(self, i):
        # type: (int) -> List[int]
        return clean_tree_get(
            self.justification, i, _default=[self.default_justification]
        )

    def get_mask_branch(self, i):
        # type: (int) -> List[TextAnnotationMaskAttributes] | List[None]
        return clean_tree_get(self.mask, i, _default=[None])

    def run(self):
        # type: () -> DataTree[TextAnnotation]
        text_annotations_ = self.IGH.DataTree(TextAnnotation)
        for i, branch in enumerate(self.text.Branches):
            # -- Get the right tree branch
            size_branch = self.get_size_branch(i)
            loc_branch = self.get_location_branch(i)
            format_branch = self.get_format_branch(i)
            justify_branch = self.get_justification_branch(i)
            mask_branch = self.get_mask_branch(i)

            for k, txt in enumerate(branch):
                # -- Get the right data from the tree branch
                size = cleaner_get(list(size_branch), k, 0.25)
                location = cleaner_get(list(loc_branch), k, self.default_location)
                format = cleaner_get(list(format_branch), k, self.default_format)
                justification = cleaner_get(
                    list(justify_branch), k, self.default_justification
                )
                mask = cleaner_get(list(mask_branch), k, None)

                # -- Build the TextAnnotation
                new_label = TextAnnotation(
                    self.IGH, txt, size, location, format, justification, False, mask
                )
                text_annotations_.Add(new_label, self.IGH.GH_Path(i))

        return text_annotations_
