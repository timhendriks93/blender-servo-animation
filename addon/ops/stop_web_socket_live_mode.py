import bpy

from bpy.types import Operator
from ..utils.live import LIVE_MODE_CONTROLLER
from ..ops.start_web_socket_live_mode import StartWebSocketLiveMode


class StopWebSocketLiveMode(Operator):
    bl_idname = "export_anim.stop_web_socket_live_mode"
    bl_label = "Stop Web Socket Live Mode"
    bl_description = "Stop sending live position values via the current web socket connection"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.servo_animation.live_mode

    def execute(self, context):
        if LIVE_MODE_CONTROLLER.has_open_web_socket_connection():
            socket_host, socket_port = LIVE_MODE_CONTROLLER.tcp_connection.getpeername()
            message = f"Closed web socket connection with host {socket_host} and port {socket_port}"

        LIVE_MODE_CONTROLLER.close_open_connection()

        context.window_manager.servo_animation.live_mode = False
        bpy.app.handlers.frame_change_post.remove(StartWebSocketLiveMode.handle_live_mode)
        bpy.app.handlers.depsgraph_update_post.remove(StartWebSocketLiveMode.handle_live_mode)

        if message:
            self.report({'INFO'}, message)

        return {'FINISHED'}
