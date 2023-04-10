import time
import pytest

COMMAND_LENGTH = 5
COMMAND_START = b"<"
COMMAND_END = b">"


@pytest.mark.parametrize(
    "baud_rate, frame, position, servo_id",
    [
        (115200, 1, 90, 0),
        (19200, 33, 45, 1),
        (192500, 66, 135, 12),
    ],
    ids=['115200 baud rate', '19200 baud rate', '192500 baud rate']
)
def test_start_stop(blender, serial_stub, baud_rate, frame, position, servo_id):
    tty_name = serial_stub.open()

    blender.set_file("examples/Simple/simple.blend")
    blender.start()
    blender.send_lines([
        "import bpy",
        f"bpy.context.scene.frame_set({frame})",
        f"bpy.data.armatures['Armature'].bones['Bone'].servo_settings.servo_id = {servo_id}",
        "".join((
            "bpy.ops.export_anim.start_serial_live_mode(",
            f"'EXEC_DEFAULT', serial_port='{tty_name}', baud_rate={baud_rate}",
            ")"
        ))
    ])
    blender.expect(f"Opened serial connection on port {tty_name} with baud rate {baud_rate}")
    blender.send_line("bpy.ops.export_anim.stop_live_mode()")
    blender.expect(f"Closed serial connection on port {tty_name}")
    blender.send_line("bpy.context.scene.frame_set(33)")
    blender.close()

    read_bytes = serial_stub.read_bytes()

    assert len(read_bytes) == COMMAND_LENGTH
    assert read_bytes[0] == COMMAND_START
    assert int.from_bytes(read_bytes[1], 'big') == servo_id
    assert int.from_bytes(read_bytes[2]+read_bytes[3], 'big') == position
    assert read_bytes[4] == COMMAND_END


@pytest.mark.parametrize(
    "handling, threshold, frame, positions",
    [
        (False, 20, 33, [90, 45]),
        (True, 20, 33, range(90, 44, -1)),
        (True, 20, 10, [90, 81]),
        (True, 50, 33, [90, 45]),
    ],
    ids=[
        'Without handling',
        'Threshold reached',
        'Threshold not reached - small frame jump',
        'Threshold not reached - increased threshold'
    ]
)
def test_position_jump_handling(blender, serial_stub, handling, threshold, frame, positions):
    tty_name = serial_stub.open()
    baud_rate = 115200

    blender.set_file("examples/Simple/simple.blend")
    blender.start()
    blender.send_lines([
        "import bpy",
        "".join((
            "bpy.ops.export_anim.start_serial_live_mode(",
            f"'EXEC_DEFAULT', serial_port='{tty_name}', baud_rate={baud_rate}",
            ")"
        ))
    ])
    blender.expect(f"Opened serial connection on port {tty_name} with baud rate {baud_rate}")
    blender.send_lines([
        f"bpy.context.window_manager.servo_animation.position_jump_handling = {handling}",
        f"bpy.context.window_manager.servo_animation.position_jump_threshold = {threshold}",
        f"bpy.context.scene.frame_set({frame})"
    ])
    time.sleep(.5)
    blender.close()

    read_bytes = serial_stub.read_bytes()

    assert len(read_bytes) == len(positions) * COMMAND_LENGTH

    for i, position in enumerate(positions):
        offset = i * COMMAND_LENGTH
        position_byte_a = read_bytes[offset + 2]
        position_byte_b = read_bytes[offset + 3]

        assert read_bytes[offset] == COMMAND_START
        assert int.from_bytes(read_bytes[offset + 1], 'big') == 0
        assert int.from_bytes(position_byte_a+position_byte_b, 'big') == position
        assert read_bytes[offset + 4] == COMMAND_END


@pytest.mark.parametrize(
    "serial_port, baud_rate",
    [
        ("/dev/ttyInvalid", 115200),
        (None, -1),
    ],
    ids=['Invalid serial port', 'Invalid baud rate']
)
def test_invalid_serial_port(blender, serial_stub, serial_port, baud_rate):
    tty_name = serial_stub.open()

    if serial_port is None:
        serial_port = tty_name

    blender.set_file("examples/Simple/simple.blend")
    blender.start()
    blender.send_lines([
        "import bpy",
        "".join((
            "bpy.ops.export_anim.start_serial_live_mode(",
            f"'EXEC_DEFAULT', serial_port='{serial_port}', baud_rate={baud_rate}",
            ")"
        ))
    ])
    blender.expect(f"Failed to open serial connection on port {serial_port} with baud rate {baud_rate}")
    blender.close()

    assert len(serial_stub.read_bytes()) == 0
