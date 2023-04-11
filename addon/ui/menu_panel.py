from bpy.types import Panel
from ..ops.json_export import JsonExport
from ..ops.arduino_export import ArduinoExport
from ..ops.start_serial_live_mode import StartSerialLiveMode
from ..ops.start_web_socket_live_mode import StartWebSocketLiveMode
from ..ops.stop_serial_live_mode import StopSerialLiveMode
from ..ops.stop_web_socket_live_mode import StopWebSocketLiveMode
from ..utils.live import LIVE_MODE_CONTROLLER


class MenuPanel(Panel):
    bl_label = "Servo Positions"
    bl_idname = "TIMELINE_PT_servo"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'HEADER'

    def draw(self, context):
        servo_animation = context.window_manager.servo_animation

        if (
            not LIVE_MODE_CONTROLLER.has_open_serial_connection()
            and not LIVE_MODE_CONTROLLER.has_open_web_socket_connection()
        ):
            servo_animation.live_mode = False

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.label(text="Live Mode")

        if servo_animation.live_mode:
            if servo_animation.live_mode_method == StartSerialLiveMode.METHOD:
                col.operator(StopSerialLiveMode.bl_idname,
                         text="Disconnect", depress=True)
            elif servo_animation.live_mode_method == StartWebSocketLiveMode.METHOD:
                col.operator(StopWebSocketLiveMode.bl_idname,
                         text="Disconnect", depress=True)
        elif servo_animation.live_mode_method == StartSerialLiveMode.METHOD:
            col.operator(StartSerialLiveMode.bl_idname, text="Connect")
        elif servo_animation.live_mode_method == StartWebSocketLiveMode.METHOD:
            col.operator(StartWebSocketLiveMode.bl_idname, text="Connect")

        col = layout.column(align=True)
        col.enabled = not servo_animation.live_mode
        col.prop(servo_animation, "live_mode_method")

        if servo_animation.live_mode_method == StartSerialLiveMode.METHOD:
            col.prop(servo_animation, "serial_port")
            col.prop(servo_animation, "baud_rate")
        elif servo_animation.live_mode_method == StartWebSocketLiveMode.METHOD:
            col.prop(servo_animation, "socket_ip")
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
