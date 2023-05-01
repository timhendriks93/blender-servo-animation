import re
import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport
from ..utils.servo_settings import get_pose_bone_by_servo_id


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

    progmem: bpy.props.BoolProperty(
        name="Add PROGMEM modifier",
        description=(
            "Add the PROGMEM modifier to each position array which enables "
            "an Arduino micro controller to handle large arrays"
        ),
        default=True
    )

    animation_variables: bpy.props.BoolProperty(
        name="Add animation variables",
        description="Add the fps and frames count as constant variables",
        default=True
    )

    namespace: bpy.props.BoolProperty(
        name="Add scene namespace",
        description=(
            "Use the current scene name to wrap the position arrays and "
            "variables in a namespace"
        )
    )

    def export(self, positions, context):
        variable_type = 'int' if self.precision == 0 else 'float'
        fps, frames, seconds = self.get_time_meta(context.scene)
        filename = self.get_blend_filename()

        content = (
            "/*\n  Blender Servo Animation Positions\n\n  "
            f"FPS: {fps}\n  Frames: {frames}\n  Seconds: {seconds}\n  "
            f"Bones: {len(positions)}\n  Armature: {context.object.name}\n  "
            f"Scene: {context.scene.name}\n  File: {filename}\n*/\n"
        )

        if self.progmem or self.animation_variables:
            content += "\n#include <Arduino.h>\n"

        if self.namespace:
            content += f"\nnamespace {context.scene.name} {{\n"

        if self.animation_variables:
            content += (
                f"\nconst byte FPS = {fps};"
                f"\nconst int FRAMES = {frames};\n"
            )

        for servo_id in positions:
            pose_bone = get_pose_bone_by_servo_id(servo_id, context.scene)
            bone_positions = list(map(str, positions[servo_id]))
            variable_name = re.sub('[^a-zA-Z0-9_]', '', pose_bone.bone.name)
            array_size = "FRAMES" if self.animation_variables else frames
            content += (
                f"\n// Servo ID: {servo_id}\n"
                f"const {variable_type} {variable_name}[{array_size}] "
            )

            if self.progmem:
                content += 'PROGMEM '

            content += '= {\n'

            for i in range(0, len(bone_positions), self.position_chunk_size):
                content += '  ' + \
                    ', '.join(
                        bone_positions[i:i + self.position_chunk_size]) + ',\n'

            content += '};\n'

        if self.namespace:
            content += f"\n}} // namespace {context.scene.name}\n"

        return content
