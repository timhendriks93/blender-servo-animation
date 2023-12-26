import time
import bpy

from ..utils.converter import calculate_positions
from ..utils.live_mode import LiveMode


class BaseExport:
    COMMAND_START = 0x3C
    COMMAND_END = 0x3E

    precision: bpy.props.IntProperty(
        name="Precision",
        description="The number of decimal digits to round to",
        default=0,
        min=0,
        max=6
    )

    @classmethod
    def poll(cls, context):
        if not context.object or context.object.type != 'ARMATURE':
            return False
        for pose_bone in context.object.pose.bones:
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
            positions = calculate_positions(context, self.precision)
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
        self.report(
            {'INFO'}, f"Animation servo positions exported after {duration} seconds")

        return {'FINISHED'}

    @classmethod
    def get_command(cls, servo_id, position):
        command = [cls.COMMAND_START, servo_id]
        command += position.to_bytes(2, 'big')
        command += [cls.COMMAND_END]

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
