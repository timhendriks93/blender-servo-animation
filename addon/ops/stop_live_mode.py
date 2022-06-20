import bpy

from bpy.types import Operator
from ..utils.uart import UART_CONTROLLER


class StopLiveMode(Operator):
    bl_idname = "export_anim.stop_live_mode"
    bl_label = "Stop Live Mode"
    bl_description = "Stop sending live position values via the current serial connection"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.servo_animation.live_mode

    def execute(self, context):
        message = "Closed serial connection"

        if UART_CONTROLLER.is_connected():
            serial_port = UART_CONTROLLER.serial_connection.port
            message += f" on port {serial_port}"

        UART_CONTROLLER.close_serial_connection()

        bpy.app.handlers.frame_change_post.remove(
            UART_CONTROLLER.update_positions)
        bpy.app.handlers.depsgraph_update_post.remove(
            UART_CONTROLLER.update_positions)

        context.window_manager.servo_animation.live_mode = False

        self.report({'INFO'}, message)

        return {'FINISHED'}
