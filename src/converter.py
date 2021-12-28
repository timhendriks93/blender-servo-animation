import math
import mathutils


class ServoAnimationConverter:
    positions = {}

    def range_map(self, value, from_low, from_high, to_low, to_high):
        return (value - from_low) * (to_high - to_low) / (from_high - from_low) + to_low

    def matrix_visual(self, pose_bone):
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

    def calculate_position(self, pose_bone, precision):
        servo_settings = pose_bone.bone.servo_settings
        rotation_euler = self.matrix_visual(pose_bone).to_euler()
        rotation_axis_index = int(servo_settings.rotation_axis)
        rotation_in_degrees = round(math.degrees(
            rotation_euler[rotation_axis_index]) * servo_settings.multiplier, 2)

        if servo_settings.reverse_direction:
            rotation_in_degrees = rotation_in_degrees * -1

        angle = servo_settings.neutral_angle - rotation_in_degrees
        position = round(self.range_map(angle, 0, servo_settings.rotation_range,
                         servo_settings.position_min, servo_settings.position_max), precision)

        check_min = servo_settings.position_min
        check_max = servo_settings.position_max

        if servo_settings.set_position_limits:
            check_min = servo_settings.position_limit_start
            check_max = servo_settings.position_limit_end

        if position < check_min or position > check_max:
            in_range = False
        else:
            in_range = True

        return position, in_range

    def calculate_positions_for_frame(self, frame, pose_bones, scene, precision):
        scene.frame_set(frame)

        for pose_bone in pose_bones:
            bone = pose_bone.bone
            position, in_range = self.calculate_position(pose_bone, precision)

            if not in_range:
                raise RuntimeError(
                    'Calculated position %d for bone %s is out of range at frame %d.' %
                    (position, bone.name, frame)
                )

            self.positions[bone.name].append(str(position))

    def calculate_positions(self, context, precision):
        pose_bones = []
        scene = context.scene
        window_manager = context.window_manager
        start = scene.frame_start
        end = scene.frame_end + 1

        self.positions = {}

        for pose_bone in context.object.pose.bones:
            if pose_bone.bone.servo_settings.active:
                pose_bones.append(pose_bone)
                self.positions[pose_bone.bone.name] = []

        if precision == 0:
            precision = None

        window_manager.progress_begin(min=start, max=end)

        for frame in range(start, end):
            self.calculate_positions_for_frame(
                frame, pose_bones, scene, precision)
            window_manager.progress_update(frame)

        window_manager.progress_end()

        return self.positions
