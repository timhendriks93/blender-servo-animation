import importlib
import time
import bpy

try:
    import serial
    import serial.tools.list_ports
    import websocket

    DEPS_INSTALLED = True
except ModuleNotFoundError as e:
    DEPS_INSTALLED = False

from bpy.types import Operator

from ..utils.converter import calculate_position
from ..utils.servo_settings import get_active_pose_bones


class LiveMode(Operator):
    bl_idname = "export_anim.live_mode"
    bl_label = "Live Mode"
    bl_description = "Start sending live position values via a live mode connection"
    bl_options = {'INTERNAL', 'BLOCKING'}

    COMMAND_START = 0x3C
    COMMAND_END = 0x3E

    METHOD_SERIAL = "SERIAL"
    METHOD_SOCKET = "SOCKET"

    METHOD_ITEMS = [
        (METHOD_SERIAL, "Serial", "Connect via USB"),
        (METHOD_SOCKET, "Web Socket", "Connect via a web socket"),
    ]

    _last_positions = {}
    _is_handling = False
    _is_available = DEPS_INSTALLED

    _serial_connection = None
    _socket_connection = None

    method: bpy.props.EnumProperty(items=METHOD_ITEMS)

    serial_port: bpy.props.StringProperty()
    serial_baud: bpy.props.IntProperty()

    socket_host: bpy.props.StringProperty()
    socket_port: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        servo_animation = context.window_manager.servo_animation

        return (
            not cls.is_active()
            and (
                (
                    servo_animation.live_mode_method == cls.METHOD_SERIAL
                    and servo_animation.serial_port != ""
                )
                or (
                    servo_animation.live_mode_method == cls.METHOD_SOCKET
                    and servo_animation.socket_host != ""
                )
            )
        )

    @classmethod
    def handler(cls, _scene, _depsgraph):
        if cls._is_handling:
            return

        cls._is_handling = True

        diffs = []
        target_positions = {}
        servo_animation = bpy.context.window_manager.servo_animation

        for pose_bone in get_active_pose_bones(bpy.context.scene):
            target_position, in_range = calculate_position(pose_bone, None)

            if not in_range:
                continue

            servo_id = pose_bone.bone.servo_settings.servo_id
            target_positions[servo_id] = target_position

            if servo_id in cls._last_positions:
                diffs.append(
                    abs(target_position - cls._last_positions[servo_id]))

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

        cls._is_handling = False

    @classmethod
    def register_handlers(cls):
        bpy.app.handlers.frame_change_post.append(LiveMode.handler)
        bpy.app.handlers.depsgraph_update_post.append(LiveMode.handler)
        cls.handler(bpy.context.scene, None)

    @classmethod
    def unregister_handlers(cls):
        if bpy.app.handlers.frame_change_post.count(LiveMode.handler):
            bpy.app.handlers.frame_change_post.remove(LiveMode.handler)

        if bpy.app.handlers.depsgraph_update_post.count(LiveMode.handler):
            bpy.app.handlers.depsgraph_update_post.remove(LiveMode.handler)

    @classmethod
    def get_serial_ports(cls):
        ports = []

        for port in serial.tools.list_ports.comports():
            ports.append(port.device)

        return ports

    @classmethod
    def has_serial_connection(cls):
        return (
            isinstance(cls._serial_connection, serial.Serial)
            and cls._serial_connection.is_open
            and (
                cls._serial_connection.port in cls.get_serial_ports()
                or bpy.app.background
            )
        )

    @classmethod
    def has_socket_connection(cls):
        return (
            isinstance(cls._socket_connection, websocket.WebSocket)
            and cls._socket_connection.connected
        )

    @classmethod
    def is_available(cls):
        return cls._is_available

    @classmethod
    def update_dependencies(cls):
        modules = ["serial", "serial.tools.list_ports", "websocket"]

        try:
            for module in modules:
                globals()[module] = importlib.import_module(module)

            cls._is_available = True
        except ModuleNotFoundError:
            cls._is_available = False

    @classmethod
    def is_active(cls):
        method = bpy.context.window_manager.servo_animation.live_mode_method

        return (
            (
                method == cls.METHOD_SERIAL
                and cls.has_serial_connection()
            )
            or (
                method == cls.METHOD_SOCKET
                and cls.has_socket_connection()
            )
        )

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
                previous_position = cls._last_positions[servo_id]
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
        if position == cls._last_positions.get(servo_id):
            return

        command = [cls.COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [cls.COMMAND_END]

        servo_animation = bpy.context.window_manager.servo_animation

        try:
            if servo_animation.live_mode_method == cls.METHOD_SERIAL:
                cls._serial_connection.write(command)
            elif servo_animation.live_mode_method == cls.METHOD_SOCKET:
                cls._socket_connection.send_binary(bytes(command))

            cls._last_positions[servo_id] = position
        except (serial.SerialException, websocket.WebSocketException, OSError):
            bpy.ops.export_anim.stop_live_mode(unexpected=True)

    def execute(self, context):
        servo_animation = context.window_manager.servo_animation
        servo_animation.live_mode_method = self.method

        if self.method == self.METHOD_SERIAL:
            return self.open_serial(context)

        if self.method == self.METHOD_SOCKET:
            return self.open_socket(context)

        self.report({'ERROR'}, "Unknown live mode method")

        return {'CANCELLED'}

    def open_serial(self, _context):
        try:
            LiveMode._serial_connection = serial.Serial(
                port=self.serial_port, baudrate=self.serial_baud)
        except (serial.SerialException, ValueError):
            self.report(
                {'ERROR'},
                (
                    f"Failed to open serial connection on port {self.serial_port} "
                    f"with baud rate {self.serial_baud}"
                )
            )

            return {'CANCELLED'}

        self.register_handlers()
        self.report(
            {'INFO'},
            f"Opened serial connection on port {self.serial_port} with baud rate {self.serial_baud}"
        )

        return {'FINISHED'}

    def open_socket(self, _context):
        socket_url = f"ws://{self.socket_host}:{self.socket_port}/ws"
        socket_connection = websocket.WebSocket()
        socket_connection.settimeout(1)

        try:
            socket_connection.connect(socket_url)
        except (websocket.WebSocketException, OSError):
            self.report(
                {'ERROR'},
                (
                    f"Failed to open web socket connection with host {self.socket_host} "
                    f"on port {self.socket_port}"
                )
            )

            return {'CANCELLED'}

        LiveMode._socket_connection = socket_connection

        self.register_handlers()
        self.report(
            {'INFO'},
            f"Opened web socket connection with host {self.socket_host} on port {self.socket_port}"
        )

        return {'FINISHED'}

    @classmethod
    def close_connections(cls):
        method = bpy.context.window_manager.servo_animation.live_mode_method

        if (
            method == cls.METHOD_SERIAL
            and isinstance(cls._serial_connection, serial.Serial)
        ):
            cls._serial_connection.close()

        if (
            method == cls.METHOD_SOCKET
            and isinstance(cls._socket_connection, websocket.WebSocket)
        ):
            cls._socket_connection.close()

    def invoke(self, context, _event):
        servo_animation = context.window_manager.servo_animation

        self.method = servo_animation.live_mode_method

        self.serial_port = servo_animation.serial_port
        self.serial_baud = int(servo_animation.serial_baud)

        self.socket_host = servo_animation.socket_host
        self.socket_port = servo_animation.socket_port

        return self.execute(context)
