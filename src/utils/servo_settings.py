def get_active_pose_bones(scene):
    pose_bones = []

    for obj in scene.objects:
        if obj.type != "ARMATURE":
            continue

        for pose_bone in obj.pose.bones:
            if pose_bone.bone.servo_settings.active:
                pose_bones.append(pose_bone)

    return pose_bones
