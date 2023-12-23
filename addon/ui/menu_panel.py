from bpy.types import Panel
from ..ops.json_export import JsonExport
from ..ops.arduino_export import ArduinoExport
from ..ops.servoanim_export import ServoanimExport
from ..ops.stop_live_mode import StopLiveMode
from ..ops.install_dependencies import InstallDependencies
from ..ops.start_live_mode import StartLiveMode
from ..utils.live_mode import LiveMode


class MenuPanel(Panel):
    bl_label = "Servo Positions"
    bl_idname = "TIMELINE_PT_servo"
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'HEADER'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column()
        col.label(text="Live Mode")

        if InstallDependencies.installed():
            self.draw_live_mode(context, layout, col)
        else:
            self.draw_live_mode_deps(col)

        col = layout.column()
        col.label(text="Export")
        row = col.row(align=True)
        row.operator(ArduinoExport.bl_idname, text="Arduino (.h)")
        row.operator(JsonExport.bl_idname, text="JSON (.json)")
        row.operator(ServoanimExport.bl_idname, text="Servoanim (.servoanim)")

    @classmethod
    def draw_live_mode(cls, context, layout, col):
        servo_animation = context.window_manager.servo_animation
        live_mode_is_connected = LiveMode.is_connected()

        if live_mode_is_connected:
            col.operator(StopLiveMode.bl_idname,
                         text="Disconnect", depress=True)
        else:
            col.operator(StartLiveMode.bl_idname, text="Connect")

        col = layout.column(align=True)
        col.enabled = not live_mode_is_connected
        col.prop(servo_animation, "live_mode_method")

        if servo_animation.live_mode_method == LiveMode.METHOD_SERIAL:
            sub = col.column(align=True)
            sub.prop(servo_animation, "serial_port")
            col.prop(servo_animation, "serial_baud")

            if servo_animation.serial_port == 'NONE':
                sub.enabled = False

        elif servo_animation.live_mode_method == LiveMode.METHOD_SOCKET:
            col.prop(servo_animation, "socket_host")
            col.prop(servo_animation, "socket_port")
            col.prop(servo_animation, "socket_path")

        col = layout.column()
        col.prop(servo_animation, "position_jump_handling")

    @classmethod
    def draw_live_mode_deps(cls, col):
        col.label(text="You are missing dependencies", icon="ERROR")
        col.operator(InstallDependencies.bl_idname, text="Install dependencies")
