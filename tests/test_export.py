import unittest
import os
import json
import io
import re

from contextlib import redirect_stdout
from parameterized import parameterized

import bpy

parameters = [
    ("without precision", 0, {
        0: 90,
        11: 78,
        32: 45,
        54: 112,
        65: 135,
        88: 101,
        99: 90,
    }),
    ("with precision", 2, {
        0: 90.0,
        11: 77.7,
        32: 45.0,
        54: 111.67,
        65: 135.0,
        88: 101.08,
        99: 90.0,
    })
]

class TestExport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_dir = os.path.dirname(__file__)
        cls.output_dir = test_dir + "/output"
        os.mkdir(cls.output_dir)

    @classmethod
    def tearDownClass(cls):
        os.rmdir(cls.output_dir)
        bpy.data.armatures['Armature'].bones['Bone'].servo_settings.active = True

    @parameterized.expand(parameters)
    def test_json_export(self, _name, precision, expected):
        export_file = self.output_dir + "/export.json"

        if os.path.exists(export_file):
            os.remove(export_file)

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            bpy.ops.export_anim.servo_positions_json(filepath=export_file, precision=precision)

        assert os.path.exists(export_file), "expected export file to be present"

        with open(export_file, 'r', encoding='utf-8') as file:
            parsed = json.load(file)

        assert parsed["file"] == "simple.blend"
        assert parsed["frames"] == 100
        assert len(parsed["servos"]["0"]["positions"]) == 100

        for frame, exp in expected.items():
            got = parsed["servos"]["0"]["positions"][frame]
            assert exp == got, f"expected position value {exp} for frame {frame}, got {got} instead"

        os.remove(export_file)

    @parameterized.expand(parameters)
    def test_arduino_export(self, _name, precision, expected):
        export_file = self.output_dir + "/export.h"

        if os.path.exists(export_file):
            os.remove(export_file)

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            bpy.ops.export_anim.servo_positions_arduino(filepath=export_file, precision=precision)

        assert os.path.exists(export_file), "expected export file to be present"

        with open(export_file, 'r', encoding='utf-8') as file:
            content = file.read()

        regex = re.compile(r"\{(.+)\}", re.MULTILINE | re.DOTALL)
        match = regex.search(content)

        assert match is not None

        json_string = match.group(0).replace("{\n ", "[").replace(",\n}", "]").replace("\n", "")
        parsed = json.loads(json_string)

        assert "Frames: 100" in content
        assert len(parsed) == 100

        for frame, exp in expected.items():
            got = parsed[frame]
            assert exp == got, f"expected position value {exp} for frame {frame}, got {got} instead"

        os.remove(export_file)

    @parameterized.expand([
        ("arduino", ".h"),
        ("json", ".json")
    ])
    def test_no_servo_settings(self, export_type, extension):
        export_file = self.output_dir + "/export" + extension

        bpy.data.armatures['Armature'].bones['Bone'].servo_settings.active = False

        error_msg = ""

        try:
            if export_type == "arduino":
                bpy.ops.export_anim.servo_positions_arduino(filepath=export_file)
            elif export_type == "json":
                bpy.ops.export_anim.servo_positions_json(filepath=export_file)
        except RuntimeError as error:
            error_msg = str(error)

        assert not os.path.exists(export_file), "did not expect export file to be present"

        exp = (
            f"Operator bpy.ops.export_anim.servo_positions_{export_type}.poll() failed, "
            "context is incorrect"
        )
        got = error_msg
        assert got == exp, f"expected error message '{exp}', got '{got}' instead"
