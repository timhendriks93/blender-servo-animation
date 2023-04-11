import time
import socket
import bpy
import serial

from bpy.types import Operator

from ..utils.converter import calculate_position
from ..utils.servo_settings import get_active_pose_bones
from ..utils.uart import get_serial_ports


class LiveMode(Operator):
    bl_idname = "export_anim.live_mode"
    bl_label = "Live Mode Handling"
    bl_options = {'INTERNAL', 'BLOCKING'}

    COMMAND_START = 0x3C
    COMMAND_END = 0x3E

    METHOD_SERIAL = "SERIAL"
    METHOD_WEB_SOCKET = "WEB_SOCKET"

    _positions = {}
    _handling = False

    serial_connection = None
    tcp_connection = None

    @classmethod
    def poll(cls, context):
        return context.window_manager.servo_animation.live_mode

    @classmethod
    def handler(cls, _scene, _depsgraph):
        if cls._handling:
            return

        cls._handling = True
        bpy.ops.export_anim.live_mode()
        cls._handling = False

    @classmethod
    def register_handler(cls):
        bpy.context.window_manager.servo_animation.live_mode = True
        bpy.app.handlers.frame_change_post.append(LiveMode.handler)
        bpy.app.handlers.depsgraph_update_post.append(LiveMode.handler)
        cls.handler(bpy.context.scene, None)

    @classmethod
    def unregister_handler(cls):
        bpy.context.window_manager.servo_animation.live_mode = False
        bpy.app.handlers.frame_change_post.remove(LiveMode.handler)
        bpy.app.handlers.depsgraph_update_post.remove(LiveMode.handler)

    @classmethod
    def has_open_serial_connection(cls):
        return (
            isinstance(cls.serial_connection, serial.Serial)
            and cls.serial_connection.is_open
            and (
                cls.serial_connection.port in get_serial_ports()
                or bpy.app.background
            )
        )

    @classmethod
    def has_open_web_socket_connection(cls):
        return isinstance(cls.tcp_connection, socket.socket)

    def execute(self, context):
        diffs = []
        target_positions = {}
        servo_animation = context.window_manager.servo_animation

        for pose_bone in get_active_pose_bones(context.scene):
            target_position, in_range = calculate_position(pose_bone, None)

            if not in_range:
                continue

            servo_id = pose_bone.bone.servo_settings.servo_id
            target_positions[servo_id] = target_position

            if servo_id in self._positions:
                diffs.append(
                    abs(target_position - self._positions[servo_id]))

        if len(diffs) > 0:
            steps = max(diffs)
        else:
            steps = 0

        if (
            servo_animation.position_jump_handling
            and steps > servo_animation.position_jump_threshold
        ):
            self.handle_position_jump(target_positions, steps, context)
        else:
            self.handle_default(target_positions, context)

        return {'FINISHED'}

    def send_position(self, servo_id, position, context):
        if position == self._positions.get(servo_id):
            return

        command = [self.COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [self.COMMAND_END]

        servo_animation = context.window_manager.servo_animation

        try:
            if servo_animation.live_mode_method == self.METHOD_SERIAL:
                self.serial_connection.write(command)
            elif servo_animation.live_mode_method == self.METHOD_WEB_SOCKET:
                self.tcp_connection.send(bytes(command))

            self._positions[servo_id] = position
        except (
            serial.SerialException, BlockingIOError, BrokenPipeError, ConnectionAbortedError,
            ConnectionResetError, InterruptedError, TypeError
        ):
            bpy.ops.export_anim.stop_live_mode()

    def handle_default(self, target_positions, context):
        for servo_id, target_position in target_positions.items():
            self.send_position(servo_id, target_position, context)

    def handle_position_jump(self, target_positions, steps, context):
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)

        window_manager = context.window_manager
        window_manager.progress_begin(0, steps)

        for step in range(steps):
            window_manager.progress_update(step)
            for servo_id, target_position in target_positions.items():
                previous_position = self._positions[servo_id]
                if target_position == previous_position:
                    continue
                if target_position > previous_position:
                    new_position = previous_position + 1
                else:
                    new_position = previous_position - 1
                self.send_position(servo_id, new_position, context)
            time.sleep(.01)

        window_manager.progress_end()
