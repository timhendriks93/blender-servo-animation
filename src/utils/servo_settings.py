def get_active_pose_bones(scene):
    pose_bones = []

    for obj in scene.objects:
        if obj.type != "ARMATURE":
            continue

        for pose_bone in obj.pose.bones:
            if pose_bone.bone.servo_settings.active:
                pose_bones.append(pose_bone)

    return pose_bones


def range_limit_value(value, min_value, max_value):
    if min_value is not None and value < min_value:
        return min_value
    if max_value is not None and value > max_value:
        return max_value
    return value
