def test_servo_settings_active(blender):
    blender.set_file("examples/Simple/example.blend")
    blender.set_script("servo_settings_active.py")

    assert blender.run() == 0, "expected status code to be 0"
