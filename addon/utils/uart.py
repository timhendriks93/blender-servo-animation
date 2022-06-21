import bpy
import serial
import serial.tools.list_ports

COMMAND_START = 0x3C
COMMAND_END = 0x3E


class UartController:
    positions = {}
    serial_ports = []
    serial_connection = None
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
            self.serial_connection.write(command)
            self.positions[servo_id] = position
        except serial.SerialException:
            bpy.ops.export_anim.stop_live_mode()

    def scan_serial_ports(self):
        self.serial_ports.clear()

        for port in serial.tools.list_ports.comports():
            self.serial_ports.append(port.device)

    def get_serial_ports(self):
        return self.serial_ports

    def open_serial_connection(self, port, baud_rate):
        try:
            self.serial_connection = serial.Serial(
                port=port, baudrate=baud_rate)
            return True
        except (serial.SerialException, ValueError):
            return False

    def close_serial_connection(self):
        if self.is_connected():
            self.serial_connection.close()

        self.serial_connection = None
        self.positions = {}

    def is_connected(self):
        return (
            isinstance(self.serial_connection, serial.Serial)
            and self.serial_connection.is_open
            and (
                self.serial_connection.port in self.serial_ports
                or bpy.app.background
            )
        )


UART_CONTROLLER = UartController()
