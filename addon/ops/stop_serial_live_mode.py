from bpy.types import Operator
from ..ops.live_mode import LiveMode


class StopSerialLiveMode(Operator):
    bl_idname = "export_anim.stop_serial_live_mode"
    bl_label = "Stop Serial Live Mode"
    bl_description = "Stop sending live position values via the current serial connection"
    bl_options = {'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return (
            context.window_manager.servo_animation.live_mode
            and LiveMode.has_open_serial_connection()
        )

    def execute(self, _context):
        if LiveMode.has_open_serial_connection():
            serial_port = LiveMode.serial_connection.port
            message = f"Closed serial connection on port {serial_port}"

        LiveMode.serial_connection.close()
        LiveMode.serial_connection = None
        LiveMode.unregister_handler()

        if message:
            self.report({'INFO'}, message)

        return {'FINISHED'}
