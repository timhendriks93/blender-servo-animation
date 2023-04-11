import bpy

from bpy.types import Operator
from .live_mode import LiveMode


class StopLiveMode(Operator):
    bl_idname = "export_anim.stop_live_mode"
    bl_label = "Stop Live Mode"
    bl_description = "Stop sending live position values via the current live mode connection"
    bl_options = {'INTERNAL'}

    method: bpy.props.EnumProperty(items=LiveMode.METHOD_ITEMS)

    @classmethod
    def poll(cls, context):
        servo_animation = context.window_manager.servo_animation

        return (
            servo_animation.live_mode
            and (
                (
                    servo_animation.live_mode_method == LiveMode.METHOD_SERIAL
                    and LiveMode.has_open_serial_connection()
                )
                or (
                    servo_animation.live_mode_method == LiveMode.METHOD_WEB_SOCKET
                    and LiveMode.has_open_web_socket_connection()
                )
            )
        )

    def execute(self, _context):
        if self.method == LiveMode.METHOD_SERIAL:
            serial_port = LiveMode.serial_connection.port

            LiveMode.serial_connection.close()
            LiveMode.serial_connection = None

            self.report({'INFO'}, f"Closed serial connection on port {serial_port}")
        elif self.method == LiveMode.METHOD_WEB_SOCKET:
            socket_host, socket_port = LiveMode.tcp_connection.getpeername()

            LiveMode.tcp_connection.close()
            LiveMode.tcp_connection = None

            self.report(
                {'INFO'},
                f"Closed web socket connection with host {socket_host} and port {socket_port}"
            )
        else:
            self.report({'ERROR'}, "Unknown live mode method")

            return {'CANCELLED'}

        LiveMode.unregister_handler()

        return {'FINISHED'}

    def invoke(self, context, _event):
        servo_animation = context.window_manager.servo_animation
        self.method = servo_animation.live_mode_method

        return self.execute(context)
