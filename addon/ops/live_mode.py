import time
import socket
import bpy
import serial

from bpy.types import Operator

from ..utils.converter import calculate_position
from ..utils.servo_settings import get_active_pose_bones
from ..utils.uart import get_serial_ports
from ..utils.web import is_ip


class LiveMode(Operator):
    bl_idname = "export_anim.live_mode"
    bl_label = "Live Mode Handling"
    bl_options = {'INTERNAL', 'BLOCKING'}

    COMMAND_START = 0x3C
    COMMAND_END = 0x3E

    METHOD_SERIAL = "SERIAL"
    METHOD_WEB_SOCKET = "WEB_SOCKET"
    METHOD_ITEMS = [
        (METHOD_SERIAL, "Serial", "Connect via USB"),
        (METHOD_WEB_SOCKET, "Web Socket", "Connect via a web socket"),
    ]

    _positions = {}
    _handling = False

    serial_connection = None
    tcp_connection = None

    method: bpy.props.EnumProperty(items=METHOD_ITEMS)
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
                    servo_animation.live_mode_method == cls.METHOD_SERIAL
                    and servo_animation.serial_port != ""
                    and not LiveMode.has_open_serial_connection()
                )
                or (
                    servo_animation.live_mode_method == cls.METHOD_WEB_SOCKET
                    and is_ip(servo_animation.socket_ip)
                    and not LiveMode.has_open_web_socket_connection()
                )
            )
        )

    @classmethod
    def handler(cls, _scene, _depsgraph):
        if cls._handling:
            return

        cls._handling = True
        diffs = []
        target_positions = {}
        servo_animation = bpy.context.window_manager.servo_animation

        for pose_bone in get_active_pose_bones(bpy.context.scene):
            target_position, in_range = calculate_position(pose_bone, None)

            if not in_range:
                continue

            servo_id = pose_bone.bone.servo_settings.servo_id
            target_positions[servo_id] = target_position

            if servo_id in cls._positions:
                diffs.append(
                    abs(target_position - cls._positions[servo_id]))

        if len(diffs) > 0:
            steps = max(diffs)
        else:
            steps = 0

        if (
            servo_animation.position_jump_handling
            and steps > servo_animation.position_jump_threshold
        ):
            cls.handle_position_jump(target_positions, steps)
        else:
            cls.handle_default(target_positions)

        cls._handling = False

    @classmethod
    def register_handler(cls):
        bpy.context.window_manager.servo_animation.live_mode = True
        bpy.app.handlers.frame_change_post.append(LiveMode.handler)
        bpy.app.handlers.depsgraph_update_post.append(LiveMode.handler)
        cls.handler(bpy.context.scene, None)

    @classmethod
    def unregister_handler(cls):
        bpy.context.window_manager.servo_animation.live_mode = False
        bpy.app.handlers.frame_change_post.remove(LiveMode.handler)
        bpy.app.handlers.depsgraph_update_post.remove(LiveMode.handler)

    @classmethod
    def has_open_serial_connection(cls):
        return (
            isinstance(cls.serial_connection, serial.Serial)
            and cls.serial_connection.is_open
            and (
                cls.serial_connection.port in get_serial_ports()
                or bpy.app.background
            )
        )

    @classmethod
    def has_open_web_socket_connection(cls):
        return isinstance(cls.tcp_connection, socket.socket)

    @classmethod
    def handle_default(cls, target_positions):
        for servo_id, target_position in target_positions.items():
            cls.send_position(servo_id, target_position)

    @classmethod
    def handle_position_jump(cls, target_positions, steps):
        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)

        window_manager = bpy.context.window_manager
        window_manager.progress_begin(0, steps)

        for step in range(steps):
            window_manager.progress_update(step)
            for servo_id, target_position in target_positions.items():
                previous_position = cls._positions[servo_id]
                if target_position == previous_position:
                    continue
                if target_position > previous_position:
                    new_position = previous_position + 1
                else:
                    new_position = previous_position - 1
                cls.send_position(servo_id, new_position)
            time.sleep(.01)

        window_manager.progress_end()

    @classmethod
    def send_position(cls, servo_id, position):
        if position == cls._positions.get(servo_id):
            return

        command = [cls.COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [cls.COMMAND_END]

        servo_animation = bpy.context.window_manager.servo_animation

        try:
            if servo_animation.live_mode_method == cls.METHOD_SERIAL:
                cls.serial_connection.write(command)
            elif servo_animation.live_mode_method == cls.METHOD_WEB_SOCKET:
                cls.tcp_connection.send(bytes(command))

            cls._positions[servo_id] = position
        except (
            serial.SerialException, BlockingIOError, BrokenPipeError, ConnectionAbortedError,
            ConnectionResetError, InterruptedError, TypeError
        ):
            bpy.ops.export_anim.stop_live_mode()

    def execute(self, context):
        servo_animation = context.window_manager.servo_animation
        servo_animation.live_mode_method = self.method

        if self.method == self.METHOD_SERIAL:
            return self.start_serial(context)

        if self.method == self.METHOD_WEB_SOCKET:
            return self.start_web_socket(context)

        self.report({'ERROR'}, "Unknown live mode method")

        return {'CANCELLED'}

    def start_serial(self, context):
        try:
            LiveMode.serial_connection = serial.Serial(
                port=self.serial_port, baudrate=self.baud_rate)
        except (serial.SerialException, ValueError):
            context.window_manager.servo_animation.live_mode = False
            self.report(
                {'ERROR'},
                f"Failed to open serial connection on port {self.serial_port} with baud rate {self.baud_rate}"
            )

            return {'CANCELLED'}

        self.register_handler()
        self.report(
            {'INFO'},
            f"Opened serial connection on port {self.serial_port} with baud rate {self.baud_rate}"
        )

        return {'FINISHED'}

    def start_web_socket(self, context):
        servo_animation = context.window_manager.servo_animation

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

        self.register_handler()
        self.report(
            {'INFO'},
            f"Opened web socket connection with host {self.socket_host} on port {self.socket_port}"
        )

        return {'FINISHED'}

    def invoke(self, context, _event):
        servo_animation = context.window_manager.servo_animation
        self.method = servo_animation.live_mode_method
        self.serial_port = servo_animation.serial_port
        self.baud_rate = int(servo_animation.baud_rate)
        self.socket_host = servo_animation.socket_ip
        self.socket_port = servo_animation.socket_port

        return self.execute(context)
