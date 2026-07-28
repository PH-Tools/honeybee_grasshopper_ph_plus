from __future__ import absolute_import

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace


class _UnitM(object):
    def __init__(self, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value


def _load_win_create_types(monkeypatch):
    validators = ModuleType("honeybee_ph_rhino.gh_compo_io.ghio_validators")
    validators.UnitM = _UnitM

    gh_compo_io = ModuleType("honeybee_ph_rhino.gh_compo_io")
    gh_compo_io.ghio_validators = validators
    honeybee_ph_rhino = ModuleType("honeybee_ph_rhino")
    honeybee_ph_rhino.gh_compo_io = gh_compo_io

    component_io = ModuleType("ph_gh_component_io")
    component_io.gh_io = SimpleNamespace(IGH=object)

    converter = ModuleType("ph_units.converter")
    converter.convert = lambda value, _from_unit, _to_unit: value
    ph_units = ModuleType("ph_units")
    ph_units.converter = converter

    monkeypatch.setitem(sys.modules, "honeybee_ph_rhino", honeybee_ph_rhino)
    monkeypatch.setitem(sys.modules, "honeybee_ph_rhino.gh_compo_io", gh_compo_io)
    monkeypatch.setitem(sys.modules, "honeybee_ph_rhino.gh_compo_io.ghio_validators", validators)
    monkeypatch.setitem(sys.modules, "ph_gh_component_io", component_io)
    monkeypatch.setitem(sys.modules, "ph_units", ph_units)
    monkeypatch.setitem(sys.modules, "ph_units.converter", converter)

    path = Path(__file__).parents[1] / "honeybee_ph_plus_rhino" / "gh_compo_io" / "hb_tools" / "win_create_types.py"
    spec = importlib.util.spec_from_file_location("win_create_types_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Plane(object):
    def __init__(self, x):
        self.Origin = x


class _GeometryComponents(object):
    @staticmethod
    def EndPoints(base_curve):
        return base_curve

    @staticmethod
    def Vector2Pt(start, end, _unitize):
        return SimpleNamespace(vector=(end - start) / abs(end - start))

    @staticmethod
    def UnitZ(_magnitude):
        return 1.0

    @staticmethod
    def ConstructPlane(start, _x_vector, _y_vector):
        return _Plane(start)

    @staticmethod
    def Amplitude(vector, magnitude):
        return vector * magnitude

    @staticmethod
    def Move(geometry, vector):
        if isinstance(geometry, _Plane):
            geometry = _Plane(geometry.Origin + vector)
        else:
            geometry += vector
        return SimpleNamespace(geometry=geometry)

    @staticmethod
    def Line(start, end):
        return start, end

    @staticmethod
    def Extrude(base_curve, height):
        return {"start_x": base_curve[0], "height": height}


class _IGH(object):
    ghc = _GeometryComponents()

    @staticmethod
    def get_rhino_unit_system_name():
        return "M"


def test_build_uses_absolute_column_index_when_a_grid_column_has_no_elements(monkeypatch):
    module = _load_win_create_types(monkeypatch)
    window_type = module.WindowUnitType(
        _IGH(),
        "Void column",
        _row_heights_m=[1.0],
        _col_widths_m=[1.0, 2.0, 3.0],
    )
    window_type.elements = [
        module.WindowElement(1.0, 1.0, 0, 0),
        module.WindowElement(3.0, 1.0, 2, 0),
    ]

    surfaces, id_data = window_type.build((0.0, 6.0))

    assert [surface["start_x"] for surface in surfaces] == [0.0, 3.0]
    assert [value["col"] for value in id_data.values()] == [0, 2]
