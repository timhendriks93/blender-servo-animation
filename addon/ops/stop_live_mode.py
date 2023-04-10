from bpy.types import Operator
from ..utils.live import LIVE_MODE_CONTROLLER
from ..ops.base_live_mode import BaseLiveMode


class StopLiveMode(Operator, BaseLiveMode):
    bl_idname = "export_anim.stop_live_mode"
    bl_label = "Stop Live Mode"
    bl_description = "Stop sending live position values via the current live connection"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.window_manager.servo_animation.live_mode

    def execute(self, _context):
        if LIVE_MODE_CONTROLLER.has_open_serial_connection():
            serial_port = LIVE_MODE_CONTROLLER.serial_connection.port
            message = f"Closed serial connection on port {serial_port}"
        elif LIVE_MODE_CONTROLLER.has_open_web_socket_connection():
            socket_host, socket_port = LIVE_MODE_CONTROLLER.tcp_connection.getpeername()
            message = f"Closed web socket connection with host {socket_host} and port {socket_port}"
        else:
            message = "Closed live connection"

        LIVE_MODE_CONTROLLER.close_open_connection()

        self.unregister_handlers()

        self.report({'INFO'}, message)

        return {'FINISHED'}
