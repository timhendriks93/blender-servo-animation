import bpy

from bpy.types import Operator
from ..utils.web import is_ip
from ..utils.live import LIVE_MODE_CONTROLLER
from ..ops.live_mode import LiveMode


class StartWebSocketLiveMode(Operator):
    bl_idname = "export_anim.start_web_socket_live_mode"
    bl_label = "Start Web Socket Live Mode"
    bl_description = "Start sending live position values via the given web socket connection"
    bl_options = {'INTERNAL'}

    socket_host: bpy.props.StringProperty()
    socket_port: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return (
            not context.window_manager.servo_animation.live_mode
            and is_ip(context.window_manager.servo_animation.socket_ip)
        )

    @classmethod
    def handle_live_mode(cls, _scene, _depsgraph):
        if LIVE_MODE_CONTROLLER.handling:
            return

        LIVE_MODE_CONTROLLER.handling = True
        bpy.ops.export_anim.live_mode()
        LIVE_MODE_CONTROLLER.handling = False

    def execute(self, context):
        servo_animation = context.window_manager.servo_animation
        LIVE_MODE_CONTROLLER.close_open_connection()

        if (
            not LIVE_MODE_CONTROLLER.open_web_socket_connection(self.socket_host, self.socket_port)
        ):
            servo_animation.live_mode = False
            self.report(
                {'ERROR'},
                "".join((
                    f"Failed to open web socket connection with host {self.socket_host} ",
                    f"on port {self.socket_port}"
                ))
            )

            return {'CANCELLED'}

        LiveMode.register_handler()

        self.report(
            {'INFO'},
            f"Opened web socket connection with host {self.socket_host} on port {self.socket_port}"
        )

        return {'FINISHED'}

    def invoke(self, context, _event):
        servo_animation = context.window_manager.servo_animation
        self.socket_host = servo_animation.socket_ip
        self.socket_port = servo_animation.socket_port

        return self.execute(context)
