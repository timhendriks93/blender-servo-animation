import re
import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport
from ..utils.system import get_blend_filename


class ArduinoExport(Operator, BaseExport, ExportHelper):
    bl_idname = "export_anim.servo_positions_arduino"
    bl_label = "Animation Servo Positions (.h)"
    bl_description = "Save an Arduino header file with servo position values of the active armature"

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

    def export(self, positions, context):
        variable_type = 'int' if self.precision == 0 else 'float'
        fps, frames, seconds = self.get_time_meta(context.scene)
        filename = get_blend_filename()

        content = (
            "/*\n  Blender Animation Servo Positions\n\n  "
            f"FPS: {fps}\n  Frames: {frames}\n  Seconds: {seconds}\n  "
            f"Bones: {len(positions)}\n  Armature: {context.object.name}\n  "
            f"File: {filename}\n*/\n\n"
        )

        for bone_name in positions:
            bone_positions = positions[bone_name]
            variable_name = re.sub('[^a-zA-Z0-9_]', '', bone_name)
            content += f"const {variable_type} {variable_name}[{frames}] "

            if self.use_progmem:
                content += 'PROGMEM '

            content += '= {\n'

            for i in range(0, len(bone_positions), self.position_chunk_size):
                content += '  ' + \
                    ', '.join(
                        bone_positions[i:i + self.position_chunk_size]) + ',\n'

            content += '};\n'

        return content
