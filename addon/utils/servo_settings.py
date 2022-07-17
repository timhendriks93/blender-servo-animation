def get_active_pose_bones(scene):
    pose_bones = []

    for obj in scene.objects:
        if obj.type != "ARMATURE":
            continue

        for pose_bone in obj.pose.bones:
            if pose_bone.bone.servo_settings.active:
                pose_bones.append(pose_bone)

    return pose_bones


def get_pose_bone_by_servo_id(servo_id, scene):
    for pose_bone in get_active_pose_bones(scene):
        if pose_bone.bone.servo_settings.servo_id == servo_id:
            return pose_bone

    return None


def range_limit_value(value, min_value, max_value):
    if min_value is not None and value < min_value:
        return min_value
    if max_value is not None and value > max_value:
        return max_value
    return value


def has_unique_servo_id(bone, scene):
    for pose_bone in get_active_pose_bones(scene):
        if pose_bone.bone.name == bone.name:
            continue
        if pose_bone.bone.servo_settings.servo_id == bone.servo_settings.servo_id:
            return False

    return True
