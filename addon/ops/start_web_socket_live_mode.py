import socket
import bpy

from bpy.types import Operator
from ..utils.web import is_ip
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
            and not LiveMode.has_open_web_socket_connection()
        )

    def execute(self, context):
        servo_animation = context.window_manager.servo_animation
        servo_animation.live_mode_method = LiveMode.METHOD_WEB_SOCKET

        tcp_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_connection.settimeout(1)

        try:
            tcp_connection.connect((self.socket_host, self.socket_port))
        except (socket.timeout, socket.error):
            servo_animation.live_mode = False
            self.report(
                {'ERROR'},
                "".join((
                    f"Failed to open web socket connection with host {self.socket_host} ",
                    f"on port {self.socket_port}"
                ))
            )

            return {'CANCELLED'}

        LiveMode.tcp_connection = tcp_connection
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
