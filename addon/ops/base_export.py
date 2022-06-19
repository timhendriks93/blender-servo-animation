import time
import bpy

from ..utils.converter import calculate_positions


class BaseExport:
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
        servo_animation = context.window_manager.servo_animation
        original_frame = context.scene.frame_current
        original_live_mode = servo_animation.live_mode

        if original_live_mode is True:
            bpy.ops.export_anim.stop_live_mode()

        try:
            positions = calculate_positions(context, self.precision)
            content = self.export(positions, context)
        except RuntimeError as error:
            self.report({'ERROR'}, str(error))

            return {'CANCELLED'}
        finally:
            context.scene.frame_set(original_frame)

            if original_live_mode is True:
                bpy.ops.export_anim.start_live_mode('INVOKE_DEFAULT')

        with open(self.filepath, 'w', encoding='utf-8') as file:
            file.write(content)

        end = time.time()
        duration = round(end - start)
        self.report(
            {'INFO'}, f"Animation servo positions exported after {duration} seconds")

        return {'FINISHED'}

    @staticmethod
    def get_time_meta(scene):
        fps = scene.render.fps
        frames = scene.frame_end - scene.frame_start + 1
        seconds = round(frames / scene.render.fps)

        return fps, frames, seconds
