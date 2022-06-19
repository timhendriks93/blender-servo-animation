import bpy

from bpy.types import Operator
from ..utils.uart import UART_CONTROLLER


class StartLiveMode(Operator):
    bl_idname = "export_anim.start_live_mode"
    bl_label = "Start Live Mode"
    bl_description = "Start sending live position values via the given serial connection"
    bl_options = {'INTERNAL'}

    serial_port: bpy.props.StringProperty()
    baud_rate: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return (
            not context.window_manager.servo_animation.live_mode
            and not UART_CONTROLLER.is_connected()
        )

    def execute(self, context):
        servo_animation = context.window_manager.servo_animation

        if self.properties.serial_port == "":
            self.properties.serial_port = servo_animation.serial_port

        if self.properties.baud_rate == 0:
            self.properties.baud_rate = int(servo_animation.baud_rate)

        if UART_CONTROLLER.open_serial_connection(self.serial_port, self.baud_rate):
            bpy.app.handlers.frame_change_post.append(
                UART_CONTROLLER.update_positions)
            bpy.app.handlers.depsgraph_update_post.append(
                UART_CONTROLLER.update_positions)
            servo_animation.live_mode = True
            UART_CONTROLLER.update_positions(context.scene, None)
            self.report(
                {'INFO'},
                f"Opened serial connection for port {self.serial_port} with baud rate {self.baud_rate}"
            )

            return {'FINISHED'}

        servo_animation.live_mode = False
        self.report(
            {'ERROR'},
            f"Failed to open serial connection for port {self.serial_port} with baud rate {self.baud_rate}"
        )

        return {'CANCELLED'}
