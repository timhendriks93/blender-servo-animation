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


def calculate_position(pose_bone):
    servo_settings = pose_bone.bone.servo_settings
    rotation_euler = matrix_visual(pose_bone).to_euler()
    rotation_axis_index = int(servo_settings.rotation_axis)
    rotation_in_degrees = round(math.degrees(
        rotation_euler[rotation_axis_index]) * servo_settings.multiplier, 2)

    if servo_settings.reverse_direction:
        rotation_in_degrees = rotation_in_degrees * -1

    angle = servo_settings.neutral_angle - rotation_in_degrees
    position = round(range_map(angle, 0, servo_settings.rotation_range,
                     servo_settings.position_min, servo_settings.position_max))

    in_range = servo_settings.position_min <= position <= servo_settings.position_max

    return position, round(angle, 2), in_range


def calculate_positions(context, skip_duplicates):
    pose_bones = []
    positions = []
    last_positions = {}
    window_manager = context.window_manager
    start = context.scene.frame_start
    end = context.scene.frame_end + 1

    window_manager.progress_begin(min=start, max=end)

    for pose_bone in context.object.pose.bones:
        servo_settings = pose_bone.bone.servo_settings
        if servo_settings.active:
            pose_bones.append(pose_bone)

    for frame in range(start, end):
        frame_positions = calculate_frame_positions(
            context, pose_bones, last_positions, skip_duplicates, frame)
        positions.append(frame_positions)
        window_manager.progress_update(frame)

    window_manager.progress_end()

    return positions


def calculate_frame_positions(context, pose_bones, last_positions, skip_duplicates, frame):
    frame_positions = {}

    context.scene.frame_set(frame)

    for pose_bone in pose_bones:
        bone = pose_bone.bone
        servo_id = bone.servo_settings.servo_id
        position, _angle, in_range = calculate_position(pose_bone)

        if servo_id not in last_positions:
            last_positions[servo_id] = None

        if not in_range or (skip_duplicates and last_positions[servo_id] == position):
            continue

        frame_positions[servo_id] = position
        last_positions[servo_id] = position

    return frame_positions
