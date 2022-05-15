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
        scene = context.scene
        original_frame = scene.frame_current

        try:
            positions = calculate_positions(context, self.precision)
            fps = scene.render.fps
            frames = scene.frame_end - scene.frame_start + 1
            seconds = round(frames / scene.render.fps)
            bones = len(positions)
            armature = context.object.name
            filename = bpy.path.basename(bpy.context.blend_data.filepath)
            content = self.export(fps, frames, seconds,
                                  bones, positions, armature, filename)
        except RuntimeError as error:
            scene.frame_set(original_frame)
            self.report({'ERROR'}, str(error))

            return {'CANCELLED'}

        scene.frame_set(original_frame)

        file = open(self.filepath, 'w', encoding='utf-8')
        file.write(content)
        file.close()

        end = time.time()
        duration = end - start
        self.report(
            {'INFO'}, 'Animation servo positions exported after %d seconds' % duration)

        return {'FINISHED'}
