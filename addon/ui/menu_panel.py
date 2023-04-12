from bpy.types import Panel
from ..ops.json_export import JsonExport
from ..ops.arduino_export import ArduinoExport
from ..ops.stop_live_mode import StopLiveMode
from ..ops.live_mode import LiveMode


class MenuPanel(Panel):
    bl_label = "Servo Positions"
    bl_idname = "TIMELINE_PT_servo"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'HEADER'

    def draw(self, context):
        servo_animation = context.window_manager.servo_animation

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.label(text="Live Mode")

        live_mode_is_active = LiveMode.is_active()

        if live_mode_is_active:
            col.operator(StopLiveMode.bl_idname,
                         text="Disconnect", depress=True)
        else:
            col.operator(LiveMode.bl_idname, text="Connect")

        col = layout.column(align=True)
        col.enabled = not live_mode_is_active
        col.prop(servo_animation, "live_mode_method")

        if servo_animation.live_mode_method == LiveMode.METHOD_SERIAL:
            col.prop(servo_animation, "serial_port")
            col.prop(servo_animation, "serial_baud")
        elif servo_animation.live_mode_method == LiveMode.METHOD_SOCKET:
            col.prop(servo_animation, "socket_host")
            col.prop(servo_animation, "socket_port")

        col = layout.column()
        col.prop(servo_animation, "position_jump_handling")
        col = layout.column()
        col.active = servo_animation.position_jump_handling
        col.prop(servo_animation, "position_jump_threshold")

        layout.separator()

        col = layout.column()
        col.label(text="Export")
        row = col.row(align=True)
        row.operator(ArduinoExport.bl_idname, text="Arduino (.h)")
        row.operator(JsonExport.bl_idname, text="JSON (.json)")
