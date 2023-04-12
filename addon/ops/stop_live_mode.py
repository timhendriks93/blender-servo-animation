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
        return (
            LiveMode.is_active()
            and (
                LiveMode.has_serial_connection()
                or LiveMode.has_socket_connection()
            )
        )

    def execute(self, _context):
        if LiveMode.has_serial_connection():
            serial_port = LiveMode.serial_connection.port

            LiveMode.serial_connection.close()
            LiveMode.serial_connection = None

            self.report({'INFO'}, f"Closed serial connection on port {serial_port}")

        if LiveMode.has_socket_connection():
            socket_host, socket_port = LiveMode.socket_connection.getpeername()

            LiveMode.socket_connection.close()
            LiveMode.socket_connection = None

            self.report(
                {'INFO'},
                f"Closed web socket connection with host {socket_host} and port {socket_port}"
            )

        LiveMode.unregister_handler()

        return {'FINISHED'}

    def invoke(self, context, _event):
        servo_animation = context.window_manager.servo_animation
        self.method = servo_animation.live_mode_method

        return self.execute(context)
