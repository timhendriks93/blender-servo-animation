import unittest
import os

from parameterized import parameterized

import bpy

COMMAND_LENGTH = 5
COMMAND_START = b"<"
COMMAND_END = b">"


class TestSerialLiveMode(unittest.TestCase):
    def setUp(self):
        self.receiver, self.sender = os.openpty()
        self.ttyname = os.ttyname(self.sender)

    def tearDown(self):
        try:
            os.close(self.sender)
            os.close(self.receiver)
        except OSError:
            pass

        bpy.context.window_manager.servo_animation.position_jump_handling = False
        bpy.context.window_manager.servo_animation.transition_speed = 2
        bpy.context.object.data.bones['Bone'].servo_settings.servo_id = 0
        bpy.context.object.data.bones['Bone'].servo_settings.use_custom_transition_speed = False
        bpy.context.object.data.bones['Bone'].servo_settings.transition_speed = 2
        bpy.context.scene.frame_set(1)

    def read_bytes(self):
        read_bytes = []

        try:
            os.close(self.sender)
            with os.fdopen(self.receiver, "rb") as reader:
                while len(reader.peek()) > 0:
                    byte = reader.read(1)
                    read_bytes.append(byte)
        except OSError:
            pass

        return read_bytes

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
        ("115200 baud rate", 115200, 1, 90, 0),
        ("19200 baud rate", 19200, 33, 45, 1),
        ("192500 baud rate", 192500, 66, 135, 12),
    ])
    def test_start_stop(self, _name, baud_rate, frame, position, servo_id):
        bpy.context.scene.frame_set(frame)
        bpy.context.object.data.bones['Bone'].servo_settings.servo_id = servo_id

        bpy.ops.servo_animation.start_live_mode(
            'EXEC_DEFAULT',
            method='SERIAL',
            serial_port=self.ttyname,
            serial_baud=baud_rate
        )
        bpy.ops.servo_animation.stop_live_mode('EXEC_DEFAULT')
        bpy.context.scene.frame_set(33)

        read_bytes = self.read_bytes()

        assert len(read_bytes) == COMMAND_LENGTH
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
            method='SERIAL',
            serial_port=self.ttyname,
            serial_baud=115200
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
        ("invalid serial port", "/dev/ttyInvalid", 115200),
        ("invalid baud rate", None, -1),
    ])
    def test_invalid_serial_port(self, _name, serial_port, baud_rate):
        if serial_port is None:
            serial_port = self.ttyname

        raised_exception = False

        try:
            bpy.ops.servo_animation.start_live_mode(
                'EXEC_DEFAULT',
                method='SERIAL',
                serial_port=serial_port,
                serial_baud=baud_rate
            )
        except RuntimeError:
            raised_exception = True

        assert raised_exception is True
        assert len(self.read_bytes()) == 0
