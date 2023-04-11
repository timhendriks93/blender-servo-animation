from bpy.types import Operator
from ..ops.live_mode import LiveMode


class StopWebSocketLiveMode(Operator):
    bl_idname = "export_anim.stop_web_socket_live_mode"
    bl_label = "Stop Web Socket Live Mode"
    bl_description = "Stop sending live position values via the current web socket connection"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (
            context.window_manager.servo_animation.live_mode
            and LiveMode.has_open_web_socket_connection()
        )

    def execute(self, _context):
        if LiveMode.has_open_web_socket_connection():
            socket_host, socket_port = LiveMode.tcp_connection.getpeername()
            message = f"Closed web socket connection with host {socket_host} and port {socket_port}"

        LiveMode.tcp_connection.close()
        LiveMode.tcp_connection = None
        LiveMode.unregister_handler()

        if message:
            self.report({'INFO'}, message)

        return {'FINISHED'}
