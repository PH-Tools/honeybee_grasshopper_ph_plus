"""Tests for the PH-Navigator V1 route-3 schema fork, focused on the `installs` block.

The module under test has no third-party imports (only `copy` and a guarded
`typing`), so it is loaded straight off disk rather than through the package
`__init__`, which would drag in the Rhino-only component modules.
"""

from __future__ import absolute_import

import importlib.util
from pathlib import Path

import pytest

_MODULE_PATH = (
    Path(__file__).parents[1]
    / "honeybee_ph_plus_rhino"
    / "gh_compo_io"
    / "ph_navigator"
    / "v1"
    / "window_types_schema.py"
)


def _load_schema():
    spec = importlib.util.spec_from_file_location("ph_nav_v1_window_types_schema_under_test", _MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def schema():
    return _load_schema()


# -- Payload fragments copied from a live BT 1234 route-3 response (2026-08-26).


def _frame_dict():
    return {
        "name": "PHN-Default-Frame",
        "frame_type": {
            "id": "pfrm_5d446ca7d9a1",
            "name": "PHN-Default-Frame",
            "width_mm": 50.0,
            "u_value_w_m2k": 1.5,
            "psi_g_w_mk": 0.04,
            "psi_install_w_mk": 0.04,
        },
    }


def _glazing_dict():
    return {
        "name": "PHN-Default-Glass",
        "glazing_type": {"name": "PHN-Default-Glass", "u_value_w_m2k": 1.0, "g_value": 0.5},
    }


def _default_install():
    return {
        "install_type_id": "apit_default",
        "name": "Default",
        "psi_install_w_mk": 0.04,
        "source": "default",
    }


def _mull_install():
    return {"install_type_id": None, "name": None, "psi_install_w_mk": 0.0, "source": "mull"}


def _element_dict(_column_number=0, _mulled_side="right", _row_number=0):
    """Element 'A' of BT 1234: default on three edges, a mull on one."""
    installs = dict((side, _default_install()) for side in ("top", "right", "bottom", "left"))
    if _mulled_side is not None:
        installs[_mulled_side] = _mull_install()
    return {
        "name": "A",
        "row_number": _row_number,
        "column_number": _column_number,
        "row_span": 1,
        "col_span": 1,
        "glazing": _glazing_dict(),
        "frames": dict((side, _frame_dict()) for side in ("top", "right", "bottom", "left")),
        "installs": installs,
    }


# -- InstallData ---------------------------------------------------------------


def test_install_data_parses_an_assigned_edge(schema):
    install = schema.InstallData.from_dict(_default_install())

    assert install.install_type_id == "apit_default"
    assert install.name == "Default"
    assert install.display_name == "Default"
    assert install.psi_install_w_mk == pytest.approx(0.04)
    assert install.source == "default"
    assert install.is_mull is False


def test_install_data_parses_a_mulled_edge_with_null_identity(schema):
    install = schema.InstallData.from_dict(_mull_install())

    assert install.install_type_id is None
    assert install.name is None
    assert install.psi_install_w_mk == pytest.approx(0.0)
    assert install.source == "mull"
    assert install.is_mull is True


def test_install_data_null_psi_falls_back_to_zero_not_the_frame_placeholder(schema):
    """0.0, never 0.04 - this block is resolved truth, so absent means 'no bridge'."""
    install = schema.InstallData.from_dict({"install_type_id": None, "name": None, "psi_install_w_mk": None})

    assert install.psi_install_w_mk == pytest.approx(0.0)
    assert install.source == ""


# -- InstallsData --------------------------------------------------------------


def test_installs_data_parses_all_four_sides(schema):
    installs = schema.InstallsData.from_dict(_element_dict()["installs"])

    assert installs.top.psi_install_w_mk == pytest.approx(0.04)
    assert installs.right.psi_install_w_mk == pytest.approx(0.0)
    assert installs.bottom.psi_install_w_mk == pytest.approx(0.04)
    assert installs.left.psi_install_w_mk == pytest.approx(0.04)
    assert installs.right.is_mull is True


def test_get_all_installs_is_top_right_bottom_left(schema):
    """The order every downstream consumer assumes; pinned so it cannot drift."""
    installs = schema.InstallsData.from_dict(_element_dict()["installs"])

    assert schema.InstallsData.SIDES == ("top", "right", "bottom", "left")
    assert [i.psi_install_w_mk for i in installs.get_all_installs()] == pytest.approx([0.04, 0.0, 0.04, 0.04])


def test_get_all_installs_keeps_none_entries_so_positions_stay_aligned(schema):
    installs = schema.InstallsData.from_dict({"top": _default_install(), "bottom": _mull_install()})
    all_installs = installs.get_all_installs()

    assert len(all_installs) == 4
    assert all_installs[1] is None  # right
    assert all_installs[3] is None  # left
    assert all_installs[0].source == "default"
    assert all_installs[2].source == "mull"


def test_get_install_by_side(schema):
    installs = schema.InstallsData.from_dict(_element_dict()["installs"])

    assert installs.get_install_by_side("right").is_mull is True
    assert installs.get_install_by_side("top").install_type_id == "apit_default"
    assert installs.get_install_by_side("nonsense") is None


def test_a_null_side_stays_none_rather_than_becoming_a_zero_psi_edge(schema):
    installs = schema.InstallsData.from_dict({"top": None, "right": _default_install()})

    assert installs.top is None
    assert installs.right.psi_install_w_mk == pytest.approx(0.04)


# -- ElementData ---------------------------------------------------------------


def test_element_parses_the_installs_block(schema):
    element = schema.ElementData.from_dict(_element_dict(), "Test Aperture")

    assert element.type_name == "Test Aperture_C0_R0"
    assert element.installs is not None
    assert element.installs.right.source == "mull"


def test_element_without_installs_key_is_unchanged_from_legacy_behaviour(schema):
    legacy = _element_dict()
    del legacy["installs"]

    element = schema.ElementData.from_dict(legacy, "Test Aperture")

    assert element.installs is None
    # -- the legacy uniform-default path still works exactly as before
    assert element.frames.top.frame_type.psi_install_w_mk == pytest.approx(0.04)


def test_element_with_explicitly_null_installs_is_treated_as_legacy(schema):
    payload = _element_dict()
    payload["installs"] = None

    assert schema.ElementData.from_dict(payload, "Test Aperture").installs is None


def test_element_copy_deep_copies_installs(schema):
    """`reverse_elements_row_order` copies every element, so a shared mutable
    InstallsData would leak one element's edges onto another."""
    element = schema.ElementData.from_dict(_element_dict(), "Test Aperture")
    duplicate = schema.copy(element)

    assert duplicate.installs is not element.installs
    assert duplicate.installs.right is not element.installs.right

    duplicate.installs.right.psi_install_w_mk = 99.0
    assert element.installs.right.psi_install_w_mk == pytest.approx(0.0)


def test_element_copy_of_a_legacy_element_keeps_installs_none(schema):
    legacy = _element_dict()
    del legacy["installs"]

    assert schema.copy(schema.ElementData.from_dict(legacy, "Test Aperture")).installs is None


# -- The standing trap: row reversal must not touch side names -----------------


def test_row_reversal_reindexes_rows_without_renaming_sides(schema):
    """`reverse_elements_row_order` re-indexes the grid for Rhino's bottom-to-top
    build order. It does not mirror it, so an element's own top edge is still its
    top edge. Pinned because getting this wrong swaps head and sill psi-installs."""
    aperture = schema.ApertureTypeData.from_dict(
        {
            "name": "Two Rows",
            "row_heights_mm": [1000.0, 1000.0],
            "column_widths_mm": [1000.0],
            "elements": [
                _element_dict(_row_number=0, _mulled_side="bottom"),  # PHN top row
                _element_dict(_row_number=1, _mulled_side="top"),  # PHN bottom row
            ],
        }
    )

    by_row = dict((element.row_number, element) for element in aperture.elements)

    # -- PHN row 0 (visually top) becomes Rhino row 1 (visually top); not mirrored.
    assert sorted(by_row) == [0, 1]
    assert by_row[1].installs.bottom.is_mull is True
    assert by_row[1].installs.top.is_mull is False
    assert by_row[0].installs.top.is_mull is True
    assert by_row[0].installs.bottom.is_mull is False


def test_single_row_aperture_keeps_r0_keys(schema):
    """The BT 1234 shape: two columns, one row, keys stay `..._C0_R0` / `..._C1_R0`."""
    aperture = schema.ApertureTypeData.from_dict(
        {
            "name": "Test Aperture",
            "row_heights_mm": [1000.0],
            "column_widths_mm": [1000.0, 1000.0],
            "elements": [
                _element_dict(_column_number=0, _mulled_side="right"),
                _element_dict(_column_number=1, _mulled_side="left"),
            ],
        }
    )

    assert [e.type_name for e in aperture.elements] == ["Test Aperture_C0_R0", "Test Aperture_C1_R0"]
    assert aperture.elements[0].installs.right.is_mull is True
    assert aperture.elements[1].installs.left.is_mull is True
