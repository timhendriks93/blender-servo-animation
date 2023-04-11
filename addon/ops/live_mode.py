import time
import bpy
import serial

from bpy.types import Operator

from ..utils.live import LIVE_MODE_CONTROLLER
from ..utils.converter import calculate_position
from ..utils.servo_settings import get_active_pose_bones
from ..ops.start_serial_live_mode import StartSerialLiveMode
from ..ops.start_web_socket_live_mode import StartWebSocketLiveMode


class LiveMode(Operator):
    bl_idname = "export_anim.live_mode"
    bl_label = "Live Mode Handling"
    bl_options = {'INTERNAL', 'BLOCKING'}

    COMMAND_START = 0x3C
    COMMAND_END = 0x3E

    positions = {}

    @classmethod
    def poll(cls, context):
        return context.window_manager.servo_animation.live_mode

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

            if servo_id in self.positions:
                diffs.append(
                    abs(target_position - self.positions[servo_id]))

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

    def send_position(self, servo_id, position, _context):
        if position == self.positions.get(servo_id):
            return

        command = [self.COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [self.COMMAND_END]

        try:
            if LIVE_MODE_CONTROLLER.connection_method == StartSerialLiveMode.METHOD:
                LIVE_MODE_CONTROLLER.serial_connection.write(command)
            elif LIVE_MODE_CONTROLLER.connection_method == StartWebSocketLiveMode.METHOD:
                LIVE_MODE_CONTROLLER.tcp_connection.send(bytes(command))

            self.positions[servo_id] = position
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
                previous_position = self.positions[servo_id]
                if target_position == previous_position:
                    continue
                if target_position > previous_position:
                    new_position = previous_position + 1
                else:
                    new_position = previous_position - 1
                self.send_position(servo_id, new_position, context)
            time.sleep(.01)

        window_manager.progress_end()
