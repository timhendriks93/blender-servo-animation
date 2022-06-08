from bpy.types import Panel
from ..export.json_export import JsonExport
from ..export.arduino_export import ArduinoExport
from ..utils.uart import UART_CONTROLLER


class MenuPanel(Panel):
    bl_label = "Servo Positions"
    bl_idname = "TIMELINE_PT_servo"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        UART_CONTROLLER.scan_serial_ports()
        servo_animation = context.window_manager.servo_animation

        if not UART_CONTROLLER.is_connected():
            servo_animation.live_mode = False

        layout = self.layout
        layout.use_property_split = True

        if not UART_CONTROLLER.has_serial_ports():
            box = layout.box()
            box.label(text="No serial port available", icon="ERROR")

        col = layout.column()
        col.prop(servo_animation, "live_mode")

        col = layout.column(align=True)
        col.active = servo_animation.live_mode
        col.prop(servo_animation, "serial_port")
        col.prop(servo_animation, "baud_rate")

        col = layout.column()
        col.active = servo_animation.live_mode
        col.prop(servo_animation, "position_jump_handling")

        layout.separator()

        col = layout.column()
        col.label(text="Export")
        row = col.row(align=True)
        row.operator(ArduinoExport.bl_idname, text="Arduino (.h)")
        row.operator(JsonExport.bl_idname, text="JSON (.json)")