# pylint: disable=import-outside-toplevel, broad-exception-caught

import time
import math
import bpy

from ..utils.servo_settings import get_active_pose_bones
from ..utils.converter import calculate_position

class LiveMode:
    COMMAND_START = 0x3C
    COMMAND_END = 0x3E

    METHOD_SERIAL = "SERIAL"
    METHOD_SOCKET = "SOCKET"

    STEP_DURATION_BASE = .3

    _last_positions = {}
    _connection = None
    _handler_enabled = True

    @classmethod
    def set_connection(cls, connection):
        cls._connection = connection

    @classmethod
    def is_connected(cls):
        import serial
        import websocket

        method = bpy.context.window_manager.servo_animation.live_mode_method

        if method == LiveMode.METHOD_SERIAL:
            return (
                isinstance(cls._connection, serial.Serial)
                and cls._connection.is_open
                and (
                    cls._connection.port in cls.get_serial_ports()
                    or bpy.app.background
                )
            )

        if method == LiveMode.METHOD_SOCKET:
            return (
                isinstance(cls._connection, websocket.WebSocket)
                and cls._connection.connected
            )

        return False

    @classmethod
    def is_handler_enabled(cls):
        return cls._handler_enabled

    @classmethod
    def enable_handler(cls):
        cls._handler_enabled = True

    @classmethod
    def disable_handler(cls):
        cls._handler_enabled = False

    @classmethod
    def get_serial_ports(cls):
        from serial.tools import list_ports

        ports = []

        for port in list_ports.comports():
            ports.append(port.device)

        return ports

    @classmethod
    def get_last_position(cls, servo_id):
        if servo_id in cls._last_positions:
            return cls._last_positions[servo_id]

        return None

    @classmethod
    def handler(cls, _scene, _depsgraph):
        if not cls.is_handler_enabled():
            return

        cls.disable_handler()

        threshold_exceeded = False
        target_positions = []
        servo_animation = bpy.context.window_manager.servo_animation

        for pose_bone in get_active_pose_bones(bpy.context.scene):
            position, _angle, in_range = calculate_position(pose_bone)

            if not in_range:
                continue

            servo_settings = pose_bone.bone.servo_settings
            servo_id = servo_settings.servo_id
            step = round(servo_settings.threshold / 10)
            target_positions.append((servo_id, position, step))

            if (
                servo_id in cls._last_positions
                and abs(position - cls._last_positions[servo_id]) > servo_settings.threshold
            ):
                threshold_exceeded = True

        if (servo_animation.position_jump_handling and threshold_exceeded):
            cls.handle_position_jump(target_positions)
        else:
            cls.handle_default(target_positions)

        cls.enable_handler()

    @classmethod
    def handle_default(cls, target_positions):
        for servo_id, position, _step in target_positions:
            cls.send_position(servo_id, position)

    @classmethod
    def handle_position_jump(cls, target_positions):
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)

        abs_steps = 0

        for servo_id, position, step in target_positions:
            diff = abs(position - cls._last_positions[servo_id])
            steps = math.ceil(diff / step)
            abs_steps = max(abs_steps, steps)

        window_manager = bpy.context.window_manager
        window_manager.progress_begin(0, abs_steps)

        for abs_step in range(abs_steps):
            window_manager.progress_update(abs_step)

            for servo_id, position, step in target_positions:
                new_position = cls._last_positions[servo_id]

                if position == new_position:
                    continue

                if position > new_position:
                    new_position += step
                else:
                    new_position -= step

                if abs(position - new_position) < step:
                    new_position = position

                cls.send_position(servo_id, new_position)

            time.sleep(.01)

        window_manager.progress_end()

    @classmethod
    def send_position(cls, servo_id, position):
        if position == cls._last_positions.get(servo_id):
            return

        command = [cls.COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [cls.COMMAND_END]

        servo_animation = bpy.context.window_manager.servo_animation

        try:
            if servo_animation.live_mode_method == LiveMode.METHOD_SERIAL:
                cls._connection.write(command)
            elif servo_animation.live_mode_method == LiveMode.METHOD_SOCKET:
                cls._connection.send_binary(bytes(command))

            cls._last_positions[servo_id] = position
        except Exception:
            bpy.ops.servo_animation.stop_live_mode(unexpected=True)

    @classmethod
    def close_connection(cls):
        cls._last_positions = {}

        if cls._connection:
            cls._connection.close()
