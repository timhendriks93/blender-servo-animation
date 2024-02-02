import unittest
import os
import shutil
import hashlib

from parameterized import parameterized

import bpy


def assert_file_hash(file_path, expected):
    assert os.path.exists(
        file_path), "expected export file to be present"

    hash_object = hashlib.sha256()

    with open(file_path, "rb") as file:
        hash_object.update(file.read())

    file_hash = hash_object.hexdigest()

    assert file_hash == expected, f"expected file has to be {expected}, got {file_hash} instead"


class TestExport(unittest.TestCase):
    def setUp(self):
        test_dir = os.path.dirname(__file__)
        self.output_dir = test_dir + "/output"
        shutil.rmtree(self.output_dir, ignore_errors=True)
        os.mkdir(self.output_dir)

    def tearDown(self):
        shutil.rmtree(self.output_dir, ignore_errors=True)
        bpy.data.armatures['Armature'].bones['Bone'].servo_settings.active = True

    @parameterized.expand([
        ("with skipping and indent of 2", True, "2",
         "7576d368e9680a35a67a62df0200f08fd310e0f830e1497f8f12a3138e5ff24b"),
        ("without skipping and indent of 2", False, "2",
         "f96d14717222b184740f4258842f766eee341f0768eac42c44a4efd8e45f5814"),
        ("with skipping and no indent", True, "None",
         "88b4da9ceee71fbbe75f1f0f73727b69bc8b6ba21358a86932efb41ab5b1a1e6"),
        ("with skipping and indent of 4", True, "4",
         "87f25f8fab6a8996393a0e277d6e2891c70194d24c8283bf937097970c5033c8")
    ])
    def test_json_export(self, _name, skip_duplicates, indent, expected):
        export_file = self.output_dir + "/export.json"

        bpy.ops.export_anim.servo_animation_json(
            filepath=export_file, skip_duplicates=skip_duplicates, indent=indent)

        assert_file_hash(export_file, expected)

    @parameterized.expand([
        ("with skipping and no namespace", True, False,
         "5b8b6abd5ae925a394020dcfe2341705c74a3b1f2dd3a2a5230d73e56b85b4c5"),
        ("without skipping and no namespace", False, False,
         "38d458c7061ca3d252da01995199e7f23e646e9889d5b4a6609328fa57b9a237"),
        ("with skipping and namespace", True, True,
         "fc3e0c39b24bc2147c56d6cc3f65181839478e0df54b0b580328f50b0587a6d1"),
        ("without skipping and namespace", False, True,
         "e1abc66c2dc73bb13828c83bbd30c8967a1a0bb346a01ad542d5e74321b68e2a")
    ])
    def test_arduino_export(self, _name, skip_duplicates, namespace, expected):
        export_file = self.output_dir + "/export.h"

        bpy.ops.export_anim.servo_animation_arduino(
            filepath=export_file,
            skip_duplicates=skip_duplicates,
            namespace=namespace
        )

        assert_file_hash(export_file, expected)

    @parameterized.expand([
        ("with skipping", True,
         "f6d5d5b3e0012e63e28b51bfe7416ffebf9517b67e4a873f947ff1c998a4a512"),
        ("without skipping", False,
         "11f06c27463865d5e6a4f014c515a01c1c0212c413d0434698908a562c13237f")
    ])
    def test_binary_export(self, _name, skip_duplicates, expected):
        export_file = self.output_dir + "/export.bin"

        bpy.ops.export_anim.servo_animation_binary(
            filepath=export_file,
            skip_duplicates=skip_duplicates
        )

        assert_file_hash(export_file, expected)

    @parameterized.expand([
        ("arduino", ".h"),
        ("json", ".json"),
        ("binary", ".bin")
    ])
    def test_no_servo_settings(self, export_type, extension):
        export_file = self.output_dir + "/export" + extension

        bpy.data.armatures['Armature'].bones['Bone'].servo_settings.active = False

        error_msg = ""

        try:
            if export_type == "arduino":
                bpy.ops.export_anim.servo_animation_arduino(
                    filepath=export_file)
            elif export_type == "json":
                bpy.ops.export_anim.servo_animation_json(filepath=export_file)
            elif export_type == "binary":
                bpy.ops.export_anim.servo_animation_binary(
                    filepath=export_file)
        except RuntimeError as error:
            error_msg = str(error)

        assert not os.path.exists(
            export_file), "did not expect export file to be present"

        exp = (
            f"Operator bpy.ops.export_anim.servo_animation_{export_type}.poll() failed, "
            "context is incorrect"
        )
        got = error_msg
        assert got == exp, f"expected error message '{exp}', got '{got}' instead"


if __name__ == '__main__':
    unittest.main()
