import os
import pty

def test_live_mode(blender):
    sender, receiver = pty.openpty()
    ttyname = os.ttyname(receiver)
    baud_rate = 115200

    blender.set_file("examples/Simple/example.blend")
    blender.start()
    blender.send_lines([
        "import bpy",
        f"bpy.ops.export_anim.start_live_mode('EXEC_DEFAULT', serial_port='{ttyname}', baud_rate={baud_rate})"
    ])
    blender.expect(f"Opened serial connection for port {ttyname} with baud rate {baud_rate}")
    blender.close()

    read_bytes = []

    os.close(receiver)

    try:
        with os.fdopen(sender, "rb") as reader:
            while len(reader.peek()) > 0:
                byte = reader.read(1)
                read_bytes.append(byte)
    except OSError:
        pass

    assert len(read_bytes) == 5
    assert read_bytes[0] == b"<"
    assert int.from_bytes(read_bytes[1], 'big') == 0
    assert int.from_bytes(read_bytes[2]+read_bytes[3], 'big') == 90
    assert read_bytes[4] == b">"
