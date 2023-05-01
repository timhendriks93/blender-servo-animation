import math
import mathutils


def range_map(value, from_low, from_high, to_low, to_high):
    return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low


def matrix_visual(pose_bone):
    bone = pose_bone.bone

    matrix_pose_bone = pose_bone.matrix
    matrix_bone = bone.matrix_local

    if bone.parent:
        matrix_parent_bone = bone.parent.matrix_local.copy()
        matrix_parent_pose_bone = pose_bone.parent.matrix.copy()
    else:
        matrix_parent_bone = mathutils.Matrix()
        matrix_parent_pose_bone = mathutils.Matrix()

    matrix_bone_inverted = matrix_bone.copy().inverted()
    matrix_parent_pose_bone_inverted = matrix_parent_pose_bone.copy().inverted()

    return (
        matrix_bone_inverted
        @ matrix_parent_bone
        @ matrix_parent_pose_bone_inverted
        @ matrix_pose_bone
    )


def calculate_position(pose_bone, precision):
    servo_settings = pose_bone.bone.servo_settings
    rotation_euler = matrix_visual(pose_bone).to_euler()
    rotation_axis_index = int(servo_settings.rotation_axis)
    rotation_in_degrees = round(math.degrees(
        rotation_euler[rotation_axis_index]) * servo_settings.multiplier, 2)

    if servo_settings.reverse_direction:
        rotation_in_degrees = rotation_in_degrees * -1

    angle = servo_settings.neutral_angle - rotation_in_degrees
    position = round(range_map(angle, 0, servo_settings.rotation_range,
                               servo_settings.position_min, servo_settings.position_max), precision)

    check_min = servo_settings.position_min
    check_max = servo_settings.position_max

    if position < check_min or position > check_max:
        in_range = False
    else:
        in_range = True

    return position, round(angle, 2), in_range


def calculate_positions(context, precision):
    pose_bones = []
    scene = context.scene
    window_manager = context.window_manager
    start = scene.frame_start
    end = scene.frame_end + 1

    positions = {}

    for pose_bone in context.object.pose.bones:
        servo_settings = pose_bone.bone.servo_settings
        if servo_settings.active:
            pose_bones.append(pose_bone)
            positions[servo_settings.servo_id] = []

    if precision == 0:
        precision = None

    window_manager.progress_begin(min=start, max=end)

    for frame in range(start, end):
        scene.frame_set(frame)

        for pose_bone in pose_bones:
            bone = pose_bone.bone
            position, _angle, in_range = calculate_position(pose_bone, precision)

            if not in_range:
                raise RuntimeError(
                    f"Calculated position {position} for bone {bone.name} "
                    + f"is out of range at frame {frame}."
                )

            positions[bone.servo_settings.servo_id].append(position)

        window_manager.progress_update(frame)

    window_manager.progress_end()

    return positions
