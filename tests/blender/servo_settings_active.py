import bpy

POSE_BONE = bpy.context.active_pose_bone

assert POSE_BONE is not None

bone = POSE_BONE.bone

assert bone.servo_settings.active is True
