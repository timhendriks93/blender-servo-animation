import re
import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport


class ServoAnimationArduinoExport(Operator, BaseExport, ExportHelper):
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
    use_progmem: bpy.props.BoolProperty(
        name="Add PROGMEM modifier",
        description=(
            "Add the PROGMEM modifier to each position array which enables "
            "an Arduino micro controller to handle large arrays"
        ),
        default=True
    )

    def export(self, fps, frames, seconds, bones, positions, armature, filename):
        variable_type = 'int' if self.precision == 0 else 'float'
        content = (
            '/*\n  Blender Animation Servo Positions\n\n  '
            'FPS: %d\n  Frames: %d\n  Seconds: %d\n  Bones: %d\n  '
            'Armature: %s\n  File: %s\n*/\n\n'
        ) % (fps, frames, seconds, bones, armature, filename)

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

        return content
