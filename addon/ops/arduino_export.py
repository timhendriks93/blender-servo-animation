import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport


class ArduinoExport(Operator, BaseExport, ExportHelper):
    bl_idname = "export_anim.servo_animation_arduino"
    bl_label = "Servo Animation (.h)"
    bl_description = "Save an Arduino header file with servo position values of the active armature"

    filename_ext = ".h"
    chunk_size = 12

    filter_glob: bpy.props.StringProperty(
        default="*.h",
        options={'HIDDEN'},
        maxlen=255
    )

    namespace: bpy.props.BoolProperty(
        name="Add scene namespace",
        description=(
            "Use the current scene name to wrap the position arrays and "
            "variables in a namespace"
        )
    )

    def export(self, positions, filepath, context):
        fps, frames, seconds = self.get_time_meta(context.scene)
        filename = self.get_blend_filename()

        content = (
            "/*\n  Blender Servo Animation Positions\n\n  "
            f"FPS: {fps}\n  Frames: {frames}\n  Seconds: {seconds}\n  "
            f"Bones: {len(positions[0])}\n  Armature: {context.object.name}\n  "
            f"Scene: {context.scene.name}\n  File: {filename}\n*/\n\n"
            "#include <Arduino.h>\n"
        )

        commands = self.get_commands(positions)
        length = len(commands)
        lines = self.join_by_chunk_size(commands, self.chunk_size)

        if self.namespace:
            content += f"\nnamespace {context.scene.name} {{\n"

        content += (
            f"\nconst byte FPS = {fps};"
            f"\nconst int FRAMES = {frames};"
            f"\nconst int LENGTH = {length};\n\n"
        )

        content += f'const byte PROGMEM ANIMATION_DATA[LENGTH] = {{\n{lines}}};\n'

        if self.namespace:
            content += f"\n}} // namespace {context.scene.name}\n"

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)

    @classmethod
    def join_by_chunk_size(cls, iterable, chunk_size):
        output = ''
        str_iterable = list(map(cls.format_hex, iterable))

        for i in range(0, len(str_iterable), chunk_size):
            output += '    ' + ', '.join(str_iterable[i:i + chunk_size]) + ',\n'

        return output

    @classmethod
    def format_hex(cls, byte):
        return f'{byte:#04x}'
