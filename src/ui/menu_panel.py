
from bpy.types import Panel
from ..export.json_export import JsonExport
from ..export.arduino_export import ArduinoExport
from ..utils.uart import UART_CONTROLLER


class MenuPanel(Panel):
    bl_label = "Servo Animation"
    bl_idname = "TIMELINE_PT_servo"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        UART_CONTROLLER.scan_serial_ports()
        servo_animation = context.window_manager.servo_animation

        if not UART_CONTROLLER.is_connected():
            servo_animation.live_mode = False

        layout = self.layout

        split = layout.split()
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Live Mode")
        col = split.column(align=True)
        col.prop(servo_animation, "live_mode", text="Enable")
        col.prop_menu_enum(servo_animation, "serial_port")
        col.prop_menu_enum(servo_animation, "baud_rate")

        layout.separator()

        split = layout.split()
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Export")
        col = split.column(align=True)
        col.operator(ArduinoExport.bl_idname, text="Arduino (.h)")
        col.operator(JsonExport.bl_idname, text="JSON (.json)")
