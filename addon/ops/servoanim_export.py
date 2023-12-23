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

    def export(self, positions, context):
        fps, frames, seconds = self.get_time_meta(context.scene)
        positions_keys = list(positions.keys())
        ids = ",".join(str(x) for x in positions_keys)

        content = f"fps:{fps} frames:{frames} seconds:{seconds} ids:{ids}\n\n"

        for frame in range(frames):
            for servo_id in range(255):
                if servo_id not in positions:
                    continue
                pos = positions[servo_id][frame]
                content += str(pos) + " "
            content = content[:-1] + "\n"

        return content
