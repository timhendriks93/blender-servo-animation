from bpy.types import Operator
from ..utils.live import LIVE_MODE_CONTROLLER
from ..ops.live_mode import LiveMode


class StopWebSocketLiveMode(Operator):
    bl_idname = "export_anim.stop_web_socket_live_mode"
    bl_label = "Stop Web Socket Live Mode"
    bl_description = "Stop sending live position values via the current web socket connection"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.servo_animation.live_mode

    def execute(self, _context):
        if LIVE_MODE_CONTROLLER.has_open_web_socket_connection():
            socket_host, socket_port = LIVE_MODE_CONTROLLER.tcp_connection.getpeername()
            message = f"Closed web socket connection with host {socket_host} and port {socket_port}"

        LIVE_MODE_CONTROLLER.close_open_connection()

        LiveMode.unregister_handler()

        if message:
            self.report({'INFO'}, message)

        return {'FINISHED'}
