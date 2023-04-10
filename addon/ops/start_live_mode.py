import bpy

from bpy.types import Operator
from ..utils.web import is_ip
from ..utils.live import LIVE_MODE_CONTROLLER, METHOD_SERIAL, METHOD_WEB_SOCKET


class StartLiveMode(Operator):
    bl_idname = "export_anim.start_live_mode"
    bl_label = "Start Live Mode"
    bl_description = "Start sending live position values via the given live connection"
    bl_options = {'INTERNAL'}

    method: bpy.props.StringProperty()
    serial_port: bpy.props.StringProperty()
    baud_rate: bpy.props.IntProperty()
    socket_host: bpy.props.StringProperty()
    socket_port: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        servo_animation = context.window_manager.servo_animation

        return (
            not servo_animation.live_mode
            and (
                (
                    servo_animation.live_mode_method == METHOD_SERIAL
                    and servo_animation.serial_port != ""
                )
                or (
                    servo_animation.live_mode_method == METHOD_WEB_SOCKET
                    and is_ip(servo_animation.socket_ip)
                )
                or bpy.app.background
            )
        )

    def execute(self, context):
        servo_animation = context.window_manager.servo_animation
        LIVE_MODE_CONTROLLER.close_open_connection()

        if (
            self.method == METHOD_SERIAL
            and not LIVE_MODE_CONTROLLER.open_serial_connection(self.serial_port, self.baud_rate)
        ):
            servo_animation.live_mode = False
            self.report(
                {'ERROR'},
                f"Failed to open serial connection on port {self.serial_port} with baud rate {self.baud_rate}"
            )

            return {'CANCELLED'}

        if (
            self.method == METHOD_WEB_SOCKET
            and not LIVE_MODE_CONTROLLER.open_web_socket_connection(self.socket_host, self.socket_port)
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

        if self.method == METHOD_SERIAL:
            self.report(
                {'INFO'},
                f"Opened serial connection on port {self.serial_port} with baud rate {self.baud_rate}"
            )
        elif self.method == METHOD_WEB_SOCKET:
            self.report(
                {'INFO'},
                f"Opened web socket connection with host {self.socket_host} on port {self.socket_port}"
            )

        return {'FINISHED'}

    def invoke(self, context, _event):
        servo_animation = context.window_manager.servo_animation
        self.method = servo_animation.live_mode_method

        if self.method == METHOD_SERIAL:
            self.serial_port = servo_animation.serial_port
            self.baud_rate = int(servo_animation.baud_rate)
        elif self.method == METHOD_WEB_SOCKET:
            self.socket_host = servo_animation.socket_ip
            self.socket_port = servo_animation.socket_port

        return self.execute(context)
