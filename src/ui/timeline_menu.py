from bpy.types import Menu

from ..export.json_export import JsonExport
from ..export.arduino_export import ArduinoExport
from ..utils.uart import uart_controller


class TimelineMenu(Menu):
    bl_label = "Servo Animation"
    bl_idname = "SERVO_ANIM_MT_timeline"

    def draw(self, context):
        uart_controller.scan_serial_ports()
        servo_animation = context.window_manager.servo_animation

        if not uart_controller.is_connected():
            servo_animation.live_mode = False

        layout = self.layout
        layout.operator(ArduinoExport.bl_idname)
        layout.operator(JsonExport.bl_idname)
        layout.separator()
        layout.prop_menu_enum(servo_animation, "baud_rate")
        layout.prop_menu_enum(servo_animation, "serial_port")
        layout.prop(servo_animation, "live_mode")
