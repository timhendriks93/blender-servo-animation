import unittest
import threading

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
        bpy.context.window_manager.servo_animation.transition_speed = 2
        bpy.context.object.data.bones['Bone'].servo_settings.servo_id = 0
        bpy.context.object.data.bones['Bone'].servo_settings.use_custom_transition_speed = False
        bpy.context.object.data.bones['Bone'].servo_settings.transition_speed = 2
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
        con.connect(f"ws://{self.host}:{self.port}")
        con.send("stop")
        con.close()

        while self.server_thread.is_alive():
            pass

        return self.received_data

    def read_positions(self):
        read_bytes = self.read_bytes()
        positions = []

        assert len(read_bytes) % COMMAND_LENGTH == 0

        for offset in range(0, len(read_bytes), COMMAND_LENGTH):
            position_byte_a = read_bytes[offset + 2]
            position_byte_b = read_bytes[offset + 3]

            assert read_bytes[offset] == COMMAND_START
            assert int.from_bytes(read_bytes[offset + 1], 'big') == 0
            assert read_bytes[offset + 4] == COMMAND_END

            positions.append(int.from_bytes(position_byte_a + position_byte_b, 'big'))

        return positions

    @parameterized.expand([
        ("frame 1", 1, 90, 0),
        ("frame 33", 33, 45, 1),
        ("frame 66", 66, 135, 12),
    ])
    def test_start_stop(self, _name, frame, position, servo_id):
        bpy.context.scene.frame_set(frame)
        bpy.context.object.data.bones['Bone'].servo_settings.servo_id = servo_id

        bpy.ops.servo_animation.start_live_mode(
            'EXEC_DEFAULT',
            method='SOCKET',
            socket_host=self.host,
            socket_port=self.port
        )
        bpy.ops.servo_animation.stop_live_mode('EXEC_DEFAULT')
        bpy.context.scene.frame_set(33)

        read_bytes = self.read_bytes()

        assert len(read_bytes) == COMMAND_LENGTH, f"got {len(read_bytes)}"
        assert read_bytes[0] == COMMAND_START
        assert int.from_bytes(read_bytes[1], 'big') == servo_id
        assert int.from_bytes(read_bytes[2]+read_bytes[3], 'big') == position
        assert read_bytes[4] == COMMAND_END

    @parameterized.expand([
            ('without handling', False, 33, [90, 45], None),
            ('small frame diff keeps direct move', True, 10, [90, 81], None),
            (
                'large frame diff uses global transition speed',
                True,
                33,
                [90, 88, 86, 84, 82, 80, 78, 76, 74, 72, 70, 68, 66, 64, 62, 60, 58, 56, 54, 52, 50, 48, 45],
                2
            ),
            ('large frame diff uses custom transition speed', True, 33, [90, 80, 70, 60, 45], 10),
        ])
    def test_position_jump(self, _name, handling, frame, expected_positions, transition_speed):
        bpy.ops.servo_animation.start_live_mode(
            'EXEC_DEFAULT',
            method='SOCKET',
            socket_host=self.host,
            socket_port=self.port
        )
        bpy.context.window_manager.servo_animation.position_jump_handling = handling
        if transition_speed is not None:
            servo_settings = bpy.context.object.data.bones['Bone'].servo_settings
            servo_settings.use_custom_transition_speed = True
            servo_settings.transition_speed = transition_speed

        bpy.context.scene.frame_set(frame)
        bpy.ops.servo_animation.stop_live_mode('EXEC_DEFAULT')

        positions = self.read_positions()

        assert positions == expected_positions

    @parameterized.expand([
        ("invalid IP", "127.0.0.1234", 80),
        ("invalid port", "127.0.0.1", 1234)
    ])
    def test_invalid_connection(self, _name, socket_host, socket_port):
        raised_exception = False

        try:
            bpy.ops.servo_animation.start_live_mode(
                'EXEC_DEFAULT',
                method='SOCKET',
                socket_host=socket_host,
                socket_port=socket_port
            )
        except RuntimeError:
            raised_exception = True

        assert raised_exception is True
        assert len(self.read_bytes()) == 0
