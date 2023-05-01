import bpy

from bpy.types import Operator
from ..utils.live_mode import LiveMode


def send_position_min(self, context):
    LiveMode.send_position(
        context.active_bone.servo_settings.servo_id,
        self.position_min
    )

def send_position_max(self, context):
    LiveMode.send_position(
        context.active_bone.servo_settings.servo_id,
        self.position_max
    )

def toggle_position(self, context):
    if self.toggle == 'MIN':
        send_position_min(self, context)
    else:
        send_position_max(self, context)


class CalibrateServo(Operator):
    bl_idname = "servo_animation.calibrate"
    bl_label = "Calibrate servo"
    bl_description = "Calibrate servo during live mode by setting the min and max position values"
    bl_options = {'INTERNAL', 'BLOCKING'}

    toggle: bpy.props.EnumProperty(
        name="Position type",
        items=[
            ('MIN', 'Min position', ''),
            ('MAX', 'Max position', '')
        ],
        default='MIN',
        options={'SKIP_SAVE'},
        update=toggle_position
    )
    position_min: bpy.props.IntProperty(
        name="Position value",
        min=0,
        max=10000,
        description="The minimum position value before the servo physically stops moving",
        update=send_position_min
    )
    position_max: bpy.props.IntProperty(
        name="Position value",
        min=0,
        max=10000,
        description="The maximum position value before the servo physically stops moving",
        update=send_position_max
    )

    @classmethod
    def poll(cls, context):
        return context.active_bone and LiveMode.is_connected()

    def execute(self, context):
        servo_settings = context.active_bone.servo_settings
        servo_settings.position_min = self.position_min
        servo_settings.position_max = self.position_max

        self.stop()

        return {'FINISHED'}

    def __del__(self):
        self.stop()

    @classmethod
    def stop(cls):
        if not LiveMode.is_handler_enabled():
            LiveMode.enable_handler()
            LiveMode.handler(None, None)

    def invoke(self, context, _event):
        servo_id = context.active_bone.servo_settings.servo_id
        last_position = LiveMode.get_last_position(servo_id)

        if last_position is None:
            self.report({'ERROR'}, f"Could not find last position for servo with ID {servo_id}")

            return {'CANCELLED'}

        self.position_min = last_position
        self.position_max = last_position

        LiveMode.disable_handler()

        return context.window_manager.invoke_props_dialog(self)

    def draw(self, _context):
        layout = self.layout
        layout.use_property_split = True

        box = layout.box()
        box.label(text="Changes move servo immediately", icon="ERROR")

        layout.separator()

        col = self.layout.column(align=True)
        col.prop(self, "toggle")

        if self.toggle == 'MIN':
            col.prop(self, "position_min")
        else:
            col.prop(self, "position_max")

        layout.separator()
