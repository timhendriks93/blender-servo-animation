import unittest
import io
import threading

from contextlib import redirect_stdout
from websocket import WebSocket
from parameterized import parameterized
from websockets.sync.server import serve

import bpy

COMMAND_LENGTH = 5
COMMAND_START = b"<"
COMMAND_END = b">"


class TestSocketLiveMode(unittest.TestCase):
    def setUp(self):
        self.received_data = []
        self.server = serve(self.handler, "localhost", 0)
        self.host, self.port = self.server.socket.getsockname()
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.start()

    def tearDown(self):
        self.stop_server()

        bpy.context.window_manager.servo_animation.position_jump_handling = False
        bpy.context.object.data.bones['Bone'].servo_settings.servo_id = 0
        bpy.context.scene.frame_set(1)

    def run_server(self):
        self.server.serve_forever()

    def stop_server(self):
        self.server.shutdown()
        self.server_thread.join()

    def handler(self, socket):
        for message in socket:
            if message == "stop":
                self.stop_server()
                break

            for integer in message:
                byte = integer.to_bytes(length=1, byteorder='big')
                self.received_data.append(byte)

    def read_bytes(self):
        con = WebSocket()
        con.connect(f"ws://{self.host}:{self.port}/ws")
        con.send("stop")
        con.close()

        while self.server_thread.is_alive():
            pass

        return self.received_data

    @parameterized.expand([
        ("frame 1", 1, 90, 0),
        ("frame 33", 33, 45, 1),
        ("frame 66", 66, 135, 12),
    ])
    def test_start_stop(self, _name, frame, position, servo_id):
        bpy.context.scene.frame_set(frame)
        bpy.context.object.data.bones['Bone'].servo_settings.servo_id = servo_id

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            bpy.ops.export_anim.live_mode(
                'EXEC_DEFAULT',
                method='SOCKET',
                socket_host=self.host,
                socket_port=self.port
            )
            bpy.ops.export_anim.stop_live_mode('EXEC_DEFAULT')
            bpy.context.scene.frame_set(33)

        read_bytes = self.read_bytes()

        assert len(read_bytes) == COMMAND_LENGTH, f"got {len(read_bytes)}"
        assert read_bytes[0] == COMMAND_START
        assert int.from_bytes(read_bytes[1], 'big') == servo_id
        assert int.from_bytes(read_bytes[2]+read_bytes[3], 'big') == position
        assert read_bytes[4] == COMMAND_END

    @parameterized.expand([
            ('without handling', False, 20, 33, [90, 45]),
            ('threshold reached', True, 20, 33, range(90, 44, -1)),
            ('threshold not reached - small frame jump', True, 20, 10, [90, 81]),
            ('threshold not reached - increased threshold', True, 50, 33, [90, 45]),
        ])
    def test_position_jump(self, _name, handling, threshold, frame, positions):
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            bpy.ops.export_anim.live_mode(
                'EXEC_DEFAULT',
                method='SOCKET',
                socket_host=self.host,
                socket_port=self.port
            )
            bpy.context.window_manager.servo_animation.position_jump_handling = handling
            bpy.context.window_manager.servo_animation.position_jump_threshold = threshold
            bpy.context.scene.frame_set(frame)
            bpy.ops.export_anim.stop_live_mode('EXEC_DEFAULT')

        read_bytes = self.read_bytes()

        exp = len(positions) * COMMAND_LENGTH
        got = len(read_bytes)
        assert exp == got, f"expected {exp} bytes, got {got} instead"

        for i, position in enumerate(positions):
            offset = i * COMMAND_LENGTH
            position_byte_a = read_bytes[offset + 2]
            position_byte_b = read_bytes[offset + 3]

            assert read_bytes[offset] == COMMAND_START
            assert int.from_bytes(read_bytes[offset + 1], 'big') == 0
            assert int.from_bytes(position_byte_a+position_byte_b, 'big') == position
            assert read_bytes[offset + 4] == COMMAND_END

    @parameterized.expand([
        ("invalid IP", "127.0.0.1234", 80),
        ("invalid port", "127.0.0.1", 1234)
    ])
    def test_invalid_connection(self, _name, socket_host, socket_port):
        raised_exception = False

        stdout = io.StringIO()
        with redirect_stdout(stdout):
            try:
                bpy.ops.export_anim.live_mode(
                    'EXEC_DEFAULT',
                    method='SOCKET',
                    socket_host=socket_host,
                    socket_port=socket_port
                )
            except RuntimeError:
                raised_exception = True

        assert raised_exception is True
        assert len(self.read_bytes()) == 0
