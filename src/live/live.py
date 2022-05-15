import sys
import glob
import serial

from ..utils.converter import calculate_position
from ..utils.servo_settings import get_active_pose_bones

COMMAND_START = 0x3C
COMMAND_END = 0x3E


class Live:
    serial_ports = []
    serial_connection = None
    current_frame = 0
    cache = {}

    def scan_serial_ports(self):
        self.serial_ports.clear()

        if sys.platform.startswith('win'):
            ports = [f"COM{i + 1}" for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            ports = []

        for port in ports:
            try:
                tmp_connection = serial.Serial(port)
                tmp_connection.close()
                self.serial_ports.append(port)
            except (OSError, serial.SerialException):
                pass

    def get_serial_ports(self):
        return self.serial_ports

    def on_frame_change_pre(self, _scene):
        if not self.is_connected():
            return
        # for obj in scene.objects:
        #     if obj.type != "ARMATURE":
        #         continue
        #     for pose_bone in obj.pose.bones:
        #         servo_settings = pose_bone.bone.servo_settings
        #         if not servo_settings.active or self.cache.has_key(servo_settings.servo_id):
        #             continue
        #         position, _ = self.converter.calculate_position(
        #             pose_bone, None)
        #         self.cache[servo_settings.servo_id] = position

    def on_frame_change_post(self, scene):
        if not self.is_connected():
            return

        for pose_bone in get_active_pose_bones(scene):
            servo_settings = pose_bone.bone.servo_settings

            if not servo_settings.active:
                continue

            position, in_range = calculate_position(
                pose_bone, None)

            if not in_range:
                continue

            self.send_position(servo_settings.servo_id, position)

    def send_position(self, servo_id, position):
        command = [COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [COMMAND_END]

        try:
            self.serial_connection.write(command)
            print(f"Sent {servo_id} - {position}")
        except serial.SerialException:
            self.close_serial_connection()

    def open_serial_connection(self, port, baud_rate):
        print(f"Opening Serial Connection for port {port}")
        try:
            self.serial_connection = serial.Serial(port, baud_rate)
            return True
        except serial.SerialException:
            return False

    def close_serial_connection(self):
        if self.is_connected():
            print("Closing serial connection")
            self.serial_connection.close()
        self.serial_connection = None

    def is_connected(self):
        return isinstance(self.serial_connection, serial.Serial) and self.serial_connection.is_open


live_controller = Live()
