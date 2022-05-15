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
        original_frame = context.scene.frame_current

        try:
            positions = calculate_positions(context, self.precision)
            content = self.export(positions, context)
        except RuntimeError as error:
            context.scene.frame_set(original_frame)
            self.report({'ERROR'}, str(error))

            return {'CANCELLED'}

        context.scene.frame_set(original_frame)

        with open(self.filepath, 'w', encoding='utf-8') as file:
            file.write(content)

        end = time.time()
        duration = round(end - start)
        self.report(
            {'INFO'}, f"Animation servo positions exported after {duration} seconds")

        return {'FINISHED'}

    @classmethod
    def get_time_meta(cls, scene):
        fps = scene.render.fps
        frames = scene.frame_end - scene.frame_start + 1
        seconds = round(frames / scene.render.fps)

        return fps, frames, seconds

    @classmethod
    def get_filename(cls):
        return bpy.path.basename(bpy.context.blend_data.filepath)
