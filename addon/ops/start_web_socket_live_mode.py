import bpy

from bpy.types import Operator
from .base_live_mode import BaseLiveMode
from ..utils.web import is_ip
from ..utils.live import LIVE_MODE_CONTROLLER


class StartWebSocketLiveMode(Operator, BaseLiveMode):
    bl_idname = "export_anim.start_web_socket_live_mode"
    bl_label = "Start Web Socket Live Mode"
    bl_description = "Start sending live position values via the given web socket connection"
    bl_options = {'INTERNAL'}

    socket_host: bpy.props.StringProperty()
    socket_port: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        servo_animation = context.window_manager.servo_animation

        return (
            not servo_animation.live_mode
            and (
                is_ip(servo_animation.socket_ip)
                or bpy.app.background
            )
        )

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

        servo_animation.live_mode = True
        bpy.app.handlers.frame_change_post.append(
            LIVE_MODE_CONTROLLER.update_positions)
        bpy.app.handlers.depsgraph_update_post.append(
            LIVE_MODE_CONTROLLER.update_positions)
        LIVE_MODE_CONTROLLER.update_positions(context.scene, None)

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
