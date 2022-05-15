from bpy.types import Menu

from .json_export import ServoAnimationJsonExport
from .arduino_export import ServoAnimationArduinoExport
from .live import live_controller


class ServoAnimationTimelineMenu(Menu):
    bl_label = "Servo Animation"
    bl_idname = "SERVO_ANIM_MT_timeline"

    def draw(self, context):
        live_controller.scan_serial_ports()
        servo_animation = context.window_manager.servo_animation

        if not live_controller.is_connected():
            servo_animation.live_mode = False

        layout = self.layout
        layout.operator(ServoAnimationArduinoExport.bl_idname)
        layout.operator(ServoAnimationJsonExport.bl_idname)
        layout.separator()
        layout.prop_menu_enum(servo_animation, "baud_rate")
        layout.prop_menu_enum(servo_animation, "serial_port")
        layout.prop(servo_animation, "live_mode")
