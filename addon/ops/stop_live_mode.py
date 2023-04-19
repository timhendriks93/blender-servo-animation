import bpy

from bpy.types import Operator
from .live_mode import LiveMode


class StopLiveMode(Operator):
    bl_idname = "export_anim.stop_live_mode"
    bl_label = "Stop Live Mode"
    bl_description = "Stop sending live position values via the current live mode connection"
    bl_options = {'INTERNAL', 'BLOCKING'}

    unexpected: bpy.props.BoolProperty()

    @staticmethod
    def display_warning(popup_self, _context):
        popup_self.layout.label(text="Please check your setup and start the live mode again.")

    def execute(self, context):
        method = context.window_manager.servo_animation.live_mode_method

        LiveMode.close_connections()
        LiveMode.unregister_handlers()

        if method == LiveMode.METHOD_SERIAL:
            connection_type = "serial"
        elif method == LiveMode.METHOD_SOCKET:
            connection_type = "web socket"
        else:
            self.report({'ERROR'}, "Unknown live mode method")

            return {'CANCELLED'}

        if self.unexpected:
            report_type = {'WARNING'}
            message = f"{connection_type.capitalize()} connection closed unexpectedly"
            context.window_manager.popup_menu(self.display_warning, title=message, icon='ERROR')
        else:
            report_type = {'INFO'}
            message = f"Closed {connection_type} connection"

        self.report(report_type, message)

        return {'FINISHED'}
