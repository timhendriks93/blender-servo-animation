import unittest
import os
import json
import re
import shutil

from parameterized import parameterized

import bpy

positions = {
    "without_precision": {
        0: 90,
        11: 78,
        32: 45,
        54: 112,
        65: 135,
        88: 101,
        99: 90,
    },
    "with_precision": {
        0: 90.0,
        11: 77.7,
        32: 45.0,
        54: 111.67,
        65: 135.0,
        88: 101.08,
        99: 90.0,
    }
}

class TestExport(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        self.output_dir = test_dir + "/output"
        os.mkdir(self.output_dir)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        bpy.data.armatures['Armature'].bones['Bone'].servo_settings.active = True

    @parameterized.expand([
        ("without precision", 0, positions["without_precision"]),
        ("with precision", 2, positions["with_precision"])
    ])
    def test_json_export(self, _name, precision, expected):
        export_file = self.output_dir + "/export.json"

        if os.path.exists(export_file):
            os.remove(export_file)

        bpy.ops.export_anim.servo_animation_json(filepath=export_file, precision=precision)

        assert os.path.exists(export_file), "expected export file to be present"

        with open(export_file, 'r', encoding='utf-8') as file:
            parsed = json.load(file)

        assert parsed["file"] == "test.blend"
        assert parsed["frames"] == 100
        assert parsed["scene"] == "Scene"
        assert len(parsed["servos"]["0"]["positions"]) == 100

        for frame, exp in expected.items():
            got = parsed["servos"]["0"]["positions"][frame]
            assert exp == got, f"expected position value {exp} for frame {frame}, got {got} instead"

        os.remove(export_file)

    @parameterized.expand([
        ("without precision", 0, positions["without_precision"], False),
        ("with precision", 2, positions["with_precision"], False),
        ("namespace", 0, positions["without_precision"], True),
    ])
    def test_arduino_export(self, _name, precision, expected, namespace):
        export_file = self.output_dir + "/export.h"

        if os.path.exists(export_file):
            os.remove(export_file)

        bpy.ops.export_anim.servo_animation_arduino(
            filepath=export_file,
            precision=precision,
            namespace=namespace
        )

        assert os.path.exists(export_file), "expected export file to be present"

        with open(export_file, 'r', encoding='utf-8') as file:
            content = file.read()

        regex = re.compile(r"\= \{(.+?)\}", re.MULTILINE | re.DOTALL)
        match = regex.search(content)

        assert match is not None

        json_string = match.group(0).replace("= {\n ", "[").replace(",\n}", "]").replace("\n", "")
        parsed = json.loads(json_string)

        assert "const byte FPS = 30;" in content
        assert "const int FRAMES = 100;" in content
        assert len(parsed) == 100

        if namespace:
            assert "namespace Scene" in content
        else:
            assert "namespace Scene" not in content

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
                bpy.ops.export_anim.servo_animation_arduino(filepath=export_file)
            elif export_type == "json":
                bpy.ops.export_anim.servo_animation_json(filepath=export_file)
        except RuntimeError as error:
            error_msg = str(error)

        assert not os.path.exists(export_file), "did not expect export file to be present"

        exp = (
            f"Operator bpy.ops.export_anim.servo_animation_{export_type}.poll() failed, "
            "context is incorrect"
        )
        got = error_msg
        assert got == exp, f"expected error message '{exp}', got '{got}' instead"

if __name__ == '__main__':
    unittest.main()
