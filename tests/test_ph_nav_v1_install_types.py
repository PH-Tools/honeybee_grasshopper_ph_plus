"""Tests for the PH-Navigator V1 Install-Type builder and the 'Set Apertures' component.

Both modules live on the Rhino load path, so their honeybee / Grasshopper imports are
stubbed through `sys.modules` (the pattern in `test_win_create_types.py`) and the
modules are then loaded straight off disk. The real V1 schema module is used as-is -
it has no third-party imports - so the payload fixtures exercise the actual parse.
"""

from __future__ import absolute_import

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

_V1_DIR = Path(__file__).parents[1] / "honeybee_ph_plus_rhino" / "gh_compo_io" / "ph_navigator" / "v1"


# -- Stubs ---------------------------------------------------------------------


class _PhApertureInstallType(object):
    """Stand-in for honeybee_energy_ph.construction.window.PhApertureInstallType."""

    def __init__(self, _identifier):
        self.identifier = _identifier
        self.display_name = _identifier
        self.psi_install = 0.0
        self.source = ""


def _clean_ep_string(value):
    return value.replace(",", "").replace(";", "").strip()


def _content_keyed_identifier(_psi_install_w_mk):
    return _clean_ep_string("PhApertureInstallType_{:.4f}".format(_psi_install_w_mk))


def _build_install_type(_display_name, _psi_install_w_mk, _source=""):
    identifier = _clean_ep_string(_display_name) if _display_name else _content_keyed_identifier(_psi_install_w_mk)
    install_type = _PhApertureInstallType(identifier)
    install_type.display_name = _display_name or identifier
    install_type.psi_install = _psi_install_w_mk
    install_type.source = _source or ""
    return install_type


class _AperturePsiInstalls(object):
    SIDES = ("top", "right", "bottom", "left")

    def __init__(self):
        for side in self.SIDES:
            setattr(self, side, None)


class _Aperture(object):
    """Minimal honeybee Aperture: a name and PH-properties with install-type slots."""

    def __init__(self, display_name):
        self.display_name = display_name
        self.properties = type("_Props", (), {})()
        self.properties.ph = type("_PhProps", (), {})()
        self.properties.ph.install_types = _AperturePsiInstalls()

    def duplicate(self):
        dup = _Aperture(self.display_name)
        for side in _AperturePsiInstalls.SIDES:
            setattr(dup.properties.ph.install_types, side, getattr(self.properties.ph.install_types, side))
        return dup


class _FakeDataTree(object):
    """Just enough of Grasshopper's DataTree<T> for the component under test."""

    def __init__(self, branches=None, paths=None):
        self.Branches = list(branches or [])
        self.Paths = list(paths if paths is not None else range(len(self.Branches)))

    @classmethod
    def __class_getitem__(cls, _item):
        """Accept the .NET generic subscript, ie: `DataTree[Object]()`."""
        return cls

    def AddRange(self, items, path):
        self.Branches.append(list(items))
        self.Paths.append(path)


class _RecordingIGH(object):
    def __init__(self):
        self.warnings = []

    def warning(self, message):
        self.warnings.append(message)


class _CustomCollection(object):
    def __init__(self, mapping):
        self._storage = dict(mapping)

    def get(self, key, default):
        return self._storage.get(key, default)

    def __len__(self):
        return len(self._storage)


def _install_module(name, **attrs):
    module = ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


def _load_from_path(module_name, file_name):
    spec = importlib.util.spec_from_file_location(module_name, _V1_DIR / file_name)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def modules():
    """Load the schema, the builder, and the setter with their Rhino deps stubbed."""
    saved = dict(sys.modules)

    # -- the real schema, registered under its dotted name so the builder's absolute
    # -- import resolves to it without pulling in the component-laden package __init__
    schema = _load_from_path("hbph_v1_schema_under_test", "window_types_schema.py")
    for pkg in (
        "honeybee_ph_plus_rhino",
        "honeybee_ph_plus_rhino.gh_compo_io",
        "honeybee_ph_plus_rhino.gh_compo_io.ph_navigator",
        "honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1",
        "honeybee_ph_plus_rhino.gh_compo_io.collections",
    ):
        _install_module(pkg)
    sys.modules["honeybee_ph_plus_rhino.gh_compo_io.ph_navigator.v1.window_types_schema"] = schema
    _install_module(
        "honeybee_ph_plus_rhino.gh_compo_io.collections.create_new_collection",
        CustomCollection=_CustomCollection,
    )

    _install_module("honeybee_energy_ph")
    _install_module("honeybee_energy_ph.construction")
    _install_module("honeybee_energy_ph.construction.window", PhApertureInstallType=_PhApertureInstallType)

    _install_module("honeybee_ph_rhino")
    _install_module("honeybee_ph_rhino.gh_compo_io")
    _install_module("honeybee_ph_rhino.gh_compo_io.apertures")
    _install_module(
        "honeybee_ph_rhino.gh_compo_io.apertures.win_create_install_type",
        build_install_type=_build_install_type,
        content_keyed_identifier=_content_keyed_identifier,
    )

    _install_module("honeybee")
    _install_module("honeybee.aperture", Aperture=_Aperture)
    _install_module("honeybee_ph")
    _install_module("honeybee_ph.properties")
    _install_module("honeybee_ph.properties.aperture", AperturePsiInstalls=_AperturePsiInstalls)
    _install_module("ph_gh_component_io", gh_io=ModuleType("gh_io"))
    _install_module("Grasshopper", DataTree=_FakeDataTree)
    _install_module("System", Object=object)

    builder = _load_from_path("hbph_v1_install_types_build_under_test", "install_types_build.py")
    setter = _load_from_path("hbph_v1_apertures_set_under_test", "apertures_set.py")

    yield {"schema": schema, "builder": builder, "setter": setter}

    sys.modules.clear()
    sys.modules.update(saved)


# -- Payload fixtures (BT 1234, live response 2026-08-26) ----------------------


def _default_install():
    return {"install_type_id": "apit_default", "name": "Default", "psi_install_w_mk": 0.04, "source": "default"}


def _mull_install():
    return {"install_type_id": None, "name": None, "psi_install_w_mk": 0.0, "source": "mull"}


def _element(_column_number, _mulled_side):
    installs = dict((side, _default_install()) for side in ("top", "right", "bottom", "left"))
    installs[_mulled_side] = _mull_install()
    return {
        "name": "A",
        "row_number": 0,
        "column_number": _column_number,
        "row_span": 1,
        "col_span": 1,
        "glazing": {"name": "G", "glazing_type": {"name": "G", "u_value_w_m2k": 1.0, "g_value": 0.5}},
        "frames": {},
        "installs": installs,
    }


def _bt1234_payload():
    return {
        "name": "Test Aperture",
        "row_heights_mm": [1000.0],
        "column_widths_mm": [1000.0, 1000.0],
        "elements": [_element(0, "right"), _element(1, "left")],
    }


def _aperture_types(schema, payload=None):
    return [schema.ApertureTypeData.from_dict(payload or _bt1234_payload())]


# -- The builder ---------------------------------------------------------------


def test_the_two_side_orders_agree(modules):
    """The builder emits in `InstallsData.SIDES` order; the setter consumes in
    `AperturePsiInstalls.SIDES` order. They are separate constants in separate
    domains (payload schema vs HB model), so pin their agreement - a silent
    divergence would swap head and sill psi-installs on every window."""
    assert modules["schema"].InstallsData.SIDES == modules["setter"].SIDES


def test_builds_the_two_expected_four_item_lists(modules):
    """PRD acceptance 4.1."""
    built = modules["builder"].create_new_hbph_install_types(_aperture_types(modules["schema"]))

    assert sorted(built) == ["Test Aperture_C0_R0", "Test Aperture_C1_R0"]
    assert [i.psi_install for i in built["Test Aperture_C0_R0"]] == pytest.approx([0.04, 0.0, 0.04, 0.04])
    assert [i.psi_install for i in built["Test Aperture_C1_R0"]] == pytest.approx([0.04, 0.04, 0.04, 0.0])


def test_mull_and_default_entries_carry_the_expected_identity(modules):
    """PRD acceptance 4.2."""
    built = modules["builder"].create_new_hbph_install_types(_aperture_types(modules["schema"]))
    top, right, _, _ = built["Test Aperture_C0_R0"]

    assert top.identifier == "apit_default"
    assert top.display_name == "Default"
    assert right.psi_install == pytest.approx(0.0)
    assert right.source == "mull"


def test_one_instance_is_shared_across_every_default_edge(modules):
    """Pooling by identifier: one Install Type across 200 windows, not 200."""
    built = modules["builder"].create_new_hbph_install_types(_aperture_types(modules["schema"]))
    defaults = [i for values in built.values() for i in values if i.identifier == "apit_default"]

    assert len(defaults) == 6  # -- three default edges on each of the two elements
    assert len(set(id(i) for i in defaults)) == 1


def test_mulled_edges_share_one_content_keyed_instance(modules):
    built = modules["builder"].create_new_hbph_install_types(_aperture_types(modules["schema"]))
    mulls = [i for values in built.values() for i in values if i.source == "mull"]

    assert len(mulls) == 2
    assert len(set(id(i) for i in mulls)) == 1
    assert mulls[0].identifier == "PhApertureInstallType_0.0000"


def test_mull_identifiers_are_stable_across_runs(modules):
    """Content-keyed, never a uuid, so a re-download is idempotent (D-3)."""
    build = modules["builder"].create_new_hbph_install_types
    schema = modules["schema"]

    first = build(_aperture_types(schema))["Test Aperture_C0_R0"][1]
    second = build(_aperture_types(schema))["Test Aperture_C0_R0"][1]

    assert first.identifier == second.identifier


def test_a_legacy_payload_yields_an_empty_collection(modules):
    """PRD acceptance 4.7 - no `installs` block means no entries, not a crash."""
    payload = _bt1234_payload()
    for element in payload["elements"]:
        del element["installs"]

    assert modules["builder"].create_new_hbph_install_types(_aperture_types(modules["schema"], payload)) == {}


# -- The 'Set Apertures' component --------------------------------------------


def _run_setter(modules, apertures_tree, collection):
    component = modules["setter"].GHCompo_PHNavV1SetApertures(_RecordingIGH(), apertures_tree, collection)
    return component.run()


def test_assigns_per_element_values_from_a_flat_aperture_list(modules):
    """The D-2 regression test.

    A flat list is exactly the topology `srfc_names_` produces and the one that
    defeats branch-index matching: a positional setter would give every Aperture in
    this single branch the FIRST element's four values. Key matching must not.
    """
    schema, builder = modules["schema"], modules["builder"]
    collection = _CustomCollection(builder.create_new_hbph_install_types(_aperture_types(schema)))
    apertures = [_Aperture("Test Aperture_C0_R0"), _Aperture("Test Aperture_C1_R0")]

    result, report = _run_setter(modules, _FakeDataTree([apertures]), collection)

    c0, c1 = result.Branches[0]
    assert c0.properties.ph.install_types.right.psi_install == pytest.approx(0.0)
    assert c0.properties.ph.install_types.left.psi_install == pytest.approx(0.04)
    assert c1.properties.ph.install_types.left.psi_install == pytest.approx(0.0)
    assert c1.properties.ph.install_types.right.psi_install == pytest.approx(0.04)
    assert "2 Aperture(s) matched" in report[0]


def test_matching_is_unaffected_by_tree_topology(modules):
    """The same two Apertures, one per branch, must give the same answer."""
    schema, builder = modules["schema"], modules["builder"]
    collection = _CustomCollection(builder.create_new_hbph_install_types(_aperture_types(schema)))
    grafted = _FakeDataTree([[_Aperture("Test Aperture_C0_R0")], [_Aperture("Test Aperture_C1_R0")]])

    result, _ = _run_setter(modules, grafted, collection)

    assert result.Branches[0][0].properties.ph.install_types.right.psi_install == pytest.approx(0.0)
    assert result.Branches[1][0].properties.ph.install_types.left.psi_install == pytest.approx(0.0)


def test_input_tree_paths_are_preserved(modules):
    """A decorator, not a re-organizer: nested paths must not collapse to 0, 1, ..."""
    schema, builder = modules["schema"], modules["builder"]
    collection = _CustomCollection(builder.create_new_hbph_install_types(_aperture_types(schema)))
    tree = _FakeDataTree(
        [[_Aperture("Test Aperture_C0_R0")], [_Aperture("Test Aperture_C1_R0")]],
        paths=["{0;0}", "{0;1}"],
    )

    result, _ = _run_setter(modules, tree, collection)

    assert result.Paths == ["{0;0}", "{0;1}"]


def test_an_unmatched_aperture_passes_through_and_is_reported(modules):
    schema, builder = modules["schema"], modules["builder"]
    collection = _CustomCollection(builder.create_new_hbph_install_types(_aperture_types(schema)))
    stranger = _Aperture("Some Other Window")

    result, report = _run_setter(modules, _FakeDataTree([[stranger]]), collection)

    assert result.Branches[0][0] is stranger  # -- untouched, not even duplicated
    assert stranger.properties.ph.install_types.top is None
    assert "1 of 1 Aperture(s) did not match" in report[0]
    assert "Some Other Window" in report


def test_an_empty_collection_passes_the_apertures_through_unchanged(modules):
    """PRD acceptance 4.7 - a legacy payload must not raise here either."""
    apertures = _FakeDataTree([[_Aperture("Test Aperture_C0_R0")]])

    result, report = _run_setter(modules, apertures, _CustomCollection({}))

    assert result is apertures
    assert report == []


def test_a_short_install_type_list_is_refused_rather_than_half_applied(modules):
    """zip() would truncate silently, leaving some edges assigned and some inherited."""
    aperture = _Aperture("Test Aperture_C0_R0")
    collection = _CustomCollection({"Test Aperture_C0_R0": [_build_install_type(None, 0.0, "mull")]})

    result, report = _run_setter(modules, _FakeDataTree([[aperture]]), collection)

    assert result.Branches[0][0] is aperture
    assert aperture.properties.ph.install_types.top is None
    assert "did not match" in report[0]
