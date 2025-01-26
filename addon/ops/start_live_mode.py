# pylint: disable=import-outside-toplevel

import bpy

from bpy.types import Operator
from ..utils.live_mode import LiveMode


class StartLiveMode(Operator):
    bl_idname = "servo_animation.start_live_mode"
    bl_label = "Live Mode"
    bl_description = "Start sending live position values via a live mode connection"
    bl_options = {'INTERNAL', 'BLOCKING'}

    METHOD_ITEMS = [
        (LiveMode.METHOD_SERIAL, "Serial", "Connect via USB"),
        (LiveMode.METHOD_SOCKET, "Web Socket", "Connect via a web socket"),
    ]

    method: bpy.props.EnumProperty(items=METHOD_ITEMS)

    serial_port: bpy.props.StringProperty()
    serial_baud: bpy.props.IntProperty()

    socket_host: bpy.props.StringProperty()
    socket_port: bpy.props.IntProperty()
    socket_path: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        servo_animation = context.window_manager.servo_animation

        return (
            not LiveMode.is_connected()
            and (
                (
                    servo_animation.live_mode_method == LiveMode.METHOD_SERIAL
                    and servo_animation.serial_port != "NONE"
                )
                or (
                    servo_animation.live_mode_method == LiveMode.METHOD_SOCKET
                    and servo_animation.socket_host != ""
                ) or bpy.app.background
            )
        )

    @classmethod
    def register_handler(cls):
        bpy.app.handlers.frame_change_post.append(LiveMode.handler)
        bpy.app.handlers.depsgraph_update_post.append(LiveMode.handler)
        LiveMode.handler(bpy.context.scene, None)

    def execute(self, context):
        servo_animation = context.window_manager.servo_animation
        servo_animation.live_mode_method = self.method

        if self.method == LiveMode.METHOD_SERIAL:
            return self.open_serial(context)

        if self.method == LiveMode.METHOD_SOCKET:
            return self.open_socket(context)

        self.report({'ERROR'}, "Unknown live mode method")

        return {'CANCELLED'}

    def open_serial(self, _context):
        import serial

        try:
            serial_connection = serial.Serial(self.serial_port, self.serial_baud)
        except (serial.SerialException, ValueError):
            self.report(
                {'ERROR'},
                (
                    f"Failed to open serial connection on port {self.serial_port} "
                    f"with baud rate {self.serial_baud}"
                )
            )

            return {'CANCELLED'}

        LiveMode.set_connection(serial_connection)

        self.register_handler()
        self.report(
            {'INFO'},
            f"Opened serial connection on port {self.serial_port} with baud rate {self.serial_baud}"
        )

        return {'FINISHED'}

    def open_socket(self, _context):
        import websocket

        socket_url = f"ws://{self.socket_host}:{self.socket_port}{self.socket_path}"
        socket_connection = websocket.WebSocket()
        socket_connection.settimeout(1)

        try:
            socket_connection.connect(socket_url)
        except (websocket.WebSocketException, OSError):
            self.report({'ERROR'}, f"Failed to open web socket connection with {socket_url}")

            return {'CANCELLED'}

        LiveMode.set_connection(socket_connection)

        self.register_handler()
        self.report({'INFO'}, f"Opened web socket connection with {socket_url}")

        return {'FINISHED'}

    def invoke(self, context, _event):
        servo_animation = context.window_manager.servo_animation

        self.method = servo_animation.live_mode_method

        self.serial_port = servo_animation.serial_port
        self.serial_baud = int(servo_animation.serial_baud)

        self.socket_host = servo_animation.socket_host
        self.socket_port = servo_animation.socket_port
        self.socket_path = servo_animation.socket_path

        return self.execute(context)
