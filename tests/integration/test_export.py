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
         "d9daf933670642efc973b2cf2a44516630a0c31a7b11ca64cc7668d64b550cb8"),
        ("without skipping and indent of 2", False, "2",
         "1815631c5f69b09af4db932b14af502b723072e7cebf72a7a5d47512dfaf0dac"),
        ("with skipping and no indent", True, "None",
         "69ca1146a3d51aec9ce899d1500a8766b57208f169428186413f6db7931b93c5"),
        ("with skipping and indent of 4", True, "4",
         "163b928792a3cf9aae4e080ab21272d9c2e8ff6a45fce33f81c7ae4ecba59740")
    ])
    def test_json_export(self, _name, skip_duplicates, indent, expected):
        export_file = self.output_dir + "/export.json"

        bpy.ops.export_anim.servo_animation_json(
            filepath=export_file, skip_duplicates=skip_duplicates, indent=indent)

        assert_file_hash(export_file, expected)

    @parameterized.expand([
        ("with skipping and no namespace", True, False,
         "91f67d84a30e52f6c1f985c392596fc492d8441691becf118fb76c91f54b192d"),
        ("without skipping and no namespace", False, False,
         "ea0159399d5256392e193271e5458bb5537fec7b5cd392b5a0eb83c329ec22d5"),
        ("with skipping and namespace", True, True,
         "3339a271a3f5adad5ab4d9c24b41c390a49f7bae640be98cd3322e8dfd6e35fc"),
        ("without skipping and namespace", False, True,
         "eba932e01ee399807ac580eeb60ffad6280f7d7d7ec66610769514eedbf89aae")
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
