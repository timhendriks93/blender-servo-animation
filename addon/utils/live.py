import socket
import bpy
import serial

from ..utils.uart import get_serial_ports

METHOD_SERIAL = "SERIAL"
METHOD_WEB_SOCKET = "WEB_SOCKET"

COMMAND_START = 0x3C
COMMAND_END = 0x3E


class LiveModeController:
    positions = {}
    connection_method = None
    serial_connection = None
    tcp_connection = None
    handling = False

    def update_positions(self, _scene, _depsgraph):
        if self.handling:
            return
        self.handling = True
        bpy.ops.export_anim.live_mode()
        self.handling = False

    def send_position(self, servo_id, position):
        if position == self.positions.get(servo_id):
            return

        command = [COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [COMMAND_END]

        try:
            if self.connection_method == METHOD_SERIAL:
                self.serial_connection.write(command)
            elif self.connection_method == METHOD_WEB_SOCKET:
                self.tcp_connection.send(bytes(command))

            self.positions[servo_id] = position
        except (
            serial.SerialException, BlockingIOError, BrokenPipeError, ConnectionAbortedError,
            ConnectionResetError, InterruptedError, TypeError
        ):
            bpy.ops.export_anim.stop_live_mode()

    def open_serial_connection(self, port, baud_rate):
        try:
            self.serial_connection = serial.Serial(
                port=port, baudrate=baud_rate)
            self.connection_method = METHOD_SERIAL
            return True
        except (serial.SerialException, ValueError):
            return False

    def close_open_connection(self):
        if self.has_open_serial_connection():
            self.serial_connection.close()

        if self.has_open_web_socket_connection():
            self.tcp_connection.close()

        self.serial_connection = None
        self.tcp_connection = None
        self.connection_method = None
        self.positions = {}

    def has_open_serial_connection(self):
        return (
            isinstance(self.serial_connection, serial.Serial)
            and self.serial_connection.is_open
            and (
                self.serial_connection.port in get_serial_ports()
                or bpy.app.background
            )
        )

    def has_open_web_socket_connection(self):
        return isinstance(self.tcp_connection, socket.socket)

    def open_web_socket_connection(self, host, port):
        self.tcp_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_connection.settimeout(1)

        try:
            self.tcp_connection.connect((host, port))
            self.connection_method = METHOD_WEB_SOCKET
            return True
        except (socket.timeout, socket.error):
            return False


LIVE_MODE_CONTROLLER = LiveModeController()
