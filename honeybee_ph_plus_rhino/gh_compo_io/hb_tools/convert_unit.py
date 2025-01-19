# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""GHCompo Interface: HBPH - Clean Input Breps."""

try:
    from typing import Any
except ImportError:
    pass  # IronPython 2.7

try:
    from honeybee_ph_rhino import gh_io
except ImportError as e:
    raise ImportError("Failed to import honeybee_ph_rhino:\n\t{}".format(e))

try:
    from ph_units.converter import convert, unit_type_dict, validate_unit_type
    from ph_units.parser import parse_input
except ImportError as e:
    raise ImportError("Failed to import ph_units:\n\t{}".format(e))


class GHCompo_ConvertValueToUnit(object):

    def __init__(self, _IGH, _in, *args, **kwargs):
        # type: (gh_io.IGH, str, *Any, **Any) -> None
        self.IGH = _IGH
        self._in = _in

    @property
    def ready(self):
        # type: () -> bool
        if self._in is None:
            return False
        return True

    def find_delimiter(self, _in):
        # type: (str) -> str | None
        # check for 'x to y' or 'x as y' ...

        if " to " in _in:
            return " to "
        elif " as " in _in:
            return " as "
        else:
            return None

    def find_input_string_parts(self, _input):
        # type: (str) -> tuple[str, str | None, str | None]
        """Return a tuple of the 'input value', 'input unit', and 'target unit' from an input string.

        The input string is assumed to use 'as' or 'in' as the separator between the input
        value and the target unit. No cleanup is done on the substring parts returned.

        example:
            * "45.6 M to cm" -> (45.6, 'M', 'cm')
            * "12.5 "Btu/hr-ft2-F to W/M2-K" -> (12.5, 'Btu/hr-ft2-F', 'W/M2-K')
        """

        delimiter = self.find_delimiter(_input.strip())
        a, b = _input.split(delimiter)
        input_value, input_unit = parse_input(a)
        target_unit = validate_unit_type(b)
        return input_value, input_unit, target_unit

    def run(self):
        # type: () -> int | float | str | None
        if not self.ready:
            msg = "\n".join(["Valid unit types:"] + sorted(unit_type_dict.keys()))
            self.IGH.remark(msg)
            return msg

        # -- Get the input string parts
        try:
            input_value, input_unit, output_unit = self.find_input_string_parts(self._in)
        except Exception as e:
            self.IGH.remark(str(e))
            return str(e)
        if input_unit is None or output_unit is None:
            return None
        elif str(input_value) == "0":
            return 0

        # -- Convert the input value
        result_value = convert(input_value, input_unit, output_unit)
        if result_value is None:
            return None

        # -- Package the results
        msg = "Converting {:,.3f} from {} to {:,.3f} {}.".format(
            float(input_value), input_unit, float(result_value), output_unit
        )
        self.IGH.remark(msg)
        return result_value
