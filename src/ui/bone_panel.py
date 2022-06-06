
from bpy.types import Panel
from ..utils.converter import calculate_position
from ..utils.servo_settings import has_unique_servo_id
from ..utils.uart import UART_CONTROLLER


class BonePanel(Panel):
    bl_label = "Servo Settings"
    bl_idname = "BONE_PT_servo"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        return context.active_bone is not None

    def draw_servo_id(self, servo_settings, context):
        layout = self.layout
        split = layout.split()
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Servo ID")
        col = split.column(align=True)
        col.prop(servo_settings, "servo_id", text="")

        if has_unique_servo_id(context.active_bone, context.scene) is False:
            box = layout.box()
            box.label(text="Servo ID is not unique", icon="ERROR")

    def draw(self, context):
        layout = self.layout
        servo_settings = context.active_bone.servo_settings

        split = layout.split()
        col = split.column()
        col = split.column(align=True)
        col.prop(servo_settings, "active")

        if not servo_settings.active:
            return

        self.draw_servo_id(servo_settings, context)

        split = layout.split()
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Position Min")
        col.label(text="Max")
        col = split.column(align=True)
        col.prop(servo_settings, "position_min", text="")
        col.prop(servo_settings, "position_max", text="")
        col.prop(servo_settings, "set_position_limits")

        if servo_settings.set_position_limits:
            self.draw_limit(servo_settings)

        split = layout.split()
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Neutral Angle")
        col.label(text="Rotation Range")
        col = split.column(align=True)
        col.prop(servo_settings, "neutral_angle", text="")
        col.prop(servo_settings, "rotation_range", text="")

        split = layout.split()
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Rotation Axis")
        col.label(text="Multiplier")
        col = split.column(align=True)
        col.prop(servo_settings, "rotation_axis", text="")
        col.prop(servo_settings, "multiplier", text="")
        col.prop(servo_settings, "reverse_direction")

        if context.active_pose_bone is not None:
            self.draw_current(servo_settings.servo_id, context)

    def draw_limit(self, servo_settings):
        layout = self.layout
        split = layout.split()
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Limit Start")
        col.label(text="End")
        col = split.column(align=True)
        col.prop(servo_settings, "position_limit_start", text="")
        col.prop(servo_settings, "position_limit_end", text="")

    def draw_current(self, servo_id, context):
        layout = self.layout
        position, in_range = calculate_position(
            context.active_pose_bone, None)

        split = layout.split()
        col = split.column()
        col.alignment = 'RIGHT'
        col.label(text="Current frame")
        col.label(text="Current position value")
        col = split.column(align=True)
        col.label(text=str(context.scene.frame_current))
        col.label(text=str(position))

        if not in_range:
            box = layout.box()
            box.label(text="Position is out of range", icon="ERROR")
        elif UART_CONTROLLER.is_connected():
            UART_CONTROLLER.send_position(servo_id, position)
