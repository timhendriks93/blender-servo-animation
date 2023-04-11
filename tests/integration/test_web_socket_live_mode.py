import time
import pytest

COMMAND_LENGTH = 5
COMMAND_START = b"<"
COMMAND_END = b">"


@pytest.mark.parametrize(
    "frame, position, servo_id",
    [
        (1, 90, 0),
        (33, 45, 1),
        (66, 135, 12),
    ],
    ids=['Frame 1', 'Frame 33', 'Frame 66']
)
def test_start_stop(blender, socket_stub, frame, position, servo_id):
    host = socket_stub.host
    port = socket_stub.port
    blender.set_file("examples/Simple/simple.blend")
    blender.start()
    blender.send_lines([
        "import bpy",
        f"bpy.context.scene.frame_set({frame})",
        f"bpy.data.armatures['Armature'].bones['Bone'].servo_settings.servo_id = {servo_id}",
        "".join((
            "bpy.ops.export_anim.live_mode(",
            f"'EXEC_DEFAULT', method='WEB_SOCKET', socket_host='{host}', socket_port={port}",
            ")"
        ))
    ])
    blender.expect(f"Opened web socket connection with host {host} on port {port}")
    blender.send_line("bpy.ops.export_anim.stop_live_mode('EXEC_DEFAULT', method='WEB_SOCKET')")
    blender.expect(f"Closed web socket connection with host {host} and port {port}")
    blender.send_line("bpy.context.scene.frame_set(33)")
    blender.close()

    read_bytes = socket_stub.received_data

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
def test_position_jump_handling(blender, socket_stub, handling, threshold, frame, positions):
    host = socket_stub.host
    port = socket_stub.port
    blender.set_file("examples/Simple/simple.blend")
    blender.start()
    blender.send_lines([
        "import bpy",
        "".join((
            "bpy.ops.export_anim.live_mode(",
            f"'EXEC_DEFAULT', method='WEB_SOCKET', socket_host='{host}', socket_port={port}",
            ")"
        ))
    ])
    blender.expect(f"Opened web socket connection with host {host} on port {port}")
    blender.send_lines([
        f"bpy.context.window_manager.servo_animation.position_jump_handling = {handling}",
        f"bpy.context.window_manager.servo_animation.position_jump_threshold = {threshold}",
        f"bpy.context.scene.frame_set({frame})"
    ])
    time.sleep(.5)
    blender.close()

    read_bytes = socket_stub.received_data

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
    "socket_host, socket_port",
    [
        ("127.0.0.1234", 80),
        ("127.0.0.1", 1234)
    ],
    ids=['Invalid IP', 'Invalid port']
)
def test_invalid_connection(blender, socket_host, socket_port):
    blender.set_file("examples/Simple/simple.blend")
    blender.start()
    blender.send_lines([
        "import bpy",
        "".join((
            "bpy.ops.export_anim.live_mode(",
            f"'EXEC_DEFAULT', method='WEB_SOCKET', socket_host='{socket_host}', socket_port={socket_port}",
            ")"
        ))
    ])
    blender.expect(f"Failed to open web socket connection with host {socket_host} on port {socket_port}")
    blender.close()
