import bpy
import serial

from bpy.types import Operator
from ..ops.live_mode import LiveMode


class StartSerialLiveMode(Operator):
    bl_idname = "export_anim.start_serial_live_mode"
    bl_label = "Start Serial Live Mode"
    bl_description = "Start sending live position values via the given serial connection"
    bl_options = {'INTERNAL'}

    serial_port: bpy.props.StringProperty()
    baud_rate: bpy.props.IntProperty()

    @classmethod
    def poll(cls, context):
        return (
            not context.window_manager.servo_animation.live_mode
            and context.window_manager.servo_animation.serial_port != ""
            and not LiveMode.has_open_serial_connection()
        )

    def execute(self, context):
        servo_animation = context.window_manager.servo_animation
        servo_animation.live_mode_method = LiveMode.METHOD_SERIAL

        try:
            LiveMode.serial_connection = serial.Serial(
                port=self.serial_port, baudrate=self.baud_rate)
        except (serial.SerialException, ValueError):
            servo_animation.live_mode = False
            self.report(
                {'ERROR'},
                f"Failed to open serial connection on port {self.serial_port} with baud rate {self.baud_rate}"
            )

            return {'CANCELLED'}

        LiveMode.register_handler()

        self.report(
            {'INFO'},
            f"Opened serial connection on port {self.serial_port} with baud rate {self.baud_rate}"
        )

        return {'FINISHED'}

    def invoke(self, context, _event):
        servo_animation = context.window_manager.servo_animation
        self.serial_port = servo_animation.serial_port
        self.baud_rate = int(servo_animation.baud_rate)

        return self.execute(context)
