from bpy.types import Panel
from ..export.json_export import JsonExport
from ..export.arduino_export import ArduinoExport
from ..utils.uart import UART_CONTROLLER, SERIAL_MODULE


class MenuPanel(Panel):
    bl_label = "Servo Positions"
    bl_idname = "TIMELINE_PT_servo"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'HEADER'

    def draw(self, context):
        layout = self.layout

        if SERIAL_MODULE:
            self.draw_live_mode(context)
            layout.separator()
        else:
            box = layout.box()
            box.label(text="Live mode not available.", icon="ERROR")
            box.label(text="Install missing dependency first.")

        col = layout.column()
        col.label(text="Export")
        row = col.row(align=True)
        row.operator(ArduinoExport.bl_idname, text="Arduino (.h)")
        row.operator(JsonExport.bl_idname, text="JSON (.json)")

    def draw_live_mode(self, context):
        UART_CONTROLLER.scan_serial_ports()
        servo_animation = context.window_manager.servo_animation

        if not UART_CONTROLLER.is_connected():
            servo_animation.live_mode = False

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        if not UART_CONTROLLER.has_serial_ports():
            box = layout.box()
            box.label(text="No serial port available", icon="ERROR")

        if servo_animation.live_mode:
            button_text = "Disconnect"
        else:
            button_text = "Connect"

        col = layout.column(heading="Live Mode")
        col.prop(servo_animation, "live_mode", toggle=True, text=button_text)

        col = layout.column(align=True)
        col.active = not servo_animation.live_mode
        col.prop(servo_animation, "serial_port")
        col.prop(servo_animation, "baud_rate")

        col = layout.column()
        col.active = servo_animation.live_mode
        col.prop(servo_animation, "position_jump_handling")
        col = layout.column()
        col.active = servo_animation.live_mode and servo_animation.position_jump_handling
        col.prop(servo_animation, "position_jump_threshold")
