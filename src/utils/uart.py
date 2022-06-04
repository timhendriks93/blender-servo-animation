import sys
import glob
import time
import serial
import bpy

from ..utils.converter import calculate_position
from ..utils.servo_settings import get_active_pose_bones

COMMAND_START = 0x3C
COMMAND_END = 0x3E

COMMAND_TYPE_HANDSHAKE = 0
COMMAND_TYPE_MOVE_SERVO = 1
COMMAND_TYPE_FRAME_JUMP = 2


class UartController:
    serial_ports = []
    serial_connection = None
    frame = None
    positions = {}

    def on_frame_change_post(self, scene):
        if not self.is_connected():
            return

        frame_jump = self.frame is not None and abs(
            scene.frame_current - self.frame) > 10

        if frame_jump:
            self.handle_frame_jump(scene)
        else:
            self.handle_default(scene)

        self.frame = scene.frame_current

    def send_position(self, servo_id, position):
        command = [COMMAND_START, COMMAND_TYPE_MOVE_SERVO, servo_id]
        command += position.to_bytes(2, 'big')
        command += [COMMAND_END]

        try:
            self.serial_connection.write(command)
            self.positions[servo_id] = position
        except serial.SerialException:
            self.close_serial_connection()

    def handle_default(self, scene):
        for pose_bone in get_active_pose_bones(scene):
            bone = pose_bone.bone
            servo_id = bone.servo_settings.servo_id
            previous_position = self.positions.get(servo_id)
            position, in_range = calculate_position(pose_bone, None)

            if not in_range or previous_position == position:
                continue

            self.send_position(servo_id, position)

    def handle_frame_jump(self, scene):
        diffs = []
        target_positions = {}

        for pose_bone in get_active_pose_bones(scene):
            target_position, in_range = calculate_position(pose_bone, None)
            if in_range:
                servo_id = pose_bone.bone.servo_settings.servo_id
                target_positions[servo_id] = target_position
                diffs.append(abs(target_position - self.positions[servo_id]))

        steps = max(diffs)

        if bpy.context.screen.is_animation_playing:
            bpy.ops.screen.animation_cancel(restore_frame=False)

        window_manager = bpy.context.window_manager
        window_manager.progress_begin(0, steps)

        for step in range(steps):
            window_manager.progress_update(step)
            for servo_id, target_position in target_positions.items():
                previous_position = self.positions[servo_id]
                if target_position == previous_position:
                    continue
                if target_position > previous_position:
                    new_position = previous_position + 1
                else:
                    new_position = previous_position - 1
                self.send_position(servo_id, new_position)
            time.sleep(.01)

        window_manager.progress_end()

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

    def has_serial_ports(self):
        return len(self.get_serial_ports()) > 0

    def open_serial_connection(self):
        servo_animation = bpy.context.window_manager.servo_animation
        port = servo_animation.serial_port
        baud_rate = servo_animation.baud_rate
        print(
            f"Opening Serial Connection for port {port} with baud rate {baud_rate}")
        try:
            self.serial_connection = serial.Serial(port=port, baudrate=baud_rate)
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


UART_CONTROLLER = UartController()
