# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""TextAnnotation-Mask dataclass used for writing to PDF."""

try:
    from typing import Any, List
except ImportError:
    pass  # IronPython 2.7

try:
    from System.Drawing import Color  # type: ignore
except ImportError:
    raise ImportError(
        "Failed to import System.Drawing.\n"
        "Module '{}' cannot be used outside Rhino.".format(__name__)
    )
try:
    from Rhino.DocObjects.DimensionStyle import MaskFrame  # type: ignore
except ImportError:
    raise ImportError(
        "Failed to import Rhino.DocObjects.DimensionStyle.\n"
        "Module '{}' cannot be used outside Rhino.".format(__name__)
    )

try:
    from Grasshopper import DataTree  # type: ignore
except ImportError:
    raise ImportError(
        "Failed to import Grasshopper.\n"
        "Module '{}' cannot be used outside Rhino.".format(__name__)
    )

try:
    from honeybee_ph_rhino import gh_io
    from honeybee_ph_rhino.gh_compo_io import ghio_validators
except ImportError:
    raise ImportError("Failed to import honeybee_ph_rhino")

try:
    from honeybee_ph_utils.input_tools import clean_tree_get, cleaner_get
except ImportError as e:
    raise ImportError("{}\nFailed to import honeybee_ph_utils".format(e))


class RHMaskFrameType(ghio_validators.Validated):
    """Validator for Integer user-input conversion into Rhino.Geometry.TextJustification Enum."""

    def validate(self, name, new_value, old_value):
        if new_value is None:
            return old_value

        if isinstance(new_value, MaskFrame):
            return new_value

        # if it's an integer input, convert to a MaskFrame
        mapping = {
            0: MaskFrame.NoFrame,
            1: MaskFrame.RectFrame,
            2: MaskFrame.CapsuleFrame,
        }

        try:
            return mapping[int(new_value)]
        except KeyError as e:
            msg = "Error: {} is not a valid Mask Frame Type?".format(new_value)
            raise KeyError("{}\n{}".format(e, msg))


class TextAnnotationMaskAttributes(object):
    frame_type = RHMaskFrameType("frame_type")

    def __init__(
        self,
        _show_mask=True,
        _mask_color=Color.FromArgb(50, 0, 0, 0),
        _mask_offset=0.0,
        _frame_type=1,
        _show_frame=True,
    ):
        self.show_mask = _show_mask
        self.mask_color = _mask_color
        self.mask_offset = _mask_offset
        self.frame_type = _frame_type  # type: MaskFrame
        self.show_frame = _show_frame

    def __copy__(self):
        return TextAnnotationMaskAttributes(
            self.show_mask,
            self.mask_color,
            self.mask_offset,
            self.frame_type,
            self.show_frame,
        )

    def __str__(self):
        return "{}({})".format(
            self.__class__.__name__, ["{}={}".format(k, v) for k, v in vars(self).items()]
        )

    def __repr__(self):
        return str(self)

    def ToString(self):
        return str(self)


class GHCompo_CreateTextAnnotationMask(object):
    default_show_mask = True
    default_color = Color.FromArgb(50, 0, 0, 0)
    default_offset = 0.0
    default_frame_type = MaskFrame.RectFrame
    default_show_frame = True

    def __init__(
        self, _IGH, _show_mask, _color, _offset, _frame_type, _show_frame, *args, **kwargs
    ):
        # type: (gh_io.IGH, DataTree, DataTree, DataTree, DataTree, DataTree, *Any, **Any) -> None
        self.IGH = _IGH
        self.show_mask = _show_mask
        self.color = _color
        self.offset = _offset
        self.frame_type = _frame_type
        self.show_frame = _show_frame

    def get_show_mask_branch(self, i):
        # type: (int) -> List[bool]
        """Get the i-th branch of the show_mask DataTree."""
        return clean_tree_get(self.show_mask, i, _default=[self.default_show_mask])

    def get_color_branch(self, i):
        # type: (int) -> List[Color]
        """Get the i-th branch of the color DataTree."""
        return clean_tree_get(self.color, i, _default=[self.default_color])

    def get_offset_branch(self, i):
        # type: (int) -> List[float]
        """Get the i-th branch of the offset DataTree."""
        return clean_tree_get(self.offset, i, _default=[self.default_offset])

    def get_frame_type_branch(self, i):
        # type: (int) -> List[int]
        """Get the i-th branch of the frame_type DataTree."""
        return clean_tree_get(self.frame_type, i, _default=[self.default_frame_type])

    def get_show_frame_branch(self, i):
        # type: (int) -> List[bool]
        """Get the i-th branch of the show_frame DataTree."""
        return clean_tree_get(self.show_frame, i, _default=[self.default_show_frame])

    @property
    def longest_branch_count_input(self):
        # type: () -> int
        """Get the Branch-Count of the longest DataTree input."""
        return (
            max(
                [
                    self.show_mask.BranchCount,
                    self.color.BranchCount,
                    self.offset.BranchCount,
                    self.frame_type.BranchCount,
                    self.show_frame.BranchCount,
                ]
            )
            or 1
        )

    def max_list_length(self, _lists):
        # type: (List[List[Any]]) -> int
        """Get the length of the longest list in a list of lists."""
        return max([len(lst) for lst in _lists]) or 1

    def run(self):
        # type: () -> DataTree[TextAnnotationMaskAttributes]
        text_annotation_masks_ = self.IGH.DataTree(TextAnnotationMaskAttributes)
        for i in range(self.longest_branch_count_input):
            show_mask_branch = self.get_show_mask_branch(i)
            color_branch = self.get_color_branch(i)
            offset_branch = self.get_offset_branch(i)
            frame_type_branch = self.get_frame_type_branch(i)
            show_frame_branch = self.get_show_frame_branch(i)

            for k in range(
                self.max_list_length(
                    [
                        show_mask_branch,
                        color_branch,
                        offset_branch,
                        frame_type_branch,
                        show_frame_branch,
                    ]
                )
            ):
                # -- Get the right data from the tree branch
                show_mask = cleaner_get(
                    list(show_mask_branch), k, _default=self.default_show_mask
                )
                color = cleaner_get(list(color_branch), k, _default=self.default_color)
                offset = cleaner_get(list(offset_branch), k, _default=self.default_offset)
                frame_type = cleaner_get(
                    list(frame_type_branch), k, _default=self.default_frame_type
                )
                show_frame = cleaner_get(
                    list(show_frame_branch), k, _default=self.default_show_frame
                )

                # -- Build the TextAnnotationMaskAttributes
                new_mask = TextAnnotationMaskAttributes(
                    show_mask, color, offset, frame_type, show_frame
                )

                text_annotation_masks_.Add(new_mask)

        return text_annotation_masks_
