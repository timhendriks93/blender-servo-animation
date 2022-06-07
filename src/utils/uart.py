import time
import serial
import serial.tools.list_ports
import bpy

from ..utils.converter import calculate_position
from ..utils.servo_settings import get_active_pose_bones

COMMAND_START = 0x3C
COMMAND_END = 0x3E

COMMAND_TYPE_HANDSHAKE = 0
COMMAND_TYPE_MOVE_SERVO = 1
COMMAND_TYPE_POSITION_JUMP = 2


class UartController:
    positions = {}
    serial_ports = {}
    serial_connection = None

    @classmethod
    def timer(cls):
        if not bpy.context.screen.is_animation_playing:
            UART_CONTROLLER.update_positions(bpy.context.scene)
        return .03

    def update_positions(self, scene):
        if not self.is_connected():
            return

        diffs = []
        target_positions = {}
        servo_animation = bpy.context.window_manager.servo_animation

        for pose_bone in get_active_pose_bones(scene):
            target_position, in_range = calculate_position(pose_bone, None)

            if not in_range:
                continue

            servo_id = pose_bone.bone.servo_settings.servo_id
            target_positions[servo_id] = target_position

            if servo_id in self.positions:
                diffs.append(abs(target_position - self.positions[servo_id]))

        if len(diffs) > 0:
            steps = max(diffs)
        else:
            steps = 0

        if steps > 20 and servo_animation.position_jump_handling:
            self.handle_position_jump(target_positions, steps)
        else:
            self.handle_default(target_positions)

    def handle_default(self, target_positions):
        for servo_id, target_position in target_positions.items():
            self.send_position(servo_id, target_position)

    def handle_position_jump(self, target_positions, steps):
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

    def send_position(self, servo_id, position):
        if position == self.positions.get(servo_id):
            return

        command = [COMMAND_START, COMMAND_TYPE_MOVE_SERVO, servo_id]
        command += position.to_bytes(2, 'big')
        command += [COMMAND_END]

        try:
            self.serial_connection.write(command)
            self.positions[servo_id] = position
        except serial.SerialException:
            self.close_serial_connection()

    def scan_serial_ports(self):
        self.serial_ports.clear()

        for port in serial.tools.list_ports.comports():
            self.serial_ports[port.device] = port

    def get_serial_ports(self):
        return self.serial_ports

    def has_serial_ports(self):
        return len(self.get_serial_ports()) > 0

    def open_serial_connection(self):
        servo_animation = bpy.context.window_manager.servo_animation
        port = servo_animation.serial_port
        baud_rate = servo_animation.baud_rate
        print(
            f"Opening serial connection for port {port} with baud rate {baud_rate}")
        try:
            self.serial_connection = serial.Serial(
                port=port, baudrate=baud_rate)
            return True
        except serial.SerialException:
            return False

    def close_serial_connection(self):
        if self.is_connected():
            print("Closing serial connection")
            self.serial_connection.close()
        self.serial_connection = None
        self.positions = {}

    def is_connected(self):
        return (
            isinstance(self.serial_connection, serial.Serial)
            and self.serial_connection.is_open
            and self.serial_connection.port in self.serial_ports
        )


UART_CONTROLLER = UartController()
