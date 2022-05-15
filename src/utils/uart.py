import sys
import glob
import time
import serial
import bpy

from ..utils.converter import calculate_position
from ..utils.servo_settings import get_active_pose_bones

COMMAND_START = 0x3C
COMMAND_END = 0x3E


class UartController:
    serial_ports = []
    serial_connection = None
    frame = None
    positions = {}

    def handle_frame_jump(self, scene):
        diffs = []
        new_positions = {}
        for pose_bone in get_active_pose_bones(scene):
            position, in_range = calculate_position(pose_bone, None)
            if in_range:
                servo_id = pose_bone.bone.servo_settings.servo_id
                new_positions[servo_id] = position
                diffs.append(abs(position - self.positions[servo_id]))
        steps = max(diffs)
        print(f"start frame jump handling with {steps} steps")
        window_manager = bpy.context.window_manager
        window_manager.progress_begin(0, steps)
        for step in range(steps):
            window_manager.progress_update(step)
            for servo_id, position in new_positions.items():
                target_position = self.positions[servo_id]
                if position == target_position:
                    continue
                if position > target_position:
                    new_position = target_position + 1
                else:
                    new_position = target_position - 1
                self.send_position(servo_id, new_position)
            time.sleep(.01)

        window_manager.progress_end()
        print("finished frame jump handling")

    def on_frame_change_post(self, scene):
        if not self.is_connected():
            return

        frame_jump = self.frame is not None and abs(
            scene.frame_current - self.frame) > 10

        if frame_jump:
            self.handle_frame_jump(scene)
        else:
            for pose_bone in get_active_pose_bones(scene):
                position, in_range = calculate_position(pose_bone, None)

                if in_range:
                    self.send_position(
                        pose_bone.bone.servo_settings.servo_id, position)

        self.frame = scene.frame_current

    def send_position(self, servo_id, position):
        command = [COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [COMMAND_END]

        try:
            self.serial_connection.write(command)
            self.positions[servo_id] = position
            print(f"Sent {servo_id} - {position}")
        except serial.SerialException:
            self.close_serial_connection()

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

    def open_serial_connection(self):
        servo_animation = bpy.context.window_manager.servo_animation
        port = servo_animation.serial_port
        baud_rate = servo_animation.baud_rate
        print(
            f"Opening Serial Connection for port {port} with baud rate {baud_rate}")
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


uart_controller = UartController()
