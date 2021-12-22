import bpy

from bpy.types import Panel
from .converter import SERVOANIMATION_converter


class SERVOANIMATION_PT_servo_settings(Panel):
    bl_label = "Servo Settings"
    bl_idname = "BONE_PT_servo"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        return (context.active_bone is not None)

    def draw(self, context):
        layout = self.layout
        servo_settings = context.active_bone.servo_settings

        split = layout.split()
        col = split.column()
        col = split.column(align=True)
        col.prop(servo_settings, "active")

        if servo_settings.active == True:
            split = layout.split()
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text="Position Min")
            col.label(text="Max")
            col = split.column(align=True)
            col.prop(servo_settings, "position_min", text="")
            col.prop(servo_settings, "position_max", text="")
            col.prop(servo_settings, "set_position_limits")

            if servo_settings.set_position_limits == True:
                split = layout.split()
                col = split.column()
                col.alignment = 'RIGHT'
                col.label(text="Limit Start")
                col.label(text="End")
                col = split.column(align=True)
                col.prop(servo_settings, "position_limit_start", text="")
                col.prop(servo_settings, "position_limit_end", text="")

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
                converter = SERVOANIMATION_converter()
                position, in_range = converter.calculate_position(
                    context.active_pose_bone, None)

                split = layout.split()
                col = split.column()
                col.alignment = 'RIGHT'
                col.label(text="Current frame")
                col.label(text="Current position value")
                col = split.column(align=True)
                col.label(text=str(context.scene.frame_current))
                col.label(text=str(position))

                if in_range == False:
                    box = layout.box()
                    box.label(text="Position is out of range", icon="ERROR")
