import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport


class BinaryExport(Operator, BaseExport, ExportHelper):
    bl_idname = "export_anim.servo_animation_binary"
    bl_label = "Servo Animation (.bin)"
    bl_description = "Save a binary file with servo position values of the active armature"

    filename_ext = ".bin"

    filter_glob: bpy.props.StringProperty(
        default="*.bin",
        options={'HIDDEN'},
        maxlen=255
    )

    def export(self, positions, filepath, _context):
        commands = self.get_commands(positions)

        with open(filepath, 'wb') as file:
            file.write(bytes(commands))
