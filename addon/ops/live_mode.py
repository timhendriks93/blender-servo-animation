import time
import bpy

from bpy.types import Operator

from ..utils.uart import UART_CONTROLLER
from ..utils.converter import calculate_position
from ..utils.servo_settings import get_active_pose_bones


class LiveMode(Operator):
    bl_idname = "export_anim.live_mode"
    bl_label = "Live Mode Handling"
    bl_options = {'INTERNAL', 'BLOCKING'}

    @classmethod
    def poll(cls, context):
        return (
            context.window_manager.servo_animation.live_mode
            and UART_CONTROLLER.is_connected()
        )

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

            if servo_id in UART_CONTROLLER.positions:
                diffs.append(
                    abs(target_position - UART_CONTROLLER.positions[servo_id]))

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
            self.handle_default(target_positions)

        return {'FINISHED'}

    @staticmethod
    def handle_default(target_positions):
        for servo_id, target_position in target_positions.items():
            UART_CONTROLLER.send_position(servo_id, target_position)

    @staticmethod
    def handle_position_jump(target_positions, steps, context):
        if context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)

        window_manager = context.window_manager
        window_manager.progress_begin(0, steps)

        for step in range(steps):
            window_manager.progress_update(step)
            for servo_id, target_position in target_positions.items():
                previous_position = UART_CONTROLLER.positions[servo_id]
                if target_position == previous_position:
                    continue
                if target_position > previous_position:
                    new_position = previous_position + 1
                else:
                    new_position = previous_position - 1
                UART_CONTROLLER.send_position(servo_id, new_position)
            time.sleep(.01)

        window_manager.progress_end()
