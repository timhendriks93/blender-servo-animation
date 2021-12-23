import re
import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .converter import ServoAnimationConverter


class ServoAnimationArduinoExport(Operator, ExportHelper):
    bl_idname = "export_anim.servo_positions_arduino"
    bl_label = "Export Animation Servo Positions (.h)"
    bl_description = "Save an Arduino header file with servo position values from an armature"

    filename_ext = ".h"
    position_chunk_size = 50

    filter_glob: bpy.props.StringProperty(
        default="*.h",
        options={'HIDDEN'},
        maxlen=255
    )
    precision: bpy.props.IntProperty(
        name="Precision",
        description="The number of decimal digits to round to",
        default=0,
        min=0,
        max=6
    )
    use_progmem: bpy.props.BoolProperty(
        name="Add PROGMEM modifier",
        description=(
            "Add the PROGMEM modifier to each position array which enables "
            "an Arduino micro controller to handle large arrays"
        ),
        default=True
    )

    @classmethod
    def poll(cls, context):
        return context.object and context.object.type == 'ARMATURE'

    def execute(self, context):
        scene = context.scene
        original_frame = scene.frame_current

        try:
            converter = ServoAnimationConverter()
            positions = converter.calculate_positions(context, self.precision)
            frames = scene.frame_end - scene.frame_start + 1
            variable_type = 'int' if self.precision == 0 else 'float'
            seconds = round(frames / scene.render.fps)
            filename = bpy.path.basename(bpy.context.blend_data.filepath)
            content = (
                '/*\n  Blender Animation Servo Positions\n\n  '
                'FPS: %d\n  Frames: %d\n  Seconds: %d\n  Bones: %d\n  '
                'Armature: %s\n  File: %s\n*/\n\n'
            ) % (scene.render.fps, frames, seconds, len(positions), context.object.name, filename)

            for bone_name in positions:
                bone_positions = positions[bone_name]
                variable_name = re.sub('[^a-zA-Z0-9_]', '', bone_name)
                content += 'const %s %s[%d] ' % (variable_type,
                                                 variable_name, frames)

                if self.use_progmem:
                    content += 'PROGMEM '

                content += '= {\n'

                for i in range(0, len(bone_positions), self.position_chunk_size):
                    content += '  ' + \
                        ', '.join(
                            bone_positions[i:i + self.position_chunk_size]) + ',\n'

                content += '};\n'

            content += '\n'
        except RuntimeError as error:
            scene.frame_set(original_frame)
            self.report({'ERROR'}, str(error))

            return {'CANCELLED'}

        scene.frame_set(original_frame)

        file = open(self.filepath, 'w', encoding='utf-8')
        file.write(content)
        file.close()

        return {'FINISHED'}