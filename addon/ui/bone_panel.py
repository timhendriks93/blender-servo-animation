
from bpy.types import Panel
from ..ops.calibrate_servo import CalibrateServo
from ..utils.converter import calculate_position
from ..utils.servo_settings import has_unique_servo_id


class BonePanel(Panel):
    bl_label = "Servo Settings"
    bl_idname = "BONE_PT_servo"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        return context.active_bone is not None

    def draw_header(self, context):
        servo_settings = context.active_bone.servo_settings
        layout = self.layout
        layout.prop(servo_settings, "active", text="")

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        servo_settings = context.active_bone.servo_settings

        layout.operator(CalibrateServo.bl_idname)
        layout.separator()

        self.draw_servo_id(servo_settings, context)

        layout.separator()

        col = layout.column(align=True)
        col.active = servo_settings.active
        col.prop(servo_settings, "position_min")
        col.prop(servo_settings, "position_max")

        col = layout.column(align=True)
        col.active = servo_settings.active
        col.prop(servo_settings, "threshold")

        layout.separator()

        col = layout.column(align=True)
        col.active = servo_settings.active
        col.prop(servo_settings, "neutral_angle")
        col.prop(servo_settings, "rotation_range")
        col.prop(servo_settings, "rotation_axis")

        layout.separator()

        col = layout.column()
        col.active = servo_settings.active
        col.prop(servo_settings, "multiplier")
        col.prop(servo_settings, "reverse_direction")

        if servo_settings.active and context.active_pose_bone is not None:
            self.draw_current(context)

    def draw_servo_id(self, servo_settings, context):
        layout = self.layout

        if servo_settings.active and not has_unique_servo_id(context.active_bone, context.scene):
            box = layout.box()
            box.label(text="Servo ID is not unique", icon="ERROR")

        col = layout.column()
        col.active = servo_settings.active
        col.prop(servo_settings, "servo_id")

    def draw_current(self, context):
        layout = self.layout
        box = layout.box()
        position, angle, in_range = calculate_position(
            context.active_pose_bone, None)

        if not in_range:
            box.label(text="Position is out of range", icon="ERROR")

        row = box.row()
        col = row.column(align=True)
        col.alignment = 'RIGHT'
        col.label(text="Frame:")
        col.label(text="Position value:")
        col.label(text="Angle:")
        col = row.column(align=True)
        col.label(text=str(context.scene.frame_current))
        col.label(text=str(position))
        col.label(text=str(angle) + "°")
