import json
import os


def test_json_export(blender):
    export_file = blender.tmp("/tests/tmp/test.json")

    if os.path.exists(export_file):
        os.remove(export_file)

    assert not os.path.exists(export_file)

    blender.set_file("examples/Simple/example.blend")
    blender.start()
    blender.send_lines([
        "import bpy",
        f"bpy.ops.export_anim.servo_positions_json(filepath='{export_file}')"
    ])
    blender.expect("{'FINISHED'}")
    blender.close()

    assert os.path.exists(export_file), "expected export file to be present"

    with open(export_file, 'r', encoding='utf-8') as file:
        parsed = json.load(file)

    assert parsed["file"] == "example.blend"
    assert parsed["frames"] == 100
    assert len(parsed["positions"]["Bone"]) == 100
    assert parsed["positions"]["Bone"][0] == 90
    assert parsed["positions"]["Bone"][32] == 45
    assert parsed["positions"]["Bone"][65] == 135
    assert parsed["positions"]["Bone"][99] == 90

    os.remove(export_file)


def test_json_arduino(blender):
    export_file = blender.tmp("/tests/tmp/test.h")

    if os.path.exists(export_file):
        os.remove(export_file)

    assert not os.path.exists(export_file)

    blender.set_file("examples/Simple/example.blend")
    blender.start()
    blender.send_lines([
        "import bpy",
        f"bpy.ops.export_anim.servo_positions_arduino(filepath='{export_file}')"
    ])
    blender.expect("{'FINISHED'}")
    blender.close()

    assert os.path.exists(export_file), "expected export file to be present"

    os.remove(export_file)
