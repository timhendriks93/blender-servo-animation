import time
import bpy

from ..utils.converter import calculate_positions
from ..utils.live_mode import LiveMode
from ..utils.servo_settings import get_active_pose_bones


class BaseExport:
    COMMAND_START = 0x3C
    COMMAND_END = 0x3E
    LINE_BREAK = 10

    skip_duplicates: bpy.props.BoolProperty(
        name="Skip unchanged positions",
        description="Skip positions which haven't changed since the last frame",
        default=True
    )

    @classmethod
    def poll(cls, context):
        pose_bones = get_active_pose_bones(context.scene)

        for pose_bone in pose_bones:
            if pose_bone.bone.servo_settings.active:
                return True

        return False

    def execute(self, context):
        start = time.time()
        original_frame = context.scene.frame_current
        original_live_mode = LiveMode.is_connected()

        if original_live_mode is True:
            bpy.ops.servo_animation.stop_live_mode()

        try:
            positions = calculate_positions(context, self.skip_duplicates)
            self.export(positions, self.filepath, context)
        except RuntimeError as error:
            self.report({'ERROR'}, str(error))

            return {'CANCELLED'}
        finally:
            context.scene.frame_set(original_frame)

            if original_live_mode is True:
                bpy.ops.servo_animation.start_live_mode('INVOKE_DEFAULT')

        end = time.time()
        duration = round(end - start)
        unit = "second" if duration == 1 else "seconds"
        self.report(
            {'INFO'}, f"Animation servo positions exported after {duration} {unit}")

        return {'FINISHED'}

    def get_commands(self, positions):
        commands = []

        for frame_positions in positions:
            for servo_id in frame_positions:
                position = frame_positions[servo_id]
                commands += self.get_command(servo_id, position)

            commands.append(self.LINE_BREAK)

        return commands

    def get_command(self, servo_id, position):
        command = [self.COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [self.COMMAND_END]

        return command

    @staticmethod
    def get_time_meta(scene):
        fps = scene.render.fps
        frames = scene.frame_end - scene.frame_start + 1
        seconds = round(frames / scene.render.fps)

        return fps, frames, seconds

    @staticmethod
    def get_blend_filename():
        return bpy.path.basename(bpy.context.blend_data.filepath)
