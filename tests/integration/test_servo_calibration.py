import unittest
import os

from parameterized import parameterized

import bpy

COMMAND_LENGTH = 5


class TestServoCalibration(unittest.TestCase):
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
        bpy.context.object.data.bones['Bone'].servo_settings.position_min = 0
        bpy.context.object.data.bones['Bone'].servo_settings.position_max = 180

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

    @parameterized.expand([
        ("without handling", False, 45, 135, 4),
        ("threshold reached", True, 45, 135, 25),
        ("threshold not reached", True, 80, 110, 4),
    ])
    def test_calibration(self, _name, handling, position_min, position_max, commands):
        servo_settings = bpy.context.object.data.bones['Bone'].servo_settings

        bpy.context.window_manager.servo_animation.position_jump_handling = handling

        assert servo_settings.position_min == 0
        assert servo_settings.position_max == 180

        bpy.ops.servo_animation.start_live_mode(
            'EXEC_DEFAULT',
            method='SERIAL',
            serial_port=self.ttyname,
            serial_baud=115200
        )
        bpy.ops.servo_animation.calibrate(
            'EXEC_DEFAULT',
            position_min=position_min,
            position_max=position_max
        )
        bpy.ops.servo_animation.stop_live_mode('EXEC_DEFAULT')

        assert servo_settings.position_min == position_min
        assert servo_settings.position_max == position_max

        read_bytes = self.read_bytes()

        assert len(read_bytes) == commands * COMMAND_LENGTH
