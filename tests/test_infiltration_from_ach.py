from __future__ import absolute_import

import importlib.util
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


def _load_infiltration_from_ach(monkeypatch):
    honeybee_boundarycondition = ModuleType("honeybee.boundarycondition")
    honeybee_boundarycondition.Ground = type("Ground", (object,), {})
    honeybee_boundarycondition.Outdoors = type("Outdoors", (object,), {})
    honeybee_face = ModuleType("honeybee.face")
    honeybee_face.Face = type("Face", (object,), {})
    honeybee_room = ModuleType("honeybee.room")
    honeybee_room.Room = type("Room", (object,), {})

    honeybee_energy_boundarycondition = ModuleType("honeybee_energy.boundarycondition")
    honeybee_energy_boundarycondition.Adiabatic = type("Adiabatic", (object,), {})

    honeybee_ph_room = ModuleType("honeybee_ph.properties.room")
    honeybee_ph_room.RoomPhProperties = type("RoomPhProperties", (object,), {})
    honeybee_ph_space = ModuleType("honeybee_ph.space")
    honeybee_ph_space.Space = type("Space", (object,), {})

    component_io = ModuleType("ph_gh_component_io")
    component_io.gh_io = SimpleNamespace(IGH=object)

    converter = ModuleType("ph_units.converter")
    converter.convert = lambda value, _from_unit, _to_unit: value

    monkeypatch.setitem(sys.modules, "honeybee.boundarycondition", honeybee_boundarycondition)
    monkeypatch.setitem(sys.modules, "honeybee.face", honeybee_face)
    monkeypatch.setitem(sys.modules, "honeybee.room", honeybee_room)
    monkeypatch.setitem(sys.modules, "honeybee_energy.boundarycondition", honeybee_energy_boundarycondition)
    monkeypatch.setitem(sys.modules, "honeybee_ph.properties.room", honeybee_ph_room)
    monkeypatch.setitem(sys.modules, "honeybee_ph.space", honeybee_ph_space)
    monkeypatch.setitem(sys.modules, "ph_gh_component_io", component_io)
    monkeypatch.setitem(sys.modules, "ph_units.converter", converter)

    path = (
        Path(__file__).parents[1] / "honeybee_ph_plus_rhino" / "gh_compo_io" / "hb_tools" / "infiltration_from_ach.py"
    )
    spec = importlib.util.spec_from_file_location("infiltration_from_ach_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _IGH(object):
    @staticmethod
    def get_rhino_volume_unit_name():
        return "M3"

    @staticmethod
    def get_rhino_areas_unit_name():
        return "M2"

    def error(self, message):
        raise AssertionError(message)


def _component(module):
    outdoors = module.Outdoors()
    room = SimpleNamespace(
        display_name="Test Room",
        faces=[SimpleNamespace(area=260.0, boundary_condition=outdoors)],
        properties=SimpleNamespace(ph=SimpleNamespace(spaces=[SimpleNamespace(net_volume=300.0)])),
    )
    return module.GHCompo_CalculateInfiltrationFromACH(_IGH(), 1.0, [room])


def test_output_pressure_ratio(monkeypatch):
    """The two outputs differ only by the power-law pressure correction."""
    module = _load_infiltration_from_ach(monkeypatch)

    at_4Pa, at_50Pa = _component(module).run()

    assert at_50Pa / at_4Pa == pytest.approx((50.0 / 4.0) ** 0.65, rel=1e-6)


def test_outputs_are_normalized_by_exposed_envelope_area(monkeypatch):
    module = _load_infiltration_from_ach(monkeypatch)

    at_4Pa, at_50Pa = _component(module).run()

    expected_at_50Pa = (1.0 * 300.0 / 3600.0) / 260.0
    assert at_50Pa == pytest.approx(expected_at_50Pa)
    assert at_4Pa == pytest.approx(expected_at_50Pa * (4.0 / 50.0) ** 0.65)
