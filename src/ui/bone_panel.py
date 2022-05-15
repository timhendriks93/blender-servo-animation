
from bpy.types import Panel
from ..utils.converter import calculate_position


class BonePanel(Panel):
    bl_label = "Servo Settings"
    bl_idname = "BONE_PT_servo"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "bone"

    @classmethod
    def poll(cls, context):
        return context.active_bone is not None

    def draw(self, context):
        layout = self.layout
        servo_settings = context.active_bone.servo_settings

        split = layout.split()
        col = split.column()
        col = split.column(align=True)
        col.prop(servo_settings, "active")

        if servo_settings.active:
            split = layout.split()
            col = split.column()
            col.alignment = 'RIGHT'
            col.label(text="Servo ID")
            col = split.column(align=True)
            col.prop(servo_settings, "servo_id", text="")

            if self.has_unique_servo_id(context.active_bone, context.scene) is False:
                box = layout.box()
                box.label(text="Servo ID is not unique", icon="ERROR")

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

    def has_unique_servo_id(self, bone, scene):
        for obj in scene.objects:
            if obj.type != "ARMATURE":
                continue
            for pose_bone in obj.pose.bones:
                servo_settings = pose_bone.bone.servo_settings
                if not servo_settings.active or pose_bone.bone.name == bone.name:
                    continue
                if servo_settings.servo_id == bone.servo_settings.servo_id:
                    return False
        return True
