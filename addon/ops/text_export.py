import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport


class TextExport(Operator, BaseExport, ExportHelper):
    bl_idname = "export_anim.servo_animation_text"
    bl_label = "Servo Animation (.txt)"
    bl_description = "Save a text file with servo position values of the active scene"

    filename_ext = ".txt"

    filter_glob: bpy.props.StringProperty(
        default="*.txt",
        options={'HIDDEN'},
        maxlen=255
    )

    def export(self, positions, filepath, _context):
        lines = [self.format_frame(frame_positions) for frame_positions in positions]
        content = "\n".join(lines)

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def format_frame(frame_positions):
        if not frame_positions:
            return ""

        commands = [
            f"{servo_id}={frame_positions[servo_id]}"
            for servo_id in frame_positions
        ]
        return ",".join(commands)
