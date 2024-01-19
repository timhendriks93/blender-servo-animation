import bpy

from bpy.types import Operator
from bpy_extras.io_utils import ExportHelper
from .base_export import BaseExport


class ServoanimExport(Operator, BaseExport, ExportHelper):
    bl_idname = "export_anim.servo_positions_servoanim"
    bl_label = "Animation Servo Positions (.servoanim)"
    bl_description = "Save an SD card optimized file with servo position values of the active armature"

    filename_ext = ".servoanim"

    filter_glob: bpy.props.StringProperty(
        default="*.servoanim",
        options={'HIDDEN'},
        maxlen=255
    )

    def export(self, positions, filepath, context):
        _fps, frames, _seconds = self.get_time_meta(context.scene)
        commands = self.get_commands(frames, positions)

        with open(filepath, 'wb') as file:
            file.write(bytes(commands))
