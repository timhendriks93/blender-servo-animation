import bpy

from bpy.types import Operator
from .base_live_mode import BaseLiveMode
from ..utils.live import LIVE_MODE_CONTROLLER


class StartSerialLiveMode(Operator, BaseLiveMode):
    bl_idname = "export_anim.start_serial_live_mode"
    bl_label = "Start Serial Live Mode"
    bl_description = "Start sending live position values via the given serial connection"
    bl_options = {'INTERNAL'}

    serial_port: bpy.props.StringProperty()
    baud_rate: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        servo_animation = context.window_manager.servo_animation

        return (
            not servo_animation.live_mode
            and (
                servo_animation.serial_port != ""
                or bpy.app.background
            )
        )

    def execute(self, context):
        servo_animation = context.window_manager.servo_animation
        LIVE_MODE_CONTROLLER.close_open_connection()

        if (
            not LIVE_MODE_CONTROLLER.open_serial_connection(self.serial_port, self.baud_rate)
        ):
            servo_animation.live_mode = False
            self.report(
                {'ERROR'},
                f"Failed to open serial connection on port {self.serial_port} with baud rate {self.baud_rate}"
            )

            return {'CANCELLED'}

        servo_animation.live_mode = True
        bpy.app.handlers.frame_change_post.append(
            LIVE_MODE_CONTROLLER.update_positions)
        bpy.app.handlers.depsgraph_update_post.append(
            LIVE_MODE_CONTROLLER.update_positions)
        LIVE_MODE_CONTROLLER.update_positions(context.scene, None)

        self.report(
            {'INFO'},
            f"Opened serial connection on port {self.serial_port} with baud rate {self.baud_rate}"
        )

        return {'FINISHED'}

    def invoke(self, context, _event):
        servo_animation = context.window_manager.servo_animation
        self.serial_port = servo_animation.serial_port
        self.baud_rate = int(servo_animation.baud_rate)

        return self.execute(context)
